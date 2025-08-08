import logging
import os
import argparse
from typing import Annotated, Literal, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator
from tavily import TavilyClient, InvalidAPIKeyError, UsageLimitExceededError
import json
import uvicorn
from dotenv import load_dotenv
from functools import lru_cache
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from tavily_server_mcp.config import load_config


# 版本信息
VERSION = "1.0.0"


# 从包中获取版本
from tavily_server_mcp import __version__ as package_version

# API密钥验证
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 初始化FastMCP和FastAPI
mcp = FastMCP("Tavily Search 🚀")
app = FastAPI(
    title="Tavily MCP API",
    description="Tavily搜索MCP服务API",
    version=VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 缓存客户端实例
@lru_cache()
def get_tavily_client(config_path=None):
    # 加载配置
    config = load_config(config_path)
    tavily_config = config.get("tavily", {})
    
    # 优先使用环境变量中的API密钥
    api_key = os.getenv("TAVILY_API_KEY") or os.getenv("API_KEY")
    
    # 如果环境变量中没有API密钥，则尝试从配置文件中获取
    if not api_key:
        api_key = tavily_config.get("api_key")
    
    if not api_key:
        raise ValueError("TAVILY_API_KEY or API_KEY environment variable or config file is required")
    
    # 获取其他配置选项
    search_options = tavily_config.get("search_options", {})
    
    # 创建客户端实例
    client = TavilyClient(api_key=api_key)
    
    # 记录日志
    logger.info(f"Tavily客户端已初始化，使用配置: {search_options}")
    
    return client

# API密钥验证依赖
async def verify_api_key(api_key: str = Depends(API_KEY_HEADER)):
    if not api_key or api_key != os.getenv("MCP_API_KEY"):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return api_key

# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": VERSION}

# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global error handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )


class SearchBase(BaseModel):
    """Base parameters for Tavily search."""
    query: Annotated[str, Field(description="Search query")]
    max_results: Annotated[
        int,
        Field(
            default=5,
            description="Maximum number of results to return",
            gt=0,
            lt=20,
        ),
    ]
    include_domains: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="List of domains to specifically include in the search results (e.g. ['example.com', 'test.org'] or 'example.com')",
        ),
    ]
    exclude_domains: Annotated[
        list[str] | None,
        Field(
            default=None,
            description="List of domains to specifically exclude from the search results (e.g. ['example.com', 'test.org'] or 'example.com')",
        ),
    ]
    days: Annotated[
        int | None,
        Field(
            default=None,
            description="Number of days back to search (default is 3)",
            gt=0,
            le=365,
        ),
    ]
    country: Annotated[
        str | None,
        Field(
            default=None,
            description="Country to search in (e.g. 'US', 'UK', 'AU')",
        ),
    ]
    time_range : Annotated[
        str | None,
        Field(
            default=None,
            description="Time range to search in (e.g. 'month', 'year')",
        ),
    ]

    @field_validator('include_domains', 'exclude_domains', mode='before')
    @classmethod
    def parse_domains_list(cls, v):
        """Parse domain lists from various input formats."""
        if v is None:
            return []
        if isinstance(v, list):
            return [domain.strip() for domain in v if domain.strip()]
        if isinstance(v, str):
            v = v.strip()
            if not v:
                return []
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [domain.strip() for domain in parsed if domain.strip()]
                return [parsed.strip()]
            except json.JSONDecodeError:
                if ',' in v:
                    return [domain.strip() for domain in v.split(',') if domain.strip()]
                return [v]
        return []


class GeneralSearch(SearchBase):
    """Parameters for general web search."""
    search_depth: Annotated[
        Literal["basic", "advanced"],
        Field(
            default="basic",
            description="Depth of search - 'basic' or 'advanced'",
        ),
    ]


class AnswerSearch(SearchBase):
    """Parameters for search with answer."""
    search_depth: Annotated[
        Literal["basic", "advanced"],
        Field(
            default="advanced",
            description="Depth of search - 'basic' or 'advanced'",
        ),
    ]


class NewsSearch(SearchBase):
    """Parameters for news search."""
    days: Annotated[
        int | None,
        Field(
            default=None,
            description="Number of days back to search (default is 3)",
            gt=0,
            le=365,
        ),
    ]


class SearchResponse(BaseModel):
    """标准化的搜索响应格式"""
    query: str
    answer: Optional[str] = None
    results: list[dict]
    included_domains: list[str] = Field(default_factory=list)
    excluded_domains: list[str] = Field(default_factory=list)

def format_results(response: dict, format_type: str = "text") -> dict:
    """格式化Tavily搜索结果
    
    Args:
        response: Tavily API响应
        format_type: 输出格式类型 (text, json, markdown)
    """
    logger.info(f"Formatting Tavily Search Results: {response}")
    
    # 构建标准响应对象
    search_response = SearchResponse(
        query=response.get("query", ""),
        answer=response.get("answer"),
        results=response.get("results", []),
        included_domains=response.get("included_domains", []),
        excluded_domains=response.get("excluded_domains", [])
    )
    
    if format_type == "json":
        return search_response.model_dump()
    
    output = []
    
    # 添加过滤器信息
    if search_response.included_domains or search_response.excluded_domains:
        filters = []
        if search_response.included_domains:
            filters.append(f"Including domains: {', '.join(search_response.included_domains)}")
        if search_response.excluded_domains:
            filters.append(f"Excluding domains: {', '.join(search_response.excluded_domains)}")
        output.append("Search Filters:")
        output.extend(filters)
        output.append("")

    # 添加答案和来源
    if search_response.answer:
        if format_type == "markdown":
            output.append(f"### Answer\n{search_response.answer}")
            output.append("\n### Sources")
        else:
            output.append(f"Answer: {search_response.answer}")
            output.append("\nSources:")
        for result in search_response.results:
            output.append(f"- {result['title']}: {result['url']}")
        output.append("")

    # 添加详细结果
    if format_type == "markdown":
        output.append("### Detailed Results")
    else:
        output.append("Detailed Results:")
    
    for result in search_response.results:
        output.append(f"\nTitle: {result['title']}")
        output.append(f"URL: {result['url']}")
        if result.get("published_date"):
            output.append(f"Published: {result['published_date']}")

    return {"text": "\n".join(output), "data": search_response.model_dump()}


class SearchResult(BaseModel):
    """搜索结果响应模型"""
    text: str
    data: dict

@mcp.tool
async def tavily_web_search(
    query: str,
    max_results: int = 5,
    search_depth: Literal["basic", "advanced"] = "basic",
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    format_type: Literal["text", "json", "markdown"] = "text",
    api_key: str = Depends(verify_api_key)
) -> SearchResult:
    """执行Tavily AI搜索引擎的综合网络搜索
    
    Args:
        query: 搜索查询
        max_results: 返回结果数量
        search_depth: 搜索深度 (basic或advanced)
        include_domains: 包含的域名列表
        exclude_domains: 排除的域名列表
        format_type: 响应格式类型
        api_key: API密钥
    """
    logger.info(f"Tavily Web Search: {query}")
    
    try:
        # 加载配置
        config = load_config(None)
        tavily_config = config.get("tavily", {})
        search_options = tavily_config.get("search_options", {})
        
        # 合并配置和参数
        args = GeneralSearch(
            query=query,
            max_results=max_results or search_options.get("max_results", 5),
            search_depth=search_depth or search_options.get("search_depth", "basic"),
            include_domains=include_domains or search_options.get("include_domains", []),
            exclude_domains=exclude_domains or search_options.get("exclude_domains", [])
        )
        
        # 使用缓存的客户端实例
        client = get_tavily_client()
        
        # 准备搜索参数
        search_params = {
            "query": args.query,
            "max_results": args.max_results,
            "search_depth": args.search_depth,
            "include_domains": args.include_domains or [],
            "exclude_domains": args.exclude_domains or []
        }
        
        # 添加可选参数
        if search_options.get("country"):
            search_params["country"] = search_options["country"]
        if search_options.get("time_range"):
            search_params["time_range"] = search_options["time_range"]
        
        # 执行搜索
        response = await client.search(**search_params)
        
        # 添加域名过滤信息
        if args.include_domains:
            response["included_domains"] = args.include_domains
        if args.exclude_domains:
            response["excluded_domains"] = args.exclude_domains
            
        # 添加原始查询
        response["query"] = query
        
        # 格式化结果
        result = format_results(response, format_type)
        return SearchResult(**result)
        
    except (InvalidAPIKeyError, UsageLimitExceededError) as e:
        logger.error(f"Tavily API error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@mcp.tool
async def tavily_answer_search(
    query: str,
    max_results: int = 5,
    search_depth: Literal["basic", "advanced"] = "advanced",
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    format_type: Literal["text", "json", "markdown"] = "text",
    api_key: str = Depends(verify_api_key)
) -> SearchResult:
    """执行Tavily AI搜索并生成直接答案
    
    Args:
        query: 搜索查询
        max_results: 返回结果数量
        search_depth: 搜索深度 (basic或advanced)
        include_domains: 包含的域名列表
        exclude_domains: 排除的域名列表
        format_type: 响应格式类型
        api_key: API密钥
    """
    logger.info(f"Tavily Answer Search: {query}")
    
    try:
        # 加载配置
        config = load_config(None)
        tavily_config = config.get("tavily", {})
        search_options = tavily_config.get("search_options", {})
        
        # 合并配置和参数
        args = AnswerSearch(
            query=query,
            max_results=max_results or search_options.get("max_results", 5),
            search_depth=search_depth or search_options.get("search_depth", "advanced"),
            include_domains=include_domains or search_options.get("include_domains", []),
            exclude_domains=exclude_domains or search_options.get("exclude_domains", [])
        )
        
        # 使用缓存的客户端实例
        client = get_tavily_client()
        
        # 准备搜索参数
        search_params = {
            "query": args.query,
            "max_results": args.max_results,
            "search_depth": args.search_depth,
            "include_answer": True,
            "include_domains": args.include_domains or [],
            "exclude_domains": args.exclude_domains or []
        }
        
        # 添加可选参数
        if search_options.get("country"):
            search_params["country"] = search_options["country"]
        if search_options.get("time_range"):
            search_params["time_range"] = search_options["time_range"]
        
        # 执行搜索
        response = await client.search(**search_params)
        
        # 添加域名过滤信息
        if args.include_domains:
            response["included_domains"] = args.include_domains
        if args.exclude_domains:
            response["excluded_domains"] = args.exclude_domains
            
        # 添加原始查询
        response["query"] = query
        
        # 格式化结果
        result = format_results(response, format_type)
        return SearchResult(**result)
        
    except (InvalidAPIKeyError, UsageLimitExceededError) as e:
        logger.error(f"Tavily API error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@mcp.tool
async def tavily_news_search(
    query: str,
    max_results: int = 5,
    days: int | None = None,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    format_type: Literal["text", "json", "markdown"] = "text",
    api_key: str = Depends(verify_api_key)
) -> SearchResult:
    """执行Tavily新闻搜索
    
    Args:
        query: 搜索查询
        max_results: 返回结果数量
        days: 搜索的时间范围（天数）
        include_domains: 包含的新闻源域名列表
        exclude_domains: 排除的新闻源域名列表
        format_type: 响应格式类型
        api_key: API密钥
    """
    logger.info(f"Tavily News Search: {query}")
    
    try:
        # 加载配置
        config = load_config(None)
        tavily_config = config.get("tavily", {})
        search_options = tavily_config.get("search_options", {})
        news_options = tavily_config.get("news_options", {})
        
        # 合并配置和参数
        args = NewsSearch(
            query=query,
            max_results=max_results or news_options.get("max_results", 5),
            days=days or news_options.get("days", 3),
            include_domains=include_domains or news_options.get("include_domains", []),
            exclude_domains=exclude_domains or news_options.get("exclude_domains", [])
        )
        
        # 使用缓存的客户端实例
        client = get_tavily_client()
        
        # 准备搜索参数
        search_params = {
            "query": args.query,
            "max_results": args.max_results,
            "topic": "news",
            "days": args.days if args.days is not None else 3,
            "include_domains": args.include_domains or [],
            "exclude_domains": args.exclude_domains or []
        }
        
        # 添加可选参数
        if search_options.get("country") or news_options.get("country"):
            search_params["country"] = news_options.get("country") or search_options.get("country")
        
        # 执行搜索
        response = await client.search(**search_params)
        
        # 添加域名过滤信息
        if args.include_domains:
            response["included_domains"] = args.include_domains
        if args.exclude_domains:
            response["excluded_domains"] = args.exclude_domains
            
        # 添加原始查询
        response["query"] = query
        
        # 格式化结果
        result = format_results(response, format_type)
        return SearchResult(**result)
        
    except (InvalidAPIKeyError, UsageLimitExceededError) as e:
        logger.error(f"Tavily API error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    from fastapi.middleware.cors import CORSMiddleware
    
    # 加载环境变量
    load_dotenv()
    
    # 验证必要的环境变量
    required_env_vars = ["TAVILY_API_KEY", "MCP_API_KEY"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    # 配置FastAPI应用
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 启动服务器
    logger.info("Starting Tavily MCP server...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8083,
        log_level="info"
    )


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="启动Tavily MCP服务器")
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.getenv("PORT", "8083")),
        help="服务器端口号 (默认: 8083)"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0",
        help="服务器主机地址 (默认: 0.0.0.0)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        help="启用自动重载模式"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        help="配置文件路径"
    )
    parser.add_argument(
        "--log-level", 
        type=str, 
        choices=["debug", "info", "warning", "error", "critical"],
        default="info",
        help="日志级别"
    )
    return parser.parse_args()

def tavily_main():
    """Tavily MCP服务器的入口点"""
    args = parse_args()
    
    # 加载配置
    config = load_config(args.config)
    tavily_config = config.get("tavily", {})
    api_config = config.get("api", {})
    
    # 命令行参数优先级高于配置文件
    host = args.host or tavily_config.get("host", "0.0.0.0")
    port = args.port or tavily_config.get("port", 8083)
    reload = args.reload or tavily_config.get("reload", False)
    log_level = args.log_level or tavily_config.get("log_level", "info")
    
    # 设置日志级别
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 检查API密钥
    api_key = os.getenv("API_KEY") or os.getenv("TAVILY_API_KEY")
    if not api_key:
        logger.warning("API_KEY或TAVILY_API_KEY环境变量未设置")
    
    # 配置CORS
    cors_origins = api_config.get("cors_origins", ["*"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logger.info(f"正在启动Tavily MCP服务器，版本: {package_version}")
    logger.info(f"端口: {port}, 主机: {host}")

    uvicorn.run(
        "tavily_server_mcp.tavily_mcp_server:app",
        host=host,
        port=port,
        reload=reload,
        log_level=log_level.lower()
    )

if __name__ == "__main__":
    tavily_main()
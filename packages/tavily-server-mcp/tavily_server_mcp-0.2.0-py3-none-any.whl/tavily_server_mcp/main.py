import logging
import os
import argparse
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from tavily_server_mcp.config import load_config

# 加载环境变量
load_dotenv()

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.get("/")
async def root():
    return {"message": "MCP Server is running"}

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="启动MCP服务器")
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.getenv("PORT", "8000")),
        help="服务器端口号 (默认: 8000)"
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

def main():
    """Main entry point for the MCP server."""
    args = parse_args()
    
    # 加载配置
    config = load_config(args.config)
    server_config = config.get("server", {})
    api_config = config.get("api", {})
    
    # 命令行参数优先级高于配置文件
    host = args.host or server_config.get("host", "0.0.0.0")
    port = args.port or server_config.get("port", 8000)
    reload = args.reload or server_config.get("reload", False)
    log_level = args.log_level or server_config.get("log_level", "info")
    
    # 设置日志级别
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 检查API密钥
    api_key = os.getenv("API_KEY")
    if not api_key:
        logger.warning("API_KEY环境变量未设置")
    
    # 配置CORS
    cors_origins = api_config.get("cors_origins", ["*"])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    logger.info(f"正在启动MCP服务器，端口: {port}, 主机: {host}")
    uvicorn.run(
        "tavily_server_mcp.main:app", 
        host=host, 
        port=port,
        reload=reload,
        log_level=log_level.lower()
    )

if __name__ == "__main__":
    main()
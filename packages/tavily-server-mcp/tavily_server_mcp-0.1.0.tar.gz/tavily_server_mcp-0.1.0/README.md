# Your MCP Server

A custom MCP (Model Control Protocol) server implementation that can be easily integrated into AI applications.

## Installation

```bash
pip install your-mcp-server
```

## Usage

### 基本用法

你可以在AI应用程序的配置中使用此服务器，如下所示：

```json
{
  "mcpServers": {
    "your-custom-server": {
      "command": "uvx",
      "args": ["your-mcp-server"],
      "env": {
        "PORT": "8000",
        "API_KEY": "${input:yourApiKey}"
      }
    }
  }
}
```

### Tavily搜索服务器

本包还提供了一个专门用于Tavily搜索的MCP服务器：

```json
{
  "mcpServers": {
    "tavily-search": {
      "command": "uvx",
      "args": ["tavily-mcp-server"],
      "env": {
        "PORT": "8083",
        "API_KEY": "${input:tavilyApiKey}"
      }
    }
  }
}
```

### 命令行选项

两个服务器都支持以下命令行选项：

```bash
# 基本MCP服务器
your-mcp-server --port 8000 --host 0.0.0.0 --reload --config /path/to/config.json --log-level debug

# Tavily MCP服务器
tavily-mcp-server --port 8083 --host 0.0.0.0 --reload --config /path/to/config.json --log-level debug
```

### 配置文件

你可以使用配置文件来设置服务器的各种参数。配置文件是一个JSON文件，可以通过`--config`选项指定。如果不指定，服务器将尝试从以下位置加载配置文件：

1. 当前工作目录下的`config.json`
2. 用户主目录下的`.your_mcp_server/config.json`

配置文件示例（`config.example.json`）：

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 8000,
    "reload": false,
    "log_level": "info"
  },
  "tavily": {
    "host": "0.0.0.0",
    "port": 8083,
    "reload": false,
    "log_level": "info",
    "api_key": "",
    "search_options": {
      "max_results": 5,
      "search_depth": "basic",
      "include_domains": [],
      "exclude_domains": [],
      "country": "US",
      "time_range": "month"
    },
    "news_options": {
      "max_results": 5,
      "days": 3,
      "include_domains": [],
      "exclude_domains": [],
      "country": "US"
    }
  },
  "api": {
    "cors_origins": ["*"],
    "rate_limit": {
      "enabled": false,
      "limit": 100,
      "period": 3600
    }
  }
}
```

注意：命令行参数的优先级高于配置文件中的设置。

### 环境检查工具

本包还提供了一个命令行工具，用于检查环境变量和依赖项是否正确设置：

```bash
# 检查环境变量和依赖项
your-mcp-check --check

# 显示版本信息
your-mcp-check --version
```

## Development

### 基本开发流程

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run the server:
   ```bash
   your-mcp-server
   ```

### 使用Makefile

本项目提供了Makefile，可以使用以下命令：

```bash
# 安装开发依赖
make install-dev

# 运行测试
make test

# 格式化代码
make format

# 构建包
make build

# 发布到PyPI
make publish

# 查看所有可用命令
make help
```

## Docker 支持

本项目提供了Docker支持，可以通过以下方式使用：

### 使用Dockerfile

```bash
# 构建镜像
docker build -t your-mcp-server .

# 运行基本MCP服务器
docker run -p 8000:8000 -e API_KEY=your_api_key your-mcp-server

# 运行Tavily MCP服务器
docker run -p 8083:8083 -e API_KEY=your_api_key -e PORT=8083 your-mcp-server tavily-mcp-server --host 0.0.0.0 --port 8083
```

### 使用Docker Compose

```bash
# 设置环境变量
export API_KEY=your_api_key
export TAVILY_API_KEY=your_tavily_api_key

# 启动所有服务
docker-compose up

# 或者只启动特定服务
docker-compose up mcp-server
docker-compose up tavily-server
```

## Examples

在`examples`目录中提供了几个示例脚本：

1. `simple_usage.py` - 展示如何在代码中使用your-mcp-server包
2. `run_server.py` - 展示如何以编程方式启动MCP服务器

运行示例：

```bash
# 运行简单使用示例
python examples/simple_usage.py

# 运行服务器示例（基本MCP服务器）
python examples/run_server.py --server main --port 8000

# 运行服务器示例（Tavily MCP服务器）
python examples/run_server.py --server tavily --port 8083
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Publishing to PyPI

To publish this package to PyPI, follow these steps:

1. Make sure you have the latest build tools:
   ```bash
   pip install --upgrade build twine
   ```

2. Build the package:
   ```bash
   python -m build
   ```

3. Upload to PyPI:
   ```bash
   python -m twine upload dist/*
   ```

   You'll need to provide your PyPI username and password.

4. Alternatively, you can upload to Test PyPI first:
   ```bash
   python -m twine upload --repository testpypi dist/*
   ```

   Then install from Test PyPI:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ your-mcp-server
   ```
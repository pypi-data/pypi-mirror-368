# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

X-Pages MCP Server是一个基于Model Context Protocol (MCP)的HTML部署服务，让AI能够直接部署HTML内容并获取访问URL。项目使用Python实现，基于FastMCP框架构建。

## 开发命令

### 环境设置和依赖管理
```bash
# 使用uv安装依赖（推荐）
uv sync

# 或使用pip安装
pip install -e .

# 检查环境变量配置
uv run python start_server.py --check-env
```

### 运行和测试
```bash
# 启动MCP服务器 - STDIO模式（用于Claude Desktop）
uv run python start_server.py --transport stdio

# 启动MCP服务器 - SSE模式（用于Web应用）
uv run python start_server.py --transport sse

# 启动MCP服务器 - HTTP模式（用于API集成）
uv run python start_server.py --transport streamable-http

# 运行测试
uv run pytest

# 运行测试并显示覆盖率
uv run pytest --cov=x_pages_mcp

# 直接使用模块方式启动
uv run x-pages-mcp --transport stdio
```

### 代码质量检查
```bash
# Ruff代码检查和格式化
uv run ruff check src/
uv run ruff format src/

# MyPy类型检查
uv run mypy src/
```

## 项目架构

### 核心组件

1. **MCP服务器** (`src/x_pages_mcp/server.py`)
   - 基于FastMCP框架实现
   - 提供4个核心工具：deploy_html, delete_html, get_site_url, create_sample_html
   - 支持多种传输模式：stdio, sse, streamable-http
   - 配置通过环境变量管理

2. **启动器** (`start_server.py`)
   - 统一的服务器启动入口
   - 环境变量验证和错误处理
   - 支持命令行参数配置传输模式

3. **脚本集合** (`scripts/`)
   - 各传输模式的便捷启动脚本
   - start_stdio.sh, start_sse.sh, start_streamable.sh

### 关键数据流

1. **HTML部署流程**：
   - 生成24位随机站点名称 (`generate_site_name()`)
   - 构建API请求到X-Pages服务 (`/html/deploy`)
   - 返回访问URL和部署信息

2. **配置管理**：
   - `XPagesConfig` Pydantic模型管理配置
   - 必需环境变量：`X_PAGES_BASE_URL`, `X_PAGES_API_TOKEN`
   - 可选配置：`X_PAGES_TIMEOUT`

### 传输模式说明

- **STDIO模式**：用于Claude Desktop等本地客户端，通过标准输入输出通信
- **SSE模式**：基于Server-Sent Events的HTTP实时通信，适合Web应用
- **Streamable HTTP模式**：支持长连接和流式响应的HTTP API

## 环境变量配置

### 方法1：使用 .env 文件（推荐）

在项目根目录创建 `.env` 文件：

```bash
# .env 文件内容
X_PAGES_BASE_URL=https://your-domain.com
X_PAGES_API_TOKEN=your-secret-token
X_PAGES_TIMEOUT=30.0
```

启动服务器时会自动加载 `.env` 文件中的环境变量。

### 方法2：直接设置环境变量

```bash
export X_PAGES_BASE_URL=https://your-domain.com
export X_PAGES_API_TOKEN=your-secret-token
export X_PAGES_TIMEOUT=30.0  # 可选，默认30秒
```

## Claude Desktop配置示例

配置文件位置：
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "x-pages-html-deployment": {
      "command": "uv",
      "args": ["run", "python", "/absolute/path/to/start_server.py", "--transport", "stdio"],
      "env": {
        "X_PAGES_BASE_URL": "https://your-domain.com",
        "X_PAGES_API_TOKEN": "your-secret-token"
      }
    }
  }
}
```

## 安装和使用

### 从 PyPI 安装（正式版）

```bash
# 使用 uvx 运行（推荐）
uvx  x-pages-mcp --transport stdio

# 或安装后使用
pip install x-pages-mcp
x-pages-mcp --transport stdio

# 使用 uv 安装
uv add x-pages-mcp
uv run x-pages-mcp --transport stdio
```

### 从 TestPyPI 安装（测试版）

```bash
# 使用 uvx（需要双索引）
uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ x-pages-mcp --transport stdio

# 使用 pip（需要双索引）
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ x-pages-mcp
```

### 可用命令

安装后可使用以下命令：

```bash
# 查看帮助
x-pages-mcp --help

# STDIO 模式（默认）
x-pages-mcp --transport stdio

# SSE 模式
x-pages-mcp --transport sse  

# Streamable HTTP 模式
x-pages-mcp --transport streamable-http
```

### 环境变量配置

运行前需要配置环境变量：

```bash
export X_PAGES_BASE_URL=https://your-domain.com
export X_PAGES_API_TOKEN=your-api-token
```

或创建 `.env` 文件：
```bash
X_PAGES_BASE_URL=https://your-domain.com
X_PAGES_API_TOKEN=your-api-token
X_PAGES_TIMEOUT=30.0
```

## 包发布指南

本项目已配置完整的 PyPI 发布流程，支持一键构建和发布。

### 准备工作

1. **获取 PyPI API Token**
   - 访问 [PyPI Account Settings](https://pypi.org/manage/account/) 创建 API token
   - 访问 [TestPyPI Account Settings](https://test.pypi.org/manage/account/) 创建测试 token

2. **配置环境变量**
   在 `.env` 文件中添加：
   ```bash
   PYPI_TOKEN=your-production-pypi-token
   TESTPYPI_TOKEN=your-test-pypi-token
   ```

### 发布流程

#### 1. 准备发布
```bash
# 安装发布工具
uv sync

# 清理旧构建文件
rm -rf dist/ build/

# 构建包
uv run python -m build
```

#### 2. 验证包质量
```bash
# 检查包完整性
uv run twine check dist/*

# 查看包内容
tar -tzf dist/*.tar.gz | head -20
```

#### 3. 测试发布（推荐）
```bash
# 发布到 TestPyPI
uv run twine upload --repository testpypi dist/* --username __token__ --password $TESTPYPI_TOKEN

# 测试安装（需要同时使用 TestPyPI 和 PyPI 来解决依赖）
uvx --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ x-pages-mcp --help

# 或使用 pip 安装
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ x-pages-mcp
```

#### 4. 正式发布
```bash
# 发布到正式 PyPI
uv run twine upload dist/* --username __token__ --password $PYPI_TOKEN
```

### 配置文件方式（可选）

创建 `~/.pypirc` 文件：
```ini
[distutils]
index-servers = 
    pypi
    testpypi

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = <your-pypi-token>

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = <your-testpypi-token>
```

配置后可直接运行：
```bash
# 测试发布
uv run twine upload --repository testpypi dist/*

# 正式发布
uv run twine upload dist/*
```

### 版本管理

更新版本号需要修改 `pyproject.toml` 中的 `version` 字段：
```toml
[project]
name = "x-pages-mcp"
version = "0.2.0"  # 更新版本号
```

### 注意事项

- 发布前确保所有测试通过
- 每次发布都需要更新版本号
- 敏感文件（如 `.env`）已通过 `MANIFEST.in` 排除
- 建议先发布到 TestPyPI 测试，确认无误后再发布到正式 PyPI
"""X-Pages MCP Server for HTML deployment service."""

import asyncio
import os
import sys
import secrets
import string
from typing import Any, Dict, Optional
from urllib.parse import urlparse, urljoin

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, AnyHttpUrl


class XPagesConfig(BaseModel):
    """Configuration for X-Pages service."""
    
    base_url: AnyHttpUrl = Field(
        description="Base URL of the X-Pages service",
        examples=["https://your-domain.com", "http://localhost:3000"]
    )
    api_token: str = Field(
        description="API token for X-Pages authentication (x-token)"
    )
    timeout: float = Field(
        default=30.0,
        description="Request timeout in seconds"
    )


class DeployResult(BaseModel):
    """Result from HTML deployment."""
    
    success: bool
    site_name: str
    deploy_url: str
    deployed_at: str
    content_length: int
    message: str


class DeleteResult(BaseModel):
    """Result from HTML deletion."""
    
    success: bool
    site_name: str
    deleted_at: str
    message: str


# Create MCP server
mcp = FastMCP("X-Pages HTML Deployment")


def get_config() -> XPagesConfig:
    """Get configuration from environment variables."""
    base_url = os.getenv("X_PAGES_BASE_URL")
    api_token = os.getenv("X_PAGES_API_TOKEN")
    
    if not base_url:
        raise ValueError(
            "X_PAGES_BASE_URL environment variable is required. "
            "Example: https://your-domain.com"
        )
    
    if not api_token:
        raise ValueError(
            "X_PAGES_API_TOKEN environment variable is required. "
            "This is your x-token for API authentication."
        )
    
    return XPagesConfig(
        base_url=base_url,
        api_token=api_token,
        timeout=float(os.getenv("X_PAGES_TIMEOUT", "30.0"))
    )


def generate_site_name() -> str:
    """Generate a 24-character unique site name using hex characters."""
    return secrets.token_hex(12)  # 12 bytes = 24 hex characters


@mcp.tool()
async def deploy_html(
    html_content: str
) -> DeployResult:
    """
    部署HTML内容到X-Pages服务。
    
    Args:
        html_content: 完整的HTML内容
    
    Returns:
        部署结果，包含访问URL和部署信息（site_name为自动生成的24位唯一标识符）
    """
    config = get_config()
    
    # 生成24位随机唯一站点名称
    site_name = generate_site_name()
    
    # 构建部署URL
    deploy_url = urljoin(str(config.base_url), "/html/deploy")
    
    # 准备请求头
    headers = {
        "Content-Type": "text/html; charset=utf-8",
        "x-token": config.api_token,
        "htmlkey": site_name
    }
    
    
    # 发送部署请求
    async with httpx.AsyncClient(timeout=config.timeout) as client:
        try:
            response = await client.post(
                deploy_url,
                content=html_content.encode('utf-8'),
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return DeployResult(
                    success=data["success"],
                    site_name=data["data"]["siteName"],
                    deploy_url=urljoin(str(config.base_url), data["data"]["deployUrl"]),
                    deployed_at=data["data"]["deployedAt"],
                    content_length=data["data"]["contentLength"],
                    message=data["message"]
                )
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error", f"HTTP {response.status_code}")
                raise Exception(f"部署失败: {error_msg}")
                
        except httpx.TimeoutException:
            raise Exception(f"请求超时 ({config.timeout}秒)")
        except httpx.RequestError as e:
            raise Exception(f"网络请求失败: {str(e)}")


@mcp.tool()
async def delete_html(site_name: str) -> DeleteResult:
    """
    从X-Pages服务删除HTML站点。
    
    Args:
        site_name: 要删除的站点名称
    
    Returns:
        删除结果信息
    """
    config = get_config()
    
    # 构建删除URL
    delete_url = urljoin(str(config.base_url), f"/html/delete?siteName={site_name}")
    
    # 准备请求头
    headers = {
        "x-token": config.api_token
    }
    
    # 发送删除请求
    async with httpx.AsyncClient(timeout=config.timeout) as client:
        try:
            response = await client.delete(delete_url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return DeleteResult(
                    success=data["success"],
                    site_name=data["data"]["siteName"],
                    deleted_at=data["data"]["deletedAt"],
                    message=data["message"]
                )
            else:
                error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                error_msg = error_data.get("error", f"HTTP {response.status_code}")
                raise Exception(f"删除失败: {error_msg}")
                
        except httpx.TimeoutException:
            raise Exception(f"请求超时 ({config.timeout}秒)")
        except httpx.RequestError as e:
            raise Exception(f"网络请求失败: {str(e)}")


@mcp.tool()
async def get_site_url(site_name: str) -> str:
    """
    获取站点的访问URL。
    
    Args:
        site_name: 站点名称
    
    Returns:
        站点的完整访问URL
    """
    config = get_config()
    return urljoin(str(config.base_url), f"/{site_name}")


@mcp.tool()
async def create_sample_html(
    title: str = "示例页面",
    heading: str = "Hello World!",
    content: str = "这是一个通过MCP部署的示例HTML页面。"
) -> str:
    """
    创建一个示例HTML页面内容。
    
    Args:
        title: HTML页面标题
        heading: 页面主标题
        content: 页面内容
    
    Returns:
        完整的HTML内容，可用于部署
    """
    html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }}
        .container {{
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 1rem;
        }}
        .content {{
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }}
        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.9rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
        }}
        .timestamp {{
            color: #999;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{heading}</h1>
        <div class="content">
            <p>{content}</p>
        </div>
        <div class="footer">
            <p>🚀 通过 <strong>X-Pages MCP</strong> 部署</p>
            <p class="timestamp">部署时间: {asyncio.get_event_loop().time()}</p>
        </div>
    </div>
</body>
</html>"""
    
    return html_template


def main() -> None:
    """Main entry point for the MCP server."""
    import argparse
    
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="X-Pages MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="传输模式 (默认: stdio)"
    )
    
    args = parser.parse_args()
    
    # 验证配置
    try:
        config = get_config()
        print(f"✅ X-Pages MCP Server 已配置")
        print(f"📡 目标服务: {config.base_url}")
        print(f"🔑 API Token: {'*' * (len(config.api_token) - 4)}{config.api_token[-4:]}")
        print(f"🚀 传输模式: {args.transport}")
    except ValueError as e:
        print(f"❌ 配置错误: {e}", file=sys.stderr)
        print("\n📝 请设置以下环境变量:")
        print("   export X_PAGES_BASE_URL=https://your-domain.com")
        print("   export X_PAGES_API_TOKEN=your-api-token")
        print("   export X_PAGES_TIMEOUT=30.0  # 可选，默认30秒")
        sys.exit(1)
    
    # 根据传输模式启动MCP服务器
    if args.transport == "stdio":
        print("📡 使用 STDIO 传输模式启动...")
        mcp.run(transport="stdio")
    elif args.transport == "sse":
        print("📡 使用 SSE 传输模式启动...")
        mcp.run(transport="sse")
    elif args.transport == "streamable-http":
        print("📡 使用 Streamable HTTP 传输模式启动...")
        mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
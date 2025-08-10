#!/usr/bin/env python3
"""
X-Pages MCP Server 启动器

支持多种传输模式：stdio, sse, streamable-http
"""

import argparse
import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    # 自动加载 .env 文件
    load_dotenv()
except ImportError:
    # 如果没有安装 python-dotenv，继续运行但给出提示
    pass

# 添加src到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from x_pages_mcp.server import main as server_main


def check_environment():
    """检查必要的环境变量"""
    required_vars = ["X_PAGES_BASE_URL", "X_PAGES_API_TOKEN"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ 缺少必要的环境变量:", file=sys.stderr)
        for var in missing_vars:
            print(f"   {var}", file=sys.stderr)
        print("\n📝 请设置环境变量:", file=sys.stderr)
        print("   export X_PAGES_BASE_URL=https://your-domain.com", file=sys.stderr)
        print("   export X_PAGES_API_TOKEN=your-api-token", file=sys.stderr)
        return False
    
    return True


def main():
    """主入口函数"""
    parser = argparse.ArgumentParser(
        description="X-Pages MCP Server 启动器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s                              # 使用默认STDIO模式
  %(prog)s --transport sse              # 使用SSE模式
  %(prog)s --transport streamable-http  # 使用Streamable HTTP模式

传输模式说明:
  stdio          - 标准输入输出模式，用于Claude Desktop等客户端
  sse            - Server-Sent Events模式，基于HTTP的实时通信
  streamable-http - 可流式HTTP模式，支持长连接和流式响应
        """
    )
    
    parser.add_argument(
        "--transport",
        "-t",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="传输模式 (默认: stdio)"
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="只检查环境变量，不启动服务器"
    )
    
    args = parser.parse_args()
    
    # 检查环境变量
    if not check_environment():
        sys.exit(1)
    
    if args.check_env:
        print("✅ 环境变量检查通过")
        return
    
    # 设置命令行参数供server_main使用
    sys.argv = [
        sys.argv[0],
        "--transport", args.transport
    ]
    
    print(f"🚀 启动 X-Pages MCP Server")
    print(f"📊 传输模式: {args.transport}")
    print("=" * 50)
    
    try:
        server_main()
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"\n❌ 服务器启动失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
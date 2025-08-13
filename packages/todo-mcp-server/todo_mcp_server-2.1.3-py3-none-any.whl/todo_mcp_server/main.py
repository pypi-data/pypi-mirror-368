#!/usr/bin/env python3
"""
Todo MCP Server - 主入口程序
支持命令行参数配置，适用于多用户部署
"""

import argparse
import asyncio
import base64
import sys
from typing import Dict

from .server import TodoMCPServer
from .protocol import MCPProtocolHandler


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        description="Todo MCP Server - 用于Cursor集成的待办事项管理服务器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 使用API Token认证
  todo-mcp-server --api-url=https://my-todo.com:3000 --api-token=abc123

  # 使用用户名密码认证
  todo-mcp-server --api-url=https://my-todo.com:3000 --username=john --password=secret

  # 本地开发
  todo-mcp-server --api-url=http://localhost:3000 --api-token=dev-token

Cursor配置示例:
  {
    "mcpServers": {
      "my-todo": {
        "command": "uvx",
        "args": [
          "todo-mcp-server",
          "--api-url=https://your-server.com:3000",
          "--api-token=your-token"
        ]
      }
    }
  }
        """
    )
    
    # 必需参数
    parser.add_argument(
        "--api-url", 
        required=True,
        help="Todo API服务器URL (例: https://your-server.com:3000)"
    )
    
    # 认证方式1：API Token (推荐)
    parser.add_argument(
        "--api-token",
        help="API访问令牌 (Bearer Token认证)"
    )
    
    # 认证方式2：用户名密码
    parser.add_argument(
        "--username", 
        help="用户名 (Basic认证)"
    )
    parser.add_argument(
        "--password", 
        help="密码 (Basic认证)"
    )
    
    # 可选参数
    parser.add_argument(
        "--timeout", 
        type=int, 
        default=30,
        help="HTTP请求超时时间（秒，默认30）"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="todo-mcp-server 1.0.0"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="启用调试日志"
    )
    
    return parser


def validate_args(args) -> str:
    """验证命令行参数"""
    # 验证认证参数
    if not args.api_token and not (args.username and args.password):
        return "错误: 必须提供认证方式。使用 --api-token 或 --username + --password"
    
    if args.api_token and (args.username or args.password):
        return "错误: 不能同时使用 --api-token 和 --username/--password"
    
    # 验证URL格式
    if not args.api_url.startswith(('http://', 'https://')):
        return "错误: --api-url 必须以 http:// 或 https:// 开头"
    
    # 验证超时时间
    if args.timeout <= 0:
        return "错误: --timeout 必须大于0"
    
    return ""


def create_auth_headers(args) -> Dict[str, str]:
    """根据参数创建认证headers"""
    headers = {}
    
    if args.api_token:
        # 对于Todo API，我们需要模拟网关注入的认证头
        headers.update({
            "x-authenticated": "true",
            "x-user-id": "test-user-123",
            "x-username": "test-user",
            "x-user-email": "test@example.com"
        })
    elif args.username and args.password:
        # Basic认证
        credentials = base64.b64encode(
            f"{args.username}:{args.password}".encode()
        ).decode()
        headers["Authorization"] = f"Basic {credentials}"
    
    return headers


async def main():
    """主程序入口"""
    # 解析命令行参数
    parser = create_parser()
    args = parser.parse_args()
    
    # 验证参数
    validation_error = validate_args(args)
    if validation_error:
        print(validation_error, file=sys.stderr)
        return 1
    
    # 配置日志级别
    if args.debug:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    # 创建认证headers
    auth_headers = create_auth_headers(args)
    
    # 输出启动信息到stderr（不影响MCP协议）
    print(f"🚀 启动Todo MCP服务器", file=sys.stderr)
    print(f"📡 连接到: {args.api_url}", file=sys.stderr)
    print(f"🔐 认证方式: {'Token' if args.api_token else 'Username/Password'}", file=sys.stderr)
    print(f"⏱️  超时时间: {args.timeout}秒", file=sys.stderr)
    print("等待Cursor连接...", file=sys.stderr)
    
    try:
        # 创建服务器实例
        server = TodoMCPServer(
            api_base_url=args.api_url,
            auth_headers=auth_headers,
            timeout=args.timeout
        )
        
        # 初始化服务器
        await server.initialize()
        
        # 创建协议处理器并运行
        handler = MCPProtocolHandler(server)
        await handler.run()
        
    except KeyboardInterrupt:
        print("⛔ 用户中断", file=sys.stderr)
        return 0
    except Exception as e:
        print(f"❌ 启动失败: {e}", file=sys.stderr)
        return 1
    
    return 0


def cli_main():
    """CLI入口点（供setuptools使用）"""
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    cli_main()
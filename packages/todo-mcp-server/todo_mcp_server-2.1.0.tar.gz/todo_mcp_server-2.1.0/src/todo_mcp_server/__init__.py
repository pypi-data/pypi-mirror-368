"""
Todo MCP Server - 用于Cursor集成的待办事项管理MCP服务器

这个包提供了一个符合MCP官方规范的服务器实现，
可以连接到任何Todo API服务器并为Cursor提供任务管理功能。
"""

__version__ = "2.0.1"
__author__ = "huangzhenxin"
__email__ = "your-email@example.com"

from .server import TodoMCPServer
from .protocol import MCPProtocolHandler

__all__ = ["TodoMCPServer", "MCPProtocolHandler"]
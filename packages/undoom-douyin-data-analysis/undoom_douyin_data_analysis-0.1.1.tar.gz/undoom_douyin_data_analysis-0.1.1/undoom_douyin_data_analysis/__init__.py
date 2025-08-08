"""抖音数据分析 MCP 服务器包"""

from .douyin_mcp_server import DouyinMCPServer, main, cli_main

__version__ = "0.1.1"
__all__ = ["DouyinMCPServer", "main", "cli_main"]
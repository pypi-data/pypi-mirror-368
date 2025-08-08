from mcp.server.fastmcp import FastMCP

from mcp_server_dongjunqaq import tools

mcp = FastMCP("mcp-server-DongJunQAQ")  # 创建MCP Server并命名
# 注册工具:
mcp.add_tool(tools.get_platform_info)
mcp.add_tool(tools.get_env)
mcp.add_tool(tools.get_compress_format)
mcp.add_tool(tools.make_archive)
mcp.add_tool(tools.download_video)


def main() -> None:
    mcp.run(transport="stdio")  # 使用stdio的方式运行该MCP Server

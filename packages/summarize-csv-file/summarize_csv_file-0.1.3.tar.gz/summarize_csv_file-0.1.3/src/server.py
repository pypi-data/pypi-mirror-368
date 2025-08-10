# server.py

from mcp.server.fastmcp import FastMCP
# This is the shared MCP server instance

mcp = FastMCP("mix_server")

# Import tools so they get registered via decorators
import tools.csv_tools
import tools.parquet_tools
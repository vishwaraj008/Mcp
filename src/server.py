from mcp.server.fastmcp import FastMCP
from tools.moadTool import register_moad
from tools.athenaTool import register_athena
from utils.logger import logger

mcp = FastMCP("Solthar-MCP")

# Register tools via decorators
register_moad(mcp)
register_athena(mcp)

if __name__ == "__main__":
    logger.info("🚀 Starting Solthar MCP Server")
    mcp.run()  # runs over stdio by default

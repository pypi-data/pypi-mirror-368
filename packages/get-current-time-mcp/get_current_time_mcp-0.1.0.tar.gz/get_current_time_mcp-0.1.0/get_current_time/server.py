from mcp.server.fastmcp import FastMCP
from datetime import datetime

# Create MCP server instance
mcp = FastMCP("GetCurrentTime")

# Define a tool
@mcp.tool()
def get_current_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Returns the current time in the given format."""
    return datetime.now().strftime(format)

# Entry point for MCP
def main():
    mcp.run()

if __name__ == "__main__":
    main()

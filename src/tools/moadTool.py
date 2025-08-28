# src/tools/moadTool.py
from mcp.server.fastmcp import FastMCP
from services.moadService import generateDocumentation

def register_moad(mcp: FastMCP):
    @mcp.tool(
        name="moad",
        description="Generate documentation for a given codebase"
    )
    async def moad(
        projectPath: str,
        outputPath: str,
        format: str = "markdown"
    ) -> dict:
        """
        Generates documentation for the given project.

        Args:
            projectPath (str): Path to the code project.
            outputPath (str): Path where docs should be saved.
            format (str): Format of output docs (default: markdown).
        """
        return await generateDocumentation(projectPath, outputPath, format)

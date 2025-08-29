# src/tools/athenaTool.py
from mcp.server.fastmcp import FastMCP
from services.athenaService import ingestFile, queryPrompt

def register_athena(mcp: FastMCP):
    @mcp.tool(
        name="athenaIngest",
        description="Ingest a file into Athena with metadata"
    )
    async def athenaIngestTool(
        file: str | bytes,
        source_type: str,
        title: str = "",
        description: str = "",
        tags: str | list[str] = None
    ) -> dict:
        return await ingestFile(file, source_type, title, description, tags)

    @mcp.tool(
        name="athenaQuery",
        description="Query Athena with a text prompt"
    )
    async def athenaQueryTool(prompt: str) -> str:
        return await queryPrompt(prompt)

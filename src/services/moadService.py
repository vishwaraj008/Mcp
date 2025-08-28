# src/services/moadService.py
import aiohttp
from config.config import MOAD_URL, MOAD_API_KEY
from utils.errors import ToolExecutionError

async def generateDocumentation(projectPath: str, outputPath: str, format: str = "markdown") -> dict:
    payload = {
        "projectPath": projectPath,
        "outputPath": outputPath,
        "format": format
    }
    headers = {"x-api-key": f"{MOAD_API_KEY}"} if MOAD_API_KEY else {}

    async with aiohttp.ClientSession() as session:
        try:
            resp = await session.post(f"{MOAD_URL}/", json=payload, headers=headers, timeout=15)
            resp.raise_for_status()
            data = await resp.json()
            return {
                "status": "success",
                "data": data
            }
        except Exception as e:
            raise ToolExecutionError("MOAD service call failed") from e

# src/utils/httpClient.py
import aiohttp

async def postJson(url: str, payload: dict, timeout: int = 15) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, timeout=timeout) as resp:
            resp.raise_for_status()
            return await resp.json()

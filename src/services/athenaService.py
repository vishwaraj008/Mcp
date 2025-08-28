import aiohttp
import io
import os
from config.config import ATHENA_BASE_URL, ATHENA_API_KEY
from utils.errors import ToolExecutionError

async def ingestFile(file: str | bytes, source_type: str, title: str, description: str, tags: list[str]) -> dict:
    data = aiohttp.FormData()

    try:
        # handle file path or raw bytes
        if isinstance(file, str):  # file path
            filename = title or os.path.basename(file)
            f = open(file, "rb")
            data.add_field("file", f, filename=filename)
        elif isinstance(file, bytes):  # raw bytes
            filename = title or "upload.bin"
            f = io.BytesIO(file)
            data.add_field("file", f, filename=filename)
        else:
            raise ToolExecutionError("Invalid file type: must be str path or bytes")

        # add other fields
        data.add_field("title", title)
        data.add_field("source_type", source_type)
        data.add_field("description", description)
        if tags:
            data.add_field("tags", ",".join(tags))  # ✅ comma-separated like Postman

        headers = {"x-api-key": ATHENA_API_KEY} if ATHENA_API_KEY else {}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{ATHENA_BASE_URL}/ingest",
                data=data,
                headers=headers,
                timeout=60
            ) as resp:
                resp.raise_for_status()
                return await resp.json()

    except aiohttp.ClientResponseError as e:
        body = await e.response.text()
        raise ToolExecutionError(f"Athena ingest failed: {e.status} {body}") from e
    except Exception as e:
        raise ToolExecutionError("Athena ingest failed") from e
    finally:
        try:
            f.close()  # ✅ ensure file/BytesIO is closed
        except Exception:
            pass




async def queryPrompt(prompt: str) -> str:
    if not ATHENA_BASE_URL:
        raise ToolExecutionError("ATHENA_URL not configured")

    payload = {"prompt": prompt}
    headers = {}
    if ATHENA_API_KEY:
        headers["x-api-key"] = ATHENA_API_KEY

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(
                f"{ATHENA_BASE_URL}/query",
                json=payload,
                headers=headers,
                timeout=20
            ) as resp:
                resp.raise_for_status()
                try:
                    data = await resp.json()
                    return data.get("response", str(data))  # fallback if key missing
                except aiohttp.ContentTypeError:
                    return await resp.text()
        except aiohttp.ClientError as e:
            raise ToolExecutionError("Athena query failed: network error") from e
        except Exception as e:
            raise ToolExecutionError("Athena query failed") from e
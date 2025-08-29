import aiohttp
import io
import os
from typing import Union, List
from config.config import ATHENA_BASE_URL, ATHENA_API_KEY
from utils.errors import ToolExecutionError

async def ingestFile(
    file: Union[str, bytes],
    source_type: str,
    title: str = "",
    description: str = "",
    tags: Union[str, List[str]] = None
) -> dict:
    """
    Upload a file to Athena API using multipart form-data.
    Supports both file paths (str) and raw file content (bytes).
    """

    # Validate inputs
    if not isinstance(source_type, str) or not source_type.strip():
        raise ToolExecutionError("source_type must be a non-empty string")
    if not isinstance(title, str):
        raise ToolExecutionError("title must be a string")
    if not isinstance(description, str):
        raise ToolExecutionError("description must be a string")
    if tags is not None and not isinstance(tags, (str, list)):
        raise ToolExecutionError("tags must be a string or list of strings")
    if isinstance(tags, list) and not all(isinstance(tag, str) for tag in tags):
        raise ToolExecutionError("All tags in the list must be strings")

    if not ATHENA_BASE_URL or not isinstance(ATHENA_BASE_URL, str):
        raise ToolExecutionError(f"Invalid or missing ATHENA_BASE_URL: {ATHENA_BASE_URL!r}")
    if not ATHENA_API_KEY or not isinstance(ATHENA_API_KEY, str):
        raise ToolExecutionError(f"Invalid or missing ATHENA_API_KEY: {ATHENA_API_KEY!r}")

    try:
        data = aiohttp.FormData()

        # Handle file input
        if isinstance(file, str):
            if not file.strip() or not os.path.isfile(file):
                raise ToolExecutionError("file path must be a non-empty string and point to an existing local file")
            with open(file, "rb") as f:
                file_bytes = f.read()
            filename = os.path.basename(file)
            data.add_field(
                "file",
                io.BytesIO(file_bytes),
                filename=filename,
                content_type="application/pdf"
            )
        elif isinstance(file, bytes):
            filename = (title.replace(" ", "_") if title else "upload") + ".pdf"
            data.add_field(
                "file",
                io.BytesIO(file),
                filename=filename,
                content_type="application/pdf"
            )
        else:
            raise ToolExecutionError(f"file must be a file path (str) or bytes, got {type(file)}")

        # Add metadata fields
        data.add_field("title", title)
        data.add_field("source_type", source_type)
        data.add_field("description", description)
        if tags:
            tags_str = tags if isinstance(tags, str) else ",".join(tags)
            data.add_field("tags", tags_str)

        headers = {"x-api-key": ATHENA_API_KEY}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{ATHENA_BASE_URL.rstrip('/')}/ingest",
                data=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise ToolExecutionError(f"Athena ingest failed: {resp.status} {body}")
                try:
                    return await resp.json()
                except aiohttp.ContentTypeError as e:
                    body = await resp.text()
                    raise ToolExecutionError(f"Invalid JSON response: {body}") from e

    except aiohttp.ClientConnectionError as e:
        raise ToolExecutionError(f"Failed to connect to Athena API: {str(e)}") from e
    except aiohttp.ClientTimeout as e:
        raise ToolExecutionError("Request to Athena API timed out") from e
    except aiohttp.ClientResponseError as e:
        body = await e.response.text()
        raise ToolExecutionError(f"Athena ingest failed: {e.status} {body}") from e
    except Exception as e:
        raise ToolExecutionError(f"Athena ingest failed: {str(e)}") from e





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
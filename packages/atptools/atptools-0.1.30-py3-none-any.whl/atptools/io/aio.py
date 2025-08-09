from pathlib import Path

import aiofiles


async def save_to_file_async(
    file_content: bytes | str,
    path: str | Path,
) -> None:
    if isinstance(file_content, str):
        file_content = file_content.encode()
    async with aiofiles.open(path, "wb") as file:
        await file.write(file_content)
        await file.flush()
    return None


async def load_from_file_async(
    path: str | Path,
) -> bytes:
    async with aiofiles.open(path, "rb") as file:
        return await file.read()


async def load_from_file_str_async(
    path: str | Path,
    encoding: str = "utf-8",
) -> str:
    async with aiofiles.open(path, encoding=encoding) as file:
        return await file.read()


# AWS S3
async def save_to_s3_async(
    file_content: bytes | str,
    bucket: str,
    key: str,
) -> None:
    # import aiobotocore

    # async with aiobotocore.get_session() as session:
    #     async with session.create_client("s3") as s3:
    #         if isinstance(file_content, str):
    #             file_content = file_content.encode()
    #         await s3.put_object(Bucket=bucket, Key=key, Body=file_content)
    return None


# Azure Blob Storage
async def save_to_azure_blob_async(
    file_content: bytes | str,
    container: str,
    blob: str,
) -> None:
    # import azure.storage.blob.aio

    # async with azure.storage.blob.aio.BlobServiceClient.from_connection_string(
    #     conn_str=os.environ["AZURE_STORAGE_CONNECTION_STRING"]
    # ) as blob_service_client:
    #     blob_client = blob_service_client.get_blob_client(container, blob)
    #     if isinstance(file_content, str):
    #         file_content = file_content.encode()
    #     await blob_client.upload_blob(file_content)
    return None


# REST API
# post to REST API json
async def post_to_rest_api_json_async(
    url: str,
    data: dict,
) -> dict:
    # import aiohttp

    # async with aiohttp.ClientSession() as session:
    #     async with session.post(url, json=data) as response:
    #         return await response.json()
    return {}


# get from REST API json
async def get_from_rest_api_json_async(
    url: str,
) -> dict:
    # import aiohttp

    # async with aiohttp.ClientSession() as session:
    #     async with session.get(url) as response:
    #         return await response.json()
    return {}

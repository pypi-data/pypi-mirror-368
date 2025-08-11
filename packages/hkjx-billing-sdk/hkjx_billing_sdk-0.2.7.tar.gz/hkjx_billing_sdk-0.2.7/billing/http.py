from collections.abc import AsyncGenerator
from typing import Any, TypeVar

import httpx
from curlify2 import Curlify
from pydantic import BaseModel

from .exceptions import BillingException

# Define a generic type for Pydantic models
T = TypeVar("T", bound=BaseModel)


class HttpClient:
    def __init__(self, base_url: str, key: str):
        self.base_url = base_url
        self.key = key
        self.headers = {
            "Content-Type": "application/json",
            "X-Admin-Key": key,
        }

    async def __merge_headers__(self, headers: dict = None):
        merged_headers = self.headers.copy()
        if headers:
            merged_headers.update(headers)
        return merged_headers

    async def get(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            merged_headers = await self.__merge_headers__(headers)

            response = await client.get(
                self.base_url + url,
                params=params,
                headers=merged_headers,
            )
            curlify = Curlify(response.request)
            print(curlify.to_curl())
            if response.is_error:
                raise BillingException(
                    f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}",
                )
            return response.json()

    async def post(
        self,
        url: str,
        json: BaseModel = None,
        params: dict = None,
        headers: dict = None,
        timeout: int = 10,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            merged_headers = await self.__merge_headers__(headers)

            # Use Pydantic's model_dump_json for serialization
            json_data = None
            if json is not None:
                json_data = json.model_dump_json()

            response = await client.post(
                self.base_url + url,
                content=json_data.encode("utf-8") if json_data else None,
                params=params,
                headers=merged_headers,
                timeout=timeout,
            )
            curlify = Curlify(response.request)
            print(curlify.to_curl())
            if response.is_error:
                raise BillingException(
                    f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}",
                )
            return response.json()
        
    async def put(
        self,
        url: str,
        json: BaseModel = None,
        params: dict = None,
        headers: dict = None,
        timeout: int = 10,
    ) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            merged_headers = await self.__merge_headers__(headers)

            # Use Pydantic's model_dump_json for serialization
            json_data = None
            if json is not None:
                json_data = json.model_dump_json()

            response = await client.put(
                self.base_url + url,
                content=json_data.encode("utf-8") if json_data else None,
                params=params,
                headers=merged_headers,
                timeout=timeout,
            )
            curlify = Curlify(response.request)
            print(curlify.to_curl())
            if response.is_error:
                raise BillingException(
                    f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}",
                )
            return response.json()



    async def delete(
        self,
        url: str,
        params: dict = None,
        content: BaseModel = None,
        headers: dict = None,
        ret_type: str = None,
    ) -> Any:
        async with httpx.AsyncClient() as client:
            merged_headers = await self.__merge_headers__(headers)

            # Use Pydantic's model_dump_json for serialization
            json_data = None
            if content is not None:
                json_data = content.model_dump_json()

            response = await client.request(
                "DELETE",
                self.base_url + url,
                params=params,
                headers=merged_headers,
                content=json_data.encode("utf-8") if json_data else None,
            )
            curlify = Curlify(response.request)
            print(curlify.to_curl())
            if response.is_error:
                raise BillingException(
                    f"请求失败，状态码: {response.status_code}, 错误信息: {response.text}",
                )
            if ret_type == "json":
                return response.json()
            if ret_type == "text":
                return response.text
            return None

    async def stream(
        self,
        url: str,
        params: dict = None,
        headers: dict = None,
        method: str = "POST",
        json: BaseModel = None,
    ) -> AsyncGenerator[bytes, None]:
        async with httpx.AsyncClient(timeout=600) as client:
            merged_headers = await self.__merge_headers__(headers)

            # Use Pydantic's model_dump_json for serialization
            json_data = None
            if json is not None:
                json_data = json.model_dump_json()

            async with client.stream(
                method,
                self.base_url + url,
                params=params,
                headers=merged_headers,
                content=json_data.encode("utf-8") if json_data else None,
            ) as response:
                curlify = Curlify(response.request)
                print(curlify.to_curl())
                if response.is_error:
                    error_content = await response.aread()
                    raise BillingException(
                        f"请求失败，状态码: {response.status_code}, 错误信息: {error_content.decode('utf-8')}",
                    )
                async for chunk in response.aiter_bytes():
                    yield chunk

from typing import List

from ..http import HttpClient
from .schemas import (
    CurrencyType,
    KeyConsumeRequest,
    KeyCreate,
    KeyDeleteResponse,
    KeyListResponse,
    KeyResponse,
)


class Keys:
    """密钥管理类."""

    def __init__(self, client: HttpClient) -> None:
        self.client = client

    async def create_key(self, key_create: KeyCreate) -> KeyResponse:
        """创建密钥.

        Args:
            key_create: 创建密钥请求

        Returns:
            KeyResponse: 密钥响应
        """
        response = await self.client.post("/keys", json=key_create)
        return KeyResponse(**response["data"])
    
    async def update_key(self, key_update: KeyCreate) -> KeyResponse:
        """修改密钥.

        Args:
            key_update: 修改密钥请求

        Returns:
            KeyResponse: 密钥响应
        """
        response = await self.client.put(f"/keys/{key_update.id}", json=key_update)
        return KeyResponse(**response["data"])

    async def list_available_keys(
        self,
        user_id: str = None,
        service_code: str = None,
        scope: List[str] = None,
        currency_type: str = None,
    ) -> KeyListResponse:
        """获取可用密钥列表.

        Args:
            user_id: 用户ID（可选）
            service_code: 服务代码（可选）
            scope: 作用域（可选）
            currency_type: 信用货币类型（可选）

        Returns:
            KeyListResponse: 密钥列表响应
        """
        # 构建查询参数
        params = {}
        if user_id is not None:
            params["user_id"] = user_id
        if service_code is not None:
            params["service_code"] = service_code
        if scope is not None:
            params["scope"] = scope
        if currency_type is not None:
            params["currency_type"] = currency_type

        response = await self.client.get("/keys/available", params=params)
        return KeyListResponse(**response["data"])
    
    async def list_all_keys(
        self,
        user_id: str = None,
        service_code: str = None,
        scope: List[str] = None,
        currency_type: str = None,
        is_available: bool | None = None,
    ) -> KeyListResponse:
        """获取可用密钥列表.

        Args:
            user_id: 用户ID（可选）
            service_code: 服务代码（可选）
            scope: 作用域（可选）
            currency_type: 信用货币类型（可选）

        Returns:
            KeyListResponse: 密钥列表响应
        """
        # 构建查询参数
        params = {}
        if user_id is not None:
            params["user_id"] = user_id
        if service_code is not None:
            params["service_code"] = service_code
        if scope is not None:
            params["scope"] = scope
        if currency_type is not None:
            params["currency_type"] = currency_type
        if is_available is not None:
            params["is_available"] = is_available

        response = await self.client.get("/keys", params=params)
        return KeyListResponse(**response["data"])

    async def consume_key(self, consume_request: KeyConsumeRequest):
        """消费密钥.

        Args:
            consume_request: 消费密钥请求

        Returns:
            KeyConsumeResponse: 消费密钥响应
        """
        await self.client.post("/keys/consume", json=consume_request)

    async def delete_key(self, key_id: str) -> KeyDeleteResponse:
        """删除密钥.

        Args:
            key_id: 密钥ID

        Returns:
            KeyDeleteResponse: 删除密钥响应
        """
        response = await self.client.delete(f"/keys/{key_id}", ret_type="json")
        return KeyDeleteResponse(**response["data"])


__all__ = [
    "Keys",
    "CurrencyType",
    "KeyCreate",
    "KeyResponse",
    "KeyListResponse",
    "KeyDeleteResponse",
    "KeyConsumeRequest",
    "KeyConsumeResponse",
]

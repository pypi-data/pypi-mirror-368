from ..http import HttpClient
from .schemas import ActivityListResponse, ActivityResponse, ActivityType


class Activities:
    """活动管理类."""

    def __init__(self, client: HttpClient) -> None:
        self.client = client

    async def list_activities(
        self,
        page: int = 1,
        limit: int = 100,
        key_id: str = None,
    ) -> ActivityListResponse:
        """获取活动列表.

        Args:
            key_id: 应用ID（可选）

        Returns:
            ActivityListResponse: 活动列表响应
        """
        # 构建查询参数
        params = {"page": page, "limit": limit}
        if key_id is not None:
            params["key_id"] = key_id


        response = await self.client.get("/activities", params=params)
        return ActivityListResponse(**response["data"])


__all__ = [
    "Activities",
    "ActivityType",
    "ActivityResponse",
    "ActivityListResponse",
]

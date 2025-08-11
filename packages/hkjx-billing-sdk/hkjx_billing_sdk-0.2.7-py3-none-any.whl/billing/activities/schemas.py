from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ActivityType(str, Enum):
    """活动类型"""

    VERIFY = "verify"  # 验证
    CONSUME = "consume"  # 消费


class ActivityResponse(BaseModel):
    """活动响应"""

    id: int
    key_id: str
    app_id: str
    user_id: str
    service_code: str  # 服务代码
    scope: Optional[List[str]] = None  # 作用域，JSON数组格式
    scope_names: Optional[List[str]] = None  # 作用域，JSON数组格式
    currency_type: Optional[str] = None
    type: ActivityType
    amount: float
    details: Optional[Dict[str, Any]] = None
    created_at: datetime


class ActivityListResponse(BaseModel):
    """活动列表响应"""

    activities: List[ActivityResponse] = Field(
        default_factory=list, description="活动列表"
    )
    total: int = Field(default=0, description="总数")
    page: int = Field(default=1, description="当前页码")
    limit: int = Field(default=10, description="每页数量")

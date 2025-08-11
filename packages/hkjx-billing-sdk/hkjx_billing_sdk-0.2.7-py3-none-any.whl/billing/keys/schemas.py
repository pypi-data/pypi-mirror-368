from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class CurrencyType(str, Enum):
    """信用货币类型"""

    # 法定货币
    CNY = "CNY"  # 人民币
    USD = "USD"  # 美元

    # 自定义货币
    LTC = "LTC"  # LLM Token Counts
    UTS = "UTS"  # Usage Times


# Key 相关模型
class KeyCreate(BaseModel):
    """创建/修改密钥请求"""
    id: Optional[str] = Field(default=None, description="密钥ID", example="key1")
    user_id: Optional[str] = Field(default=None, description="用户ID", example="user1")
    service_code: str = Field(..., description="服务代码", example="ADM")
    scope: Optional[List[str]] = Field(
        default=None,
        description="作用域，JSON数组格式",
        example=["instance1", "instance2", "instance3"],
    )
    currency_type: Optional[CurrencyType] = Field(
        default=None, description="信用货币类型", example="CNY"
    )
    credit_limit: Optional[float] = Field(
        default=None, description="额度限制", example=1000.0
    )
    expires_at: Optional[datetime] = Field(
        default=None, description="过期时间", example=datetime.now()
    )
    # 新增字段
    username: Optional[str] = Field(
        default=None, description="用户名称", example="张三"
    )
    nickname: Optional[str] = Field(
        default=None, description="昵称", example="小张"
    )
    phone: Optional[str] = Field(
        default=None, description="手机号", example="13800138000"
    )
    customer_source: Optional[str] = Field(
        default=None, description="客户来源", example="官网注册"
    )
    is_paid: Optional[bool] = Field(
        default=None, description="是否付款", example=True
    )
    payment_method: Optional[str] = Field(
        default=None, description="付款途径", example="微信支付"
    )
    payment_amount: Optional[float] = Field(
        default=None, description="付款金额", example=100.0
    )


class KeyResponse(BaseModel):
    """密钥响应"""

    id: str
    app_id: str
    user_id: str
    service_code: str  # 服务代码
    currency_type: Optional[CurrencyType]  # 信用货币类型，可能为None，表示管理密钥
    scope: Optional[List[str]] = None  # 作用域，JSON数组格式
    scope_names: Optional[List[str]] = None  # 作用域名称，JSON数组格式
    credit_limit: float
    credit_used: float
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    # 新增字段
    username: Optional[str] = None
    nickname: Optional[str] = None
    phone: Optional[str] = None
    customer_source: Optional[str] = None
    is_paid: Optional[bool] = None
    payment_method: Optional[str] = None
    payment_amount: Optional[float] = None


class KeyConsumeRequest(BaseModel):
    """消费密钥请求"""

    key_id: str = Field(..., description="密钥ID")
    model_name: Optional[str] = Field(default=None, description="模型名称")
    phone : Optional[str] = Field(default=None, description="手机号")
    amount: Optional[float] = Field(default=None, description="消费数量")
    details: Optional[Dict[str, Any]] = Field(None, description="详细信息")
    scope: Optional[List[str]] = Field(default=None, description="智能体ID")
  


class KeyListResponse(BaseModel):
    """密钥列表响应"""

    keys: List[KeyResponse] = Field(default_factory=list, description="密钥列表")


class KeyDeleteResponse(BaseModel):
    """删除密钥响应"""

    success: bool = Field(..., description="是否成功")
    key_id: str = Field(..., description="密钥ID")

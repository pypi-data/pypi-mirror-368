from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, ValidationError


# 公共的层级模型
class ResponseBaseModel(BaseModel):
    fun: str = Field(..., description="功能名称")
    msgid: int = Field(0, description="消息 ID，默认值为 0")
    status: int = Field(..., description="HTTP 状态码")
    message: str = Field(..., description="消息")


# 公共的 data 层基础模型
class DataBaseModel(BaseModel):
    code: Optional[int] = Field(0, description="状态")
    id: List[str] = Field(default_factory=list, description="ID 列表，以逗号分隔")
    message: Optional[str] = Field(None, description="信息")

    @field_validator("id", mode="before")
    def parse_id(cls, value):
        """将逗号分隔的字符串解析为列表"""
        if value is None:
            return []  # 如果未提供 id，返回空列表
        if isinstance(value, str):
            sss = value.split(",")
            return sss  # 将字符串分割为列表
        if isinstance(value, list):
            return value  # 如果已经是列表，直接返回
        raise ValueError("id 必须是逗号分隔的字符串或列表")


class CommonResponseResponseData(DataBaseModel):
    pass


class CommonResponse(ResponseBaseModel):
    data: CommonResponseResponseData = Field(..., description="公共响应数据")

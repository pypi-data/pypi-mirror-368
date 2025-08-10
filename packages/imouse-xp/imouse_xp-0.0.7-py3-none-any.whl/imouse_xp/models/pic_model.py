from typing import List

from pydantic import BaseModel, Field

from imouse_xp.models import DataBaseModel, ResponseBaseModel


class PicScreenshotResponseData(DataBaseModel):
    jpg: bool = Field(..., description="返回jpg格式")
    rect: List[int] = Field(..., description="矩形区域")
    image: str = Field(..., description="base64字符串图片数据或路径")


class PicScreenshotResponse(ResponseBaseModel):
    data: PicScreenshotResponseData = Field(..., description="截图响应数据")


class PicModelFindImageInfo(BaseModel):
    index: int = Field(..., description="索引")
    centre: List[int] = Field(..., description="找到图像的中心点")
    rect: List[int] = Field(..., description="rect")


class PicFindImageResponseData(DataBaseModel):
    list: List[PicModelFindImageInfo] = Field(..., description="找图返回数据")


class PicFindImageResponse(ResponseBaseModel):
    data: PicFindImageResponseData = Field(..., description="找图返回响应数据")


PicFindImageCvResponse = PicFindImageResponse


class PicOcrInfo(BaseModel):
    text: str = Field(..., description="识别到的文字")
    centre: List[int] = Field(..., description="文字的中心点")
    rect: List[int] = Field(..., description="文字的矩形区域")
    similarity: float = Field(..., description="相似度")


class PicOcrResponseData(DataBaseModel):
    list: List[PicOcrInfo] = Field(..., description="ocr返回数据")


class PicOcrResponse(ResponseBaseModel):
    data: PicOcrResponseData = Field(..., description="ocr返回响应数据")



PicFindTextResponse = PicOcrResponse



class PicFindMultiColorInfo(BaseModel):
    index: int = Field(..., description="索引")
    centre: List[int] = Field(..., description="中心点")


class PicFindMultiColorResponseData(DataBaseModel):
    list: List[PicFindMultiColorInfo] = Field(..., description="多点找色返回数据")


class PicFindMultiColorResponse(ResponseBaseModel):
    data: PicFindMultiColorResponseData = Field(..., description="多点找色返回响应数据")

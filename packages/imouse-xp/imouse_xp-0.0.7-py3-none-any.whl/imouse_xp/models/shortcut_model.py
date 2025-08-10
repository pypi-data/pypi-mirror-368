from typing import List

from pydantic import BaseModel, Field

from imouse_xp.models import DataBaseModel, ResponseBaseModel


class ShortcutAlbumInfo(BaseModel):
    album_name: str = Field(..., description="相册名字")
    name: str = Field(..., description="文件名")
    ext: str = Field(..., description="扩展名")
    size: str = Field(..., description="文件大小")
    create_time: str = Field(..., description="创建时间")


class ShortcutAlbumGetResponseData(DataBaseModel):
    list: List[ShortcutAlbumInfo] = Field(..., description="相册列表数据")


class ShortcutAlbumGetResponse(ResponseBaseModel):
    data: ShortcutAlbumGetResponseData = Field(..., description="相册列表响应数据")


ShortcutAlbumUploadResponse = ShortcutAlbumGetResponse
ShortcutAlbumDelResponse = ShortcutAlbumGetResponse
ShortcutAlbumClearResponse = ShortcutAlbumGetResponse


class ShortcutAlbumDownInfo(BaseModel):
    album_name: str = Field(..., description="相册名字")
    name: str = Field(..., description="文件名")
    ext: str = Field(..., description="扩展名")


class ShortcutAlbumDownResponseData(DataBaseModel):
    list: List[ShortcutAlbumDownInfo] = Field(..., description="")


class ShortcutAlbumDownResponse(ResponseBaseModel):
    data: ShortcutAlbumDownResponseData = Field(..., description="")


class ShortcutFileInfo(BaseModel):
    name: str = Field(..., description="name")
    ext: str = Field(..., description="ext")
    size: str = Field(..., description="size")
    create_time: str = Field(..., description="create_time")


class ShortcutFileResponseData(DataBaseModel):
    list: List[ShortcutFileInfo] = Field(..., description="")


class ShortcutFileResponse(ResponseBaseModel):
    data: ShortcutFileResponseData = Field(..., description="")


ShortcutFileGetResponse = ShortcutFileResponse
ShortcutFileUploadResponse = ShortcutFileResponse
ShortcutFileDleResponse = ShortcutFileResponse


class ShortcutFileDownInfo(BaseModel):
    name: str = Field(..., description="name")
    ext: str = Field(..., description="ext")


class ShortcutFileDownResponseData(DataBaseModel):
    list: List[ShortcutFileDownInfo] = Field(..., description="")


class ShortcutFileDownResponse(ResponseBaseModel):
    data: ShortcutFileDownResponseData = Field(..., description="")


class ShortcutClipboardResponseData(DataBaseModel):
    text: str = Field(..., description="text")


class ShortcutClipboardResponse(ResponseBaseModel):
    data: ShortcutClipboardResponseData = Field(..., description="")


ShortcutDeviceIpResponse = ShortcutClipboardResponse

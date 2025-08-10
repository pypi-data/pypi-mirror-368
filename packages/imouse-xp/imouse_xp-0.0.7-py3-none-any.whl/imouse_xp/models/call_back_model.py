from typing import List, Optional

from pydantic import Field, BaseModel

from imouse_xp.models import ResponseBaseModel, DataBaseModel, DeviceGetResponse


class IMConnectResponseData(DataBaseModel):
    ver: str = Field(..., description="版本号")


class IMConnectResponse(ResponseBaseModel):
    data: IMConnectResponseData = Field(..., description="内核连接响应数据")


class UserInfoResponseData(DataBaseModel):
    pass_: bool = Field(False, alias="pass", description="是否通过")
    total_license: int = Field(0, description="总许可数")
    local_total_license: int = Field(0, description="本地总许可数")
    dev_num: int = Field(0, description="设备数量")
    dev_online_num: int = Field(0, description="在线设备数量")
    create_time: Optional[int] = Field(None, description="创建时间，时间戳")
    overdue_time: Optional[int] = Field(None, description="过期时间，时间戳")
    phone: Optional[str] = Field(None, description="手机号")
    utag: Optional[int] = Field(None, description="用户标签")
    test_num: int = Field(0, description="测试数")
    user_state: Optional[int] = Field(None, description="用户状态")


class UserInfoResponse(ResponseBaseModel):
    data: UserInfoResponseData = Field(..., description="用户信息响应数据")


DeviceConnectResponse = DeviceGetResponse
DeviceDisconnectResponse = DeviceGetResponse
DeviceRotateResponse = DeviceGetResponse
DeviceChangeResponse = DeviceGetResponse


class USBInfo(BaseModel):
    vid: Optional[str] = Field(None, description="设备VID")
    pid: Optional[str] = Field(None, description="设备PID")
    uid: Optional[str] = Field(None, description="设备UID")
    ver: Optional[str] = Field(None, description="设备版本号")


class USBChangeResponseData(DataBaseModel):
    list: List[USBInfo] = Field(..., description="硬件信息列表")


class USBChangeResponse(ResponseBaseModel):
    data: USBChangeResponseData = Field(..., description="硬件列表响应数据")


class IMLogResponseData(DataBaseModel):
    call_fun: Optional[str] = Field('', description="调用功能")
    msg: Optional[str] = Field('', description="消息")


class IMLogResponse(ResponseBaseModel):
    data: IMLogResponseData = Field(..., description="内核日志响应数据")


class IMConfigChangeResponseData(DataBaseModel):
    air_play_name: str = Field(..., description="AirPlay 名称")
    lang: str = Field(..., description="语言")
    mdns_type: int = Field(..., description="mDNS 类型")
    connect_failed_retry: int = Field(..., description="连接失败的重试次数")
    air_play_ratio: int = Field(..., description="AirPlay 比例")
    opencv_num: int = Field(..., description="OpenCV 处理线程数量")
    ocr_num: int = Field(..., description="OCR 处理线程数量")
    allow_ip_list: List[str] = Field(..., description="允许的 IP 列表")
    air_play_fps: int = Field(..., description="AirPlay 帧率")
    air_play_img_fps: int = Field(..., description="AirPlay 图片帧率")
    air_play_refresh_rate: int = Field(..., description="AirPlay 刷新率")
    air_play_port: int = Field(..., description="AirPlay 端口")
    air_play_audio: bool = Field(..., description="是否启用音频")
    auto_connect: bool = Field(..., description="是否自动硬件自动投屏")
    auto_updata: bool = Field(..., description="是否自动更新")
    thread_mode: bool = Field(..., description="是否启用线程群控模式")
    mouse_mode: bool = Field(..., description="是否启用快狠准鼠标模式")
    flip_right: bool = Field(..., description="是否启用像右翻转")


class IMConfigChangeResponse(ResponseBaseModel):
    data: IMConfigChangeResponseData = Field(..., description="内核配置响应数据")

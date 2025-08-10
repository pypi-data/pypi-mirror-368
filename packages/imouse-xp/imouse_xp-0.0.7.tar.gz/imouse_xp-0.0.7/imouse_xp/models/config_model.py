from typing import List

from pydantic import BaseModel, Field

from imouse_xp.models import DataBaseModel, ResponseBaseModel


class UsbDeviceInfo(BaseModel):
    vid: str = Field(..., description="")
    pid: str = Field(..., description="")
    uid: str = Field(..., description="硬件序列号")
    ver: str = Field(..., description="硬件版本")


class ConfigUsbGetResponseData(DataBaseModel):
    list: List[UsbDeviceInfo] = Field(..., description="硬件列表")


class ConfigUsbGetResponse(ResponseBaseModel):
    data: ConfigUsbGetResponseData = Field(..., description="已连接硬件列表响应数据")


class DeviceModelCfgInfo(BaseModel):
    crc: str = Field(..., description="鼠标参数crc")
    describe: str = Field(..., description="备注")
    location: str = Field(..., description="鼠标参数")
    up_name: str = Field(..., description="上传用户")
    up_time: str = Field(..., description="上传时间")


class DeviceModelVerInfo(BaseModel):
    ver: str = Field(..., description="版本号")
    cfg_list: List[DeviceModelCfgInfo] = Field(..., description="鼠标参数列表")


class DeviceModelInfo(BaseModel):
    device_name: str = Field(..., description="手机名字")
    width: str = Field(..., description="物理宽度")
    height: str = Field(..., description="物理高度")
    model: str = Field(..., description="型号")
    scale: int = Field(..., description="物理像素和实际的比例")
    ver_list: List[DeviceModelVerInfo] = Field(..., description="版本列表")


class ConifgDeviceModelResponseData(DataBaseModel):
    list: List[DeviceModelInfo] = Field(..., description="支持手机列表")


class ConifgDeviceModelResponse(ResponseBaseModel):
    data: ConifgDeviceModelResponseData = Field(..., description="支持的手机列表响应数据")


class ConfigImServerGetResponseData(DataBaseModel):
    air_play_name: str = Field(..., description="投屏显示名字")
    restart_name: str = Field(..., description="重启名字")
    lang: str = Field(..., description="控制台语言")
    mdns_type: int = Field(..., description="投屏发现规则")
    connect_failed_retry: int = Field(..., description="连接失败重试次数")
    air_play_ratio: int = Field(..., description="投屏分辨率")
    opencv_num: int = Field(..., description="找图插件实例数")
    ocr_num: int = Field(..., description="ocr文字识别插件实例数")
    allow_ip_list: List = Field(..., description="允许的ip列表")
    air_play_fps: int = Field(..., description="投屏fps")
    air_play_img_fps: int = Field(..., description="投屏图像fps")
    air_play_refresh_rate: int = Field(..., description="投屏刷新率")
    air_play_port: int = Field(..., description="投屏通讯端口")
    air_play_audio: bool = Field(..., description="投屏声音")
    auto_connect: bool = Field(..., description="自动连接投屏")
    auto_updata: bool = Field(..., description="自动升级")
    thread_mode: bool = Field(..., description="使用线程模式批量操作硬件")
    mouse_mode: bool = Field(..., description="采用快准狠鼠标移动")
    flip_right: bool = Field(..., description="横屏向右反转的模式")


class ConfigImServerGetResponse(ResponseBaseModel):
    data: ConfigImServerGetResponseData = Field(..., description="内核配置响应数据")


ConfigImServerSetResponse = ConfigImServerGetResponse

ConfigImServerSetResponseData = ConfigImServerGetResponseData



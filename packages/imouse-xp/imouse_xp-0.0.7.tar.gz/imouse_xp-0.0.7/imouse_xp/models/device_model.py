from typing import List

from pydantic import BaseModel, Field, ValidationError

from imouse_xp.models import DataBaseModel, ResponseBaseModel

# 设备数据模型
class DeviceInfo(BaseModel):
    """
        设备信息模型
        Attributes:
            rotate (int): 旋转角度
            state (int): 设备状态, 1表示在线, 0表示离线
            imgw (int): 图片宽度
            imgh (int): 图片高度
            gid (int): 分组 ID
            air_ratio (int): 投屏分辨率
            air_fps (int): 投屏帧率
            air_refresh (int): 投屏刷新率
            air_img_fps (int): 投屏图像帧率
            air_audio (int): 声音状态
            name (str): 自定义名称
            srv_name (str): 连接投屏的名称
            width (str): 设备宽度
            height (str): 设备高度
            ip (str): IP 地址
            mac (str): MAC 地址
            user_name (str): 本机名称
            version (str): 设备版本
            model (str): 内部型号
            deviceid (str): 设备 ID
            device_name (str): 设备型号
            location_crc (str): 鼠标参数
            vid (str): VID
            pid (str): PID
            uid (str): 硬件序列号
            gname (str): 分组组名称
            uver (str): 硬件版本
        """
    rotate: int = Field(..., description="旋转角度")
    state: int = Field(..., description="设备状态,1在线,0离线")
    imgw: int = Field(..., description="图片宽度")
    imgh: int = Field(..., description="图片高度")
    gid: int = Field(..., description="分组 ID")
    air_ratio: int = Field(..., description="投屏分辨率")
    air_fps: int = Field(..., description="投屏帧率")
    air_refresh: int = Field(..., description="投屏刷新率")
    air_img_fps: int = Field(..., description="投屏图像帧率")
    air_audio: int = Field(..., description="声音状态")
    name: str = Field(..., description="自定义名称")
    srv_name: str = Field(..., description="连接投屏的名称")
    width: str = Field(..., description="设备宽度")
    height: str = Field(..., description="设备高度")
    ip: str = Field(..., description="IP 地址")
    mac: str = Field(..., description="MAC 地址")
    user_name: str = Field(..., description="本机名称")
    version: str = Field(..., description="设备版本")
    model: str = Field(..., description="内部型号")
    deviceid: str = Field(..., description="设备 ID")
    device_name: str = Field(..., description="设备型号")
    location_crc: str = Field(..., description="鼠标参数")
    vid: str = Field(..., description="")
    pid: str = Field(..., description="")
    uid: str = Field(..., description="硬件序列号")
    gname: str = Field(..., description="分组组名称")
    uver: str = Field(..., description="硬件版本")


class DeviceGroupInfo(BaseModel):
    id: str = Field(..., description="分组ID")
    name: str = Field(..., description="分组名称")


class DeviceGetResponseData(DataBaseModel):
    list: List[DeviceInfo] = Field(..., description="设备信息列表")


class DeviceGetResponse(ResponseBaseModel):
    data: DeviceGetResponseData = Field(..., description="设备列表响应数据")


class DeviceGroupGetResponseData(DataBaseModel):
    list: List[DeviceGroupInfo] = Field(..., description="分组信息列表")


class DeviceGroupGetResponse(ResponseBaseModel):
    data: DeviceGroupGetResponseData = Field(..., description="分组列表响应数据")


DeviceGroupGetDevResponse = DeviceGetResponse


class DeviceSetResponseData(DataBaseModel):
    list: List[str] = Field(..., description="设备id列表")


class DeviceSetResponse(ResponseBaseModel):
    data: DeviceSetResponseData = Field(..., description="设置设备响应数据")


DeviceDelResponse = DeviceSetResponse



DeviceGroupSetResponse = DeviceGroupGetResponse

DeviceGroupDelResponse = DeviceSetResponse


class DeviceSortSetResponseData(DataBaseModel):
    sort_index: int = Field(..., description="排序索引,从1开始")
    sort_value: int = Field(..., description="排序值,0未排序,-1升，1降")


class DeviceSortSetResponse(ResponseBaseModel):
    data: DeviceSortSetResponseData = Field(..., description="排序响应数据")

DeviceSortGetResponse = DeviceSortSetResponse

response_json = '''
{
  "data": {
    "list": [
      "90:81:58:EE:D1:9E,DC:2B:2A:14:2A:F6"
    ],
    "code": 0,
    "id": "90:81:58:EE:D1:9E",
    "message": "成功"
  },
  "status": 200,
  "message": "成功",
  "msgid": 0,
  "fun": "/device/del"
}
'''

# # 加载 JSON 数据
# response_dict = json.loads(response_json)
#
# # 将 JSON 转换为模型实例
# try:
#     response_instance = DeviceSetResponse(**response_dict)
#     print("模型实例:", response_instance)
# except ValidationError as e:
#     print("模型验证失败:", e.json())
#
# # 访问模型中的字段
# print("功能名称:", response_instance.fun)
# print("消息 ID:", response_instance.msgid)
# print("状态码:", response_instance.status)


# 转换 JSON 为模型实例
# try:
#     # 转换设备设置响应
#     response_instance = parse_json_by_fun(response_dict)
#     device_set_instance = cast(DeviceDelResponse, response_instance)
#     print(response_instance)
# except ValueError as e:
#     print("解析失败:", e)

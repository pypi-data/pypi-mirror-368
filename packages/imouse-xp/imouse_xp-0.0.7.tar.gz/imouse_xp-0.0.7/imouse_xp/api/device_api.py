from abc import abstractmethod
from typing import List, cast, Dict, Any

from imouse_xp.models import DeviceGetResponse, DeviceGroupGetResponse, DeviceGroupGetDevResponse, DeviceSetResponse, \
    DeviceDelResponse, ResponseBaseModel, DeviceGroupSetResponse, DeviceGroupDelResponse, CommonResponse, \
    DeviceSortSetResponse, DeviceSortGetResponse, FunConstants


class DeviceApi():
    def __init__(self):
        super().__init__()

    @abstractmethod
    def _call_api(self, request_dict: dict, timeout: int = 0, is_async: bool = False) -> ResponseBaseModel:
        pass

    # 获取设备列表
    def device_get(self, id: List[str] = None, timeout: int = 0, is_async: bool = False) -> DeviceGetResponse:
        """
        获取设备列表信息
        :param id: 设备 ID 列表（可选）
         """
        data: Dict[str, Any] = {
            "id": ",".join(id) if id else "",
        }
        ret = self._call_api({'fun': FunConstants.DEVICE_GET, "data": data},
                             timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(DeviceGetResponse, ret)

    # 获取分组列表
    def device_group_get(self, id: List[str] = None, timeout: int = 0,
                         is_async: bool = False) -> DeviceGroupGetResponse:
        """
        获取设备分组列表信息
        :param id: 分组 ID 列表（可选）
        """
        data: Dict[str, Any] = {
            "id": ",".join(id) if id else "",
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_GROUP_GET, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(DeviceGroupGetResponse, ret)

    # 获取分组内设备
    def device_group_get_dev(self, id: str = "0", timeout: int = 0,
                             is_async: bool = False) -> DeviceGroupGetDevResponse:
        """
        获取分组内的设备信息
        :param id: 分组 ID，默认为 "0"
        """
        data: Dict[str, Any] = {
            "id": id,
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_GROUP_GET_DEV, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(DeviceGroupGetDevResponse, ret)

    # 设置设备
    def _device_set(self, id: List[str], name: str = None, vid: str = None, pid: str = None,
                    location_crc: str = None, gid: str = None, timeout: int = 0,
                    is_async: bool = False) -> DeviceSetResponse:
        data: Dict[str, Any] = {
            "id": ",".join(id),
            "name": name or "",  # 如果为 None，转为空字符串
            "vid": vid or "",
            "pid": pid or "",
            "location_crc": location_crc or "",
            "gid": gid or ""
        }
        ret = self._call_api({'fun': FunConstants.DEVICE_SET, "data": data},
                             timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(DeviceSetResponse, ret)

    # 删除设备
    def device_del(self, id: List[str], timeout: int = 0,
                   is_async: bool = False) -> DeviceDelResponse:
        """
        删除设备
        :param id: 设备 ID 列表
        """
        data: Dict[str, Any] = {
            "id": ",".join(id),
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_DEL, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(DeviceDelResponse, ret)

    # 设置分组名称
    def device_group_set(self, id: str, name: str, timeout: int = 0,
                         is_async: bool = False) -> DeviceGroupSetResponse:
        """
        设置分组名称
        :param id: 分组id
        :param name: 分组名称
        """
        data: Dict[str, Any] = {
            "id": id,
            "name": name
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_GROUP_SET, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(DeviceGroupSetResponse, ret)

    # 删除分组
    def device_group_del(self, id: List[str], timeout: int = 0,
                         is_async: bool = False) -> DeviceGroupDelResponse:
        """
        删除分组
        :param id: 分组 ID 列表
        """
        data: Dict[str, Any] = {
            "id": ",".join(id)
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_GROUP_DEL, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(DeviceGroupDelResponse, ret)

    # 设置设备投屏配置
    def device_airplay_set(self, id: List[str], air_ratio: int = 0, air_refresh: int = 0, air_fps: int = 0,
                           air_audio: int = 0,
                           air_img_fps: int = 0, timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        设置设备的投屏配置
        :param id: 设备 ID 列表
        :param air_ratio: 投屏分辨率
        :param air_refresh: 投屏刷新率
        :param air_fps: 投屏帧率
        :param air_audio: 音频投屏开关
        :param air_img_fps: 投屏图片解码帧率
        """
        data: Dict[str, Any] = {
            "id": ",".join(id),
            "air_ratio": air_ratio,
            "air_refresh": air_refresh,
            "air_fps": air_fps,
            "air_audio": air_audio,
            "air_img_fps": air_img_fps
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_AIRPLAY_SET, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 连接投屏
    def device_airplay_connect(self, id: List[str], timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        连接投屏
        :param id: 设备 ID 列表
        """
        data: Dict[str, Any] = {
            "id": ",".join(id)
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_AIRPLAY_CONNECT, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 投屏所有
    def device_airplay_connect_all(self, timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        投屏所有设备
        :param timeout: 超时时间（秒）
        """
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_AIRPLAY_CONNECT_ALL, "data": {}},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 断开投屏
    def device_airplay_disconnect(self, id: List[str], timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        断开设备投屏
        :param id: 设备 ID 列表
        """
        data: Dict[str, Any] = {
            "id": ",".join(id)
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_AIRPLAY_DISCONNECT, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 鼠标参数采集
    def device_collection_mouse(self, id: str, cmd: int, timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        采集设备鼠标参数
        :param id: 设备 ID
        :param cmd: 指令（0 查询采集状态,1 开始采集 2 停止采集）
        """
        data: Dict[str, Any] = {
            "id": id,
            "cmd": cmd
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_COLLECTION_MOUSE, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 保存鼠标参数到公共库
    def device_collection_mouse_save(self, id: str, describe: str, timeout: int = 0,
                                     is_async: bool = False) -> CommonResponse:
        """
        保存鼠标参数到公共库
        :param id: 设备 ID
        :param describe: 参数描述信息
        """
        data: Dict[str, Any] = {
            "id": id,
            "describe": describe
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_COLLECTION_MOUSE_SAVE, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 重启设备
    def device_restart(self, id: List[str], timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        重启设备
        :param id: 设备 ID 列表
        """
        data: Dict[str, Any] = {
            "id": ",".join(id)
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_RESTART, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 重启usb
    def device_usb_restart(self, id: List[str], timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        重启设备的 USB
        :param id: 设备 ID 列表
        """
        data: Dict[str, Any] = {
            "id": ",".join(id)
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_USB_RESTART, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 设置设备列表排序
    def device_sort_set(self, sort_index: int, sort_value: int, timeout: int = 0,
                        is_async: bool = False) -> DeviceSortSetResponse:
        """
        设置设备列表的排序
        :param sort_index: 排序索引
        :param sort_value: 排序值
        """
        data: Dict[str, Any] = {
            "sort_index": sort_index,
            "sort_value": sort_value
        }
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_SORT_SET, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(DeviceSortSetResponse, ret)

    # 获取设备列表排序
    def device_sort_get(self, timeout: int = 0, is_async: bool = False) -> DeviceSortGetResponse:
        """
        获取设备列表的排序信息
        """
        ret = self._call_api(
            {'fun': FunConstants.DEVICE_SORT_GET, "data": {}},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(DeviceSortGetResponse, ret)

    # 设置设备名称
    def device_set_name(self, id: List[str], name: str, timeout: int = 0, is_async: bool = False) -> DeviceSetResponse:
        """
        设置设备名称
         :param id: 设备 ID 列表
        :param name: 名称
        """
        return self._device_set(id, name=name, timeout=timeout, is_async=is_async)

    # 绑定硬件
    def device_set_vpid(self, id: str, vid: str, pid: str, timeout: int = 0,
                        is_async: bool = False) -> DeviceSetResponse:
        """
        绑定硬件
         :param id: 设备 ID
        :param vid: 硬件vid
        :param pid: 硬件pid
        """
        return self._device_set([id], vid=vid, pid=pid, timeout=timeout, is_async=is_async)

    # 设置鼠标参数
    def device_set_location(self, id: List[str], location_crc: str, timeout: int = 0,
                            is_async: bool = False) -> DeviceSetResponse:
        """
        设置鼠标参数
         :param id: 设备 ID 列表
        :param location_crc: 鼠标参数crc
        """
        return self._device_set(id, location_crc=location_crc, timeout=timeout, is_async=is_async)

    # 设置分组
    def device_set_gid(self, id: List[str], gid: str, timeout: int = 0,
                       is_async: bool = False) -> DeviceSetResponse:
        """
        绑定硬件
         :param id: 设备 ID 列表
        :param gid:: 分组id
        """
        return self._device_set(id, gid=gid, timeout=timeout, is_async=is_async)

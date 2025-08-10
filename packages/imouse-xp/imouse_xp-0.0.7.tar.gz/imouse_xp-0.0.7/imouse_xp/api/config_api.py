from abc import abstractmethod
from typing import List, cast, Dict

from imouse_xp.models import ResponseBaseModel, CommonResponse, FunConstants, ConfigImServerSetResponse, \
    ConfigImServerSetResponseData, ConifgDeviceModelResponse, ConfigUsbGetResponse, ConfigImServerGetResponseData


class ConfigApi():
    def __init__(self):
        super().__init__()

    @abstractmethod  # 抽象方法
    def _call_api(self, request_dict: dict, timeout: int = 0, is_async: bool = False) -> ResponseBaseModel:
        pass

    # 获取已连接硬件列表
    def config_usb_get(self, timeout: int = 0, is_async: bool = False) -> ConfigUsbGetResponse:
        """
        获取已连接硬件列表
        """
        ret = self._call_api(
            {'fun': FunConstants.CONFIG_USB_GET, "data": {}},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(ConfigUsbGetResponse, ret)

    # 获取支持设备类型库列表
    def config_devicemodel_get(self, timeout: int = 0, is_async: bool = False) -> ConifgDeviceModelResponse:
        """
        获取支持设备类型库列表
        """
        ret = self._call_api(
            {'fun': FunConstants.CONFIG_DEVICEMODLE_GET, "data": {}},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(ConifgDeviceModelResponse, ret)

    # 获取内核配置
    def config_imserver_get(self, timeout: int = 0, is_async: bool = False) -> ConfigImServerGetResponseData:
        """
        获取内核配置
        """
        ret = self._call_api(
            {'fun': FunConstants.CONFIG_SERVER_GET, "data": {}},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(ConfigImServerGetResponseData, ret)

    # 设置内核配置
    def config_imserver_set(self, im_config: ConfigImServerSetResponseData, timeout: int = 0,
                            is_async: bool = False) -> ConfigImServerSetResponse:
        """
        设置内核配置
        :param im_config: 内核配置对象,通过获取内核配置对象的data里面就可以得到
        """
        ret = self._call_api(
            {'fun': FunConstants.CONFIG_SERVER_SET, "data": im_config.model_dump()},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(ConfigImServerSetResponse, ret)

    # 重新广播投屏
    def imserver_regmdns(self, timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        重新广播投屏
        """
        ret = self._call_api(
            {'fun': FunConstants.CONFIG_REGMDNS, "data": {}},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 重启内核
    def imserver_restart(self, timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        重启内核
        """
        ret = self._call_api(
            {'fun': FunConstants.CONFIG_RESTARE, "data": {}},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

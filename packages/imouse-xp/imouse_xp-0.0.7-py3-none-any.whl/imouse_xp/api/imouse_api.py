import json
import time
from typing import Callable

from imouse_xp.api.config_api import ConfigApi
from imouse_xp.api.device_api import DeviceApi
from imouse_xp.api.mouse_api import MouseApi
from imouse_xp.api.pic_api import PicApi
from imouse_xp.api.shortcut_api import ShortcutApi
from imouse_xp.api.user_api import UserApi
from imouse_xp.logs import error, debug
from imouse_xp.models import parse_json_by_fun, ResponseBaseModel, CommonResponse
from imouse_xp.net import NetBase

IMouseCallBack = Callable[[str, ResponseBaseModel], None]


def is_success(common_response: CommonResponse) -> bool:
    return common_response.status == 200 and common_response.data.code == 0


class IMouseApi(NetBase, DeviceApi, MouseApi, UserApi, ConfigApi, PicApi, ShortcutApi):
    """
    iMouse接口类
    """

    def __init__(self, host: str, imouse_call_back: IMouseCallBack = None, timeout: int = 15):
        super().__init__(host, timeout)
        self.__imouse_call_back = imouse_call_back

    def start(self):
        super().start()
        time.sleep(1)
        while not self.is_connected():
            debug(f'连接失败,延时1秒等待')
            time.sleep(1)

    def _handle_message(self, message: str):
        if self.__imouse_call_back is not None:
            response_dict = json.loads(message)
            response_instance = parse_json_by_fun(response_dict)
            self.__imouse_call_back(response_instance.fun, response_instance)

    def _call_api(self, request_dict: dict, timeout: int = 0,
                  is_async: bool = False) -> ResponseBaseModel | bytes | None:
        ret = self._network_request(json.dumps(request_dict), timeout, is_async)
        if ret is not None:
            try:
                if isinstance(ret, str):
                    return parse_json_by_fun(json.loads(ret))
                elif isinstance(ret, bytes):
                    return ret
            except ValueError as e:
                error(f'解析失败: {e}')
        return None

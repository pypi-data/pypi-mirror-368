from abc import abstractmethod
from typing import List, cast, Dict, Any

from imouse_xp.models import ResponseBaseModel, FunConstants, CommonResponse, UserInfoResponse


class UserApi():
    def __init__(self):
        super().__init__()

    @abstractmethod  # 抽象方法
    def _call_api(self, request_dict: dict, timeout: int = 0, is_async: bool = False) -> ResponseBaseModel:
        pass

    # 登录
    def user_login(self, phone: str, password: str, utag: int = 1, timeout: int = 0,
                   is_async: bool = False) -> UserInfoResponse:
        """
               用户登录
               :param phone: 用户手机号
               :param password: 用户密码
               :param utag: 子账号 默认值为 1,可以1-10
               """
        data: Dict[str, Any] = {
            "id": id,
            "phone": phone,
            "password": password,
            "utag": utag,
        }
        ret = self._call_api(
            {'fun': FunConstants.USER_LOGIN, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(UserInfoResponse, ret)

    # 退出登录
    def user_logout(self, timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        用户退出登录
        """
        ret = self._call_api(
            {'fun': FunConstants.USER_LOGOUT, "data": {}},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 获取用户信息
    def user_info(self, timeout: int = 0, is_async: bool = False) -> UserInfoResponse:
        """
        获取用户信息
        """
        ret = self._call_api(
            {'fun': FunConstants.USER_INFO, "data": {}},
            timeout=timeout, is_async=is_async)
        return cast(UserInfoResponse, ret)

    # 切换子账号
    def user_switch(self, id: int, timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        切换子账号
        """
        data: Dict[str, Any] = {
            "id": id
        }
        ret = self._call_api(
            {'fun': FunConstants.USER_SWITCH, "data": data},
            timeout=timeout, is_async=is_async)
        return cast(CommonResponse, ret)

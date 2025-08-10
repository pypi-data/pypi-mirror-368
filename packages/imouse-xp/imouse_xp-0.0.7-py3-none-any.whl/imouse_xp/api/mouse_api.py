from abc import abstractmethod
from typing import List, cast, Dict, Any

from imouse_xp.models import ResponseBaseModel, FunConstants, CommonResponse


class MouseApi():
    def __init__(self):
        super().__init__()

    @abstractmethod  # 抽象方法
    def _call_api(self, request_dict: dict, timeout: int = 0, is_async: bool = False) -> ResponseBaseModel:
        pass

    # 鼠标点击
    def mouse_click(self, id: List[str], x: int, y: int, button: str = None, time: int = None, timeout: int = 0,
                    is_async: bool = False) -> CommonResponse:
        """
        鼠标点击
        :param id: 设备 ID 列表
        :param x: 鼠标点击的 X 坐标
        :param y: 鼠标点击的 Y 坐标
        :param button: 按钮类型 1左键,2右键,3中键,为空默认左键 可选
        """
        # 过滤掉为空的
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "button": button,
                "x": x,
                "y": y,
                "time": time
            }.items()
            if value is not None
        }
        ret = self._call_api(
            {'fun': FunConstants.MOUSE_CLICK, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 鼠标滑动
    def mouse_swipe(self, id: List[str], direction: str, button: str = None, len: float = None,
                    step_sleep: int = None,
                    steping: int = None, brake: bool = None, sx: int = None, sy: int = None, ex: int = None,
                    ey: int = None,
                    timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        鼠标滑动
        :param id: 设备 ID 列表
        :param button: 按钮类型 1左键,2右键,为空默认左键 可选
        :param direction: 滑动方向 滑动方向up,down,left,right
        :param len: 滑动距离 假设0.9会从屏幕10%滑动到90% 可选
        :param step_sleep: 每步间隔时间 可选
        :param steping: 滑动步数 可选
        :param brake: 滑动完了立即停止 可选
        :param sx: 起始点 X 坐标 可选
        :param sy: 起始点 Y 坐标 可选
        :param ex: 结束点 X 坐标 可选
        :param ey: 结束点 Y 坐标 可选
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "button": button,
                "direction": direction,
                "len": len,
                "step_sleep": step_sleep,
                "steping": steping,
                "brake": brake,
                "sx": sx,
                "sy": sy,
                "ex": ex,
                "ey": ey,
            }.items()
            if value is not None
        }
        ret = self._call_api(
            {'fun': FunConstants.MOUSE_SWIPE, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 鼠标弹起
    def mouse_up(self, id: List[str], button: str = None, timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        鼠标弹起
        :param id: 设备 ID 列表
        :param button: 按钮类型 1左键,2右键,为空默认左键 可选
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "button": button,
            }.items()
            if value is not None
        }
        ret = self._call_api(
            {'fun': FunConstants.MOUSE_UP, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 鼠标按下
    def mouse_down(self, id: List[str], button: str = None, timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        鼠标按下
        :param id: 设备 ID 列表
        :param button: 按钮类型 1左键,2右键,为空默认左键 可选
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "button": button,
            }.items()
            if value is not None
        }
        ret = self._call_api(
            {'fun': FunConstants.MOUSE_DWON, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 鼠标移动
    def mouse_move(self, id: List[str], x: int, y: int, timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        鼠标移动
        :param id: 设备 ID 列表
        :param x: 鼠标移动的 X 坐标
        :param y: 鼠标移动的 Y 坐标
        """
        data: Dict[str, Any] = {
            "id": ",".join(id),
            "x": x,
            "y": y,
        }
        ret = self._call_api(
            {'fun': FunConstants.MOUSE_MOVE, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 鼠标复位
    def mouse_reset(self, id: List[str], timeout: int = 0, is_async: bool = False) -> CommonResponse:
        """
        鼠标复位
        :param id: 设备 ID 列表
        """
        data: Dict[str, Any] = {
            "id": ",".join(id)
        }
        ret = self._call_api(
            {'fun': FunConstants.MOUSE_RESET, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 鼠标滚轮
    def mouse_wheel(self, id: List[str], direction: str, len: int, number: int, timeout: int = 0,
                    is_async: bool = False) -> CommonResponse:
        """
        鼠标滚轮
        :param id: 设备 ID 列表
        :param direction: 滚轮方向 up上,down下,left左,right右
        :param len: 滚轮滚动距离
        :param number: 滚轮滚动次数
        """
        data: Dict[str, Any] = {
            "id": ",".join(id),
            "direction": direction,
            "len": len,
            "number:": number
        }
        ret = self._call_api(
            {'fun': FunConstants.MOUSE_WHEEL, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 键盘按下
    def key_down(self, id: List[str], key: str, timeout: int = 0,
                 is_async: bool = False) -> CommonResponse:
        """
        键盘按下
        :param id: 设备 ID 列表
        :param key: 按下的键值
        """
        data: Dict[str, Any] = {
            "id": ",".join(id),
            "key": key
        }
        ret = self._call_api(
            {'fun': FunConstants.KEY_DOWN, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 键盘弹起
    def key_up(self, id: List[str], key: str, timeout: int = 0,
               is_async: bool = False) -> CommonResponse:
        """
        键盘弹起
        :param id: 设备 ID 列表
        :param key: 弹起的键值
        """
        data: Dict[str, Any] = {
            "id": ",".join(id),
            "key": key
        }
        ret = self._call_api(
            {'fun': FunConstants.KEY_UP, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 键盘弹起所有
    def key_upall(self, id: List[str], timeout: int = 0,
                  is_async: bool = False) -> CommonResponse:
        """
        键盘弹起所有
        :param id: 设备 ID 列表
        """
        data: Dict[str, Any] = {
            "id": ",".join(id)
        }
        ret = self._call_api(
            {'fun': FunConstants.KEY_UPALL, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

    # 键盘输入
    def key_sendkey(self, id: List[str], key: str = None, fn_key: str = None, timeout: int = 0,
                    is_async: bool = False) -> CommonResponse:
        """
        键盘输入
        :param id: 设备 ID 列表
        :param key: 键值 可选
        :param fun_key: 使用热键的时候请将key参数留空 可选
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "key": key,
                "fn_key": fn_key
            }.items()
            if value is not None
        }
        ret = self._call_api(
            {'fun': FunConstants.KEY_SENDKEY, "data": data},
            timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(CommonResponse, ret)

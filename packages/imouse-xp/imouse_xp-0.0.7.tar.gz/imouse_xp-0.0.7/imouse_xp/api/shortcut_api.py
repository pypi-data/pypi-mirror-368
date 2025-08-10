from abc import abstractmethod
from typing import List, cast, Dict, Any

from imouse_xp.models import ResponseBaseModel, FunConstants, CommonResponse, ShortcutAlbumGetResponse, \
    ShortcutAlbumUploadResponse, ShortcutAlbumDelResponse, ShortcutAlbumClearResponse, ShortcutFileGetResponse, \
    ShortcutFileUploadResponse, ShortcutFileDleResponse, ShortcutClipboardResponse, ShortcutDeviceIpResponse


class ShortcutApi():
    def __init__(self):
        super().__init__()

    @abstractmethod  # 抽象方法
    def _call_api(self, request_dict: dict, timeout: int = 0, is_async: bool = False) -> ResponseBaseModel:
        pass

    # 获取相册列表
    def shortcut_album_get(self, id: str, album_name: str = "", num: int = 10, outtime: int = 15000):
        """
        id	字符串	设备id	不允许多个
        album_name	字符串	相册名字	不填写则获取最近项目的相册
        num	整数	获取条数	默认10条
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": id,
                "album_name": album_name,
                "num": num,
                "outtime": outtime,
            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_ALBUM_GET, "data": data},
            timeout=outtime + 1000)
        return cast(ShortcutAlbumGetResponse, ret)

    # 上传照片视频
    def shortcut_album_upload(self, id: List[str], files: List[str], album_name: str = None, zip: int = 0,
                              outtime: int = 15000):
        """
        id	字符串	设备id	多个设备用逗号隔开
        album_name	字符串	相册名字	不填写则是最近项目
        zip	整数	0不压缩,1压缩	默认不压缩,如果是一次传输很多小图片建议压缩
        files	字符串数组	上传文件的路径列表	-
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """

        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "album_name": album_name,
                "zip": zip,
                "files": files,
                "outtime": outtime,
            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_ALBUM_UPLOAD, "data": data},
            timeout=outtime + 1000)
        return cast(ShortcutAlbumUploadResponse, ret)

    # 下载照片视频
    def shortcut_album_down(self, id: str, list: List[dict], zip: int = 0, outtime: int = 15000):
        """
        id	字符串	设备id	多个设备用逗号隔开
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        list	json对象数组	需要删除的列表,例子 [{"album_name": "","name": "文件名","ext": "扩展名"}]	-
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": id,
                "zip": zip,
                "list": list,
                "outtime": outtime,
            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_ALBUM_DOWN, "data": data},
            timeout=outtime + 1000)
        return cast(CommonResponse, ret)

    # 删除照片视频
    def shortcut_album_del(self, id: List[str], list: List[dict], outtime: int = 15000):
        """

        id	字符串	设备id	多个设备用逗号隔开
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        list	json对象数组	需要删除的列表 例子 [{"album_name": "","name": "文件名","ext": "扩展名"}]	-
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "outtime": outtime,
                "list": list
            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_ALBUM_DEL, "data": data},
            timeout=outtime + 1000)
        return cast(ShortcutAlbumDelResponse, ret)

    # 清空照片视频
    def shortcut_album_clear(self, id: List[str], album_name: str = None, outtime: int = 15000):
        """

        id	字符串	设备id	多个设备用逗号隔开
        album_name	字符串	相册名字	不填写则是最近项目
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "album_name": album_name,
                "outtime": outtime,
            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_ALBUM_CLEAR, "data": data},
            timeout=outtime + 1000)
        return cast(ShortcutAlbumClearResponse, ret)

    # 获取文件列表
    def shortcut_file_get(self, id: str, path: str = None, outtime: int = 15000):
        """
        id	字符串	设备id	不允许多个
        path	字符串	路径	默认则是我的iPhone根目录
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": id,
                "path": path,
                "outtime": outtime,
            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_FILE_GET, "data": data},
            timeout=outtime + 1000)
        return cast(ShortcutFileGetResponse, ret)

    # 上传文件
    def shortcut_file_upload(self, id: List[str], files: List[str], path: str = None, zip: int = 0,
                             outtime: int = 15000):
        """
        文件的功能只有ios15和以上才支持
        id	字符串	设备id	多个设备用逗号隔开
        path	字符串	路径	默认则是我的iPhone根目录
        zip	整数	0不压缩,1压缩	默认不压缩,如果是一次传输很多小文件建议压缩
        files	字符串数组	上传文件的列表	-
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "path": path,
                "zip": zip,
                "files": files,
                "outtime": outtime,
            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_FILE_UPLOAD, "data": data},
            timeout=outtime + 1000)
        return cast(ShortcutFileUploadResponse, ret)

    # 删除文件
    def shortcut_file_down(self, id: List[str], list: List[dict], path: str = None, zip: int = 0,
                           outtime: int = 15000):
        """
        id	字符串	设备id	不允许多个
        path	字符串	路径	默认则是我的iPhone根目录
        zip	整数	0不压缩,1压缩	默认不压缩,如果是一次传输很多小文件建议压缩
        list	json对象数组	-	例子:[{"name":"文件名","ext":"扩展名"}]
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """

        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": id,
                "path": path,
                "zip": zip,
                "list": list,
                "outtime": outtime,
            }.items()
            if value is not None
        }
        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_FILE_DOWN, "data": data},
            timeout=outtime + 1000)
        return cast(CommonResponse, ret)

    # 删除文件
    def shortcut_file_del(self, id: List[str], list: List[dict], path: str = None, outtime: int = 15000):
        """

        id	字符串	设备id	多个设备用逗号隔开
        path	字符串	路径	默认则是我的iPhone根目录
        list	json对象数组	要删除的文件列表	例子:[{"name":"文件名","ext":"扩展名"}]
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒-
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "path": path,
                "outtime": outtime,
                "list": list
            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_FILE_DEL, "data": data},
            timeout=outtime)
        return cast(ShortcutFileDleResponse, ret)

    # 到手机剪切板
    def shortcut_clipboard_set(self, id: List[str], text: str, sleep: int = None, outtime: int = 15000):
        """

        id	字符串	设备id	多个设备用逗号隔开
        sleep	整数	延迟返回	秒为单位,一般无需延迟,只是在有些手机上可能要延时一下粘贴才有效
        text	字符串	要发送的文字	
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "sleep": sleep,
                "text": text,
                "outtime": outtime,
            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_CLIPBOARD_SET, "data": data},
            timeout=outtime + 1000)
        return cast(CommonResponse, ret)

    # 取手机剪切板
    def shortcut_clipboard_get(self, id: str, outtime: int = 15000):
        """

        id	字符串	设备id	不允许多个
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": id,
                "outtime": outtime,
            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_CLIPBOARD_GET, "data": data},
            timeout=outtime + 1000)
        return cast(ShortcutClipboardResponse, ret)

    # 打开url
    def shortcut_exec_url(self, id: List[str], url: str, outtime: int = 15000):
        """

        id	字符串	设备id	多个设备用逗号隔开
        url	字符串	-
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "url": url,
                "outtime": outtime,

            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_EXEC_URL, "data": data},
            timeout=outtime + 1000)
        return cast(CommonResponse, ret)

    # 关闭重启设备
    def shortcut_switch_device(self, id: List[str], state: int, outtime: int = 15000):
        """

        id	字符串	设备id	多个设备用逗号隔开
        state	整数	0关闭,1重启
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "state": state,
                "outtime": outtime,

            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_SWITCH_DEVICE, "data": data},
            timeout=outtime)
        return cast(CommonResponse, ret)

    # 亮度调节
    def shortcut_switch_bril(self, id: List[str], state: float, outtime: int = 15000):
        """
        id	字符串	设备id	多个设备用逗号隔开
        state	浮点数	亮度值	大于0小于1
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "state": state,
                "outtime": outtime,

            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_SWITCH_BRIL, "data": data},
            timeout=outtime + 1000)
        return cast(CommonResponse, ret)

    # 开关手电筒
    def shortcut_switch_torch(self, id: List[str], state: int, outtime: int = 15000):
        """
        id	字符串	设备id	多个设备用逗号隔开
        state	整数	0关闭,1打开
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "state": state,
                "outtime": outtime,

            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_SWITCH_TORCH, "data": data},
            timeout=outtime)
        return cast(CommonResponse, ret)

    # 开关飞行模式
    def shortcut_switch_flight(self, id: List[str], state: int, outtime: int = 15000):
        """
        id	字符串	设备id	多个设备用逗号隔开
        state	整数	0关闭,1打开
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "state": state,
                "outtime": outtime,

            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_SWITCH_FLIGHT, "data": data},
            timeout=outtime + 1000)
        return cast(CommonResponse, ret)

    # 开关蜂窝数据
    def shortcut_switch_cdpd(self, id: List[str], state: int, outtime: int = 15000):
        """
        id	字符串	设备id	多个设备用逗号隔开
        state	整数	0关闭,1打开
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "state": state,
                "outtime": outtime,

            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_SWITCH_CDPD, "data": data},
            timeout=outtime + 1000)
        return cast(CommonResponse, ret)

    # 开关无线局域网
    def shortcut_switch_wlan(self, id: List[str], state: int, outtime: int = 15000):
        """
        id	字符串	设备id	多个设备用逗号隔开
        state	整数	0关闭,1打开
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": ",".join(id),
                "state": state,
                "outtime": outtime,

            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_SWITCH_WLAN, "data": data},
            timeout=outtime + 1000)
        return cast(CommonResponse, ret)

    def shortcut_device_ip(self, id: str, state: int, outtime: int = 15000, timeout: int = 0, is_async: bool = False):
        """
        id	字符串	设备id	不允许多个
        state	整数	0局域网,1外网
        outtime	布尔值	超时时间	返回数据的超时时间,单位毫秒,默认15秒
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": id,
                "state": state,
                "outtime": outtime,

            }.items()
            if value is not None
        }

        ret = self._call_api(
            {'fun': FunConstants.SHORTCUT_DEVICE_IP, "data": data},
            timeout=timeout, is_async=is_async)
        return cast(ShortcutDeviceIpResponse, ret)

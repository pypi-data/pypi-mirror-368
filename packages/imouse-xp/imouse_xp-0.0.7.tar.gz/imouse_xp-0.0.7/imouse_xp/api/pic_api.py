from abc import abstractmethod
from typing import List, cast, Dict, Any

from imouse_xp.models import ResponseBaseModel, FunConstants, PicScreenshotResponse, PicFindImageResponse, \
    PicFindImageCvResponse, PicOcrResponse, PicFindTextResponse, PicFindMultiColorResponse


class PicApi():
    def __init__(self):
        super().__init__()

    @abstractmethod
    def _call_api(self, request_dict: dict, timeout: int = 0, is_async: bool = False) -> ResponseBaseModel:
        pass

    # 截图
    def pic_screenshot(self, id: str, rect: List[int] = None, binary: bool = None, jpg: bool = None,
                       save_path: str = None, timeout: int = 0,
                       is_async: bool = False) -> PicScreenshotResponse | bytes:
        """
        截图
        :param id: 设备 ID
        :param rect: 截图区域 [x1 y1 x2 y2] 左x,上y,右x,下y 可选
        :param binary: 是否返回二进制数据 可选
        :param jpg: 是否返回 JPG 格式图片 可选
        :param save_path: 保存截图的路径 可选
        :param timeout: 超时时间 单位为秒
        :param is_async: 是否为异步调用
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": id,
                "binary": binary,
                "jpg": jpg,
                "rect": rect,
                "save_path": save_path
            }.items()
            if value is not None
        }
        ret = self._call_api({'fun': FunConstants.PIC_SCREENSHOT, "data": data},
                             timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        if isinstance(ret, ResponseBaseModel):
            return cast(PicScreenshotResponse, ret)
        elif isinstance(ret, bytes):
            return ret

    # 普通找图
    def pic_find_image(self, id: str, img_list: List[str], rect: List[int] = None, delta_color: str = '111111',
                       similarity: float = 0.85,
                       all: bool = None, direction: str = None, target_img: str = None,
                       timeout: int = 0, is_async: bool = False) -> PicFindImageResponse:
        """
        普通找图
        :param id: 设备 ID
        :param img_list: 要匹配的base64字符串图片列表或者本地路径列表
        :param rect: 查找区域 [x1 y1 x2 y2] 左x,上y,右x,下y 可选
        :param delta_color: 颜色容差 默认值为 '111111'
        :param similarity: 相似度阈值 默认值为 0.85
        :param all: 是否查找所有 可选
        :param direction: 查找方向 可选
        :param target_img: 目标图片 可选
        :param timeout: 超时时间 单位为秒
        :param is_async: 是否为异步调用
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": id,
                "target_img": target_img,
                "delta_color": delta_color,
                "all": all,
                "direction": direction,
                "rect": rect,
                "similarity": similarity,
                "img_list": img_list
            }.items()
            if value is not None
        }
        ret = self._call_api({'fun': FunConstants.PIC_FIND_IMAGE, "data": data},
                             timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(PicFindImageResponse, ret)

    # opencv找图
    def pic_find_image_cv(self, id: str, img_list: List[str], rect: List[int] = None,
                          similarity: float = None,
                          same: bool = None, all: bool = None, target_img: str = None,
                          timeout: int = 0, is_async: bool = False) -> PicFindImageCvResponse:
        """
        使用 OpenCV 找图
        :param id: 设备 ID
        :param img_list: 要匹配的base64字符串图片列表或者本地路径列表
        :param rect: 查找区域 [x1 y1 x2 y2] 左x,上y,右x,下y 可选
        :param similarity: 相似度阈值 可选
        :param same: 是否查找重复的 可选
        :param all: 是否查找所有 可选
        :param target_img: 目标图片 可选
        :param timeout: 超时时间 单位为秒
        :param is_async: 是否为异步调用
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": id,
                "target_img": target_img,
                "same": same,
                "all": all,
                "rect": rect,
                "similarity": similarity,
                "img_list": img_list
            }.items()
            if value is not None
        }
        ret = self._call_api({'fun': FunConstants.PIC_FIND_IMAGE_CV, "data": data},
                             timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(PicFindImageCvResponse, ret)

    # 文字识别
    def pic_ocr(self, id: str, is_ex: bool = False, rect: List[int] = None, target_img: str = None,
                timeout: int = 0, is_async: bool = False) -> PicOcrResponse:
        """
        文字识别
        :param id: 设备 ID
        :param is_ex: 是否使用增强模式 可选
        :param rect: 识别区域 [x1 y1 x2 y2] 左x,上y,右x,下y 可选
        :param target_img: 目标图片 可选
        :param timeout: 超时时间 单位为秒
        :param is_async: 是否为异步调用
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": id,
                "target_img": target_img,
                "rect": rect,
            }.items()
            if value is not None
        }
        if is_ex:
            ret = self._call_api({'fun': FunConstants.PIC_OCR_EX, "data": data},
                                 timeout=timeout, is_async=is_async)
        else:
            ret = self._call_api({'fun': FunConstants.PIC_OCR, "data": data},
                                 timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(PicOcrResponse, ret)

    # 查找文字
    def pic_find_text(self, id: str, text: List[str], similarity: float = 0.8, contain: bool = None,
                      is_ex: bool = False,
                      rect: List[int] = None,
                      target_img: str = None,
                      timeout: int = 0, is_async: bool = False) -> PicFindTextResponse:
        """
        查找文字
        :param id: 设备 ID
        :param text: 要匹配的文本列表
        :param similarity: 相似度阈值 默认值为 0.8
        :param contain: 是否包含部分匹配 可选
        :param is_ex: 是否使用增强模式 可选
        :param rect: 查找区域 [x1 y1 x2 y2] 左x,上y,右x,下y 可选
        :param target_img: 目标图片 可选
        :param timeout: 超时时间 单位为秒
        :param is_async: 是否为异步调用
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": id,
                "similarity": similarity,
                "contain": contain,
                "target_img": target_img,
                "rect": rect,
                "text": text,
            }.items()
            if value is not None
        }
        if is_ex:
            ret = self._call_api({'fun': FunConstants.PIC_FIND_TEXT_EX, "data": data},
                                 timeout=timeout, is_async=is_async)
        else:
            ret = self._call_api({'fun': FunConstants.PIC_FIND_TEXT, "data": data},
                                 timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(PicFindTextResponse, ret)

    # 多点找色
    def pic_find_multi_color(self, id: str, color_list: List[dict], same: bool = None, all: bool = None,
                             target_img: str = None,
                             timeout: int = 0, is_async: bool = False) -> PicFindMultiColorResponse:
        """
        多点找色
        :param id: 设备 ID
        :param color_list: 要查找的颜色列表,参数填写例子[{"first_color":"被查找的颜色表","rect":[100,100,200,200],"similarity":0.85}]
        :param same: 是否查找重复的 可选
        :param all: 是否查找所有 可选
        :param target_img: 目标图片 可选
        :param timeout: 超时时间 单位为秒
        :param is_async: 是否为异步调用
        """
        data: Dict[str, Any] = {
            key: value
            for key, value in {
                "id": id,
                "same": same,
                "list": color_list,
                "all": all,
                "target_img": target_img,
            }.items()
            if value is not None
        }
        ret = self._call_api({'fun': FunConstants.PIC_FIND_MULTI_COLOR, "data": data},
                             timeout=timeout, is_async=is_async)
        if not ret:
            return ret
        return cast(PicFindMultiColorResponse, ret)

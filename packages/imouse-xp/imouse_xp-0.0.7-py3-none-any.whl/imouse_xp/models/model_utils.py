from pydantic import ValidationError

from imouse_xp.models import DeviceGetResponse, DeviceGroupGetResponse, DeviceGroupGetDevResponse, \
    DeviceSetResponse, \
    DeviceDelResponse, DeviceGroupSetResponse, DeviceGroupDelResponse, DeviceSortSetResponse, DeviceSortGetResponse, \
    CommonResponse, IMConnectResponse, UserInfoResponse, DeviceConnectResponse, DeviceDisconnectResponse, \
    DeviceRotateResponse, DeviceChangeResponse, USBChangeResponse, IMLogResponse, IMConfigChangeResponse, \
    ConifgDeviceModelResponse, ConfigImServerGetResponse, ConfigImServerSetResponse, \
    PicScreenshotResponse, PicFindImageResponse, PicFindImageCvResponse, PicOcrResponse, PicFindTextResponse, \
    PicFindMultiColorResponse, ShortcutAlbumGetResponse, \
    ShortcutAlbumUploadResponse, ShortcutAlbumDelResponse, ShortcutAlbumClearResponse, ShortcutFileGetResponse, \
    ShortcutFileUploadResponse, ShortcutFileDleResponse, ShortcutClipboardResponse, ShortcutDeviceIpResponse, \
    ConfigUsbGetResponse
from imouse_xp.logs import debug, error


# 功能常量
class FunConstants:
    # 设备相关
    DEVICE_GET = "/device/get"  # 获取设备列表
    DEVICE_GROUP_GET = "/device/group/get"  # 获取分组列表
    DEVICE_GROUP_GET_DEV = "/device/group/get-dev"  # 获取分组内设备
    DEVICE_SET = "/device/set"  # 设置设备
    DEVICE_DEL = "/device/del"  # 删除设备
    DEVICE_GROUP_SET = "/device/group/set"  # 设置分组
    DEVICE_GROUP_DEL = "/device/group/del"  # 删除分组
    DEVICE_AIRPLAY_SET = "/device/airplay/set"  # 设置设备投屏配置
    DEVICE_AIRPLAY_CONNECT = "/device/airplay/connect"  # 连接 AirPlay
    DEVICE_AIRPLAY_CONNECT_ALL = "/device/airplay/connect/all"  # 全部连接 AirPlay
    DEVICE_AIRPLAY_DISCONNECT = "/device/airplay/disconnect"  # 断开 AirPlay
    DEVICE_COLLECTION_MOUSE = "/device/collection/mouse"  # 鼠标采集
    DEVICE_COLLECTION_MOUSE_SAVE = "/device/collection/mouse/save"  # 保存鼠标采集数据
    DEVICE_RESTART = "/device/restart"  # 重启设备
    DEVICE_USB_RESTART = "/device/usb/restart"  # 重启 USB
    DEVICE_SORT_SET = "/device/sort/set"  # 设置设备排序
    DEVICE_SORT_GET = "/device/sort/get"  # 获取设备排序
    # 配置相关
    CONFIG_USB_GET = "/config/usb/get"  # 获取已连接硬件列表
    CONFIG_DEVICEMODLE_GET = "/config/devicemodel/get"  # 获取支持设备类型库列表
    CONFIG_SERVER_GET = "/config/imserver/get"  # 获取内核配置
    CONFIG_SERVER_SET = "/config/imserver/set"  # 设置内核配置
    CONFIG_RESTARE = "/imserver/restart"  # 重启内核
    CONFIG_REGMDNS = "/imserver/regmdns"  # 重启广播
    # 用户相关
    USER_LOGIN = "/config/user/login"  # 用户登录
    USER_LOGOUT = "/config/user/logout"  # 用户退出登录
    USER_INFO = "/config/user/info"  # 获取用户信息
    USER_SWITCH = "/config/user/switch"  # 切换子账号
    # 鼠标键盘相关
    MOUSE_CLICK = "/mouse/click"  # 鼠标点击
    MOUSE_SWIPE = "/mouse/swipe"  # 鼠标滑动
    MOUSE_UP = "/mouse/up"  # 鼠标抬起
    MOUSE_DWON = "/mouse/down"  # 鼠标按下
    MOUSE_MOVE = "/mouse/move"  # 鼠标移动
    MOUSE_RESET = "/mouse/reset"  # 鼠标复位
    MOUSE_WHEEL = "/mouse/wheel"  # 鼠标滑动
    KEY_DOWN = "/key/down"  # 键盘按下
    KEY_UP = "/key/up"  # 键盘弹起
    KEY_UPALL = "/key/upall"  # 键盘全部弹起
    KEY_SENDKEY = "/key/sendkey"  # 键盘输入
    # 图色相关
    PIC_SCREENSHOT = "/pic/screenshot"  # 截取屏幕
    PIC_FIND_IMAGE = "/pic/find-image"  # 普通找图
    PIC_FIND_IMAGE_CV = "/pic/find-image-cv"  # CV找图
    PIC_OCR = "/pic/ocr"  # ocr文字识别
    PIC_OCR_EX = "/pic/ocr-ex"  # ocr文字识别增强
    PIC_FIND_TEXT = "/pic/find-text"  # 识别文字
    PIC_FIND_TEXT_EX = "/pic/find-text-ex"  # 识别文字增强
    PIC_FIND_MULTI_COLOR = "/pic/find-multi-color"  # 多点找色
    # 快捷指令
    SHORTCUT_ALBUM_GET = "/shortcut/album/get"  # 获取相册列表
    SHORTCUT_ALBUM_UPLOAD = "/shortcut/album/upload"  # 上传照片视频
    SHORTCUT_ALBUM_DOWN = "/shortcut/album/down"  # 下载照片视频
    SHORTCUT_ALBUM_DEL = "/shortcut/album/del"  # 删除照片视频
    SHORTCUT_ALBUM_CLEAR = "/shortcut/album/clear"  # 清空照片视频
    SHORTCUT_FILE_GET = "/shortcut/file/get"  # 获取文件列表
    SHORTCUT_FILE_UPLOAD = "/shortcut/file/upload"  # 上次文件
    SHORTCUT_FILE_DOWN = "/shortcut/file/down"  # /文件下载
    SHORTCUT_FILE_DEL = "/shortcut/file/del"  # 删除文件
    SHORTCUT_CLIPBOARD_SET = "/shortcut/clipboard/set"  # 设置手机剪贴板
    SHORTCUT_CLIPBOARD_GET = "/shortcut/clipboard/get"  # 获取手机剪辑版
    SHORTCUT_EXEC_URL = "/shortcut/exec/url"  # 打开url
    SHORTCUT_SWITCH_DEVICE = "/shortcut/switch/device"  # 重启设备
    SHORTCUT_SWITCH_BRIL = "/shortcut/switch/bril"  # 亮度调节
    SHORTCUT_SWITCH_TORCH = "/shortcut/switch/torch"  # 打开手电筒
    SHORTCUT_SWITCH_FLIGHT = "/shortcut/switch/flight"  # 打开手电筒
    SHORTCUT_SWITCH_CDPD = "/shortcut/switch/cdpd"  # 打开蜂窝
    SHORTCUT_SWITCH_WLAN = "/shortcut/switch/wlan"  # 打开无线局域网
    SHORTCUT_DEVICE_IP = "/shortcut/device/ip"  # 获取IP


# 回调常量
class CallBackConstants:
    IM_CONNECT = 'im_connect'  # 连接内核成功
    IM_DISCONNECT = 'im_disconnect'  # 连接内核断开
    DEV_CONNECT = 'dev_connect'  # 有设备连接
    DEV_DISCONNECT = 'dev_disconnect'  # 有设备断开
    DEV_ROTATE = 'dev_rotate'  # 有设备旋转
    DEV_CHANGE = 'dev_change'  # 有设备改变
    DEV_DELETE = 'dev_delete'  # 有设备删除
    GROUP_CHANGE = 'group_change'  # 有分组改变
    GROUP_DELETE = 'group_delete'  # 有分组删除
    USB_CHANGE = 'usb_change'  # 有 USB 改变
    COLLECTION_MOUSE = 'collection_mouse'  # 采集鼠标参数状态
    AIRPLAY_CONNECT_LOG = 'airplay_connect_log'  # 自动投屏日志
    RESTART_LOG = 'restart_log'  # 调用重启手机的日志
    USER_INFO = 'user_info'  # 用户信息状态30秒左右会来一次
    IM_LOG = 'im_log'  # 内核日志,比如超出授权等
    ERROR_PUSH = 'error_push'  # 错误日志推送,比如出现未知的错误
    IM_CONFIG_CHANGE = 'im_config_change'  # 内核配置改变
    LOGOUT = 'logout'  # 账号退出登录
    DEV_SORT_CHANGE = 'dev_sort_change'  # 设备列表排序改变


FUN_MODEL_MAPPING = {
    # 设备相关
    FunConstants.DEVICE_GET: DeviceGetResponse,  # 获取设备列表
    FunConstants.DEVICE_GROUP_GET: DeviceGroupGetResponse,  # 获取分组列表
    FunConstants.DEVICE_GROUP_GET_DEV: DeviceGroupGetDevResponse,  # 获取分组内设备
    FunConstants.DEVICE_SET: DeviceSetResponse,  # 设置设备
    FunConstants.DEVICE_DEL: DeviceDelResponse,  # 删除设备
    FunConstants.DEVICE_GROUP_SET: DeviceGroupSetResponse,  # 设置分组
    FunConstants.DEVICE_GROUP_DEL: DeviceGroupDelResponse,  # 删除分组
    FunConstants.DEVICE_AIRPLAY_SET: CommonResponse,  # 设置 AirPlay
    FunConstants.DEVICE_AIRPLAY_CONNECT: CommonResponse,  # 连接 AirPlay
    FunConstants.DEVICE_AIRPLAY_DISCONNECT: CommonResponse,  # 断开 AirPlay
    FunConstants.DEVICE_AIRPLAY_CONNECT_ALL: CommonResponse,  # 全部连接 AirPlay
    FunConstants.DEVICE_COLLECTION_MOUSE: CommonResponse,  # 鼠标采集
    FunConstants.DEVICE_COLLECTION_MOUSE_SAVE: CommonResponse,  # 保存鼠标采集数据
    FunConstants.DEVICE_RESTART: CommonResponse,  # 重启设备
    FunConstants.DEVICE_USB_RESTART: CommonResponse,  # 重启 USB
    FunConstants.DEVICE_SORT_SET: DeviceSortSetResponse,  # 设置设备排序
    FunConstants.DEVICE_SORT_GET: DeviceSortGetResponse,  # 获取设备排序
    # 配置相关
    FunConstants.CONFIG_REGMDNS: CommonResponse,  # 重启广播
    FunConstants.CONFIG_RESTARE: CommonResponse,  # 重启内核
    FunConstants.CONFIG_USB_GET: ConfigUsbGetResponse,  # 获取已连接硬件列表
    FunConstants.CONFIG_DEVICEMODLE_GET: ConifgDeviceModelResponse,  # 获取支持设备类型库列表
    FunConstants.CONFIG_SERVER_GET: ConfigImServerGetResponse,  # 获取内核配置
    FunConstants.CONFIG_SERVER_SET: ConfigImServerSetResponse,  # 设置内核配置
    # 用户相关
    FunConstants.USER_LOGIN: UserInfoResponse,  # 用户登录
    FunConstants.USER_LOGOUT: CommonResponse,  # 用户退出登录
    FunConstants.USER_INFO: UserInfoResponse,  # 获取用户登录信息
    FunConstants.USER_SWITCH: CommonResponse,  # 切换子账号
    # 鼠标键盘相关
    FunConstants.MOUSE_CLICK: CommonResponse,  # 鼠标点击
    FunConstants.MOUSE_SWIPE: CommonResponse,  # 鼠标滑动
    FunConstants.MOUSE_UP: CommonResponse,  # 鼠标抬起
    FunConstants.MOUSE_DWON: CommonResponse,  # 鼠标按下
    FunConstants.MOUSE_MOVE: CommonResponse,  # 鼠标移动
    FunConstants.MOUSE_RESET: CommonResponse,  # 鼠标复位
    FunConstants.MOUSE_WHEEL: CommonResponse,  # 鼠标滑动
    FunConstants.KEY_DOWN: CommonResponse,  # 键盘按下
    FunConstants.KEY_UP: CommonResponse,  # 键盘弹起
    FunConstants.KEY_UPALL: CommonResponse,  # 键盘全部弹起
    FunConstants.KEY_SENDKEY: CommonResponse,  # 键盘输入
    # 图色相关
    FunConstants.PIC_SCREENSHOT: PicScreenshotResponse,  # 截取屏幕
    FunConstants.PIC_FIND_IMAGE: PicFindImageResponse,  # 普通找图
    FunConstants.PIC_FIND_IMAGE_CV: PicFindImageCvResponse,  # OpenCv找图
    FunConstants.PIC_OCR: PicOcrResponse,  # OCR文字识别
    FunConstants.PIC_OCR_EX: PicOcrResponse,  # OCR文字识别 EX
    FunConstants.PIC_FIND_TEXT: PicFindTextResponse,  # 识别文字
    FunConstants.PIC_FIND_TEXT_EX: PicFindTextResponse,  # 识别文字
    FunConstants.PIC_FIND_MULTI_COLOR: PicFindMultiColorResponse,  # 多点找色
    # 快捷指令
    FunConstants.SHORTCUT_ALBUM_GET: ShortcutAlbumGetResponse,  # 获取相册列表
    FunConstants.SHORTCUT_ALBUM_UPLOAD: ShortcutAlbumUploadResponse,  # 上传照片视频
    FunConstants.SHORTCUT_ALBUM_DOWN: CommonResponse,  # 下载照片视频
    FunConstants.SHORTCUT_ALBUM_DEL: ShortcutAlbumDelResponse,  # 删除照片视频
    FunConstants.SHORTCUT_ALBUM_CLEAR: ShortcutAlbumClearResponse,  # 清空照片视频
    FunConstants.SHORTCUT_FILE_GET: ShortcutFileGetResponse,  # 获取文件列表
    FunConstants.SHORTCUT_FILE_UPLOAD: ShortcutFileUploadResponse,  # 上传文件
    FunConstants.SHORTCUT_FILE_DOWN: CommonResponse,  # 下载文件
    FunConstants.SHORTCUT_FILE_DEL: ShortcutFileDleResponse,  # 删除文件
    FunConstants.SHORTCUT_CLIPBOARD_SET: CommonResponse,  # 设置手机剪辑版
    FunConstants.SHORTCUT_CLIPBOARD_GET: ShortcutClipboardResponse,  # 获取手机剪辑版
    FunConstants.SHORTCUT_EXEC_URL: CommonResponse,  # 打开url
    FunConstants.SHORTCUT_SWITCH_DEVICE: CommonResponse,  # 重启设备
    FunConstants.SHORTCUT_SWITCH_BRIL: CommonResponse,  # 亮度调节
    FunConstants.SHORTCUT_SWITCH_TORCH: CommonResponse,  # 打开手电筒
    FunConstants.SHORTCUT_SWITCH_FLIGHT: CommonResponse,  # 打开飞行模式
    FunConstants.SHORTCUT_SWITCH_CDPD: CommonResponse,  # 打开蜂窝
    FunConstants.SHORTCUT_SWITCH_WLAN: CommonResponse,  # 打开无线局域网
    FunConstants.SHORTCUT_DEVICE_IP: ShortcutDeviceIpResponse,  # 打开无线局域网

    # 回调相关
    CallBackConstants.IM_CONNECT: IMConnectResponse,  # 连接内核成功
    CallBackConstants.IM_DISCONNECT: CommonResponse,  # 连接内核断开
    CallBackConstants.DEV_CONNECT: DeviceConnectResponse,  # 有设备连接
    CallBackConstants.DEV_DISCONNECT: DeviceDisconnectResponse,  # 有设备断开
    CallBackConstants.DEV_ROTATE: DeviceRotateResponse,  # 有设备旋转
    CallBackConstants.DEV_CHANGE: DeviceChangeResponse,  # 有设备改变
    CallBackConstants.DEV_DELETE: DeviceDelResponse,  # 有设备删除
    CallBackConstants.GROUP_CHANGE: DeviceGroupSetResponse,  # 有分组改变
    CallBackConstants.GROUP_DELETE: DeviceGroupDelResponse,  # 有分组删除
    CallBackConstants.USB_CHANGE: USBChangeResponse,  # 有 USB 改变
    CallBackConstants.COLLECTION_MOUSE: CommonResponse,  # 采集鼠标参数状态
    CallBackConstants.AIRPLAY_CONNECT_LOG: CommonResponse,  # 自动投屏日志
    CallBackConstants.RESTART_LOG: CommonResponse,  # 调用重启手机的日志
    CallBackConstants.USER_INFO: UserInfoResponse,  # 用户信息状态
    CallBackConstants.IM_LOG: IMLogResponse,  # 内核日志
    CallBackConstants.ERROR_PUSH: IMLogResponse,  # 错误日志推送
    CallBackConstants.IM_CONFIG_CHANGE: IMConfigChangeResponse,  # 内核配置改变
    CallBackConstants.LOGOUT: CommonResponse,  # 账号退出登录
    CallBackConstants.DEV_SORT_CHANGE: DeviceSortGetResponse,  # 设备列表排序改变
}


# 根据功能名称，解析 JSON 数据为对应的模型实例
def parse_json_by_fun(json_data: dict):
    fun = json_data.get("fun")
    if not fun:
        error("JSON 中缺少 'fun' 字段")
    model = FUN_MODEL_MAPPING.get(fun)
    if not model:
        error(f"未找到 fun '{fun}' 对应的模型")
    try:
        return model(**json_data)
    except ValidationError as e:
        error(f"模型验证失败: {e}")

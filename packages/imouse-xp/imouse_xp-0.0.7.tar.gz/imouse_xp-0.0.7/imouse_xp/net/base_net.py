import abc
import json
import threading

import requests
import websocket
from requests.adapters import HTTPAdapter
from websocket import WebSocketApp, WebSocketException

from imouse_xp.logs import debug, error


class NetBase:
    def __init__(self, host: str, timeout: int = 15):
        """
        初始化 NetBase 类。

        :param host: 主机地址。
        :param timeout: 网络请求超时时间。
        """
        self._global_timeout = timeout
        self.host = host
        self.base_url = f'http://{host}:9911/api'
        self._ws = WebSocketApp
        self._is_working = False
        self._is_connected = False
        self._session = requests.Session()
        self._adapter = HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self._session.mount('http://', self._adapter)

    def start(self):
        """启动网络通信。"""
        self._is_working = True
        t1 = threading.Thread(target=self._initialize_websocket, name='WebSocket 初始化')
        debug('启动网络通信')
        t1.start()

    def stop(self):
        """停止网络通信。"""
        self._is_working = False
        if self._is_connected:
            self._ws.close()

    def is_connected(self) -> bool:
        """返回网络是否已连接。"""
        return self._is_connected

    def _network_request(self, data: str, timeout: int = 0, is_async: bool = False) -> str | bytes:
        """
        发送网络请求。

        :param data: 要发送的数据。
        :param timeout: 超时时间。
        :return: 响应数据。
        """
        ret = None
        try:
            if timeout == 0:
                timeout = self._global_timeout
            if is_async:
                debug(f'异步请求，timeout={timeout}: \r\n' + data)
                self._ws.send(data)
            else:
                debug(f'同步请求，timeout={timeout}: \r\n' + data)
                ret = self._session.post(self.base_url, json=json.loads(data), timeout=timeout)
                if ret.headers['Content-Type'] == 'application/octet-stream':
                    debug(f'同步响应: \r\n 二进制数据')
                    return ret.content

                else:
                    debug(f'同步响应: \r\n' + ret.text)
                    return ret.text

        except requests.exceptions.RequestException as e:
            error(f'网络请求错误: {e}')
            ret = f'{{"fun":"", "message":"{e}", "status":400}}'
        return ret

    @abc.abstractmethod
    def _handle_message(self, message: str):
        """
        抽象方法，处理接收到的消息。

        :param message: 接收到的消息。
        """
        pass

    def _on_data(self, ws, message, data_type, continue_flag):
        """
        收到数据的回调方法。

        :param ws: WebSocket 实例。
        :param message: 收到的消息。
        :param data_type: 数据类型。
        :param continue_flag: 指示消息是否继续的标志。
        """
        if data_type == websocket.ABNF.OPCODE_TEXT:
            debug(f'回调数据: \r\n{message}')
            self._handle_message(message)

    def _on_error(self, ws, error):
        """
        WebSocket 错误的回调方法。

        :param ws: WebSocket 实例。
        :param error: 错误消息。
        """
        # log.info(f'WebSocket 错误: {error}')
        pass

    def _on_close(self, ws, close_status_code, close_msg):
        """
        WebSocket 关闭事件的回调方法。

        :param ws: WebSocket 实例。
        :param close_status_code: 关闭事件的状态码。
        :param close_msg: 关闭消息。
        """

        if self._is_connected:
            self._handle_message(
                json.dumps({"fun": "im_disconnect", "status": 200, "message": "", "msgid": 0, "data": {}}))
            debug('WebSocket 连接已关闭')
        self._is_connected = False

    def _on_open(self, ws):
        """
        WebSocket 打开事件的回调方法。

        :param ws: WebSocket 实例。
        """
        self._is_connected = True
        debug('WebSocket 连接已打开')

    def _initialize_websocket(self):
        """
        初始化 WebSocket 连接。
        """
        self._ws = websocket.WebSocketApp(f'ws://{self.host}:9911/api',
                                          on_data=self._on_data,
                                          on_error=self._on_error,
                                          on_open=self._on_open,
                                          on_close=self._on_close)
        while self._is_working:
            try:
                self._ws.run_forever(ping_interval=1)
                self._is_connected = False
            except WebSocketException as e:
                self._ws.close()
                error(f'WebSocket 异常: {e}')
            except KeyboardInterrupt:
                debug('用户中断程序')
                break
            except Exception as e:
                error(f'发生异常: {e}')

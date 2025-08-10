import imouse_xp.models as models
from imouse_xp.api.imouse_api import IMouseApi


def imouse_callback(fun: str, response: models.ResponseBaseModel):
    pass


imouse = IMouseApi(host='192.168.9.9', imouse_call_back=imouse_callback)
imouse.start()

ret = imouse.device_airplay_set(['24:F0:94:2F:0A:9D', '60:9A:C1:9A:22:A1'],1080)
imouse.key_sendkey()
print(ret)

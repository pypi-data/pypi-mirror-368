import aiohttp
import logging
from .usdk_token import usdk_token
from .pb2 import get_self_info_pb2
from google.protobuf import message
class Headers:
    @classmethod
    def ProtoBuf(cls):
        return {
            "user-agent": "android 1.4.80",
            "accept": "application/x-protobuf",
            "accept-encoding": "gzip",
            "device-id": "1145141919810",
            "content-type": "application/x-protobuf",
            "token": usdk_token.Get(False)
        }
    @classmethod
    def Json(cls):
        return {
            "user-agent": "android 1.4.80",
            "accept": "application/json",
            "accept-encoding": "gzip",
            "device-id": "1145141919810",
            "content-type": "application/json",
            "token": usdk_token.Get()
        }


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('usdk.log'),
        logging.StreamHandler(),
    ],
    force=True
)

class Person:
    async def Info(self, token: str=None):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url="https://chat-go.jwzhd.com/v1/user/info", headers={
                    "user-agent": "android 1.4.80",
                    "accept": "application/x-protobuf",
                    "accept-encoding": "gzip",
                    "device-id": "1145141919810",
                    "content-type": "application/x-protobuf",
                    "token": token
                }) as res:
                    data = await res.read()
                    try:
                        proto = get_self_info_pb2.GetSelfInfo()
                    except message.DecodeError:
                        return {
                            "code": -3,
                            "msg": '数据解析失败'
                        }
                    proto.ParseFromString(data)
                    if proto.status.code != 1:
                        logging.info(f"获取个人信息失败:{proto.status.msg}")
                        return {
                            "code": proto.status.code,
                            "msg": proto.status.msg
                        }
                    logging.info("获取个人信息成功")
                    return {
                        "code": proto.status.code,
                        "msg": proto.status.msg,
                        "data": {
                            "id": proto.data.id,
                            "name": proto.data.name,
                            "avatar_url": proto.data.avatar_url,
                            "phone": proto.data.phone,
                            "email": proto.data.email,
                            "coin": proto.data.coin,
                            "vip_expired_time": proto.data.vip_expired_time,
                            'invite_code': proto.data.invitation_code, 
                        }
                    }
        except aiohttp.ClientError as e:
            return {
                "code": -1,
                "msg": "网络错误"
            }
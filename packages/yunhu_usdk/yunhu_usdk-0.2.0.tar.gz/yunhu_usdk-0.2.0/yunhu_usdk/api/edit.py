import aiohttp
from .usdk_token import usdk_token
from .pb2 import edit_message_pb2
import json
from google.protobuf import message
import logging

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

recvtype_keys = {
    "user": 1,
    "group": 2,
    "bot": 3
}

class Headers:
    @classmethod
    def Protobuf(cls):
        return {
            "user-agent": "android 1.4.80",
            "accept": "application/x-protobuf",
            "accept-encoding": "gzip",
            "device-id": "1145141919810",
            "content-type": "application/x-protobuf",
            "token": usdk_token.Get()
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

class Edit_Message:
    def __init__(self, recvId, recvType):
        self.recvId = recvId
        self.recvType = recvType

    async def Request(self, data):
        try:
            async with aiohttp.ClientSession() as requests:
                async with requests.post(
                    url="https://chat-go.jwzhd.com/v1/msg/edit-message",
                    data=data,
                    headers=Headers.Protobuf()
                ) as response:
                    return await response.read()
        except aiohttp.ClientError as e:
            logging.error(f"编辑消息失败：{e}")
            return {'code': -1, 'msg': "网络错误"}

    async def TextMessage(self, msg_id: str, text: str, content_type: int, buttons: list=[], quote_text: str=None, quote_id: str=None):
        proto = edit_message_pb2.send_message()
        proto.msg_id = msg_id
        proto.chat_id = self.recvId
        proto.chat_type = recvtype_keys[self.recvType]

        if type(buttons) is not list:
            logging.error("编辑消息失败，buttons类型错误(应为list)")
            return {'code': -2, 'msg': "buttons类型错误(应为list)"}
            
        buttons_data = json.dumps(buttons)
        if content_type == 5:
            proto.data.form = json.dumps(text)
        else:
            proto.data.text = text
        proto.msg_type = content_type
        proto.data.buttons = buttons_data
        proto.data.quote_msg_text = quote_text if quote_text else ""
        proto.quote_msg_id = quote_id if quote_id else ""

        binary_data_req = proto.SerializeToString()

        binary_data_res = await self.Request(data=binary_data_req)
        if isinstance(binary_data_res, dict) and 'code' in binary_data_res and binary_data_res['code'] < 0:
            return binary_data_res
            
        proto_res = edit_message_pb2.send_message_res()
        try:
            proto_res.ParseFromString(binary_data_res)
            result = {
                "code": proto_res.status.code,
                "msg": proto_res.status.msg
            }
            if proto_res.status.code == 1:
                logging.info(f"成功编辑消息")
                return result
            else:
                logging.error(f"编辑消息失败：{proto_res.status.msg}")
                return result
        except message.DecodeError:
            try:
                json_data = json.loads(binary_data_res)
                result = {
                    "code": json_data.get('code', -3),
                    "msg": json_data.get('msg', '未知错误')
                }
                if json_data.get('code', -3) == 1:
                    logging.info("成功编辑消息")
                    return result
                else:
                    logging.error(f"编辑消息失败：{json_data.get('msg', '未知错误')}")
                    return result
            except json.JSONDecodeError:
                logging.error("数据解析失败")
                return {'code': -3, 'msg': "数据解析失败"}

    async def Text(self, msg_id: str, text: str,buttons: list=[], quote_text: str=None, quote_id: str=None):
        if quote_text and not quote_id:
            logging.warning("当传入quote_text时，必须同时传入quote_id，否则前端显示可能失效")
        return await self.TextMessage(msg_id, text, 1, buttons=buttons, quote_text=quote_text, quote_id=quote_id)

    async def Markdown(self, msg_id: str, text: str, buttons: list=[], quote_text: str=None, quote_id: str=None):
        if quote_text and not quote_id:
            logging.warning("当传入quote_text时，必须同时传入quote_id，否则前端显示可能失效")
        return await self.TextMessage(msg_id, text, 3, buttons=buttons, quote_text=quote_text, quote_id=quote_id)

    async def Html(self, msg_id: str, text: str, buttons: list=[], quote_text: str=None, quote_id: str=None):
        if quote_text and not quote_id:
            logging.warning("当传入quote_text时，必须同时传入quote_id，否则前端显示可能失效")
        return await self.TextMessage(msg_id, text, 8, buttons=buttons, quote_text=quote_text, quote_id=quote_id)
    
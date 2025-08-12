import aiohttp
from .usdk_token import usdk_token
from .pb2 import send_message_pb2
import uuid
import json
from .upload import Upload
from google.protobuf import message
import os
import hashlib
import logging
from tinytag import TinyTag
from PIL import Image
from .post import Post_Message

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

upload = Upload()
post = Post_Message()

recvtype_keys = {
    "user": 1,
    "group": 2,
    "bot": 3
}

class Headers:
    Protobuf = {
        "user-agent": "android 1.4.80",
        "accept": "application/x-protobuf",
        "accept-encoding": "gzip",
        "device-id": "1145141919810",
        "content-type": "application/x-protobuf",
        "token": usdk_token.Get()
    }
    Json = {
        "user-agent": "android 1.4.80",
        "accept": "application/json",
        "accept-encoding": "gzip",
        "device-id": "1145141919810",
        "content-type": "application/json",
        "token": usdk_token.Get()
    }

class Send_Message:
    def __init__(self, recvId, recvType):
        self.recvId = recvId
        self.recvType = recvType

    async def Request(self, data):
        try:
            async with aiohttp.ClientSession() as requests:
                async with requests.post(
                    url="https://chat-go.jwzhd.com/v1/msg/send-message",
                    data=data,
                    headers=Headers.Protobuf
                ) as response:
                    return await response.read()
        except aiohttp.ClientError as e:
            logging.error(f"发送消息失败：{e}")
            return {'code': -1, 'msg': "网络错误"}

    async def TextMessage(self, text: str, content_type: int, command_id: int=None, buttons: list=[], quote_text: str=None, quote_id: str=None, at_users: list=[]):
        proto = send_message_pb2.send_message()
        proto.msg_id = uuid.uuid4().hex
        proto.chat_id = self.recvId
        proto.chat_type = recvtype_keys[self.recvType]

        if command_id and type(command_id) is not int:
            logging.error("发送消息失败，command_id类型错误(应为int)")
            return {'code': -2, 'msg': "command_id类型错误(应为int)"}
        if type(buttons) is not list:
            logging.error("发送消息失败，buttons类型错误(应为list)")
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
        proto.command_id = command_id if command_id else 0
        if type(at_users) is not list:
            logging.error("发送消息失败，at_users类型错误(应为list)")
            return {'code': -2, 'msg': "at_users类型错误(应为list)"}
        proto.data.mentioned_id.extend(at_users)

        binary_data_req = proto.SerializeToString()

        binary_data_res = await self.Request(data=binary_data_req)
        if isinstance(binary_data_res, dict) and 'code' in binary_data_res and binary_data_res['code'] < 0:
            return binary_data_res
            
        proto_res = send_message_pb2.send_message_res()
        try:
            proto_res.ParseFromString(binary_data_res)
            result = {
                "code": proto_res.status.code,
                "msg": proto_res.status.msg
            }
            if proto_res.status.code == 1:
                logging.info(f"成功发送消息")
                return result
            else:
                logging.error(f"发送消息失败：{proto_res.status.msg}")
                return result
        except message.DecodeError:
            try:
                json_data = json.loads(binary_data_res)
                result = {
                    "code": json_data.get('code', -3),
                    "msg": json_data.get('msg', '未知错误')
                }
                if json_data.get('code', -3) == 1:
                    logging.info("成功发送消息")
                    return result
                else:
                    logging.error(f"发送消息失败：{json_data.get('msg', '未知错误')}")
                    return result
            except json.JSONDecodeError:
                logging.error("数据解析失败")
                return {'code': -3, 'msg': "数据解析失败"}

    async def Text(self, text: str, command_id: int=None, buttons: list=[], quote_text: str=None, quote_id: str=None, at_users: list=[]):
        if quote_text and not quote_id:
            logging.warning("当传入quote_text时，必须同时传入quote_id，否则前端显示可能失效")
        return await self.TextMessage(text, 1, command_id=command_id, buttons=buttons, quote_text=quote_text, quote_id=quote_id, at_users=at_users)

    async def Markdown(self, text: str, command_id: int=None, buttons: list=[], quote_text: str=None, quote_id: str=None, at_users: list=[]):
        if quote_text and not quote_id:
            logging.warning("当传入quote_text时，必须同时传入quote_id，否则前端显示可能失效")
        return await self.TextMessage(text, 3, command_id=command_id, buttons=buttons, quote_text=quote_text, quote_id=quote_id, at_users=at_users)

    async def Html(self, text: str, command_id: int=None, buttons: list=[], quote_text: str=None, quote_id: str=None, at_users: list=[]):
        if quote_text and not quote_id:
            logging.warning("当传入quote_text时，必须同时传入quote_id，否则前端显示可能失效")
        return await self.TextMessage(text, 8, command_id=command_id, buttons=buttons, quote_text=quote_text, quote_id=quote_id, at_users=at_users)

    async def FileMessage(self, file_type: int, file_data: dict, command_id: int=None, quote_text: str=None, quote_id: str=None, buttons: list=[], at_users: list=[]):
        proto = send_message_pb2.send_message()
        proto.msg_id = uuid.uuid4().hex
        proto.chat_id = self.recvId
        proto.chat_type = recvtype_keys[self.recvType]
        
        if command_id and type(command_id) is not int:
            logging.error("发送消息失败，command_id类型错误(应为int)")
            return {'code': -2, 'msg': "command_id类型错误(应为int)"}
        if type(buttons) is not list:
            logging.error("发送消息失败，buttons类型错误(应为list)")
            return {'code': -2, 'msg': "buttons类型错误(应为list)"}
        
        proto.command_id = command_id if command_id else 0
        proto.data.buttons = json.dumps(buttons)
        proto.msg_type = file_type
        proto.data.quote_msg_text = quote_text if quote_text else ""
        proto.quote_msg_id = quote_id if quote_id else ""
        if type(at_users) is not list:
            logging.error("发送消息失败，at_users类型错误(应为list)")
            return {'code': -2, 'msg': "at_users类型错误(应为list)"}
        proto.data.mentioned_id.extend(at_users)
        
        if file_type == 4:
            proto.data.file_name = file_data['file_name']
            proto.data.file_key = file_data['file_key']
            proto.file.file_hash = file_data['file_key']
            proto.data.file_size = file_data['file_size']
            proto.file.file_size = file_data['file_current_size']
            proto.file.file_suffix = file_data['file_suffix']
            proto.file.file_key = file_data['file_token']
            proto.file.file_key2 = file_data['file_token']
        elif file_type == 2:
            proto.data.image = file_data['file_key'] + file_data['file_suffix']
            proto.file.file_hash = file_data['file_key'] + file_data['file_suffix']
            proto.file.file_size = file_data['file_current_size']
            proto.file.file_suffix = file_data['file_suffix']
            proto.file.file_key = file_data['file_token']
            proto.file.file_key2 = file_data['file_token']
            proto.file.file_type = "image/jpeg"
            proto.file.image_width = file_data['file_width']
            proto.file.image_height = file_data['file_height']
        elif file_type == 10:
            proto.data.video = file_data['file_key']
            proto.file.file_hash = file_data['file_key']
            proto.file.file_size = file_data['file_current_size']
            proto.file.file_suffix = file_data['file_suffix']
            proto.file.file_key = file_data['file_token']
            proto.file.file_key2 = file_data['file_token']
            proto.file.file_type = "video/mp4"
            proto.data.file_size = file_data['file_current_size']
        elif file_type == 11:
            proto.data.audio = file_data['file_key']
            proto.file.file_hash = file_data['file_key']
            proto.file.file_size = file_data['file_current_size']
            proto.file.file_suffix = file_data['file_suffix']
            proto.file.file_key = file_data['file_token']
            proto.file.file_key2 = file_data['file_token']
            proto.file.file_type = "video/mp4"
            proto.data.file_size = file_data['file_current_size']
            proto.data.audio_time = file_data['audio_time']

        binary_data_req = proto.SerializeToString()
        binary_data_res = await self.Request(data=binary_data_req)
        if isinstance(binary_data_res, dict) and 'code' in binary_data_res and binary_data_res['code'] < 0:
            return binary_data_res
            
        proto_res = send_message_pb2.send_message_res()
        try:
            proto_res.ParseFromString(binary_data_res)
            result = {
                "code": proto_res.status.code,
                "msg": proto_res.status.msg
            }
            if proto_res.status.code == 1:
                logging.info(f"成功发送消息")
                return result
            else:
                logging.error(f"发送消息失败：{proto_res.status.msg}({proto_res.status.code})")
                return result
        except message.DecodeError:
            try:
                json_data = json.loads(binary_data_res)
                result = {
                    "code": json_data.get('code', -3),
                    "msg": json_data.get('msg', '未知错误')
                }
                if json_data.get('code', -3) == 1:
                    logging.info("成功发送消息")
                    return result
                else:
                    logging.error(f"发送消息失败：{json_data.get('msg', '未知错误')}({json_data.get('code', -3)})")
                    return result
            except json.JSONDecodeError:
                logging.error("数据解析失败")
                return {'code': -3, 'msg': "数据解析失败"}

    async def File(self, file_path: str, file_size: int=None, file_name: str=None, command_id: int=None, quote_text: str=None, quote_id: str=None, buttons: list=[], at_users: list=[]):
        if not os.path.exists(file_path):
            logging.error(f"上传文件失败：{file_path}不存在")
            return {'code': -4, 'msg': f"文件{file_path}不存在"}
        file_key = await upload.File(file_path)
        if file_key['code'] != 1:
            logging.debug(f"上传文本失败，已自动跳过发送逻辑")
            return {'code': -5, 'msg': "文件上传失败"}
        data = {
            "file_name": file_name if file_name else os.path.basename(file_path),
            "file_suffix" : os.path.splitext(os.path.basename(file_path))[1],
            "file_size": file_size if file_size else os.path.getsize(file_path),
            "file_current_size": os.path.getsize(file_path),
            "file_token": file_key,
            "file_key": hashlib.md5(open(file_path, 'rb').read()).hexdigest(),
        }
        return await self.FileMessage(4, data, command_id, quote_text, quote_id, buttons, at_users)
    
    async def Image(self, file_path: str, command_id: int=None, quote_text: str=None, quote_id: str=None, buttons: list=[], at_users: list=[]):
        if not os.path.exists(file_path):
            logging.error(f"上传图片失败：{file_path}不存在")
            return {'code': -4, 'msg': f"文件{file_path}不存在"}
        file_key = await upload.Image(file_path)
        if file_key['code'] != 1:
            logging.debug(f"上传图片失败，已自动跳过发送逻辑")
            return {'code': -5, 'msg': "图片上传失败"}
        image_current_width, image_current_height = Image.open(file_path).size
        data = {
            "file_name": os.path.basename(file_path),
            "file_suffix" : os.path.splitext(os.path.basename(file_path))[1],
            "file_current_size": os.path.getsize(file_path),
            "file_token": file_key,
            "file_key": hashlib.md5(open(file_path, 'rb').read()).hexdigest(),
            "file_width": image_current_width,
            "file_height": image_current_height,
        }
        return await self.FileMessage(2, data, command_id, quote_text, quote_id, buttons, at_users)
    
    async def Video(self, file_path: str, command_id: int=None, quote_text: str=None, quote_id: str=None, buttons: list=[], at_users: list=[]):
        if not os.path.exists(file_path):
            logging.error(f"上传视频失败：{file_path}不存在")
            return {'code': -4, 'msg': f"文件{file_path}不存在"}
        file_key = await upload.Video(file_path)
        if file_key['code'] != 1:
            logging.debug(f"上传视频失败，已自动跳过发送逻辑")
            return {'code': -5, 'msg': "视频上传失败"}
        data = {
            "file_name": os.path.basename(file_path),
            "file_suffix" : os.path.splitext(os.path.basename(file_path))[1],
            "file_current_size": os.path.getsize(file_path),
            "file_token": file_key,
            "file_key": hashlib.md5(open(file_path, 'rb').read()).hexdigest(),
        }
        return await self.FileMessage(10, data, command_id, quote_text, quote_id, buttons, at_users)

    async def Audio(self, file_path: str, audio_time :int=None, command_id: int=None, quote_text: str=None, quote_id: str=None, buttons: list=[], at_users: list=[]):
        if not os.path.exists(file_path):
            logging.error(f"上传音频失败：{file_path}不存在")
            return {'code': -4, 'msg': f"文件{file_path}不存在"}
        file_key = await upload.Audio(file_path)
        if file_key['code'] != 1:
            logging.debug(f"上传音频失败，已自动跳过发送逻辑")
            return {'code': -5, 'msg': "音频上传失败"}
        if audio_time and type(audio_time) is not int:
            logging.error("发送音频失败：audio_time类型错误")
            return {'code': -2, 'msg': "audio_time类型错误(应为int)"}
        data = {
            "file_name": os.path.basename(file_path),
            "file_suffix" : os.path.splitext(os.path.basename(file_path))[1],
            "file_current_size": os.path.getsize(file_path),
            "file_token": file_key,
            "file_key": hashlib.md5(open(file_path, 'rb').read()).hexdigest(),
            "audio_time": round(TinyTag.get(file_path).duration)
        }
        return await self.FileMessage(11, data, command_id, quote_text, quote_id, buttons, at_users)
        
    async def Post(self, post_id: int, post_type: int=None, post_title: str=None, post_content: str=None, command_id: int=None, quote_text: str=None, quote_id: str=None, buttons: list=[], at_users=[]):
        if post_type and post_type != "1" and post_type != "2":
            logging.error("发送消息错误：post_type必须为str 1或2")
            return {'code': -2, 'msg': "post_type必须为str 1或2"}
            
        if not post_title or not post_content or not post_type:
            post_data = await post.GetContent(post_id)
            if isinstance(post_data, dict) and 'code' in post_data and post_data['code'] < 0:
                logging.debug("获取文章内容出错，已跳过发送逻辑(如果该文章不存在,post_title,post_content应该必填)")
                return {'code': -5, 'msg': "获取文章内容失败"}
                
        post_title_req = post_title if post_title else post_data['post_title']
        post_content_req = post_content if post_content else post_data['post_content']
        post_type_req = post_type if post_type else post_data['post_type']

        proto = send_message_pb2.send_message()
        proto.msg_id = uuid.uuid4().hex
        proto.chat_id = self.recvId
        proto.chat_type = recvtype_keys[self.recvType]
        proto.data.post_id = str(post_id)
        proto.data.post_title = post_title_req
        proto.data.post_content = post_content_req
        proto.data.post_type = str(post_type_req)

        if command_id and type(command_id) is not int:
            logging.error("发送消息失败，command_id类型错误(应为int)")
            return {'code': -2, 'msg': "command_id类型错误(应为int)"}
        if type(buttons) is not list and type(buttons) is not str:
            logging.error("发送消息失败，buttons类型错误(应为list或str)")
            return {'code': -2, 'msg': "buttons类型错误(应为list或str)"}
        
        proto.command_id = command_id if command_id else 0
        proto.data.buttons = json.dumps(buttons)
        proto.msg_type = 6
        proto.data.quote_msg_text = quote_text if quote_text else ""
        proto.quote_msg_id = quote_id if quote_id else ""
        if type(at_users) is not list:
            logging.error("发送消息失败，at_users类型错误(应为list)")
            return {'code': -2, 'msg': "at_users类型错误(应为list)"}
        proto.data.mentioned_id.extend(at_users)

        binary_data_res = await self.Request(proto.SerializeToString())
        if isinstance(binary_data_res, dict) and 'code' in binary_data_res and binary_data_res['code'] < 0:
            return binary_data_res
            
        proto_res = send_message_pb2.send_message_res()
        try:
            proto_res.ParseFromString(binary_data_res)
            result = {
                "code": proto_res.status.code,
                "msg": proto_res.status.msg
            }
            if proto_res.status.code == 1:
                logging.info(f"成功发送消息")
                return result
            else:
                logging.error(f"发送消息失败：{proto_res.status.msg}({proto_res.status.code})")
                return result
        except message.DecodeError:
            try:
                json_data = json.loads(binary_data_res)
                result = {
                    "code": json_data.get('code', -3),
                    "msg": json_data.get('msg', '未知错误')
                }
                if json_data.get('code', -3) == 1:
                    logging.info("成功发送消息")
                    return result
                else:
                    logging.error(f"发送消息失败：{json_data.get('msg', '未知错误')}({json_data.get('code', -3)})")
                    return result
            except json.JSONDecodeError:
                logging.error("数据解析失败")
                return {'code': -3, 'msg': "数据解析失败"}

    async def Form(self, form_data: list, command_id: int=None, quote_text: str=None, quote_id: str=None, buttons: list=[], at_users=[]):
        return await self.TextMessage(form_data, 5, command_id, buttons, quote_text, quote_id, at_users)
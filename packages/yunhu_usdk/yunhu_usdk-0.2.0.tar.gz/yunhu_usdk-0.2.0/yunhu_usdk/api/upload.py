import aiohttp
from .usdk_token import usdk_token
import logging
import hashlib
import json
import os

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
class Headers:
    @classmethod
    def ProtoBuf(cls):
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


class Upload:
    async def GetToken(self, file_type):
        url_dict = {
            "image": "https://chat-go.jwzhd.com/v1/misc/qiniu-token",
            "video": "https://chat-go.jwzhd.com/v1/misc/qiniu-token-video",
            "file": 'https://chat-go.jwzhd.com/v1/misc/qiniu-token2',
            "audio": 'https://chat-go.jwzhd.com/v1/misc/qiniu-token-audio'
        }
        
        if file_type not in url_dict:
            return {'code': -2, 'msg': '参数错误: 不支持的文件类型'}
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url=url_dict[file_type],
                    headers=Headers.Json()
                ) as response:
                    json_data = await response.json()
                    if 'code' not in json_data:
                        return {'code': -3, 'msg': '数据解析错误: 服务器返回数据格式异常'}
                    
                    # 直接返回服务器响应
                    return json_data
                    
        except aiohttp.ClientError as e:
            return {'code': -1, 'msg': f'网络错误: {str(e)}'}
        except json.JSONDecodeError:
            return {'code': -3, 'msg': '数据解析错误: 响应不是有效的JSON'}
        except Exception as e:
            return {'code': -5, 'msg': f'方法调用失败: {str(e)}'}

    async def Request(self, file_path: str, file_type: str):
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return {'code': -4, 'msg': '文件不存在'}
            
        # 获取token
        token_result = await self.GetToken(file_type)
        if token_result['code'] != 1:
            return token_result
            
        try:
            data = aiohttp.FormData()
            data.add_field("token", token_result['data']['token'])
            data.add_field("key", hashlib.md5(open(file_path, 'rb').read()).hexdigest())
            data.add_field("file", open(file_path, 'rb'), filename=file_path)
            
            url = "https://up-z2.qiniup.com" if file_type == "image" else 'https://up-cn-east-2.qiniup.com'
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, data=data) as res:
                    json_data = await res.json()
                    
                    # 检查上传结果是否有error
                    if 'error' in json_data:
                        return {'code': -1, 'msg': json_data['error']}
                        
                    # 成功返回
                    return {
                        'code': 1,
                        'msg': 'success',
                        'data': json_data
                    }
                    
        except aiohttp.ClientError as e:
            return {'code': -1, 'msg': f'网络错误: {str(e)}'}
        except json.JSONDecodeError:
            return {'code': -3, 'msg': '数据解析错误: 上传响应不是有效的JSON'}
        except Exception as e:
            return {'code': -5, 'msg': f'上传失败: {str(e)}'}

    async def File(self, file_path: str):
        return await self.Request(file_path, "file")
        
    async def Image(self, file_path: str):
        return await self.Request(file_path, "image")
        
    async def Video(self, file_path: str):
        return await self.Request(file_path, "video")
        
    async def Audio(self, file_path: str):
        return await self.Request(file_path, "audio")
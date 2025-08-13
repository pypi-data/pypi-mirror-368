from .api import Send_Message, Post_Message, Upload, Person, Edit_Message
import aiohttp
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.DEBUG,
    handlers=[
        logging.FileHandler('usdk.log'),
        logging.StreamHandler(),
    ],
)
class yunhu_usdk:
    Post = Post_Message()
    Upload = Upload()
    Person = Person()
    class Edit:
        @classmethod
        def To(cls, recvId, recvType):
            return Edit_Message(recvId, recvType)
    class Send:
        @classmethod
        def To(cls, recvId, recvType):
            return Send_Message(recvId, recvType)
    class Login:
        @classmethod
        async def Email(cls, email, password, platform=None):
            if not platform:
                platform = "windows"
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url="https://chat-go.jwzhd.com/v1/user/email-login",
                    json={
                        "email": email,
                        "password": password,
                        "deviceId": "1145141919810",
                        "platform": platform
                    }
                ) as response:
                    json_data = await response.json()
                    if json_data['code'] == 1:
                        logging.info(f"成功使用{email}的账号登录")
                    else:
                        logging.error(f"登陆失败：{json_data['msg']}")
                    return json_data
    async def start(self):
        pass

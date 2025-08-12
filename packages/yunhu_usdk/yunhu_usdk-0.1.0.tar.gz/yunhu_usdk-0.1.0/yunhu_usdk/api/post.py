import aiohttp
import logging
from .usdk_token import usdk_token

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

class Post_Message:
    async def Request(self, url: str, data: dict) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=Headers.Json, json=data) as response:
                    json_data = await response.json()
                    if json_data.get('code', -1) != 1:
                        logging.error(f"请求失败: {json_data.get('msg', '未知错误')}")
                    return json_data
        except aiohttp.ClientError as e:
            logging.error(f"网络错误: {e}")
            return {"code": -1, "msg": "网络错误"}
        except Exception as e:
            logging.error(f"数据解析错误: {e}")
            return {"code": -3, "msg": "数据解析错误"}

    async def PostList(self, ba_id: int, page: int = 1, size: int = 20, typ: int=1):
        if page < 1 or size < 1:
            logging.error("页码或每页数量错误")
            return {"code": -2, "msg": "参数错误"}
        data = {'typ': typ if typ else 1, "baId": int(ba_id), "page": int(page), "size": int(size)}
        return await self.Request('https://chat-go.jwzhd.com/v1/community/posts/post-list', data)

    async def BaInfo(self, ba_id: int):
        return await self.Request(
            'https://chat-go.jwzhd.com/v1/community/ba/info',
            {"id": int(ba_id)}
        )

    async def BaList(self):
        return await self.Request(
            'https://chat-go.jwzhd.com/v1/community/ba/following-ba-list',
            data={}
        )

    async def RewardRecord(self, type: int, page: int=1, size: int=20):
        return await self.Request(
            'https://chat-go.jwzhd.com/v1/community/ba/reward-record',
            data={
                "typ": type,
                "page": page,
                "size": size,
            }
        )

    async def GetContent(self, post_id: int):
        json_data = await self.Request(
            'https://chat-go.jwzhd.com/v1/community/posts/post-detail',
            {"id": int(post_id)}
        )
        if json_data.get('code', -1) != 1:
            return json_data
        return {
            'code': 1,
            'msg': '成功',
            'data': {
                'post_title': json_data['data']['post']['title'],
                'post_type': str(json_data['data']['post']['contentType']),
                'post_content': json_data['data']['post']['content'],
            }
        }

    async def Create(self, baId: int, title: str, content: str, contentType: int, group_id: str = None):
        data = {
            "baId": int(baId),
            "title": title,
            "content": content,
            "contentType": int(contentType),
            "group_id": group_id if group_id else ""
        }
        return await self.Request('https://chat-go.jwzhd.com/v1/community/posts/create', data)

    async def Delete(self, post_id: int):
        return await self.Request(
            'https://chat-go.jwzhd.com/v1/community/posts/delete',
            {"id": int(post_id)}
        )

    async def Edit(self, post_id: int, title: str = None, content: str = None, contentType: int = None):
        if not title or not content or not contentType:
            data = await self.GetContent(post_id)
            if data.get('code', -1) != 1:
                logging.error("获取文章内容失败，请主动传入title,content或contentType参数")
                return {"code": -5, "msg": "调用的方法失败"}
            title = title if title else data['data']['post_title']
            content = content if content else data['data']['post_content']
            contentType = contentType if contentType else data['data']['post_type']
        
        return await self.Request(
            "https://chat-go.jwzhd.com/v1/community/posts/edit",
            {
                "post_id": post_id,
                "title": title,
                "content": content,
                "contentType": contentType,
            }
        )

    async def Comment(self, post_id: int, content: str, comment_id: int = None):
        return await self.Request(
            'https://chat-go.jwzhd.com/v1/community/comment/comment',
            {
                "post_id": post_id,
                "content": content,
                "comment_id": comment_id if comment_id else 0
            }
        )

    async def Like(self, post_id: int):
        return await self.Request(
            "https://chat-go.jwzhd.com/v1/community/posts/post-like",
            {'id': post_id}
        )

    async def Collect(self, post_id: int):
        return await self.Request(
            "https://chat-go.jwzhd.com/v1/community/posts/post-collect",
            {'id': post_id}
        )

    async def Reward(self, post_id: int, amount: float, commentId: int = None):
        url = ("https://chat-go.jwzhd.com/v1/community/comment/comment-reward" 
            if commentId else "https://chat-go.jwzhd.com/v1/community/posts/post-reward")
        return await self.Request(url, {'id': post_id, 'amount': amount})
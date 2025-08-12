import logging
import json
import os

class usdk_token:
    @classmethod
    def Get(cls):
        if not os.path.exists("./config.json"):
            logging.error("当前项目未初始化，请执行：python -m usdk init")
            return None  # Explicitly return None if file doesn't exist
            
        token = None  # Initialize token with a default value
        try:
            with open("config.json", "r", encoding="utf-8") as f:
                token = json.loads(f.read()).get("token", "")
        except KeyboardInterrupt:
            logging.debug("已退出")
            return None
        except json.JSONDecodeError:
            logging.error("配置文件结构不正确，请使用python -m yunhu_usdk init重新定义")
            return None
        
        if token:
            return token
        else:
            logging.error("当前未设置token，请在配置文件中填入token")
            return None
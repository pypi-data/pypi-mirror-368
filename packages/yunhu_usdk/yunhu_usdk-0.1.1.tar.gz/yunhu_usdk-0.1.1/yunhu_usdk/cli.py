# usdk/cli.py
import asyncclick as click
import logging
import os
import json
from getpass import getpass
from yunhu_usdk import yunhu_usdk
# 基本配置
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
@click.group()  # 定义一个命令组
async def cli():
    pass

@cli.command()  # 定义 "init" 子命令
async def init():
    usdk = yunhu_usdk()
    logging.info("正在初始化项目.....")
    if os.path.exists("config.json"):
        with open("config.json", "r", encoding="utf-8") as f:
            config = json.loads(f.read())
        if config.get("email", ""):
            logging.warning(f"当前目录已经存在配置文件(已检测到{config['email']}的登录)，如果继续将替换掉原有配置文件。")
        else:
            logging.warning(f"当前目录已经存在配置文件，如果继续将替换掉原有配置文件。")
        logging.info("如果程序可以正常运行，我们建议您不要更换token")
        choice = input("是否要继续？(Y/n)")
        while True:
            if choice == "N" or choice == 'n':
                logging.info("退出初始化成功")
                return
            elif choice == "y" or choice == "Y":
                break
            else:
                logging.error("未知选项，请重新输入")
                choice = input("是否要继续？(Y/n)")
                continue
    logging.info("正在进行项目初始化...")
    login_choice = input("""(1)邮箱+密码登录
(2)直接填入token
(0)暂时不登陆
请选择登陆方式：""")
    if login_choice == "0":
        pass
    elif login_choice == "1":
        email = input("请输入邮箱：")
        password = getpass("请输入密码：")
        login_data, status = await usdk.Login.Email(email, password)
        if status:
            token = login_data['data']['token']
            with open("config.json", "w", encoding="utf-8") as f:
                data = {
                    "token": token,
                    "email": email
                }
                f.write(json.dumps(data))
        logging.info("项目初始化完成")
    elif login_choice == "2":
        token = input("请输入token：")
        with open("config.json", "w", encoding="utf-8") as f:
            data = {
                "token": token
            }
            f.write(json.dumps(data))
        logging.info("项目初始化完成")
    elif login_choice == "3":
        with open("config.json", "w", encoding="utf-8") as f:
            f.write("""{
    "token": ""
}""")
        logging.info("项目初始化完成，请前往./config.json下填写用户token")
    

if __name__ == "__main__":
    cli(_anyio_backend="asyncio")
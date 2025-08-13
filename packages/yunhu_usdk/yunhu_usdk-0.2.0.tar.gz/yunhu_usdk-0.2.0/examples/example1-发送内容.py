# 本文件介绍了如何发送消息，涵盖已支持的所有方法
from yunhu_usdk import yunhu_usdk
async def main():
    usdk = yunhu_usdk()
    # data:返回的数据，统一格式为{'code': 1, 'msg': '返回信息，成功为success'}，code:成功为1
    # status:是否成功，返回bool值(True为成功，False为失败)
    # 任何消息类型都会返回相同的字段，可以直接使用code和msg，具体错误可以查看wiki(https://bgithub.xyz/shanfishapp/yunhu_usdk/wiki/错误码)

    # 发送文本类消息
    data, status = await usdk.Send.To("聊天id", "聊天类型").Text(
        text="Hello World!",
        command_id=1234,
        buttons=[
            {'actionType': 1, 'text': '跳转链接', 'url': 'https://www.baidu.com'},
            {'actionType': 2, 'text': '复制文本', 'value': '要复制的内容'}
        ],
        quote_text="引用显示的文本内容",
        quote_id="引用的消息id",
        at_users=['1234567', '6666666', '要at的用户id']
    )
    # Markdown和Html消息类型与Text消息参数以及返回内容完全相同，此处不再赘述
    data, status = await usdk.Send.To("聊天id", "聊天类型").Markdown(...)
    data, status = await usdk.Send.To("聊天id", "聊天类型").Html(...)
    
    # 发送文件类消息
    data, status = await usdk.Send.To("聊天id", "聊天类型").Image(
        file_path='文件路径',
        command_id=1234,
        buttons=[
            {'actionType': 1, 'text': '跳转链接', 'url': 'https://www.baidu.com'},
            {'actionType': 2, 'text': '复制文本', 'value': '要复制的内容'}
        ],
        quote_text="引用显示的文本内容",
        quote_id="引用的消息id",
        at_users=['1234567', '6666666', '要at的用户id']
    )
    data, status = await usdk.Send.To(...).Video(...)

    # 音频方法支持传入音频时长，如果不传入则自动读取音频时长(前端显示效果会随之更改)
    data, status = await usdk.Send.To(...).Audio(..., audio_time=100)
    # 文件方法支持传入文件大小,文件名称，如果不传入则自动读取信息(前端显示效果会随之更改)
    # file_size为int64类型，可以为负数，但不得超出int64的限制
    data, status = await usdk.Send.To(...).File(..., file_size=100, file_name="文件名称")

    # 发送其他类消息
    # 文章消息，并不是创建文章，而是类似分享文章，post_type,post_title,post_content用于前端显示，可以不填，将会自动获取
    data, status = await usdk.Send.To(...).Post(
        post_id=30000,
        post_type=1, # 1-文本，2-Markdown,
        post_title="标题",
        post_content="内容",
        command_id=1234,
        buttons=[
            {'actionType': 1, 'text': '跳转链接', 'url': 'https://www.baidu.com'},
            {'actionType': 2, 'text': '复制文本', 'value': '要复制的内容'}
        ],
        quote_text="引用显示的文本内容",
        quote_id="引用的消息id",
        at_users=['1234567', '6666666', '要at的用户id']
    )
    # 表单消息
    usdk.Send.To(...).Form(
        form_data={
            "dtmubv":{
                "label":"测试", # 标签
                "value":"测试内容", # 内容
                "id":"dtmubv", # 表单id
                "type":"textarea" # 类型
            }
        },
        command_id=1234,
        buttons=[
            {'actionType': 1, 'text': '跳转链接', 'url': 'https://www.baidu.com'},
            {'actionType': 2, 'text': '复制文本', 'value': '要复制的内容'}
        ],
        quote_text="引用显示的文本内容",
        quote_id="引用的消息id",
        at_users=['1234567', '6666666', '要at的用户id']
    )
    # form_data可以直接复制官方机器人发送表单消息的返回数据进行使用

import os

list_dir = os.listdir('proto/')
for i in list_dir:
    code = os.system(f'protoc -I=proto --python_out=./yunhu_usdk/api/pb2/ proto/{i}')
    if code == 0:
        print(f'{i} 编译成功')
    else:
        print(f"{i} 编译失败")
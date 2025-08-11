import os
import sys

CWD = os.path.dirname(os.path.abspath(__file__))
SDK_PATH = os.path.dirname(CWD)

sys.path.append(SDK_PATH)

from tboxsdk.tbox import TboxClient

authorization = os.getenv("HTTP_CLIENT_AUTHORIZATION")
if authorization is None:
    raise Exception("env HTTP_CLIENT_AUTHORIZATION is not set")

tbox_client = TboxClient(authorization=authorization)

try:
    response = tbox_client.upload_file(file_path="/Users/haoxuan/Downloads/模型效果盲测接入指南.pdf")
    print(f"--------------------------------------------------------")
    print(f"response: {response}")
    print(f"--------------------------------------------------------")
    
    if response.get("errorCode") == "0":
        file_id = response.get("data", "")
        print(f"文件ID: {file_id}")
    else:
        print(f"上传失败: {response.get('errorMsg')}")
except Exception as e:
    print(f"上传出错: {e}")

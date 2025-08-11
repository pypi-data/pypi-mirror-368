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

# 测试1: 基本创建会话
print("=== 测试1: 基本创建会话 ===")
try:
    # 使用一个测试用的appId，你需要替换为实际可用的appId
    response = tbox_client.create_conversation(app_id="202411APWG5400162068")
    print(f"--------------------------------------------------------")
    print(f"response: {response}")
    print(f"--------------------------------------------------------")
    
    if response.get("errorCode") == "0":
        conversation_id = response.get("data")
        print(f"创建成功！会话ID: {conversation_id}")
        print(f"追踪ID: {response.get('traceId')}")
    else:
        print(f"创建失败: {response.get('errorMsg')}")
except Exception as e:
    print(f"创建出错: {e}")

print("\n" + "="*50 + "\n")

# 测试2: 创建会话并进行对话
print("=== 测试2: 创建会话并进行对话 ===")
try:
    # 创建新会话
    create_response = tbox_client.create_conversation(app_id="202411APWG5400162068")
    
    if create_response.get("errorCode") == "0":
        conversation_id = create_response.get("data")
        print(f"创建会话成功，会话ID: {conversation_id}")
        
        # 使用新创建的会话进行对话
        chat_response = tbox_client.chat(
            app_id="202411APWG5400162068",
            query="你好，请介绍一下你自己",
            user_id="test_user_123",
            conversation_id=conversation_id
        )
        
        print("对话响应:")
        for chunk in chat_response:
            print(f"--------------------------------------------------------")
            print(f"chunk: {chunk}")
            print(f"--------------------------------------------------------")
    else:
        print(f"创建会话失败: {create_response.get('errorMsg')}")
except Exception as e:
    print(f"测试出错: {e}")

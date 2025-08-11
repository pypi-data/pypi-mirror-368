import os
import sys

CWD = os.path.dirname(os.path.abspath(__file__))
SDK_PATH = os.path.dirname(CWD)

sys.path.append(SDK_PATH)

from tboxsdk.tbox import TboxClient
from tboxsdk.model.conversation import ConversationSource, Conversation

authorization = os.getenv("HTTP_CLIENT_AUTHORIZATION")
if authorization is None:
    raise Exception("env HTTP_CLIENT_AUTHORIZATION is not set")

tbox_client = TboxClient(authorization=authorization)

print("=== 测试1: 基本查询会话列表 ===")
try:
    response = tbox_client.get_conversations(app_id="202411APWG5400162068")
    print(f"--------------------------------------------------------")
    print(f"response: {response}")
    print(f"--------------------------------------------------------")
    
    if response.get("errorCode") == "0":
        conversations = response.get("data", {}).get("conversations", [])
        print(f"找到 {len(conversations)} 个会话")
        
        for conv in conversations:
            print(f"会话ID: {conv['conversationId']}")
            print(f"用户ID: {conv['userId']}")
            print(f"渠道: {conv['source']}")
            print(f"创建时间: {conv['createAt']}")
            print("---")
    else:
        print(f"查询失败: {response.get('errorMsg')}")
except Exception as e:
    print(f"查询出错: {e}")

print("\n" + "="*50 + "\n")

print("=== 测试2: 带参数的查询会话列表 ===")
try:
    response = tbox_client.get_conversations(
        app_id="202411APWG5400162068",
        user_id="1234567890",  # 指定用户ID
        source=ConversationSource.AGENT_SDK,  # 使用枚举类型指定渠道
        page_num=1,  # 第一页
        page_size=10,  # 每页10条
        sort_order="DESC"  # 按创建时间降序排列
    )
    print(f"--------------------------------------------------------")
    print(f"response: {response}")
    print(f"--------------------------------------------------------")
    
    if response.get("errorCode") == "0":
        conversations = response.get("data", {}).get("conversations", [])
        print(f"找到 {len(conversations)} 个会话")
        
        # 使用Conversation模型处理数据
        for conv_data in conversations:
            conversation = Conversation.from_dict(conv_data)
            print(f"会话ID: {conversation.get_conversation_id()}")
            print(f"用户ID: {conversation.get_user_id()}")
            print(f"渠道: {conversation.get_source()}")
            print(f"创建时间: {conversation.get_create_at()}")
            print("---")
    else:
        print(f"查询失败: {response.get('errorMsg')}")
except Exception as e:
    print(f"查询出错: {e}")

print("\n" + "="*50 + "\n")

print("=== 测试3: 使用字符串指定渠道 ===")
try:
    response = tbox_client.get_conversations(
        app_id="202411APWG5400162068",
        source="AGENT_SDK"  # 直接使用字符串
    )
    print(f"--------------------------------------------------------")
    print(f"response: {response}")
    print(f"--------------------------------------------------------")
    
    if response.get("errorCode") == "0":
        conversations = response.get("data", {}).get("conversations", [])
        print(f"找到 {len(conversations)} 个AGENT_SDK渠道的会话")
    else:
        print(f"查询失败: {response.get('errorMsg')}")
except Exception as e:
    print(f"查询出错: {e}")

print("\n" + "="*50 + "\n")

print("=== 测试4: 分页查询示例 ===")
page_num = 1
page_size = 5

while True:
    try:
        response = tbox_client.get_conversations(
            app_id="202411APWG5400162068",
            page_num=page_num,
            page_size=page_size
        )
        
        if response.get("errorCode") == "0":
            conversations = response.get("data", {}).get("conversations", [])
            if not conversations:
                print(f"第 {page_num} 页没有数据，查询结束")
                break
            
            print(f"第 {page_num} 页，找到 {len(conversations)} 个会话")
            for conv in conversations:
                print(f"  - {conv['conversationId']} ({conv['userId']})")
            
            page_num += 1
            
            # 如果返回的数据少于page_size，说明已经是最后一页
            if len(conversations) < page_size:
                print("已到达最后一页")
                break
        else:
            print(f"查询失败: {response.get('errorMsg')}")
            break
    except Exception as e:
        print(f"查询出错: {e}")
        break 
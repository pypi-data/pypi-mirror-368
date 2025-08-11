import os
import sys

CWD = os.path.dirname(os.path.abspath(__file__))
SDK_PATH = os.path.dirname(CWD)

sys.path.append(SDK_PATH)

from tboxsdk.tbox import TboxClient
from tboxsdk.model.message import Message, Answer, MessageStatus, MediaType

authorization = os.getenv("HTTP_CLIENT_AUTHORIZATION")
if authorization is None:
    raise Exception("env HTTP_CLIENT_AUTHORIZATION is not set")

tbox_client = TboxClient(authorization=authorization)

# 测试1: 基本查询消息列表
print("=== 测试1: 基本查询消息列表 ===")
try:
    # 使用一个测试用的conversationId，你需要替换为实际可用的conversationId
    response = tbox_client.get_messages(conversation_id="20250731sVPw37464974")
    print(f"--------------------------------------------------------")
    print(f"response: {response}")
    print(f"--------------------------------------------------------")
    
    if response.get("errorCode") == "0":
        messages = response.get("data", {}).get("messages", [])
        print(f"找到 {len(messages)} 条消息")
        
        for msg in messages:
            print(f"消息ID: {msg['messageId']}")
            print(f"会话ID: {msg['conversationId']}")
            print(f"智能体ID: {msg['appId']}")
            print(f"用户问题: {msg['query']}")
            print(f"状态: {msg['status']}")
            print(f"创建时间: {msg['createAt']}")
            print(f"更新时间: {msg['updateAt']}")
            
            # 显示回答
            answers = msg.get('answers', [])
            print(f"回答数量: {len(answers)}")
            for answer in answers:
                print(f"  - 流水线: {answer.get('lane')}")
                print(f"  - 媒体类型: {answer.get('mediaType')}")
                print(f"  - 文本内容: {answer.get('text')}")
                if answer.get('url'):
                    print(f"  - 图片链接: {answer.get('url')}")
            
            # 显示文件
            files = msg.get('files', [])
            print(f"文件数量: {len(files)}")
            for file in files:
                print(f"  - 文件ID: {file.get('fileId')}")
                print(f"  - 文件类型: {file.get('type')}")
                print(f"  - 预览链接: {file.get('url')}")
            
            print("---")
    else:
        print(f"查询失败: {response.get('errorMsg')}")
except Exception as e:
    print(f"查询出错: {e}")

print("\n" + "="*50 + "\n")

# 测试2: 带参数的查询消息列表
print("=== 测试2: 带参数的查询消息列表 ===")
try:
    response = tbox_client.get_messages(
        conversation_id="20250731sVPw37464974",
        page_num=1,  # 第一页
        page_size=10,  # 每页10条
        sort_order="DESC"  # 按创建时间降序排列
    )
    print(f"--------------------------------------------------------")
    print(f"response: {response}")
    print(f"--------------------------------------------------------")
    
    if response.get("errorCode") == "0":
        messages = response.get("data", {}).get("messages", [])
        print(f"找到 {len(messages)} 条消息")
        
        # 使用Message模型处理数据
        for msg_data in messages:
            message = Message.from_dict(msg_data)
            print(f"消息ID: {message.get_message_id()}")
            print(f"会话ID: {message.get_conversation_id()}")
            print(f"智能体ID: {message.get_app_id()}")
            print(f"用户问题: {message.get_query()}")
            print(f"状态: {message.get_status()}")
            print(f"创建时间: {message.get_create_at()}")
            print(f"更新时间: {message.get_update_at()}")
            
            # 显示回答
            answers = message.get_answers()
            print(f"回答数量: {len(answers)}")
            for answer in answers:
                print(f"  - 流水线: {answer.get_lane()}")
                print(f"  - 媒体类型: {answer.get_media_type()}")
                print(f"  - 文本内容: {answer.get_text()}")
                if answer.get_url():
                    print(f"  - 图片链接: {answer.get_url()}")
            
            print("---")
    else:
        print(f"查询失败: {response.get('errorMsg')}")
except Exception as e:
    print(f"查询出错: {e}")

print("\n" + "="*50 + "\n")

# 测试3: 分页查询示例
print("=== 测试3: 分页查询示例 ===")
page_num = 1
page_size = 5

while True:
    try:
        response = tbox_client.get_messages(
            conversation_id="20250731sVPw37464974",
            page_num=page_num,
            page_size=page_size
        )
        
        if response.get("errorCode") == "0":
            messages = response.get("data", {}).get("messages", [])
            if not messages:
                print(f"第 {page_num} 页没有数据，查询结束")
                break
            
            print(f"第 {page_num} 页，找到 {len(messages)} 条消息")
            for msg in messages:
                print(f"  - {msg['messageId']} ({msg['query'][:20]}...)")
            
            page_num += 1
            
            # 如果返回的数据少于page_size，说明已经是最后一页
            if len(messages) < page_size:
                print("已到达最后一页")
                break
        else:
            print(f"查询失败: {response.get('errorMsg')}")
            break
    except Exception as e:
        print(f"查询出错: {e}")
        break

print("\n" + "="*50 + "\n")

# 测试4: 测试Message和Answer模型
print("=== 测试4: 测试Message和Answer模型 ===")
try:
    # 创建测试数据
    test_answer_data = {
        "lane": "default",
        "mediaType": "text",
        "text": "这是一个测试回答",
        "url": ["https://example.com/image1.jpg"],
        "expireAt": 1640995200
    }
    
    test_message_data = {
        "messageId": "test_msg_123",
        "conversationId": "test_conv_456",
        "appId": "test_app_789",
        "query": "这是一个测试问题",
        "answers": [test_answer_data],
        "files": [
            {
                "fileId": "test_file_001",
                "type": "image",
                "url": "https://example.com/file.jpg",
                "expireAt": 1640995200
            }
        ],
        "createAt": 1640995200,
        "updateAt": 1640995200,
        "status": "SUCCESS"
    }
    
    # 测试Answer模型
    answer = Answer.from_dict(test_answer_data)
    print(f"Answer - 流水线: {answer.get_lane()}")
    print(f"Answer - 媒体类型: {answer.get_media_type()}")
    print(f"Answer - 文本内容: {answer.get_text()}")
    print(f"Answer - 图片链接: {answer.get_url()}")
    
    # 测试Message模型
    message = Message.from_dict(test_message_data)
    print(f"Message - 消息ID: {message.get_message_id()}")
    print(f"Message - 会话ID: {message.get_conversation_id()}")
    print(f"Message - 智能体ID: {message.get_app_id()}")
    print(f"Message - 用户问题: {message.get_query()}")
    print(f"Message - 状态: {message.get_status()}")
    print(f"Message - 回答数量: {len(message.get_answers())}")
    print(f"Message - 文件数量: {len(message.get_files())}")
    
    # 测试转换为字典
    answer_dict = answer.to_dict()
    message_dict = message.to_dict()
    print(f"Answer转字典: {answer_dict}")
    print(f"Message转字典: {message_dict}")
    
except Exception as e:
    print(f"模型测试出错: {e}") 
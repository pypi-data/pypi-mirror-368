import json
import os
import sys

CWD = os.path.dirname(os.path.abspath(__file__))
SDK_PATH = os.path.dirname(CWD)

sys.path.append(SDK_PATH)

from tboxsdk.core.httpclient import HttpClientConfig
from tboxsdk.tbox import TboxClient

authorization = os.getenv("HTTP_CLIENT_AUTHORIZATION")
if authorization is None:
    raise Exception("env HTTP_CLIENT_AUTHORIZATION is not set")

tbox_client = TboxClient(authorization=authorization)
# response = tbox_client.chat(app_id="202504APhQ9F00382583", query="今天杭州天气怎么样？", with_meta=True)
response = tbox_client.chat(app_id="202411APWG5400162068", query="今天杭州天气怎么样？", user_id="1234567890", stream=False)
resp_str = json.dumps(response, ensure_ascii=False)
# --------------------------------------------------------
# data: {"default": {"type": "text", "header": {"entity": {"node_type": "output", "execute_id": "5", "node_name": "\u8f93\u51fa\u5185\u5bb9", "node_id": "OU_awwbf6"}, "lane": "default", "payload": {"extraParams": {}, "mediaType": "text", "requestId": "f124a2d7-a6a4-4649-9055-61759a90467b", "sessionId": "20250523pIXp28796986"}, "type": "header"}, "data": "\u4eca\u5929\uff082025\u5e7405\u670823\u65e5\uff09\u676d\u5dde\u5e02\u7684\u5929\u6c14\u60c5\u51b5\u5982\u4e0b\uff1a\n\n- \u767d\u5929\uff1a\u5c0f\u96e8\uff0c\u6e29\u5ea6\u7ea6\u4e3a27\u2103\uff0c\u98ce\u5411\u4e3a\u897f\u5317\u98ce\uff0c\u98ce\u529b1-3\u7ea7\u3002\n- \u665a\u4e0a\uff1a\u591a\u4e91\uff0c\u6e29\u5ea6\u4e0b\u964d\u5230\u7ea617\u2103\uff0c\u98ce\u5411\u4ecd\u7136\u4e3a\u897f\u5317\u98ce\uff0c\u98ce\u529b\u7ef4\u6301\u57281-3\u7ea7\u3002\n\n\u8bf7\u8bb0\u5f97\u5e26\u4f1e\uff0c\u5e76\u6839\u636e\u5929\u6c14\u53d8\u5316\u9002\u5f53\u589e\u51cf\u8863\u7269\u3002", "messages": [{"lane": "default", "payload": {"text": "\u4eca\u5929"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\uff08202"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "5\u5e7405"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u670823\u65e5"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\uff09\u676d\u5dde\u5e02\u7684\u5929\u6c14"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u60c5\u51b5\u5982\u4e0b\uff1a\n\n-"}, "type": "chunk"}, {"lane": "default", "payload": {"text": " \u767d\u5929\uff1a"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u5c0f\u96e8\uff0c\u6e29\u5ea6"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u7ea6\u4e3a27\u2103"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\uff0c\u98ce\u5411\u4e3a"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u897f\u5317\u98ce\uff0c\u98ce"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u529b1-3"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u7ea7\u3002\n-"}, "type": "chunk"}, {"lane": "default", "payload": {"text": " \u665a\u4e0a\uff1a"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u591a\u4e91\uff0c\u6e29\u5ea6"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u4e0b\u964d\u5230\u7ea61"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "7\u2103\uff0c\u98ce"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u5411\u4ecd\u7136\u4e3a\u897f\u5317"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u98ce\uff0c\u98ce\u529b"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u7ef4\u6301\u57281-"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "3\u7ea7\u3002\n\n\u8bf7"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u8bb0\u5f97\u5e26\u4f1e\uff0c\u5e76"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u6839\u636e\u5929\u6c14\u53d8\u5316\u9002\u5f53"}, "type": "chunk"}, {"lane": "default", "payload": {"text": "\u589e\u51cf\u8863\u7269\u3002"}, "type": "chunk"}]}}
# --------------------------------------------------------
print(f"--------------------------------------------------------")
print(f"data: {resp_str}")
print(f"--------------------------------------------------------")

import os
import sys
import json

CWD = os.path.dirname(os.path.abspath(__file__))
SDK_PATH = os.path.dirname(CWD)

sys.path.append(SDK_PATH)

from tboxsdk.tbox import TboxClient

authorization = os.getenv("HTTP_CLIENT_AUTHORIZATION")
if authorization is None:
    raise Exception("env HTTP_CLIENT_AUTHORIZATION is not set")

tbox_client = TboxClient(authorization=authorization)
response = tbox_client.completion(app_id="202508APoOVW00502583", inputs={"主题": "太阳"}, user_id="1234567890", stream=False)
json_str = json.dumps(response, ensure_ascii=False)
print(f"--------------------------------------------------------")
print(f"data: {json_str}")
print(f"--------------------------------------------------------")

# --------------------------------------------------------
# data: {"mvz20luv": {"type": "text", "header": {"entity": {"node_type": "output", "execute_id": "2", "node_name": "\u7ed3\u675f", "node_id": "output_isn9lm"}, "lane": "mvz20luv", "payload": {"extraParams": {}, "mediaType": "text", "name": "\u56de\u7b54", "requestId": "1fc33bbf-1413-4f7f-b721-b2573b8f97ac", "sessionId": "2025052347It28836461"}, "type": "header"}, "data": "\u4eca\u5929\u676d\u5dde\u7684\u5929\u6c14\u5c31\u50cf\u662f\u897f\u6e56\u4e0a\u7684\u8f7b\u96fe\uff0c\u6668\u95f4\u6709\u4e9b\u5fae\u51c9\u4e14\u6726\u80e7\uff0c\u5348\u540e\u9633\u5149\u6e10\u6e10\u7a7f\u900f\u4e91\u5c42\uff0c\u5e26\u6765\u51e0\u5206\u6e29\u6696\u548c\u660e\u5a9a\u3002\u8bb0\u5f97\u65e9\u665a\u6dfb\u8863\uff0c\u4eab\u53d7\u8fd9\u5b9c\u4eba\u7684\u79cb\u65e5\u65f6\u5149\u54e6\uff01", "messages": [{"lane": "mvz20luv", "payload": {"text": "\u4eca\u5929"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\u676d\u5dde"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\u7684"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\u5929\u6c14\u5c31\u50cf\u662f\u897f\u6e56\u4e0a\u7684"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\u8f7b\u96fe\uff0c\u6668"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\u95f4\u6709\u4e9b\u5fae\u51c9"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\u4e14\u6726\u80e7\uff0c\u5348\u540e"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\u9633\u5149\u6e10\u6e10\u7a7f\u900f\u4e91"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\u5c42\uff0c\u5e26\u6765\u51e0\u5206"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\u6e29\u6696\u548c\u660e\u5a9a\u3002"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\u8bb0\u5f97\u65e9\u665a\u6dfb\u8863"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\uff0c\u4eab\u53d7\u8fd9\u5b9c"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\u4eba\u7684\u79cb\u65e5\u65f6\u5149"}, "type": "chunk"}, {"lane": "mvz20luv", "payload": {"text": "\u54e6\uff01"}, "type": "chunk"}]}}
# --------------------------------------------------------

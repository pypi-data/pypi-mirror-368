import os
import sys

CWD = os.path.dirname(os.path.abspath(__file__))
SDK_PATH = os.path.dirname(CWD)

sys.path.append(SDK_PATH)

from tboxsdk.core.httpclient import HttpClient, HttpClientConfig

authorization = os.getenv("HTTP_CLIENT_AUTHORIZATION")
if authorization is None:
    raise Exception("env HTTP_CLIENT_AUTHORIZATION is not set")

httpClient = HttpClient(HttpClientConfig(authorization=authorization))

data = {"appId":"202504APhQ9F00382583", "query":"今天杭州天气怎么样？", "userId": "1234567890"}

event_generator = httpClient.post_stream("/api/chat", data=data)

for event in event_generator:
    print(f"--------------------------------------------------------")
    print(f"id: {event.id}, event: {event.event}")
    print(f"data: {event.data}")
    print(f"--------------------------------------------------------")

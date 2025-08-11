import os
import sys

CWD = os.path.dirname(os.path.abspath(__file__))
SDK_PATH = os.path.dirname(CWD)

sys.path.append(SDK_PATH)

from tboxsdk.tbox import TboxClient
from tboxsdk.core.httpclient import HttpClientConfig

authorization = os.getenv("HTTP_CLIENT_AUTHORIZATION")
if authorization is None:
    raise Exception("env HTTP_CLIENT_AUTHORIZATION is not set")

http_client_config = HttpClientConfig(
    authorization=authorization,
    schema="http",
    host="localhost:8888"
)
tbox_client = TboxClient(http_client_config=http_client_config)

# tbox_client = TboxClient(authorization=authorization)
# response = tbox_client.chat(app_id="202504APhQ9F00382583", query="今天杭州天气怎么样？", with_meta=True)
response = tbox_client.chat(app_id="202411APWG5400162068", query="今天杭州天气怎么样？", user_id="1234567890")

if __name__ == "__main__":
    for chunk in response:
        print(response)
        print(f"--------------------------------------------------------")
        print(f"data: {chunk}")
        print(f"--------------------------------------------------------")

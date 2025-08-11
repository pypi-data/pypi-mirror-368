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
response = httpClient.post("/api/cec60ad8d7f0ed756734dcd9a8672265/sample", data={}, headers={})

print(response)

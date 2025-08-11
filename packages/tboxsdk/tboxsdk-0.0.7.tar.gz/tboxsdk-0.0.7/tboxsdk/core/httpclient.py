import httpx
import sseclient
import logging
from .exception import TboxClientConfigException, TboxHttpResponseException

logger = logging.getLogger("tbox.client")


class HttpClientConfig(object):
    """
    http client config
    """
    # authorization, http协议头中的 authorization
    authorization: str = None
    # schema, https或者http
    schema: str = None
    # host, http协议头中的 host
    host: str = None

    def __init__(self,
                 authorization: str = None,
                 schema: str = None,
                 host: str = None
                 ):
        """
        init

        :param authorization: http协议头中的 authorization
        :param schema: https 或者是 http
        :param host: 域名
        """
        self.authorization = authorization
        self.schema = schema if schema is not None else "https"
        self.host = host if host is not None else "api.tbox.cn"
        return


class HttpResponseEvent(object):
    """
    http response event
    用来持有http sse 响应 Event 报文
    """
    """
    http response event id
    """
    id: int = None
    """
    http response event event
    """
    event: str = None
    """
    http response event
    """
    data: str = None

    def __init__(self, event: str, data: str, id: int = None):
        """
        初始化 http sse 响应 Event 报文持有对象
        :param event: http response event event
        :param data: http response event
        :param id: http response event id
        """
        self.event = event
        self.data = data
        self.id = id


class HttpClient(object):
    """
    http client
    """

    http_client_config: HttpClientConfig = None

    def __init__(self, http_client_config: HttpClientConfig = None):
        """
        init
        :param http_client_config: http client config
        """
        if http_client_config is None:
            # FIXME: 后续有文档以后，这里应该引用文档，然后引导使用者怎么配置
            raise TboxClientConfigException("http_client_config is None")
        self.http_client_config = http_client_config
        return

    def post(self, path, data, headers=None, timeout=300):
        """
        :param url:
        :param data:
        :param headers:
        :return:
        """
        if not path.startswith("/"):
            path = f"/{path}"
        url = f"{self.http_client_config.schema}://{self.http_client_config.host}{path}"
        response = httpx.post(url, json=data, headers=self.generate_headers(headers), timeout=timeout)
        if response.status_code != 200:
            logger.error(f"request TBox failed, http status code: {response.status_code}, error message: {response.text}")
            raise TboxHttpResponseException(f"request TBox failed, http status code: {response.status_code}, "
                                            f"error message: {response.text}")
        logger.info(f"http request success, status_code: {response.status_code}, text: {response.text}")
        return response.json()

    def post_stream(self, path, data, headers=None, timeout=300):
        """
        :param url:
        :param data:
        :param headers:
        :return:
        """
        if not path.startswith("/"):
            path = f"/{path}"
        url = f"{self.http_client_config.schema}://{self.http_client_config.host}{path}"
        with httpx.stream(method="POST", url=url, json=data, headers=self.generate_headers(headers),
                          timeout=timeout) as response:
            if not response.status_code == 200:
                response.read()
                raise TboxHttpResponseException(f"request TBox failed, http status code: {response.status_code}, "
                                                f"error message: {response.text}")
            content_type = response.headers.get('Content-Type')
            if content_type:
                content_type = content_type.split(';')[0]
            if content_type == 'application/json':
                response.read()
                raise TboxHttpResponseException(f"request TBox failed, http status code: {response.status_code}, "
                                                f"error message: {response.text}")
            if not content_type == 'text/event-stream':
                logger.error('Server response invalid content type {}'.format(content_type))
                logger.error('Server response text {}'.format(response.text))
                raise TboxHttpResponseException('Server response invalid content type {}'.format(content_type))
            generator = sseclient.SSEClient(response.iter_raw(128))
            for event in generator.events():
                logger.info('Server response event id {}, event {}, data'.format(event.id, event.event, event.data))
                yield HttpResponseEvent(data=event.data, event=event.event, id=event.id)

    def get(self, path, query=None, headers=None):
        """
        :param path: API路径
        :param query: 查询参数
        :param headers: 请求头
        :return:
        """
        if not path.startswith("/"):
            path = f"/{path}"
        url = f"{self.http_client_config.schema}://{self.http_client_config.host}{path}"
        response = httpx.get(url, params=query, headers=self.generate_headers(headers))
        if response.status_code != 200:
            logger.error(f"request TBox failed, http status code: {response.status_code}, error message: {response.text}")
            raise TboxHttpResponseException(f"request TBox failed, http status code: {response.status_code}, "
                                            f"error message: {response.text}")
        logger.info(f"http request success, status_code: {response.status_code}, text: {response.text}")
        return response.json()

    def post_file(self, path, files, data=None, headers=None, timeout=30):
        """
        :param path: API路径
        :param files: 文件字典，格式为 {'file': ('filename', file_object, 'content_type')}
        :param data: 表单数据
        :param headers: 请求头
        :param timeout: 超时时间
        :return:
        """
        if not path.startswith("/"):
            path = f"/{path}"
        url = f"{self.http_client_config.schema}://{self.http_client_config.host}{path}"
        
        request_headers = {}
        if self.http_client_config.authorization is not None:
            request_headers["Authorization"] = self.http_client_config.authorization
        request_headers["source"] = "AGENT_SDK"
        if headers:
            request_headers.update(headers)
        
        response = httpx.post(url, files=files, data=data, headers=request_headers, timeout=timeout)
        if response.status_code != 200:
            logger.error(f"request TBox failed, http status code: {response.status_code}, error message: {response.text}")
            raise TboxHttpResponseException(f"request TBox failed, http status code: {response.status_code}, "
                                            f"error message: {response.text}")
        logger.info(f"http request success, status_code: {response.status_code}, text: {response.text}")
        return response.json()

    def generate_headers(self, headers):
        """
        generate headers
        主要是将
        """
        if headers is None:
            headers = {}
        if self.http_client_config.authorization is not None:
            headers["Authorization"] = self.http_client_config.authorization
        if headers.get("Content-Type") is None:
            headers["Content-Type"] = "application/json"
        headers["source"] = "AGENT_SDK"
        return headers

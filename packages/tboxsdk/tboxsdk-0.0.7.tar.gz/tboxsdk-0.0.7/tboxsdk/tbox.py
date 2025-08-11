from typing import List, Optional, Union

from .core.httpclient import HttpClientConfig, HttpClient
from .core.exception import TboxClientConfigException
from .model.message import MessageParser
from .model.file import File
from .model.conversation import ConversationSource


class TboxClient(object):
    """
    Tbox client
    """

    """
    tbox client config
    """
    http_client_config: HttpClientConfig = None
    """
    http client
    """
    http_client: HttpClient = None

    def __init__(self, http_client_config: HttpClientConfig = None, authorization: str = None):
        """
        :param http_client_config:
        :param authorization:
        """
        self.http_client_config = http_client_config if http_client_config is not None else HttpClientConfig()
        # 这里加个简化写法的代码, 方便使用者初始化客户端
        if authorization is not None:
            self.http_client_config.authorization = authorization
        self.http_client = HttpClient(self.http_client_config)
        return

    def chat(self,
             app_id: str,
             query: str,
             user_id: str,
             conversation_id: str = None,
             request_id: str = None,
             inputs: dict = None,
             client_properties: dict = None,
             files: List[File] = None,
             with_meta: bool = False,
             message_parser: MessageParser = None,
             search_engine: bool = False,
             stream: bool = True
             ):
        """
        tbox client chat
        用于调用 tbox 的 chat 类型应用
        返回格式是统一的流式响应格式
        """
        data = {
            "appId": app_id,
            "query": query,
            "stream": stream,
            "searchEngine": search_engine
        }
        if conversation_id is not None:
            data["conversationId"] = conversation_id
        if request_id is not None:
            data["requestId"] = request_id
        if inputs is not None:
            data["inputs"] = inputs
        if user_id is not None:
            data["userId"] = user_id
        if client_properties is not None:
            data["clientProperties"] = client_properties
        if files is not None:
            data["files"] = files
        
        if stream:
            response_iter = self.http_client.post_stream('/api/chat', data=data, timeout=300)
            return self._stream(response_iter, message_parser=message_parser, with_meta=with_meta)
        else:
            response = self.http_client.post('/api/chat', data=data, timeout=300)
            return response

    def completion(self,
                   app_id: str,
                   user_id: str,
                   conversation_id: str = None,
                   request_id: str = None,
                   inputs: dict = None,
                   client_properties: dict = None,
                   files: List[File] = None,
                   with_meta: bool = False,
                   message_parser: MessageParser = None,
                   stream: bool = True
                   ):
        data = {
            "appId": app_id,
            "stream": stream
        }
        if conversation_id is not None:
            data["conversationId"] = conversation_id
        if request_id is not None:
            data["requestId"] = request_id
        if inputs is not None:
            data["inputs"] = inputs
        if user_id is not None:
            data["userId"] = user_id
        if client_properties is not None:
            data["clientProperties"] = client_properties
        if files is not None:
            data["files"] = files

        if stream:
            response_iter = self.http_client.post_stream('/api/completion', data=data, timeout=300)
            return self._stream(response_iter, message_parser=message_parser, with_meta=with_meta)
        else:
            response = self.http_client.post('/api/completion', data=data, timeout=300)
            return response

    def _stream(self, response_iter, message_parser: MessageParser = None, with_meta=False):
        """
        stream
        :param response_iter: http response iter
        :param message_parser: message parser
        """
        if message_parser is not None:
            parser = message_parser
        else:
            parser = MessageParser()
        for event in response_iter:
            # 解析响应内容的list，如果其中有一个是 error，则抛出异常
            if event.event == 'error':
                raise TboxClientConfigException(event.data)
            # 判断下这段内容是否需要解析
            if parser.need_parse(event):
                data = parser.parse(event)
                if data.get("type") == 'meta':
                    if with_meta:
                        yield data
                else:
                    yield data

    def get_conversations(self,
                         app_id: str,
                         user_id: Optional[str] = None,
                         source: Optional[Union[str, ConversationSource]] = None,
                         page_num: Optional[int] = None,
                         page_size: Optional[int] = None,
                         sort_order: Optional[str] = None) -> dict:
        """
        查询会话列表
        用于查询指定智能体的会话列表
        
        Args:
            app_id: 智能体ID (必填)
            user_id: 用户ID，指定时查询该用户的会话列表，不指定时返回所有用户的会话列表 (可选)
            source: 渠道，用于过滤指定渠道的会话，不指定时返回所有渠道 (可选)
            page_num: 页码，从1开始，默认为1 (可选)
            page_size: 每页数据条数，默认为10，最大为50 (可选)
            sort_order: 会话列表排序方式，默认为DESC (可选)
                - ASC: 升序，按创建时间升序排列，最早创建的会话在前
                - DESC: 降序，按创建时间降序排列，最近创建的会话在前
        
        Returns:
            包含会话列表的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": [
                    "currentPage": 当前页码,
                    "pageSize": 总页数,
                    "total": 总条数,
                    "conversations": [
                        {
                            "conversationId": "会话ID",
                            "userId": "用户ID",
                            "source": "渠道",
                            "createAt": 创建时间戳,
                        }
                    ]
                ],
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        query_params = {
            "appId": app_id
        }
        
        if user_id is not None:
            query_params["userId"] = user_id
        
        if source is not None:
            if isinstance(source, ConversationSource):
                query_params["source"] = source.value
            else:
                query_params["source"] = source
        
        if page_num is not None:
            query_params["pageNum"] = page_num
        
        if page_size is not None:
            query_params["pageSize"] = page_size
        
        if sort_order is not None:
            query_params["sortOrder"] = sort_order
        
        response = self.http_client.get('/api/conversation/conversations', query=query_params)
        return response

    def get_messages(self,
                    conversation_id: str,
                    page_num: Optional[int] = None,
                    page_size: Optional[int] = None,
                    sort_order: Optional[str] = None) -> dict:
        """
        查询消息列表
        用于查询指定会话的消息列表
        
        Args:
            conversation_id: 会话ID (必填)
            page_num: 页码，从1开始，默认为1 (可选)
            page_size: 每页数据条数，默认为50，最大为50 (可选)
            sort_order: 消息列表排序方式，默认为DESC (可选)
                - ASC: 升序，按创建时间升序排列，最早创建的消息在前
                - DESC: 降序，按创建时间降序排列，最近创建的消息在前
        
        Returns:
            包含消息列表的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": {
                    "currentPage": 当前页码,
                    "pageSize": 总页数,
                    "total": 总条数,
                    "messages": [
                        {
                            "messageId": "消息ID",
                            "conversationId": "会话ID",
                            "appId": "智能体ID",
                            "query": "用户问题内容",
                            "answers": [
                                {
                                    "lane": "流水线标识",
                                    "mediaType": "媒体类型",
                                    "text": "文本内容",
                                    "url": ["图片链接"],
                                    "expireAt": 过期时间戳
                                }
                            ],
                            "files": [
                                {
                                    "type": "文件类型",
                                    "url": "预览链接",
                                    "expireAt": 过期时间戳
                                }
                            ],
                            "createAt": 创建时间戳,
                            "updateAt": 更新时间戳,
                            "status": "消息状态"
                        }
                    ]
                },
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        # 构建查询参数
        query_params = {
            "conversationId": conversation_id
        }
        
        if page_num is not None:
            query_params["pageNum"] = page_num
        
        if page_size is not None:
            query_params["pageSize"] = page_size
        
        if sort_order is not None:
            query_params["sortOrder"] = sort_order
        
        # 发送GET请求
        response = self.http_client.get('/api/conversation/messages', query=query_params)
        return response

    def create_conversation(self, app_id: str) -> dict:
        """
        创建会话
        用于创建新的会话
        
        Args:
            app_id: 应用ID (必填)
        
        Returns:
            包含会话ID的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": "会话ID",
                "traceId": "追踪ID"
            }
        
        Raises:
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        # 构建请求数据
        data = {
            "appId": app_id
        }
        
        # 发送POST请求
        response = self.http_client.post('/api/conversation/create', data=data)
        return response

    def upload_file(self, file_path: str) -> dict:
        """
        上传文件
        用于上传文件到服务器
        
        Args:
            file_path: 需要上传的文件路径 (必填)
        
        Returns:
            包含文件ID的响应数据，格式如下：
            {
                "errorCode": "0",
                "errorMsg": "success",
                "data": "文件ID",
                "traceId": "追踪ID"
            }
        
        Raises:
            FileNotFoundError: 文件不存在时抛出
            TboxClientConfigException: 配置错误时抛出
            TboxHttpResponseException: HTTP请求失败时抛出
        """
        import os
        import mimetypes
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        # 获取文件名和MIME类型
        filename = os.path.basename(file_path)
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # 打开文件并上传
        with open(file_path, 'rb') as file:
            files = {
                'file': (filename, file, content_type)
            }
            
            # 发送POST请求
            response = self.http_client.post_file('/api/file/upload', files=files)
            return response

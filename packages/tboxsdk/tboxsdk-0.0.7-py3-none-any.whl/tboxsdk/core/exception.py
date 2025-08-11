
class TboxClientException(Exception):
    """
    tbox client exception
    异常基类
    """
    pass

class TboxServerException(TboxClientException):
    """
    tbox server exception
    用来标识tbox server 异常
    """
    """
    持有具体的错误信息
    """
    error_context: dict = None

class TboxClientConfigException(TboxClientException):
    """
    tbox client config exception
    用来标识tbox client 配置异常
    """
    pass


class TboxHttpResponseException(TboxClientException):
    """
    http response exception
    用来标识client 发起http请求，触发的响应异常
    """
    pass
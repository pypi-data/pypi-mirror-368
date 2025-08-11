import json
import logging

from tboxsdk.core.httpclient import HttpResponseEvent
from tboxsdk.core.exception import TboxServerException
from enum import Enum
from typing import List, Optional


logger = logging.getLogger("tbox.client")

class MessageStatus(Enum):
    """消息状态"""
    SUCCESS = "SUCCESS"      # 成功
    ERROR = "ERROR"          # 失败
    BLOCK = "BLOCK"          # 安全拦截
    PENDING = "PENDING"      # 执行中


class MediaType(Enum):
    """媒体类型"""
    TEXT = "text"            # 文本
    IMAGE = "image"          # 图片


class Answer:
    """回答定义"""
    
    def __init__(self,
                 lane: str,
                 media_type: str,
                 text: Optional[str] = None,
                 url: Optional[List[str]] = None,
                 expire_at: Optional[int] = None):
        """
        构造Answer实例
        
        Args:
            lane: 流水线标识(默认为 default)
            media_type: 输出的内容类型 (text/image)
            text: 文本内容
            url: 图片链接(有效期24h)
            expire_at: 链接过期时间,时间戳,单位s
        """
        self.lane = lane
        self.media_type = media_type
        self.text = text
        self.url = url
        self.expire_at = expire_at
    
    def get_lane(self) -> str:
        """获取流水线标识"""
        return self.lane
    
    def get_media_type(self) -> str:
        """获取媒体类型"""
        return self.media_type
    
    def get_text(self) -> Optional[str]:
        """获取文本内容"""
        return self.text
    
    def get_url(self) -> Optional[List[str]]:
        """获取图片链接"""
        return self.url
    
    def get_expire_at(self) -> Optional[int]:
        """获取链接过期时间"""
        return self.expire_at
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Answer':
        """
        从字典创建Answer实例
        
        Args:
            data: 包含回答信息的字典
            
        Returns:
            Answer实例
        """
        return cls(
            lane=data.get('lane', 'default'),
            media_type=data.get('mediaType', ''),
            text=data.get('text'),
            url=data.get('url'),
            expire_at=data.get('expireAt')
        )
    
    def to_dict(self) -> dict:
        """
        转换为字典
        
        Returns:
            包含回答信息的字典
        """
        result = {
            'lane': self.lane,
            'mediaType': self.media_type
        }
        if self.text is not None:
            result['text'] = self.text
        if self.url is not None:
            result['url'] = self.url
        if self.expire_at is not None:
            result['expireAt'] = self.expire_at
        return result


class Message:
    """消息定义"""
    
    def __init__(self,
                 message_id: str,
                 conversation_id: str,
                 app_id: str,
                 query: str,
                 answers: List[Answer],
                 files: List[dict],
                 create_at: int,
                 update_at: int,
                 status: str):
        """
        构造Message实例
        
        Args:
            message_id: 消息ID
            conversation_id: 会话ID
            app_id: 智能体ID
            query: 用户发给智能体的问题内容
            answers: 智能体的回答
            files: 用户上传的文件集合
            create_at: 消息创建时间,时间戳,单位为s
            update_at: 消息更新时间,时间戳,单位为s
            status: 消息状态 (SUCCESS/ERROR/BLOCK/PENDING)
        """
        self.message_id = message_id
        self.conversation_id = conversation_id
        self.app_id = app_id
        self.query = query
        self.answers = answers
        self.files = files
        self.create_at = create_at
        self.update_at = update_at
        self.status = status
    
    def get_message_id(self) -> str:
        """获取消息ID"""
        return self.message_id
    
    def get_conversation_id(self) -> str:
        """获取会话ID"""
        return self.conversation_id
    
    def get_app_id(self) -> str:
        """获取智能体ID"""
        return self.app_id
    
    def get_query(self) -> str:
        """获取用户问题内容"""
        return self.query
    
    def get_answers(self) -> List[Answer]:
        """获取智能体回答"""
        return self.answers
    
    def get_files(self) -> List[dict]:
        """获取用户上传的文件集合"""
        return self.files
    
    def get_create_at(self) -> int:
        """获取创建时间"""
        return self.create_at
    
    def get_update_at(self) -> int:
        """获取更新时间"""
        return self.update_at
    
    def get_status(self) -> str:
        """获取消息状态"""
        return self.status
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        """
        从字典创建Message实例
        
        Args:
            data: 包含消息信息的字典
            
        Returns:
            Message实例
        """
        answers = []
        if data.get('answers'):
            for answer_data in data['answers']:
                answers.append(Answer.from_dict(answer_data))
        
        return cls(
            message_id=data.get('messageId', ''),
            conversation_id=data.get('conversationId', ''),
            app_id=data.get('appId', ''),
            query=data.get('query', ''),
            answers=answers,
            files=data.get('files', []),
            create_at=data.get('createAt', 0),
            update_at=data.get('updateAt', 0),
            status=data.get('status', '')
        )
    
    def to_dict(self) -> dict:
        """
        转换为字典
        
        Returns:
            包含消息信息的字典
        """
        return {
            'messageId': self.message_id,
            'conversationId': self.conversation_id,
            'appId': self.app_id,
            'query': self.query,
            'answers': [answer.to_dict() for answer in self.answers],
            'files': self.files,
            'createAt': self.create_at,
            'updateAt': self.update_at,
            'status': self.status
        }


class MessageParser(object):
    """
    message parser
    用来解析 http sse 响应报文
    """

    """
    用来持有 answers 的众多结果。
    用来保存多返回的内容是什么结构、类型
    answers ==> {
        "lane_key" :{ // 用来持有 响应的 lane,默认default，在工作流中可以查看有哪些响应key 
            "type" : "text", // 用来持有 响应类型： text、images、object等等
            "data": {}, // 用来持有 各种类型的响应值的最终聚合数据，比如text类型的流式响应，会被归集为一个字符串
            "header" : {}, // 用来持有每个lane的响应头
            "messages" : [] // 用来持有所有的chunk 类型的报文，保存在这里
        }
    
    }
    """
    answers_holder: dict = {}

    def need_parse(self, response_event: HttpResponseEvent) -> bool:
        """
        need parse
        :param response_event: http response event
        """
        if response_event.event in ("message", "error"):
            return True
        else:
            return False

    def parse(self, response_event: HttpResponseEvent) -> dict:
        if response_event.event == "error":
            self.parse_error(response_event)
        """
        parse
        :param response_event: http response event
        """
        if response_event.event == "message":
            data = json.loads(response_event.data)
            # 这里会有：header/chunk/meta/revoke/error/charge/end/unknown/followup
            if data.get("type") == "meta":
                return self.parse_meta_message(data)
            elif data.get("type") == "header":
                return self.parse_header_message(data)
            elif data.get("type") == "chunk":
                return self.parse_chunk_message(data)
            elif data.get("type") == "revoke":
                return self.parse_revoke_message(data)
            elif data.get("type") == "error":
                return self.parse_error_message(data)
            elif data.get("type") == "charge":
                return self.parse_charge_message(data)
            elif data.get("type") == "end":
                return self.parse_end_message(data)
            elif data.get("type") == "unknown":
                return self.parse_unknown_message(data)
            elif data.get("type") == "followup":
                return self.parse_followup_message(data)
            else:
                return data

        return json.loads(response_event.data)

    def parse_chunk_message(self, data: dict) -> dict:
        """
        parse message
        :param response_event: http response event
        """
        lane = data.get("lane", "default")
        mediaType = self.answers_holder.get(lane, {}).get("type", 'text');
        data['payload'] = json.loads(data.get("payload", "{}"))
        if mediaType == "text":
            self.answers_holder[lane]["data"] += data.get("payload", {}).get("text", "")
        self.answers_holder[lane]["messages"].append(data)
        return data

    def parse_meta_message(self, data: dict) -> dict:
        """
        parse meta
        :param response_event: http response event
        """
        return data

    def parse_header_message(self, data: dict) -> dict:
        """
        parse message
        :param data: http response event's data
        """
        if data.get("lane") is None:
            data["lane"] = "default"
        # 拆解playload
        payload = json.loads(data.get("payload", "{}"))
        data["payload"] = payload
        media_type = payload.get("mediaType")

        # 将内容写入到 answer holder 中
        if self.answers_holder.get(data["lane"]) is None:
            self.answers_holder[data["lane"]] = {
                "type": media_type,
                "header": data,
                "data": "",
                "messages": [],
            }
        else:
            self.answers_holder[data["lane"]]["header"] = data
            self.answers_holder[data["lane"]]["type"] = media_type
        return data

    def parse_revoke_message(self, data: dict) -> dict:
        return data

    def parse_error_message(self, data: dict) -> dict:
        return data

    def parse_charge_message(self, data: dict) -> dict:
        return data

    def parse_end_message(self, data: dict) -> dict:
        return data

    def parse_unknown_message(self, data: dict) -> dict:
        return data

    def parse_followup_message(self, data: dict) -> dict:
        return data

    def parse_error(self, response_event: HttpResponseEvent) -> None:
        error_context = json.loads(response_event.data)
        message = error_context.get("description", "unknown error")
        exception = TboxServerException(message)
        exception.error_context = error_context
        raise exception

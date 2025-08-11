from enum import Enum


class ConversationSource(Enum):
    """会话来源渠道"""
    AGENT_SDK = "AGENT_SDK"  # SDK渠道
    OPENAPI = "OPENAPI"      # OpenAPI渠道
    IOT_SDK = "IOT_SDK"      # IOT SDK渠道


class Conversation:
    """会话定义"""
    
    def __init__(self, 
                 conversation_id: str,
                 user_id: str,
                 source: str,
                 create_at: int
                 ):
        """
        构造Conversation实例
        
        Args:
            conversation_id: 会话id
            user_id: 用户id
            source: 渠道 (AGENT_SDK/OPENAPI/IOT_SDK)
            create_at: 创建时间,时间戳,单位为s
        """
        self.conversation_id = conversation_id
        self.user_id = user_id
        self.source = source
        self.create_at = create_at
    
    def get_conversation_id(self) -> str:
        """获取会话ID"""
        return self.conversation_id
    
    def get_user_id(self) -> str:
        """获取用户ID"""
        return self.user_id
    
    def get_source(self) -> str:
        """获取渠道"""
        return self.source
    
    def get_create_at(self) -> int:
        """获取创建时间"""
        return self.create_at
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Conversation':
        """
        从字典创建Conversation实例
        
        Args:
            data: 包含会话信息的字典
            
        Returns:
            Conversation实例
        """
        return cls(
            conversation_id=data.get('conversationId', ''),
            user_id=data.get('userId', ''),
            source=data.get('source', ''),
            create_at=data.get('createAt', 0),
        )
    
    def to_dict(self) -> dict:
        """
        转换为字典
        
        Returns:
            包含会话信息的字典
        """
        return {
            'conversationId': self.conversation_id,
            'userId': self.user_id,
            'source': self.source,
            'createAt': self.create_at
        } 
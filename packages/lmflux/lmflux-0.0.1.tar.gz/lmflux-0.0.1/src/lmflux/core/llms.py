from dataclasses import dataclass
from abc import ABC, abstractmethod
from lmflux.core.components import (Message, LLMOptions, SystemPrompt, Conversation, Tool)

class LLMModel(ABC):
    def __init__(self, system_prompt:SystemPrompt, model_id:str, options:LLMOptions):
        self.model_id = model_id
        self.options = options
        self.system_prompt = system_prompt
        self.tools = []
        self.reset_state()
        self.conversation_update_callback = None
        if self.options is None:
            self.options = LLMOptions()
    
    def set_conversation_update_callback(self, callback: callable):
        self.conversation_update_callback = callback
    
    def reset_state(self,):
        self.conversation = Conversation(messages=[self.system_prompt.get_message()])
    
    def add_tool(self, tool:Tool):
        self.tools.append(tool)
        
    def add_tools(self, tools: list[Tool]):
        self.tools += tools
    
    @abstractmethod
    def __chat_endpoint__(self, tool_use_callback:callable) -> Message: pass
    
    def chat(self, msg: Message, tool_use_callback:callable=None):
        self.conversation.add_message(msg)
        response = self.__chat_endpoint__(tool_use_callback)
        for message in response:
            self.conversation.add_message(message)
        if self.conversation_update_callback:
            self.conversation_update_callback(self.conversation)
        return response[-1]

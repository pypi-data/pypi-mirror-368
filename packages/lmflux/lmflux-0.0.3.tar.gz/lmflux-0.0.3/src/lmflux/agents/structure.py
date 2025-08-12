from abc import ABC, abstractmethod
from lmflux.core.llms import LLMModel
from lmflux.core.components import Message, Tool
from lmflux.agents.components import AgentRef
from lmflux.agents.sessions import Session

class Agent(ABC):
    def __init__(self,):
        self.agent_tools = self.get_tools()
        self.llm, self.agent_id = self.initialize(self.agent_tools)
        self.agent_ref = AgentRef(self.agent_id, self)

    @abstractmethod
    def reset_agent_state(): pass

    @abstractmethod
    def get_tools(self) -> list[Tool]: pass
        
    @abstractmethod
    def initialize(self, tools:list[Tool]) -> tuple[LLMModel, str]: pass
    
    @abstractmethod
    def pre_act(self, session: Session): pass
    
    @abstractmethod
    def post_act(self, session: Session): pass
    
    @abstractmethod
    def act(self, session: Session): pass
    
    @abstractmethod
    def tool_callback(self, tool_call, result, session: Session): pass
    
    def conversate(self, message:Message, session: Session) -> Message:
        callback = lambda tool_call, result: self.tool_callback(tool_call, result, session)
        data = self.llm.chat(message, tool_use_callback=callback)
        return data
    
    def log_agent_step(self, session:Session, step_message: str, messages:list[Message], print_full_message=False):
        messages_log = '\n'.join([str(message) for message in messages])
        full_log = f'({self.agent_id}) {step_message}'
        if print_full_message:
            full_log  += f'\n-----\n{messages_log}\n-----\n'
        session.logger.info(full_log)
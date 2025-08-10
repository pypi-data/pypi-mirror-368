from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lmflux.agents import Agent
    

@dataclass
class AgentRef:
    agent_id: str
    agent:'Agent'
    
    def get_agent(self) -> 'Agent':
        return self.agent
    
    def __str__(self):
        return f"AGENT_REF[{self.agent_id}]"
    def __repr__(self):
        return self.__str__

@dataclass
class Context:
    # The reason for the split here is that we might need the cumulative context to be thread safe.
    context: dict
    context_cumulative: dict
    
    def set(self, key, value):
        self.context[key] = value
    def remove(self, key):
        del self.context[key]
    def get(self, key, default=None):
        return self.context.get(key, default)
    def get_context(self):
        return self.context
    def set_cumulative(self, key, value):
        if key not in self.context_cumulative:
            self.context_cumulative[key] = []
        self.context_cumulative[key].append(value)
    def get_cumulative(self, key):
        return self.context_cumulative.get(key)
    
    def __str__(self):
        return f"Context[{self.context}]"
    def __repr__(self):
        return self.__str__()
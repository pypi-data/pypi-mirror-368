from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lmflux.agents import Agent
    
from lmflux.logger import PipelinesLogger
from copy import deepcopy
from uuid import uuid4

class Context:
    # The reason for the split here is that we might need the cumulative context to be thread safe.
    def __init__(self):
        self.context = {}
        self.context_cumulative = {}
        
    def clone_context(self, context: 'Context'):
        self.context = deepcopy(context.context)
        self.context_cumulative = deepcopy(self.context_cumulative)
    
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

class Session:
    global_context: Context
    logger:PipelinesLogger = PipelinesLogger.get_instance()

    def __init__(self, starting_context:Context=None):
        self.session_id = str(uuid4())
        
        if starting_context:
            self.context = Context()
            self.context.clone_context(starting_context)
        else:
            self.context = Context()
    
    def context_as_dict(self) -> dict:
        return self.context.get_context()
from lmflux.core.llms import LLMModel
from lmflux.flow.definitions import AgentDefinition
from lmflux.flow.toolbox import ToolBox, tool

def new_toolbox():
    return ToolBox()

def create_agent(llm:LLMModel, agent_id: str):
    return AgentDefinition(llm, agent_id)
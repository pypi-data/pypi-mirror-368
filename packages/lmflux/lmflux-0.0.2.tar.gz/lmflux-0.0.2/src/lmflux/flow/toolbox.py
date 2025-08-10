from lmflux.core.llms import LLMModel
from lmflux.core.components import Tool, ToolParam
from lmflux.agents.sessions import Session
from lmflux.agents.structure import Agent

import inspect
from typing import get_args, get_origin
from types import GenericAlias

from enum import Enum

def parse_llm_type(py_type, allow_generic=True) -> str:
    if type(py_type) == GenericAlias and allow_generic:
        origin = get_origin(py_type)
        args = get_args(py_type)
        sub_type = None
        if origin is not list:
            raise AttributeError(f"When using GenericAlias types such as {py_type} only lists are supported for now.")
        parsed_sub_types = []
        for arg in args:
           parsed_sub_types.append(parse_llm_type(arg, allow_generic=False))
        sub_parsed_type = '|'.join(parsed_sub_types)
        return f'array[{sub_parsed_type}]'
    elif py_type in [int, float]:
        return "number"
    elif py_type == str:
        return "string"
    elif py_type == bool:
        return "boolean"
    elif py_type == list:
        raise AttributeError("To use list please define the sub type example: `list[str]`")
    elif issubclass(py_type, Enum):
        found_type = "enum"
        raise AttributeError("Enums not implemented yet")
    else:
        raise AttributeError(f"Cannot define tool of type {py_type}")

def tool(func:callable):
    signature = inspect.signature(func)
    tool_params = []
    description = func.__doc__
    if not description:
        raise AttributeError(
            "Tools are required to have descriptions (docstrings)"
        )
    for param in signature.parameters.values():
        py_type = param.annotation
        if py_type != inspect.Signature.empty:
            found_type = ""
            found_type = parse_llm_type(py_type)
            tool_params.append(
                ToolParam(
                    type=found_type, 
                    name=param.name, 
                    is_required=param.POSITIONAL_ONLY
                )
            )
        else:
            raise AttributeError("Tools are required to be typed")
    root_param = ToolParam(
        type="object",
        name="parameters",
        property=tool_params
    )
    tool_def = (
        Tool(
            name=func.__name__,
            description=description,
            root_param=root_param,
            func=func
        )
    )
    def wraps(*args, **kword_args):
        return func(*args, **kword_args)
    wraps.__setattr__('__is_tool_definition__', True)
    wraps.__setattr__('__tool_definition__', tool_def)
    return wraps

class ToolBox:
    def __init__(self):
        self.tools = []
    def __add_tool__(self, tool: Tool):
        self.tools.append(tool)
    def add_to_toolbox(self, func: callable):
        try:
            func.__getattribute__('__is_tool_definition__')
        except AttributeError as e:
            raise AttributeError("The function passed to `add_to_toolbox` is not a proper tool, did you add the @tool decorator while declaring it?")
        else:
            self.__add_tool__(func.__getattribute__("__tool_definition__"))
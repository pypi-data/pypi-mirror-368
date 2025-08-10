from lmflux.core.llms import LLMModel
from lmflux.core.components import (SystemPrompt, LLMOptions, Message, Conversation)
import openai
import os

class EchoLLM(LLMModel):
    def __init__(self, model_id:str, system_prompt:SystemPrompt, options:LLMOptions=None):
        super().__init__(model_id=model_id, system_prompt=system_prompt, options=options)
    
    def __chat_endpoint__(self, tool_use_callback:callable) -> list[Message]:
        return [self.conversation[-1]]

class OpenAICompatibleEndpoint(LLMModel):
    def __init__(self, model_id:str, system_prompt:SystemPrompt, options:LLMOptions=None):
        super().__init__(model_id=model_id, system_prompt=system_prompt, options=options)

        self.client = openai.OpenAI(
            base_url=os.environ.get('OPENAI_API_BASE'),
            api_key=os.environ.get('OPENAI_API_KEY'),
        )
        self.last_len_tools = 0
        self.compiled_tools = None

    def __compile_tools__(self,):
        if self.last_len_tools == len(self.tools):
            return
        if len(self.tools) == 0:
            self.compiled_tools = None
        self.compiled_tools = [
            tool.build_tool_call()
            for tool in self.tools
        ]
        self.last_len_tools = len(self.tools)
    
    def __call_function__(self, tool_call, tool_use_callback:callable) -> Message:
        tool_call_id = tool_call.id
        function_name = tool_call.function.name
        args = tool_call.function.arguments
        result = None
        for tool in self.tools:
            if tool.name == function_name:
                result = tool.get_call_response(args)
                break
        if not result:
            result = "[ERROR] - Tool not found"
        if tool_use_callback:
            tool_use_callback(tool_call, result)
        return Message(
            role="tool", content=str(result),
            call_id=tool_call_id,
            name=function_name
        )
    
    def __parse_tool_call__(self, tool_calls):
        if tool_calls:
            return [{
                "id": tool_call.id,
                "type": "function",
                "function": { 
                    "name": tool_call.function.name, 
                    "arguments": tool_call.function.arguments
                }
            } for tool_call in tool_calls]
        return None
    
    def __chat_endpoint__(self, tool_use_callback:callable, max_turns=3) -> list[Message]:
        accum_messages = Conversation([])
        conversation_dump = self.conversation.dump_conversation()
        num_turns = 0
        self.__compile_tools__()
        while(True):
            num_turns += 1
            tool_called = False
            accum_dump = accum_messages.dump_conversation()
            chat_completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=conversation_dump+accum_dump,
                tools=self.compiled_tools,
                **self.options.dict()
            )
            
            accum_messages.add_message(
                Message(
                    chat_completion.choices[0].message.role, 
                    content=chat_completion.choices[0].message.content,
                    reasoning_content=chat_completion.choices[0].message.reasoning_content,
                    tool_calls = self.__parse_tool_call__(chat_completion.choices[0].message.tool_calls)   
                )
            )
            if chat_completion.choices[0].message.tool_calls:
                for tool_call in chat_completion.choices[0].message.tool_calls:
                    accum_messages.add_message(
                        self.__call_function__(tool_call, tool_use_callback)
                    )
                    tool_called = True
            if not tool_called:
                break
            if (num_turns > max_turns):
                raise ValueError("Max turns exceeded when calling tools")
        return accum_messages.messages
    
class NamedOAICompatible(OpenAICompatibleEndpoint):
    def __init__(self, model_id, system_prompt:SystemPrompt, options:LLMOptions=None):
        if options is None:
            options = LLMOptions()
        super().__init__(model_id=model_id, 
                         system_prompt=system_prompt, options=options)
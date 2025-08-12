import json
from lmflux import variables
from dataclasses import dataclass, asdict
from uuid import uuid4

def get_template(prompt_id):
    prompt_path = prompt_id.split('.')
    path = '/'.join(prompt_path[:-1])
    sub_location = f'{path}/{prompt_path[-1]}'
    with open(f'{variables.PROMPT_LOCATION}/{sub_location}.md') as f:
        return f.read()

## BASE LLM ##
@dataclass
class LLMOptions():
    temperature:float = 0.7
    max_tokens:int = None
    
    def dict(self):
        return {k: str(v) for k, v in asdict(self).items() if v is not None}

@dataclass
class Message:
    role: str
    content: str
    
    reasoning_content: str = None
    call_id: str = None    
    tool_calls: list[dict] = None
    name: str = None

    message_id: str = str(uuid4())

    def dump_message(self):
        base_data = {"role": self.role, "content": self.content if self.content else ""}
        if self.tool_calls:
            base_data["tool_calls"] = self.tool_calls
        if self.call_id:
            base_data["tool_call_id"] = self.call_id
        if self.name:
            base_data['name'] = self.name
        if self.reasoning_content:
            base_data['reasoning_content'] = self.reasoning_content
        return base_data
    
    def __str__(self):
        main_str = f"Message({self.role}):"
        if self.name:
            main_str += f"\n\tname: {self.name}"
        if self.call_id:
            main_str += f"\n\ttool call: {self.call_id}"
        if self.tool_calls:
            main_str += f"\n\ttool call: {self.tool_calls}"
        if self.content:
            main_str += f"\n\tcontent: {self.content}"
        return main_str
    
    def __repr__(self):
        return self.__str__()

## PROMPTS ##
@dataclass
class SystemPrompt:
    system_prompt_id: str = None
    
    def get_message(self)->Message:
        if self.system_prompt_id:
            content = get_template(self.system_prompt_id)
            message = Message(role="system", content=content)
        else:
            message = Message(role="system", content="You are a helpful assistant")
        return message
    
@dataclass
class TemplatedPrompt:
    prompt_id: str
    role: str
    
    def get_message(self, context:dict, )->Message:
        content = get_template(self.prompt_id)
        for key, value in context.items():
            content = content.replace('{{'+key+'}}', str(value))
        message = Message(role=self.role, content=content)
        return message
    
## TOOLS ##
@dataclass
class ToolParam:
    type: str
    name: str
    property: list['ToolParam'] = None
    additional_properties: bool = False
    is_required:bool = False
    
    def make_definition(self,) -> tuple[str, dict]:
        if self.property == None:
            if 'array' in self.type:
                sub_type = self.type.replace('array[', '').replace(']', '')
                data = {'type': 'array', 'items': {"type": sub_type}}
            else:
                data = {'type': self.type}
        else:
            if self.type != 'object':
                raise ValueError(
                    f"ToolParam can't be of type '{self.type}' and have property must be of type 'object'."
                )
            props = {}
            required = []
            for subtool in self.property:
                name, data, is_required = subtool.make_definition()
                props[name] = data
                if is_required:
                    required.append(name)
            data = {
                'type': 'object',
                'properties': props,
                'required': required,
                'additionalProperties': self.additional_properties
            }
        return self.name, data, self.is_required

@dataclass
class Tool:
    #type: str
    name: str
    description: str
    root_param: ToolParam
    func: callable

    def build_tool_call(self,) -> dict:
        # Auto-caching
        if hasattr(self, 'definition'):
            return self.definition
        if self.root_param.type != 'object':
            raise ValueError("root param must be of type object")
        _, data, _ = self.root_param.make_definition()
        self.definition = {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": data,
                "strict": True
            }
        }
        return self.definition

    def get_call_response(self, args_json) -> dict[str, str]:
        args = json.loads(args_json)
        return self.func(**args)
    
@dataclass
class Conversation:
    messages: list[Message]
    
    def add_message(self, message: Message):
        self.messages.append(message)        
    
    def dump_conversation(self):
        return [
            message.dump_message()
            for message in self.messages
        ]
    
    def __len__(self):
        return len(self.messages)

    def __getitem__(self, index: int | slice):
        return self.messages[index]

    def __repr__(self):
        main_str = "Conversation:\n----\n"
        for message in self.messages:
            main_str += str(message)+'\n'
        return main_str+'----\n'

    def __iter__(self):
        return iter(self.messages)
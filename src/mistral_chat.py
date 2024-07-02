import os
from enum import Enum

from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage, ResponseFormats

MISTRAL_API_KEY = "6pgrrmzn12qeHd9BtKW8OuTTLDGodKBo"


class Role(Enum):  # specific to mistral-ai
    system: str = 'system'
    user: str = 'user'
    assistant: str = 'assistant'
    tool: str = 'tool'


class MistralModel(Enum):
    mistral_medium: str = 'mistral-medium-latest'
    mistral_large: str = 'mistral-large-latest'


class MistralChat:
    def __init__(self, system_prompt=None, model_name: MistralModel = MistralModel.mistral_large, memory: bool = True):
        self.system: str = system_prompt
        self.messages = []
        self.trace = []  # Same as message but persistent
        self.model_name: MistralModel = model_name
        self.memory: bool = memory
        self.client = MistralClient(api_key=MISTRAL_API_KEY)

        if self.system:
            self.messages.append(ChatMessage(role=Role.system, content=system_prompt))
            self.trace.append(ChatMessage(role=Role.system, content=system_prompt))

    def chat(self, message: str, role: Role = Role.user, response_format: ResponseFormats = ResponseFormats.text):
        self.messages.append(ChatMessage(role=role, content=message))
        self.trace.append(ChatMessage(role=role, content=message))

        llm_response = self.client.chat(model=self.model_name.value, messages=self.messages)

        response_ = llm_response.choices[0].message.content

        self.messages.append(ChatMessage(role=Role.assistant, content=response_))
        self.trace.append(ChatMessage(role=Role.assistant, content=response_))

        if not self.memory:  # if memory is turned off
            self.messages.pop()
            self.messages.pop()
        return response_

import typing as t
from enum import Enum
from pydantic import BaseModel


class Role(str, Enum):
    system = "system"  # setup (system prompt)
    user = "user"  # user input
    assistant = "assistant"  # model output


class Message(BaseModel):
    role: Role
    content: str


class Feedback(BaseModel):
    prompt: str
    improvement: str


class TreeNode(BaseModel):
    children: t.List["TreeNode"]
    conversation: t.List[Message]
    feedback: t.Optional[Feedback]
    response: t.Optional[str]
    on_topic: t.Optional[bool]
    score: t.Optional[int]


class Parameters(BaseModel):
    model: str
    temperature: float = 1.0
    max_tokens: int = 512
    top_p: float = 0.9


class ChatRequest(Parameters):
    context: str
    prompt: str


class LogLevelEnum(Enum):
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10


ChatFunction = t.Callable[[t.List[Message]], Message]
Conversation = t.List[Message]

from dataclasses import dataclass
from collections.abc import Callable, Awaitable

from google.protobuf.message import Message

from twirp import context

TwirpMethod = Callable[[context.Context, Message], Awaitable[Message]]


@dataclass
class Endpoint:
    service_name: str
    name: str
    function: TwirpMethod
    input: type[Message]
    output: type[Message]

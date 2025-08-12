import functools
from collections.abc import Awaitable
from typing import Any
from collections.abc import Callable

from google.protobuf import json_format, message
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.message import Message

from . import context

from . import server
from . import exceptions
from . import errors
from . import hook as vtwirp_hook
from .endpoint import Endpoint, TwirpMethod

_sym_lookup = _symbol_database.Default().GetSymbol

Middleware = Callable[[context.Context, Message, TwirpMethod], Awaitable[Message]]


class TwirpBaseApp:
    def __init__(
        self,
        *middlewares: Middleware,
        hook: vtwirp_hook.TwirpHook | None = None,
        prefix: str = "",
        max_receive_message_length: int = 1024 * 100 * 100,
        ctx_class: type[context.Context] | None = None,
    ) -> None:
        self._prefix: str = prefix
        self._services: dict[str, server.TwirpServer] = {}
        self._max_receive_message_length: int = max_receive_message_length
        if ctx_class is None:
            ctx_class = context.Context
        assert issubclass(ctx_class, context.Context)
        self._ctx_class: type[context.Context] = ctx_class
        self._middlewares: tuple[Middleware, ...] = middlewares
        if hook is None:
            hook = vtwirp_hook.TwirpHook()
        assert isinstance(hook, vtwirp_hook.TwirpHook)
        self._hook: vtwirp_hook.TwirpHook = hook

    def add_service(self, svc: server.TwirpServer) -> None:
        self._services[self._prefix + svc.prefix] = svc

    def _get_endpoint(self, path: str) -> Endpoint:
        svc = self._services.get(path.rsplit("/", 1)[0], None)
        if svc is None:
            raise exceptions.TwirpServerException(code=errors.Errors.NotFound, message="not found")

        return svc.get_endpoint(path[len(self._prefix) :])

    @staticmethod
    def json_decoder(body: bytes, data_obj: type[Message]) -> Message:
        data = data_obj()
        try:
            json_format.Parse(body, data)
        except json_format.ParseError as exc:
            raise exceptions.TwirpServerException(
                code=errors.Errors.Malformed,
                message="the json request could not be decoded",
            ) from exc
        return data

    @staticmethod
    def json_encoder(value: Any, data_obj: type[Message]) -> tuple[bytes, dict[str, str]]:
        if not isinstance(value, data_obj):
            raise exceptions.TwirpServerException(
                code=errors.Errors.Internal,
                message=(
                    "bad service response type " + str(type(value)) + ", expecting: " + data_obj.DESCRIPTOR.full_name
                ),
            )

        return json_format.MessageToJson(value, preserving_proto_field_name=True).encode("utf-8"), {
            "Content-Type": "application/json"
        }

    @staticmethod
    def proto_decoder(body: bytes, data_obj: type[Message]) -> Message:
        data = data_obj()
        try:
            data.ParseFromString(body)
        except message.DecodeError as exc:
            raise exceptions.TwirpServerException(
                code=errors.Errors.Malformed,
                message="the protobuf request could not be decoded",
            ) from exc
        return data

    @staticmethod
    def proto_encoder(value: Any, data_obj: type[Message]) -> tuple[bytes, dict[str, str]]:
        if not isinstance(value, data_obj):
            raise exceptions.TwirpServerException(
                code=errors.Errors.Internal,
                message=(
                    "bad service response type " + str(type(value)) + ", expecting: " + data_obj.DESCRIPTOR.full_name
                ),
            )

        return value.SerializeToString(), {"Content-Type": "application/protobuf"}

    def _get_encoder_decoder(
        self, endpoint: Endpoint, headers: dict[str, str]
    ) -> tuple[Callable[[Any], tuple[bytes, dict[str, str]]], Callable[[bytes], Message]]:
        ctype = headers.get("content-type", None)
        if "application/json" == ctype:
            decoder = functools.partial(self.json_decoder, data_obj=endpoint.input)
            encoder = functools.partial(self.json_encoder, data_obj=endpoint.output)
        elif "application/protobuf" == ctype:
            decoder = functools.partial(self.proto_decoder, data_obj=endpoint.input)
            encoder = functools.partial(self.proto_encoder, data_obj=endpoint.output)
        else:
            raise exceptions.TwirpServerException(
                code=errors.Errors.BadRoute, message="unexpected Content-Type: " + str(ctype)
            )
        return encoder, decoder

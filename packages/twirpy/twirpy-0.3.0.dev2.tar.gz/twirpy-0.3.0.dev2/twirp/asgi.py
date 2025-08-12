import traceback

from asgiref.typing import (
    ASGIReceiveCallable,
    ASGISendCallable,
    Scope,
    HTTPResponseStartEvent,
    HTTPResponseBodyEvent,
    ASGIReceiveEvent,
)
from google.protobuf.message import Message

from twirp.endpoint import Endpoint, TwirpMethod
from . import base
from . import exceptions
from . import errors
from . import ctxkeys
from . import context

Headers = dict[str, str]


class TwirpASGIApp(base.TwirpBaseApp):
    async def __call__(self, scope: Scope, receive: ASGIReceiveCallable, send: ASGISendCallable) -> None:
        assert scope["type"] == "http"
        ctx = self._ctx_class()
        try:
            http_method = scope["method"]
            if http_method != "POST":
                raise exceptions.TwirpServerException(
                    code=errors.Errors.BadRoute,
                    message="unsupported method " + http_method + " (only POST is allowed)",
                    meta={"twirp_invalid_route": http_method + " " + scope["path"]},
                )

            headers = {k.decode("utf-8"): v.decode("utf-8") for (k, v) in scope["headers"]}
            ctx.set(ctxkeys.RAW_REQUEST_PATH, scope["path"])
            ctx.set(ctxkeys.RAW_HEADERS, headers)
            self._hook.request_received(ctx=ctx)

            endpoint: Endpoint = self._get_endpoint(scope["path"])
            headers = {k.decode("utf-8"): v.decode("utf-8") for (k, v) in scope["headers"]}
            self.validate_content_length(headers=headers)
            encoder, decoder = self._get_encoder_decoder(endpoint, headers)

            # add headers from request into context
            ctx.set(ctxkeys.SERVICE_NAME, endpoint.service_name)
            ctx.set(ctxkeys.METHOD_NAME, endpoint.name)
            ctx.set(ctxkeys.RESPONSE_STATUS, 200)
            self._hook.request_routed(ctx=ctx)
            raw_receive = await self._recv_all(receive)
            request = decoder(raw_receive)
            response_data: Message = await self._with_middlewares(func=endpoint.function, ctx=ctx, request=request)
            self._hook.response_prepared(ctx=ctx)

            body_bytes, headers = encoder(response_data)
            headers = dict(ctx.get_response_headers(), **headers)
            # Todo: middleware
            await self._respond(send=send, status=200, headers=headers, body_bytes=body_bytes)
            self._hook.response_sent(ctx=ctx)
        except Exception as e:
            await self.handle_error(ctx, e, scope, receive, send)

    async def _with_middlewares(self, *, func: TwirpMethod, ctx: context.Context, request: Message) -> Message:
        chain = iter(self._middlewares)

        def _bind_next() -> TwirpMethod:
            try:
                middleware = next(chain)

                async def _next(ctx_: context.Context, request_: Message) -> Message:
                    return await middleware(ctx_, request_, _bind_next())

                return _next
            except StopIteration:
                return func

        fn = _bind_next()
        return await fn(ctx, request)

    async def handle_error(
        self, ctx: context.Context, exc: Exception, scope_: Scope, receive_: ASGIReceiveCallable, send: ASGISendCallable
    ) -> None:
        status = 500
        logger = ctx.get_logger()
        error_data = {}
        ctx.set(ctxkeys.ORIGINAL_EXCEPTION, exc)
        try:
            if not isinstance(exc, exceptions.TwirpServerException):
                error_data["raw_error"] = str(exc)
                error_data["raw_trace"] = traceback.format_exc()
                logger.exception("got non-twirp exception while processing request", **error_data)
                exc = exceptions.TwirpServerException(code=errors.Errors.Internal, message="Internal non-Twirp Error")

            body_bytes = exc.to_json_bytes()
            status = errors.Errors.get_status_code(exc.code)
        except Exception:
            exc = exceptions.TwirpServerException(
                code=errors.Errors.Internal, message="There was an error but it could not be serialized into JSON"
            )
            error_data["raw_error"] = str(exc)
            error_data["raw_trace"] = traceback.format_exc()
            logger.exception("got exception while processing request", **error_data)
            body_bytes = exc.to_json_bytes()

        ctx.set_logger(logger.bind(**error_data))
        ctx.set(ctxkeys.RESPONSE_STATUS, status)
        self._hook.error(ctx=ctx, exc=exc)
        await self._respond(
            send=send, status=status, headers={"Content-Type": "application/json"}, body_bytes=body_bytes
        )
        self._hook.response_sent(ctx=ctx)

    @staticmethod
    async def _respond(*, send: ASGISendCallable, status: int, headers: Headers, body_bytes: bytes) -> None:
        headers["Content-Length"] = str(len(body_bytes))
        resp_headers = [(k.encode("utf-8"), v.encode("utf-8")) for (k, v) in headers.items()]
        await send(
            HTTPResponseStartEvent(
                type="http.response.start",
                status=status,
                headers=resp_headers,
                trailers=False,
            )
        )
        await send(
            HTTPResponseBodyEvent(
                type="http.response.body",
                body=body_bytes,
                more_body=False,
            )
        )

    async def _recv_all(self, receive: ASGIReceiveCallable) -> bytes:
        body = b""
        more_body = True
        while more_body:
            message: ASGIReceiveEvent = await receive()
            if message["type"] != "http.request":
                raise exceptions.TwirpServerException(
                    code=errors.Errors.Internal,
                    message="expected http.request message type, got " + message["type"],
                )
            body += message.get("body", b"")
            more_body = message.get("more_body", False)

            # the body length exceeded than the size set, raise a valid exception
            # so that proper error is returned to the client
            if self._max_receive_message_length < len(body):
                raise exceptions.TwirpServerException(
                    code=errors.Errors.InvalidArgument,
                    message=f"message body exceeds the specified length of {self._max_receive_message_length} bytes",
                )

        return body

    # we will check content-length header value and make sure it is
    # below the limit set
    def validate_content_length(self, headers: Headers) -> None:
        try:
            raw_value = headers.get("content-length", None)
            if not raw_value:
                return
            content_length = int(raw_value)
        except (ValueError, TypeError):
            return

        if self._max_receive_message_length < content_length:
            raise exceptions.TwirpServerException(
                code=errors.Errors.InvalidArgument,
                message=f"message body exceeds the specified length of {self._max_receive_message_length} bytes",
            )

from typing import Any

import requests
from google.protobuf.message import Message

from . import context
from . import exceptions
from . import errors


class TwirpClient:
    def __init__(self, address: str, timeout: int = 5) -> None:
        self._address = address
        self._timeout = timeout

    def _make_request[Req: Message, Resp: Message](
        self, *, url: str, ctx: context.Context, request: Req, response_obj: type[Resp], **kwargs: Any
    ) -> Resp:
        if "timeout" not in kwargs:
            kwargs["timeout"] = self._timeout
        headers = ctx.get_headers()
        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        kwargs["headers"]["Content-Type"] = "application/protobuf"
        try:
            resp = requests.post(url=self._address + url, data=request.SerializeToString(), **kwargs)
            if resp.status_code == 200:
                response: Resp = response_obj()
                response.ParseFromString(resp.content)
                return response
            try:
                raise exceptions.TwirpServerException.from_json(resp.json())
            except requests.JSONDecodeError:
                raise exceptions.twirp_error_from_intermediary(
                    resp.status_code, resp.reason, resp.headers, resp.text
                ) from None
            # Todo: handle error
        except requests.exceptions.Timeout as e:
            raise exceptions.TwirpServerException(
                code=errors.Errors.DeadlineExceeded,
                message=str(e),
                meta={"original_exception": e},
            )
        except requests.exceptions.ConnectionError as e:
            raise exceptions.TwirpServerException(
                code=errors.Errors.Unavailable,
                message=str(e),
                meta={"original_exception": e},
            )

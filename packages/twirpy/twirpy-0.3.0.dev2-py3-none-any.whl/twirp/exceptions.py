import json
from http.client import HTTPException
from typing import Any, TypedDict, Self

from multidict import CIMultiDictProxy
from requests.structures import CaseInsensitiveDict

from . import errors


class TwirpServerExceptionDict(TypedDict, total=False):
    code: str
    msg: str
    meta: dict[str, Any]


class TwirpServerException(HTTPException):
    def __init__(self, *, code: errors.Errors | str, message: str, meta: dict[str, Any] | None = None):
        try:
            self._code = errors.Errors(code)
        except ValueError:
            self._code = errors.Errors.Unknown
        self._message = message
        self._meta = meta or {}
        super().__init__(message)

    @property
    def code(self) -> errors.Errors:
        if isinstance(self._code, errors.Errors):
            return self._code
        return errors.Errors.Unknown

    @property
    def message(self) -> str:
        return self._message

    @property
    def meta(self) -> dict[str, Any]:
        return self._meta

    def to_dict(self) -> TwirpServerExceptionDict:
        err: TwirpServerExceptionDict = {"code": self._code.value, "msg": self._message, "meta": {}}
        for k, v in self._meta.items():
            err["meta"][k] = str(v)
        return err

    def to_json_bytes(self) -> bytes:
        return json.dumps(self.to_dict()).encode("utf-8")

    @classmethod
    def from_json(cls, err_dict: TwirpServerExceptionDict) -> Self:
        return cls(
            code=err_dict.get("code", errors.Errors.Unknown),
            message=err_dict.get("msg", ""),
            meta=err_dict.get("meta", {}),
        )


def InvalidArgument(*, argument: str, error: str) -> TwirpServerException:
    return TwirpServerException(
        code=errors.Errors.InvalidArgument, message=f"{argument} {error}", meta={"argument": argument}
    )


def RequiredArgument(*, argument: str) -> TwirpServerException:
    return InvalidArgument(argument=argument, error="is required")


def twirp_error_from_intermediary(
    status: int, reason: str | None, headers: CaseInsensitiveDict[str] | CIMultiDictProxy[str], body: str
) -> TwirpServerException:
    # see https://twitchtv.github.io/twirp/docs/errors.html#http-errors-from-intermediary-proxies
    meta: dict[str, str | None] = {
        "http_error_from_intermediary": "true",
        "status_code": str(status),
    }

    if 300 <= status < 400:
        # twirp uses POST which should not redirect
        code = errors.Errors.Internal
        location = headers.get("location")
        message = 'unexpected HTTP status code %d "%s" received, Location="%s"' % (
            status,
            reason,
            location,
        )
        meta["location"] = location

    else:
        code = {
            400: errors.Errors.Internal,  # JSON response should have been returned
            401: errors.Errors.Unauthenticated,
            403: errors.Errors.PermissionDenied,
            404: errors.Errors.BadRoute,
            429: errors.Errors.ResourceExhausted,
            502: errors.Errors.Unavailable,
            503: errors.Errors.Unavailable,
            504: errors.Errors.Unavailable,
        }.get(status, errors.Errors.Unknown)

        message = 'Error from intermediary with HTTP status code %d "%s"' % (
            status,
            reason,
        )
        meta["body"] = body

    return TwirpServerException(code=code, message=message, meta=meta)

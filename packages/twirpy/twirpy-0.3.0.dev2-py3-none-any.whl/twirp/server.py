from typing import Any

from .endpoint import Endpoint
from . import exceptions
from . import errors


class TwirpServer:
    def __init__(self, *, service: Any) -> None:
        self.service: Any = service
        self._endpoints: dict[str, Endpoint] = {}
        self._prefix: str = ""

    @property
    def prefix(self) -> str:
        return self._prefix

    def get_endpoint(self, path: str) -> Endpoint:
        (_, url_pre, rpc_method) = path.rpartition(self._prefix + "/")
        if not url_pre or not rpc_method:
            raise exceptions.TwirpServerException(
                code=errors.Errors.BadRoute,
                message="no handler for path " + path,
                meta={"twirp_invalid_route": "POST " + path},
            )

        endpoint: Endpoint | None = self._endpoints.get(rpc_method, None)
        if not endpoint:
            raise exceptions.TwirpServerException(
                code=errors.Errors.Unimplemented,
                message="service has no endpoint " + rpc_method,
                meta={"twirp_invalide_route": "POST " + path},
            )

        return endpoint

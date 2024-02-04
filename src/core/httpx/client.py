from typing import Any, Optional, Union

import orjson
from httpx import AsyncClient as _AsyncClient
from httpx import Request, Response, Timeout
from multipart.multipart import parse_options_header

from settings import TIMEOUT_SECHOND


class AsyncClient(_AsyncClient):

    def __init__(self, *args, timeout=Timeout(TIMEOUT_SECHOND), **kwargs):
        super().__init__(*args, timeout=timeout, **kwargs)

    @staticmethod
    def get_headers(input_: Union[Request, Response]) -> dict:
        return dict(input_.headers)

    @staticmethod
    def get_body(input_: Union[Request, Response]) -> Optional[Union[dict, str]]:
        context_type, _ = parse_options_header(input_.headers.get('Content-Type'))

        body: dict[str, Any] = {'raw': None, 'json': None, 'form': None}
        try:
            if context_type == b'application/json':
                body['json'] = orjson.loads(input_.content)  # pylint: disable=no-member
            else:
                body['raw'] = str(input_.content)
        except Exception:
            body['raw'] = str(input_.content)

        return body

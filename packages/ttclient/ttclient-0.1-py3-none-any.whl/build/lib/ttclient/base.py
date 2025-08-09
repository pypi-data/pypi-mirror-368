import logging
from contextlib import suppress

import httpx

from .exceptions import (InputDataError, NoAccessError, RedirectError,
                         ServerError, TooManyRequestsError, UnauthorizedError)


class BaseClient:
    __secret__: str = ''
    host: str = ''
    log = logging.getLogger('ttclient')

    def __init__(self, secret: str, host: str) -> None:
        self.__secret__ = secret
        self.host = f'https://{host}'

    def __repr__(self) -> str:
        return f'Client [{self.host}]' + (' with ' if self.__secret__ else ' no ') + 'secret'

    async def api_call(self, uri: str, method: str = 'GET', data: dict | None = None) -> dict:
        async with httpx.AsyncClient(headers={'X-APIToken': self.__secret__}) as client:
            result = {}
            resp = await client.request(method, f'{self.host}{uri}', json=data or {})
            self.log.info('API %s %s: %s', method, uri, resp.status_code)

            with suppress(Exception):
                result = resp.json()

            match resp.status_code:
                case 400:
                    raise InputDataError(f'{method} {uri} \n<- {data} \n-> {result}')
                case 401:
                    raise UnauthorizedError(f'{method} {uri} \n-> {result}')
                case 403:
                    raise NoAccessError(f'{method} {uri} \n<- {data} \n-> {result}')
                case 429:
                    raise TooManyRequestsError(f'{method} {uri}\n-> {result}')
                case 301 | 302:
                    raise RedirectError(f'{method} {uri}')
                case 500 | 502 | 503 | 504:
                    raise ServerError(f'{method} {uri} > HTTP{resp.status_code}')

            return result

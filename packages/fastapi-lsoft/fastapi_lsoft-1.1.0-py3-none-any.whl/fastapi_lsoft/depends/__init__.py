from asyncio import iscoroutinefunction
from typing import Callable

from starlette.requests import Request
from starlette.responses import Response


class CacheControlDepends:
    def __init__(
        self,
        max_age: int | None = None,
    ):
        self.max_age = max_age

    async def __call__(self, request: Request):
        request.state.lsoft_cache_control = {"max_age": self.max_age}

class EtagDepends:
    def __init__(
        self,
        etag_generator: Callable | None = lambda x: None,
    ):
        self.etag_generator = etag_generator

    async def __call__(self, request: Request, response: Response):
        # etag = (
        #     await self.etag_gen(response)  # type: ignore
        #     if iscoroutinefunction(self.etag_generator)
        #     else self.etag_generator(response)
        # )
        request.state.lsoft_etag_generator = self.etag_generator

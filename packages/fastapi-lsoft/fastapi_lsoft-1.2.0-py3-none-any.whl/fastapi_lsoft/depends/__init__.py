from asyncio import iscoroutinefunction
from typing import Callable

from starlette.requests import Request
from starlette.responses import Response


class CacheControlDepends:
    """
    Handles configuration of Cache-Control headers for HTTP requests.

    This class enables dynamic configuration of Cache-Control headers
    based on provided initialization parameters. It is intended for
    use in web frameworks for controlling caching behavior of responses.

    :ivar max_age: The maximum amount of time, in seconds, that a resource
        is considered fresh. If None is provided, there is no maximum age set.
    :type max_age: int or None
    :ivar stale_while_revalidate: Whether the client can use a stale cached resource
        while asynchronously updating the cache. Defaults to False.
    :type stale_while_revalidate: bool or None
    :ivar must_revalidate: Whether the client must revalidate the resource with the
        server before using the cached response. Defaults to False.
    :type must_revalidate: bool or None
    :ivar private: Indicates if the response is specific to an individual user and
        should not be cached by shared caches (e.g., proxies). Defaults to True.
    :type private: bool or None
    :ivar public: Indicates if the response can be cached by any cache, even if it
        has HTTP authentication or is otherwise non-cacheable by default. Defaults to False.
    :type public: bool or None
    """
    def __init__(
        self,
        max_age: int | None = None,
        stale_while_revalidate: bool | None = False,
        must_revalidate: bool | None = False,
        private: bool | None = True,
        public:  bool | None = False,

    ):
        self.max_age = max_age
        self.stale_while_revalidate = stale_while_revalidate
        self.must_revalidate = must_revalidate
        self.private = private
        self.public = public


    async def __call__(self, request: Request):
        request.state.lsoft_cache_control = {
            "max_age": self.max_age,
            "stale_while_revalidate": self.stale_while_revalidate,
            "must_revalidate": self.must_revalidate,
            "private": self.private,
            "public": self.public
        }

class EtagDepends:
    """
    Manages ETag generation and associates a generator callable with the request's state.

    This class facilitates the assignment of a custom ETag generator callable to a
    request, allowing dynamic or predefined ETag values to be generated and utilized
    for HTTP responses. This can be helpful in optimizing caching and verifying
    resource state consistency.

    :ivar etag_generator: Callable used to generate ETag values. Defaults to a lambda
        returning None.
    :type etag_generator: Callable | None
    """
    def __init__(
        self,
        etag_generator: Callable | None = lambda x: None,
    ):
        self.etag_generator = etag_generator

    async def __call__(self, request: Request, response: Response):
        request.state.lsoft_etag_generator = self.etag_generator

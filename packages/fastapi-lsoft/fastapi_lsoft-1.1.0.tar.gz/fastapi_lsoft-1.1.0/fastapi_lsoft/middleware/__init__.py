from asyncio import iscoroutinefunction

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class FastapiLsoftMiddleware(BaseHTTPMiddleware):
    """
    Middleware class for intercepting and manipulating HTTP request and response headers.

    This middleware is used to ensure that the original `cache-control` header value from
    the incoming HTTP request persists in the response. It intercepts requests and responses
    to modify the `cache-control` header if it was present in the incoming request headers.
    This can be used for scenarios where maintaining specific client-defined cache
    control policies is required.

    """
    async def dispatch(self, request: Request, call_next):
        request_cache_control = request.headers.get("cache-control")
        response = await call_next(request)
        cache_control = getattr(request.state, "lsoft_cache_control", None)
        etag_generator = getattr(request.state, "lsoft_etag_generator", None)

        if etag_generator is not None:
            etag = (
                await etag_generator(response)  # type: ignore
                if iscoroutinefunction(etag_generator)
                else etag_generator(response)
            )
            response.headers["etag"] = etag

        if cache_control is not None and request_cache_control is None:
            cache_control_list = []
            max_age = cache_control.get("max_age")
            if max_age is not None:
                cache_control_list.append(f"max-age={cache_control.get('max_age')}")

            if len(cache_control_list) > 0:
                response.headers["cache-control"] = ",".join(cache_control_list)

        if request_cache_control is not None:
            response.headers["cache-control"] = request_cache_control

        return response

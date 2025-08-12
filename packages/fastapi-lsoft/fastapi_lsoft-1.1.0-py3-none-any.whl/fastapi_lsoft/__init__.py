import functools
import logging
import datetime

from pydantic import BaseModel
from starlette.responses import JSONResponse, Response

log = logging.getLogger(__name__)

def cache_control(max_age: int | None = None):
    """
    A decorator function that applies a specific Cache-Control header to the response returned by
    an asynchronous FastAPI route handler. It accepts an optional `max_age` parameter that specifies
    the maximum age, in seconds, for the cached resource.

    :param max_age: Optional maximum age for the cache, in seconds. If not provided,
                    the cache control will be handled without this directive.
    :type max_age: int | None
    :return: An asynchronous decorator for a FastAPI route handler that wraps the handler
             with the desired Cache-Control logic.
    :rtype: Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Response]]]
    """
    def decorator(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            func._fastapi_lsoft_cache_control_max_age = max_age
            ret = await func(*args, **kwargs)
            if not isinstance(ret, Response):
                if isinstance(ret, BaseModel):
                    ret = ret.model_dump()
                response = JSONResponse(ret)
            else:
                response = ret

            cache_control_list = []
            if max_age is not None:
                cache_control_list.append(f"max-age={max_age}")

            if len(cache_control_list) > 0:
                cache_control_string = ",".join(cache_control_list)
                response.headers["Cache-Control"] = cache_control_string
            return response

        return inner

    return decorator

def etag(max_age: int | None = None):
    def decorator(func):
        @functools.wraps(func)
        async def inner(*args, **kwargs):
            etag, ret = await func(*args, **kwargs)
            print("etag", etag, "ret", ret)

            if not isinstance(ret, Response):
                if isinstance(ret, BaseModel):
                    ret = ret.model_dump()
                response = JSONResponse(ret)
            else:
                response = ret


            return response
        return inner
    return decorator


def next_midnight(tz_info: datetime.tzinfo = None):
    dt = datetime.datetime.now(tz_info)
    dt = dt.replace(hour=0, minute=0, second=0)
    return dt + datetime.timedelta(days=1)



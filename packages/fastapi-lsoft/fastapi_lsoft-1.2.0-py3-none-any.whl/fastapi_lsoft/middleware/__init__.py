from asyncio import iscoroutinefunction

import lsjsonclasses
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from fastapi_lsoft import cache_control_to_dict, cache_control_to_string


class FastapiLsoftMiddleware(BaseHTTPMiddleware):
    """
    Middleware for handling ETag and Cache-Control headers for HTTP requests
    and responses. This middleware modifies response headers based on request
    state and ensures proper caching and validation mechanisms are followed.

    :ivar request: The incoming HTTP request object containing headers and state.
    :type request: Request
    :ivar response: The HTTP response object with headers to be modified.
    :type response: Response
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)



        response = await self.handle_etag(request, response)
        response = await self.handle_cache_control(request, response)
        return response

    async def handle_cache_control(self, request: Request, response: Response)->Response:
        """
        Handles the setting of the `cache-control` header for a given HTTP response based
        on the request's `cache-control` header and current response status.

        This function processes the incoming request's `cache-control` header, merges it
        appropriately with the server-internal cache control settings stored in the request
        state, and updates the outgoing response's `cache-control` header accordingly. If the
        response indicates a failure (status code 400 or higher), the `cache-control` header
        is forcefully set to "no-cache".

        :param request: The incoming HTTP request. Must include state and headers containing
            cache control information.
        :type request: Request
        :param response: The outgoing HTTP response. Headers in this response will be updated
            with the calculated `cache-control` string.
        :type response: Response
        :return: The modified HTTP response with updated `cache-control` headers.
        :rtype: Response
        """
        cache_control = getattr(request.state, "lsoft_cache_control", {})
        request_cache_control = cache_control_to_dict(request.headers.get("cache-control", ""))


        if response.status_code < 400:
            # only modify cache-control header if response is successful

            # merge cache-control headers from request and response
            new_cache_control = cache_control | request_cache_control
            cache_control_string = cache_control_to_string(new_cache_control)
            if len(cache_control_string) > 0:
                response.headers["cache-control"] = cache_control_string

        else:
            # if response is not successful, set the cache-control header to no-cache
            response.headers["cache-control"] = "no-cache"

        return response

    async def handle_etag(self, request: Request, response: Response)->Response:
        """
        Handles ETag processing for a given HTTP request and response. Ensures
        efficient caching mechanisms by generating ETag for the response body,
        comparing it with the client's ETag, and returning a 304 status code if
        there is a match. Updates the cache-control headers accordingly based
        on the request's state.

        :param request: The incoming HTTP request object.
        :type request: Request
        :param response: The outgoing HTTP response object.
        :type response: Response
        :return: The modified HTTP response object, potentially with updated
            ETag and cache-control headers or a status code of 304 if the ETag
            matches.
        :rtype: Response
        """
        etag_generator = getattr(request.state, "lsoft_etag_generator", None)
        if etag_generator is not None:
            json_body = await self.get_json_body(response)
            # gererate etag
            etag = (
                await etag_generator(json_body)  # type: ignore
                if iscoroutinefunction(etag_generator)
                else etag_generator(json_body)
            )
            response.headers["etag"] = etag

            # update cache-control headers
            request.state.lsoft_cache_control = getattr(request.state, "lsoft_cache_control", {}) | {
                # "must-revalidate": True,
                # "stale-while-revalidate": True,
                "private": True
            }

            # return 304 if etag matches
            request_etag = request.headers.get("if-none-match", "")
            if request_etag == etag:
                return Response(status_code=304)

        return response

    async def get_json_body(self, response: Response)->dict|None:
        """
        Parses the JSON body from an HTTP response if it has a content type of
        "application/json". This function processes the response body in an
        asynchronous manner, ensuring all chunks are decoded and joined before
        parsing the JSON content.

        :param response: The HTTP response object to extract the JSON body from.
        :type response: Response
        :return: Parsed JSON content as a dictionary, or None if the content type
                 is not "application/json".
        :rtype: dict | None
        """
        if response.headers.get("content-type") != "application/json":
            return None
        response_body = [chunk async for chunk in response.body_iterator]

        # important the iterator has to be rebuild using iterate_in_threadpool for later usage,
        # because iterators can only be used once, and we used it already.
        response.body_iterator = iterate_in_threadpool(iter(response_body))

        # decode body
        json_body = lsjsonclasses.LSoftJSONDecoder.loads("".join([chunk.decode("utf8") for chunk in response_body]))
        return json_body




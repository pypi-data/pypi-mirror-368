import copy
import logging
from typing import Any, Callable, Iterator, Optional

import httpx
import pydantic

from fastcrawl import models
from fastcrawl.core import type_validation
from fastcrawl.core.component import Component


class Crawler:
    """FastCrawl crawler.

    Crawler must be included in the FastCrawl application.
    Several crawlers in one application can be used to crawl different websites
    or different parts of the same website.

    Args:
        name (str): Name of the crawler.
        http_settings (Optional[models.HttpSettings]): HTTP settings for the crawler.
            Note that the crawler HTTP settings are merged with the application HTTP settings.
            Application HTTP settings are considered as a base for the crawler HTTP settings.
            Provided HTTP settings will override the application HTTP settings for the crawler.
            If not provided, default HTTP settings will be used. Defaults to None.

    """

    name: str
    logger: logging.Logger

    _handlers: dict[Callable, Component]
    _pipelines: list[Component]
    _start_requests: list[models.Request]
    _http_settings: models.HttpSettings
    _cached_http_client: Optional[httpx.AsyncClient]

    def __init__(self, name: str, http_settings: Optional[models.HttpSettings] = None) -> None:
        self.name = name
        self.logger = logging.getLogger(name)

        self._handlers = {}
        self._pipelines = []
        self._start_requests = []
        self._http_settings = http_settings or models.HttpSettings()
        self._cached_http_client = None

    def _merge_settings(self, app_http_settings: models.HttpSettings) -> None:
        """Merges the application HTTP settings with the crawler HTTP settings.

        Args:
            app_http_settings (models.HttpSettings): Application HTTP settings to merge with the crawler HTTP settings.

        """
        self._http_settings = app_http_settings.model_copy(update=self._http_settings.model_dump(exclude_unset=True))

    @property
    def _http_client(self) -> httpx.AsyncClient:
        if not self._cached_http_client:
            kwargs = self._http_settings.model_dump()
            kwargs["params"] = kwargs.pop("query_params")
            kwargs["trust_env"] = False
            kwargs["limits"] = httpx.Limits(
                max_connections=kwargs.pop("max_connections"),
                max_keepalive_connections=kwargs.pop("max_keepalive_connections"),
                keepalive_expiry=kwargs.pop("keepalive_expiry"),
            )
            self._cached_http_client = httpx.AsyncClient(**kwargs)
        return self._cached_http_client

    def handler(self, *urls: str) -> Callable:
        """Handler that processes HTTP responses.

        Requirements for each handler:
            - Must have type annotations for its arguments and return value.
            - Must have an argument `response` of type `fastcrawl.Response`.
            - Can return or yield item(s) or new request(s).
            - Items must be instances of pydantic models.
            - Requests must be instances of `fastcrawl.Request`.

        Args:
            urls (str): URLs to handle. Can be a single string or multiple strings.
                If provided, URLs will be used to create initial requests
                and will be processed by the handler.

        Raises:
            TypeError: If any URL is not a string.

        """

        def decorator(func: Callable) -> Callable:
            self._handlers[func] = Component(
                func=func,
                expected_arg=type_validation.FuncArg(name="response", types=(models.Response,)),
                expected_return_type=type_validation.FuncReturnType(
                    is_iterator=True,
                    types=(pydantic.BaseModel, models.Request, type(None)),
                ),
            )
            for url in urls:
                if not isinstance(url, str):
                    raise TypeError(f"URL must be a string, got {type(url)}")
                self._start_requests.append(models.Request(url=url, handler=func))
            return func

        return decorator

    def pipeline(self, priority: Optional[int] = None) -> Callable:
        """Pipeline that processes items.

        Requirements for each pipeline:
            - Must have type annotations for its arguments and return value.
            - Must have an argument `item` which is a pydantic model.
                The model you specify will be the expected item type for the pipeline.
                If pipeline got an item not of the expected type, item processing will be skipped.
            - Can return processed item or None if no further processing is needed.

        Args:
            priority (Optional[int]): Priority of the pipeline.
                Must be a non-negative integer. If not provided, the pipeline
                will be added to the end of the list. Defaults to None.

        Raises:
            TypeError: If priority is not a non-negative integer.

        """

        def decorator(func: Callable) -> Callable:
            if priority is not None and (not isinstance(priority, int) or priority < 0):
                raise TypeError("Priority must be a non-negative integer.")

            component = Component(
                func=func,
                expected_arg=type_validation.FuncArg(name="item", types=(pydantic.BaseModel,)),
                expected_return_type=type_validation.FuncReturnType(
                    is_iterator=False,
                    types=(pydantic.BaseModel, type(None)),
                ),
            )
            if priority is None:
                self._pipelines.append(component)
            else:
                self._pipelines.insert(priority, component)

            return func

        return decorator

    async def _close(self) -> None:
        """Closes the HTTP client."""
        if self._cached_http_client and not self._cached_http_client.is_closed:
            await self._cached_http_client.aclose()

    async def _process_request(self, request: models.Request) -> models.Response:
        request_kwargs = request.model_dump(exclude_none=True, exclude={"handler"})
        if "query_params" in request_kwargs:
            request_kwargs["params"] = request_kwargs.pop("query_params")
        if "form_data" in request_kwargs:
            request_kwargs["data"] = request_kwargs.pop("form_data")
        if "json_data" in request_kwargs:
            request_kwargs["json"] = request_kwargs.pop("json_data")
        httpx_response = await self._http_client.request(**request_kwargs)
        response = await models.Response.from_httpx_response(httpx_response, request)
        self.logger.debug("Got response: %s", response)
        return response

    def _process_response(self, response: models.Response) -> Iterator[Any]:
        handler = self._handlers[response.request.handler]
        for result in handler.run_iter(response=response):
            if result is not None:
                yield result

    def _process_item(self, item: Any) -> None:
        processed_item = copy.deepcopy(item)
        for pipeline in self._pipelines:
            if not pipeline.is_value_match_to_arg(processed_item):
                continue
            processed_item = pipeline.run(item=processed_item)
            if not processed_item:
                break

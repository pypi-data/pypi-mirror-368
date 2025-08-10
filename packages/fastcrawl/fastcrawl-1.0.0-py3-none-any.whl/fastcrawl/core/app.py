import asyncio
import dataclasses
import logging
from typing import Any, Callable, Optional

from fastcrawl import models
from fastcrawl.core.crawler import Crawler


@dataclasses.dataclass(frozen=True)
class Task:
    """Task to be processed by the FastCrawl application.

    Attributes:
        crawler_name (str): Name of the crawler that will process this task.
        target (Any): The target of the task, which can be a request, response, or item.

    """

    crawler_name: str
    target: Any


class FastCrawl:
    """FastCrawl application.

    Args:
        name (str): Name of the application. Defaults to "FastCrawl".
        app_settings (Optional[models.AppSettings]): Application settings.
            If not provided, default settings will be used. Defaults to None.
        logging_settings (Optional[models.LoggingSettings]): Logging settings for the application.
            If not provided, default logging settings will be used. Defaults to None.
        http_settings (Optional[models.HttpSettings]): HTTP settings for the application.
            If not provided, default HTTP settings will be used. Defaults to None.
        crawlers (Optional[list[Crawler]]): List of crawlers to include in the application.
            Defaults to None, meaning no crawlers are included initially (except the main crawler).

    """

    name: str
    logger: logging.Logger
    crawlers: dict[str, Crawler]

    _app_settings: models.AppSettings
    _http_settings: models.HttpSettings
    _task_queue: asyncio.Queue[Task]

    def __init__(
        self,
        name: str = "FastCrawl",
        app_settings: Optional[models.AppSettings] = None,
        logging_settings: Optional[models.LoggingSettings] = None,
        http_settings: Optional[models.HttpSettings] = None,
        crawlers: Optional[list[Crawler]] = None,
    ) -> None:
        self.name = name
        self.logger = logging.getLogger(name)

        self._app_settings = app_settings or models.AppSettings()
        self._http_settings = http_settings or models.HttpSettings()
        self._setup_logging(logging_settings or models.LoggingSettings())

        self._task_queue = asyncio.Queue()
        self.crawlers = {self.name: Crawler(name=self.name, http_settings=self._http_settings.model_copy(deep=True))}

        if crawlers:
            for crawler in crawlers:
                self.include_crawler(crawler)

    def _setup_logging(self, logging_settings: models.LoggingSettings) -> None:
        if logging_settings.configure_globally:
            logging.basicConfig(level=logging_settings.level, format=logging_settings.format)

        logging.getLogger("asyncio").setLevel(logging_settings.level_asyncio)
        logging.getLogger("httpx").setLevel(logging_settings.level_httpx)
        logging.getLogger("httpcore").setLevel(logging_settings.level_httpcore)

    def include_crawler(self, crawler: Crawler) -> None:
        """Includes a crawler in the FastCrawl application.

        Args:
            crawler (Crawler): Crawler to include in the application.

        Raises:
            ValueError: If the crawler name is the same as the application name.
            ValueError: If a crawler with the same name already exists in the application.

        """
        if crawler.name == self.name:
            raise ValueError("Crawler name cannot be the same as the application name.")
        if crawler.name in self.crawlers:
            raise ValueError(f"Crawler with name '{crawler.name}' already exists.")
        crawler._merge_settings(self._http_settings)
        self.crawlers[crawler.name] = crawler

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
        return self.crawlers[self.name].handler(*urls)

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
        return self.crawlers[self.name].pipeline(priority)

    async def run(self, crawler_name: Optional[str] = None) -> None:
        """Runs the FastCrawl application.

        Args:
            crawler_name (Optional[str]): Name of the crawler to run.
                If you want to run only application's main crawler, provide name of the application.
                If None, all crawlers will be run including the main crawler. Defaults to None.

        Raises:
            ValueError: If the specified crawler name does not exist in the application.

        """
        if crawler_name and crawler_name not in self.crawlers:
            raise ValueError(f"Crawler with name '{crawler_name}' does not exist.")
        await self._init_tasks(crawler_name)

        workers = [asyncio.create_task(self._worker()) for _ in range(self._app_settings.workers)]
        await self._task_queue.join()
        for worker in workers:
            worker.cancel()

        for crawler in self.crawlers.values():
            await crawler._close()

    async def _init_tasks(self, crawler_name: Optional[str] = None) -> None:
        if crawler_name:
            for request in self.crawlers[crawler_name]._start_requests:
                task = Task(crawler_name=crawler_name, target=request)
                await self._task_queue.put(task)
        else:
            for crawler in self.crawlers.values():
                for request in crawler._start_requests:
                    task = Task(crawler_name=crawler.name, target=request)
                    await self._task_queue.put(task)

    async def _worker(self) -> None:
        while True:
            task = await self._task_queue.get()
            try:
                await self._process_task(task)
            except Exception:
                self.logger.exception("Error processing task: %s", task)
            self._task_queue.task_done()

    async def _process_task(self, task: Task) -> None:
        crawler = self.crawlers[task.crawler_name]
        if isinstance(task.target, models.Request):
            response = await crawler._process_request(task.target)
            await self._task_queue.put(Task(crawler_name=task.crawler_name, target=response))
        elif isinstance(task.target, models.Response):
            for target in crawler._process_response(task.target):
                await self._task_queue.put(Task(crawler_name=task.crawler_name, target=target))
        else:
            crawler._process_item(task.target)

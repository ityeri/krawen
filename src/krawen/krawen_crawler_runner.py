import asyncio
import logging
from asyncio import Task

from krawen import EndpointPath, HTTPMethod
from krawen import KrawenCrawler
from krawen.exceptions import URLOutOfBoundError, URLNotAbsoluteError


class KrawenCrawlerRunner:
    def __init__(
            self,
            crawler: KrawenCrawler,
            root_requests: set[EndpointPath],
            tick_interval: float = 0.1
    ):
        self.crawler: KrawenCrawler = crawler
        self.tick_interval: float = tick_interval
        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        self.waiting_requests: set[EndpointPath] = root_requests
        self.running_tasks: set[Task] = set()

    async def init(self):
        await self.crawler.start()
    async def stop(self):
        await self.crawler.stop()

    async def __aenter__(self):
        await self.start()
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def processing_request(self, endpoint_path: EndpointPath):
        try:
            response_info = await self.crawler.download(endpoint_path)
        except URLOutOfBoundError:
            self.logger.error(f'Url "{endpoint_path.url}" is out of bound')
            return
        except URLNotAbsoluteError:
            self.logger.error(f'Url "{endpoint_path.url}" is not absolute')
            return

        if self.crawler.is_page(response_info):
            # sub_requests = await crawler.get_network_requests(endpoint_path.url)
            sub_urls = await self.crawler.get_page_sub_urls(endpoint_path.url)

            new_found_requests = [
                EndpointPath(url=url, method=HTTPMethod.GET) for url in sub_urls
            ]

            self.waiting_requests.update(new_found_requests)

    async def start(self):
        while True:
            for endpoint_path in self.waiting_requests:
                task = asyncio.create_task(self.processing_request(endpoint_path))
                task.add_done_callback(self.running_tasks.discard)

                self.running_tasks.add(task)

            started_tasks = len(self.waiting_requests)
            self.waiting_requests.clear()

            self.logger.info(f'{started_tasks} tasks are started')
            self.logger.info(f'{len(self.running_tasks)} tasks are currently running')

            await asyncio.sleep(self.tick_interval)

import asyncio
import logging
from asyncio import Task
from itertools import islice

from krawen import EndpointPath, HTTPMethod
from krawen import KrawenCrawler
from krawen.exceptions import URLOutOfBoundError, URLNotAbsoluteError
from krawen.utils import to_absolute_url, is_valid_url


class KrawenCrawlerRunner:
    def __init__(
            self,
            crawler: KrawenCrawler,
            seed_endpoint_paths: set[EndpointPath],
            tick_interval: float = 0.5,
            exists_skip: bool = True,
            max_tasks: int | None = None
    ):
        self.crawler: KrawenCrawler = crawler
        self.tick_interval: float = tick_interval
        self.exists_skip: bool = exists_skip
        self.max_tasks: int | None = max_tasks

        self.logger: logging.Logger = logging.getLogger(self.__class__.__name__)

        self.pending_endpoint_paths: set[EndpointPath] = seed_endpoint_paths
        self.running_tasks: set[Task] = set()

    async def init(self):
        await self.crawler.init()
    async def stop(self):
        await self.crawler.stop()

    async def __aenter__(self):
        await self.init()
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()

    async def processing_endpoint_path(self, endpoint_path: EndpointPath):
        if await self.crawler.is_exists(endpoint_path):
            self.logger.warning(f'Url "{endpoint_path.url}" is already exists. skip download')
        else:
            await self.crawler.download(endpoint_path)

            response_info = await self.crawler.get_response_info(endpoint_path) # TODO test, commi

            if self.crawler.is_page(response_info):
                # sub_requests = await crawler.get_network_requests(endpoint_path.url)
                sub_urls = await self.crawler.get_page_sub_urls(endpoint_path.url)

                new_endpoint_paths = [
                    EndpointPath(
                        url=to_absolute_url(endpoint_path.url, url),
                        method=HTTPMethod.GET
                    ) for url in sub_urls
                    if is_valid_url(to_absolute_url(endpoint_path.url, url))
                ]

                self.pending_endpoint_paths.update([
                    endpoint_path
                    for endpoint_path in new_endpoint_paths
                    if not await self.crawler.is_exists(endpoint_path)
                ])

    async def processing_endpoint_path_wrap(self, endpoint_path: EndpointPath):
        try:
            await self.processing_endpoint_path(endpoint_path)
        except URLOutOfBoundError:
            pass
        except URLNotAbsoluteError:
            self.logger.error(f'Url "{endpoint_path.url}" is not absolute')
        except asyncio.TimeoutError:
            self.logger.error(f'Request for url "{endpoint_path.url}" is timed out')
        except Exception as e:
            self.logger.exception(f'Unknown error occurred while processing endpoint "{endpoint_path.url}": ')

    async def run(self):
        while True:
            if self.max_tasks is None:
                for endpoint_path in self.pending_endpoint_paths:
                    task = asyncio.create_task(self.processing_endpoint_path_wrap(endpoint_path))
                    self.running_tasks.add(task)
                    task.add_done_callback(lambda t: self.running_tasks.discard(t))

                started_tasks = len(self.pending_endpoint_paths)
                self.pending_endpoint_paths.clear()

            else:
                new_task_nums = self.max_tasks - len(self.running_tasks)

                if 0 < new_task_nums:
                    staged_endpoint_paths = set(islice(self.pending_endpoint_paths, new_task_nums))

                    for endpoint_path in staged_endpoint_paths:
                        task = asyncio.create_task(self.processing_endpoint_path_wrap(endpoint_path))
                        self.running_tasks.add(task)
                        task.add_done_callback(lambda t: self.running_tasks.discard(t))

                    started_tasks = len(staged_endpoint_paths)
                    self.pending_endpoint_paths -= staged_endpoint_paths

                else:
                    started_tasks = 0

            self.logger.info(f'{len(self.pending_endpoint_paths)} tasks are waiting')
            self.logger.info(f'{started_tasks} tasks are started')
            self.logger.info(f'{len(self.running_tasks)} tasks are currently running')

            await asyncio.sleep(self.tick_interval)

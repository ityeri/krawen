import argparse
import asyncio
import os

import reger
from yarl import URL

from krawen import KrawenCrawler, EndpointPath, HTTPMethod
from krawen.async_file_store import AsyncLocalFileStore
from krawen.endpoint_store import JsonEndpointStore
from krawen.krawen_crawler_runner import KrawenCrawlerRunner


async def run_autosave(json_store: JsonEndpointStore, interval: float):
    while True:
        await json_store.save(indent=4)
        await asyncio.sleep(interval)


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'seed_urls', help='Seed url', nargs='+'
    )
    parser.add_argument(
        '-t', '--target',
        help='Crawling target url', default=None, nargs='?'
    )
    parser.add_argument(
        '-d', '--dir',
        help='Directory path of working dir (must contain endpoints.json, store/ dir)', default='./', nargs='?'
    )
    parser.add_argument(
        '--save-interval', type=float,
        help='Autosave interval', default=1, nargs='?'
    )
    parser.add_argument(
        '--tick-interval', type=float,
        help='Crawler tick interval', default=0.5, nargs='?'
    )
    parser.add_argument(
        '-m', '--max-tasks', type=int,
        help='Max tasks that can executing concurrently. (0 is no limit)', default=2024, nargs='?'
    )
    args = parser.parse_args()

    seed_urls = map(URL, args.seed_urls)
    root_origin_url = URL(args.target) if args.target is not None else None
    working_dir = args.dir
    autosave_interval = args.save_interval
    tick_interval = args.tick_interval
    max_tasks = args.max_tasks if args.max_tasks != 0 else None

    store_path = os.path.join(working_dir, 'store/')
    json_file_path = os.path.join(working_dir, 'endpoints.json')

    os.makedirs(store_path, exist_ok=True)
    if not os.path.exists(json_file_path):
        with open(json_file_path, 'w', encoding='utf-8') as f:
            f.write('{}')

    file_store = AsyncLocalFileStore(store_path)
    endpoint_store = JsonEndpointStore(json_file_path, file_store=file_store)
    crawler = KrawenCrawler(endpoint_store=endpoint_store, root_origin_url=root_origin_url)
    crawler_runner = KrawenCrawlerRunner(
        crawler,
        seed_endpoint_paths={EndpointPath(URL(seed_url), HTTPMethod.GET) for seed_url in seed_urls},
        tick_interval=tick_interval,
        max_tasks=max_tasks
    )

    reger.setup_logging()
    await endpoint_store.load()

    async with crawler_runner:
        crawling_task = asyncio.create_task(crawler_runner.run())
        autosave_task = asyncio.create_task(run_autosave(endpoint_store, autosave_interval))

        await crawling_task
        autosave_task.cancel()


__all__ = [
    'main',
    'run_autosave'
]

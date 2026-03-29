import argparse
import os.path

import reger
from yarl import URL

from krawen import KrawenMirrorServer
from krawen.async_file_store import AsyncLocalFileStore
from krawen.endpoint_store import JsonEndpointStore


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root_origin_url', help='Root url of mirror server')
    parser.add_argument(
        '-d', '--dir',
        help='Directory path of working dir (must contain endpoints.json, store/ dir)', default='./', nargs='?'
    )
    args = parser.parse_args()

    root_origin_url = URL(args.root_origin_url)
    working_dir = args.dir

    file_store = AsyncLocalFileStore(os.path.join(working_dir, 'store/'))
    endpoint_store = JsonEndpointStore(os.path.join(working_dir, 'endpoints.json'), file_store=file_store)
    mirror_server = KrawenMirrorServer(
        root_origin_url=root_origin_url,
        endpoint_store=endpoint_store
    )

    reger.setup_logging()
    await endpoint_store.load()
    mirror_server.setup()

    await mirror_server.run()


__all__ = [
    'main'
]
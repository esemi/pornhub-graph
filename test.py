#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from collections import Counter

import asyncio
import aiohttp
import itertools
from async_timeout import timeout


START_VIDEO_HASH = 'ph5a7f1ba584481'
TIMEOUT = 10
MAX_CONCURRENT_CLIENTS = 2
DEPTH = 2
URL_TEMPLATE = 'https://www.pornhub.com/view_video.php?viewkey=%s'

# todo save graph as graph


async def task(hash: str, sem: asyncio.Semaphore, cnt: Counter) -> set:
    out = set()
    url = URL_TEMPLATE % hash
    logging.info('fetch %s url', url)
    async with sem:
        async with aiohttp.ClientSession() as session:
            try:
                async with timeout(TIMEOUT):
                    async with session.get(url) as resp:
                        code = resp.status
                        cnt[code] += 1
                        logging.info('fetch %s url code %s', url, code)
                        # todo parse videos
            except BaseException as e:
                cnt['exception'] += 1
                logging.info('fetch %s url exception %s', url, type(e))
    return out


async def run():
    current_depth = 0
    sem = asyncio.Semaphore(MAX_CONCURRENT_CLIENTS)
    cnt = Counter()
    videos_per_level = dict()
    video_hashes = {START_VIDEO_HASH}

    while current_depth <= DEPTH and len(video_hashes):
        logging.info('start %d level crawling (%d videos)', current_depth, len(video_hashes))
        tasks = [asyncio.ensure_future(task(hash, sem, cnt)) for hash in video_hashes]
        results = await asyncio.gather(*tasks)
        video_hashes = list(itertools.chain(*results))
        videos_per_level[current_depth] = video_hashes
        logging.info('end %d level crawling (%d videos found)', current_depth, len(video_hashes))
        current_depth += 1

    logging.info('end with counters %s', cnt.items())


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    ioloop = asyncio.new_event_loop()
    ioloop.run_until_complete(run())
    ioloop.close()

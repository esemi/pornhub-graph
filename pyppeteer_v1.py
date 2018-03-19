#! /usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from collections import Counter
import asyncio

from pyppeteer import launch
import lxml.html as l


START_VIDEO_HASH = 'ph59fcf23b6203e'
TIMEOUT = 20
DEPTH = 1
MAX_CONCURRENT_CLIENTS = 1
URL_TEMPLATE = 'https://www.pornhub.com/view_video.php?viewkey=%s'

# todo save result as graph
_BROWSER = None


def parse_similar_videos(source_html) -> set:
    doc = l.document_fromstring(source_html)
    return {r.get('_vkey') for r in doc.xpath('//ul[@id="relatedVideosCenter"]/li[@_vkey]') if len(r.get('_vkey')) == 15}


async def fetch_many(concurrency: int, video_hashes: set, cnt: Counter=None) -> tuple:
    global _BROWSER
    if _BROWSER is None:
        _BROWSER = await launch()
    if cnt is None:
        cnt = Counter()
    page = await _BROWSER.newPage()
    hash_buffer = []
    for hash in video_hashes:
        res = await _task(hash, page, cnt)
        hash_buffer += list(res)
    video_hashes = set(hash_buffer)
    return video_hashes, {}


async def _task(hash: str, page, cnt: Counter) -> set:
    out = set()
    url = URL_TEMPLATE % hash
    logging.info('fetch %s url', url)
    try:
        resp = await page.goto(url, timeout=TIMEOUT * 1000)
        code = resp.status
        cnt[code] += 1
        logging.info('fetch %s url code %s', url, code)
        if code == 200:
            try:
                await page.waitForSelector('head > title', timeout=TIMEOUT * 1000)
                response_content = await resp.text()
                result = parse_similar_videos(response_content)
                if result:
                    logging.info('parse %s url: found %d hashes', url, len(result))
                    out = out | result
                else:
                    logging.info('parse %s url: not found hashes', url)
                    cnt['similar_not_found'] += 1
            except Exception as e:
                cnt['exception_parse'] += 1
                logging.info('parse %s url exception %s', url, type(e))
                logging.exception(e)
    except Exception as e:
        cnt['exception_fetch'] += 1
        logging.info('fetch %s url exception %s', url, type(e))

    return out


async def run():
    current_depth = 0
    cnt = Counter()
    videos_per_level = dict()
    video_hashes = {START_VIDEO_HASH}

    while current_depth <= DEPTH and len(video_hashes):
        logging.info('start %d level crawling (%d videos)', current_depth, len(video_hashes))

        video_hashes, _ = await fetch_many(MAX_CONCURRENT_CLIENTS, video_hashes, cnt)
        videos_per_level[current_depth] = video_hashes

        logging.info('end %d level crawling (%d videos found)', current_depth, len(video_hashes))
        current_depth += 1

    logging.info('end with counters %s', cnt.items())
    try:
        await asyncio.sleep(TIMEOUT)
        await _BROWSER.close()
    except:
        pass


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    ioloop = asyncio.new_event_loop()
    ioloop.run_until_complete(run())
    ioloop.close()

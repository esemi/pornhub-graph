#! /usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import lxml.html as l
import math
import time
from collections import Counter
from pyppeteer import launch
from pyppeteer.element_handle import ElementHandle
from typing import Optional

from storage import S
from utils import get_default_arg_parser, fetch_current_top

TIMEOUT = 25
URL_TEMPLATE = 'https://www.pornhub.com/view_video.php?viewkey=%s'
MAX_TRIES_PARSE = 10
DEBUG = False

_BROWSER = None


async def parse_title(title: ElementHandle) -> Optional[str]:
    json_title = await (await title.getProperty('innerHTML')).jsonValue()
    return str(json_title).replace(' - Pornhub.com', '')


def parse_similar_videos(source_html) -> set:
    doc = l.document_fromstring(source_html)
    return {r.get('_vkey') for r in doc.xpath('//ul[@id="relatedVideosCenter"]/li[@_vkey]') if len(r.get('_vkey')) == 15}


async def crawl_many_videos_pool(concurrency: int, video_hashes, cnt: Counter=None):
    global _BROWSER
    if _BROWSER is None:
        _BROWSER = await launch(headless=not DEBUG, ignoreHTTPSErrors=False, executablePath='/usr/bin/google-chrome-stable')
    if cnt is None:
        cnt = Counter()

    async def pool_task(video_hashes: list, cnt: Counter):
        page = await _BROWSER.newPage()
        for current_video, level in video_hashes:
            relations, title = await crawl_one(current_video, page, cnt)
            if relations:
                for r in relations:
                    await S.add_video_hash(r, level + 1)
                await S.mark_video_as_parsed(current_video, title, relations)
            else:
                await S.mark_video_as_parsed_fail(current_video)
        await page.close()

    video_hashes = list(video_hashes)
    chunk_size = round(math.ceil(len(video_hashes) / min(len(video_hashes), concurrency)))
    tasks = [pool_task(video_hashes[i:i + chunk_size], cnt) for i in range(0, len(video_hashes), chunk_size)]
    await asyncio.gather(*tasks)


async def crawl_one(hash: str, page, cnt: Counter) -> tuple:
    out = set()
    title = None
    url = URL_TEMPLATE % hash
    logging.info('fetch %s url', url)
    try:
        resp = await page.goto(url, timeout=TIMEOUT * 1000)
        code = resp.status
        cnt['code%d' % code] += 1
        logging.info('fetch %s url code %s', url, code)

        # todo wait js block end before continue

        if code == 429:
            await asyncio.sleep(TIMEOUT)
        elif code == 200:
            try:
                title_elem = await page.waitForSelector('head > title', timeout=TIMEOUT * 1000)
                title = await parse_title(title_elem)
                response_content = await resp.text()
                result = parse_similar_videos(response_content)
                if not result:
                    logging.warning('parse %s url: not found hashes', url)
                    cnt['similar_not_found'] += 1
                elif not title:
                    logging.warning('parse %s url: not found title', url)
                    cnt['title_not_found'] += 1
                else:
                    logging.info('parse %s url: found %d hashes', url, len(result))
                    cnt['success'] += 1
                    cnt['found'] += len(result)
                    out = out | result
            except Exception as e:
                cnt['exception_parse'] += 1
                logging.warning('parse %s url exception %s %s', url, type(e), str(e))
    except Exception as e:
        cnt['exception_fetch'] += 1
        logging.warning('fetch %s url exception %s %s', url, type(e), str(e))

    return out, title


async def run(max_iterations: int=100, batch_size: int=100, concurrent: int=10):
    start_time = time.time()
    S.set_io_loop(asyncio.get_event_loop())
    cnt = Counter()

    logging.info('crawling start %s', (max_iterations, batch_size, concurrent))
    iter_num = 1
    while iter_num <= max_iterations:
        videos_for_parsing = await S.get_videos_for_parsing(batch_size, MAX_TRIES_PARSE)
        logging.info('start %d crawling iteration (%d videos)', iter_num, len(videos_for_parsing))
        if not len(videos_for_parsing):
            break

        await crawl_many_videos_pool(concurrent, videos_for_parsing, cnt)
        logging.info('end %d crawling iteration (%s)', iter_num, cnt.items())
        iter_num += 1

    logging.info('crawling end %s %.2fsec', cnt.items(), time.time() - start_time)
    try:
        await asyncio.sleep(5)
        await _BROWSER.close()
    except:
        pass


async def main(top_limit: int, reset: bool=False, continue_mode: bool=False, **kwargs):
    S.set_io_loop(asyncio.get_event_loop())
    if reset:
        await S.drop_all()

    if not continue_mode:
        video_hashes = fetch_current_top(top_limit)
        logging.info('fetch top%d videos (%s)', top_limit, video_hashes)
        for i in video_hashes:
            await S.add_video_hash(i)

    await run(**kwargs)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

    parser = get_default_arg_parser()
    parser.add_argument('top_limit', action='store', type=int, help='top limit value')
    parser.add_argument('--continue', action='store_true', dest='continue_mode', help='continue mode')
    args = parser.parse_args()

    ioloop = asyncio.new_event_loop()
    ioloop.run_until_complete(main(**args.__dict__))
    ioloop.close()
#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import asyncio
import random

import aiohttp

from storage import S


WAIT_SEC = 10
PROXY = [None,
         # 'http://183.111.169.207:3128',
         # 'http://54.157.185.100:10000',
         # 'http://185.92.220.84:3128',
         # 'http://91.221.61.126:3128',
         # 'http://161.68.250.139:80',
         # 'http://183.111.169.203:3128',
         # 'http://46.250.22.85:53281',
         # 'http://37.29.82.115:65103',
         # 'http://212.47.251.242:80',
         # 'http://109.105.40.39:53281',
         # 'http://104.167.5.82:8080',
         # 'http://213.136.77.246:80',
         # 'http://89.236.17.106:3128',
         # 'http://78.36.43.79:8080',
         ]
MAX_CLIENTS = max(10, len(PROXY))

URL_TEMPLATE = 'https://www.pornhub.com/webmasters/video_by_id?id=%s&thumbsize=large_hd'


async def task(video_hash, sem: asyncio.Semaphore):
    async with sem:
        logging.debug('Task {} started'.format(video_hash))
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(URL_TEMPLATE % video_hash, allow_redirects=False, timeout=35,
                                       proxy=random.choice(PROXY)) as resp:
                    logging.debug('response %s %s', resp.status, resp.content)
                    if resp.status != 200:
                        logging.warning('reponse code not success %s', resp.status)
                        await asyncio.sleep(WAIT_SEC)
                        return

                    response_json = await resp.json()
                    if 'video' not in response_json:
                        logging.warning('invalid json %s %s', video_hash, response_json)
                    elif response_json['video']['video_id'] != video_hash:
                        logging.warning('invalid video id into response %s %s', video_hash, response_json['video']['video_id'])
                    else:
                        img_src = response_json['video']['default_thumb']
                        if img_src:
                            await S.update_preview_img(video_hash, img_src)
                            logging.info('save thumb for video %s', video_hash)

            except Exception as e:
                logging.warning('Exception %s' % e)
                logging.exception(e)


async def run():
    videos_for_parse = await S.get_videos_for_fetch_additional_info()
    logging.info('found %d videos' % len(videos_for_parse))
    if videos_for_parse:
        sem = asyncio.Semaphore(MAX_CLIENTS)
        tasks = [asyncio.ensure_future(task(video, sem)) for video in videos_for_parse]
        await asyncio.wait(tasks)
    logging.info('end')


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)
    ioloop = asyncio.get_event_loop()
    ioloop.run_until_complete(run())
    ioloop.close()

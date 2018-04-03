#! /usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging

from src.crawler import run
from src.storage import S
from src.utils import fetch_current_top, get_default_arg_parser


async def main(top_limit: int, reset: bool=False, **kwargs):
    S.set_io_loop(asyncio.get_event_loop())
    if reset:
        await S.drop_all()

    video_hashes = fetch_current_top(top_limit)
    logging.info('fetch top%d videos (%s)', top_limit, video_hashes)
    for i in video_hashes:
        await S.add_video_hash(i)
    await run(**kwargs)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

    parser = get_default_arg_parser()
    parser.add_argument('top_limit', action='store', type=int, help='top limit value')
    args = parser.parse_args()

    ioloop = asyncio.new_event_loop()
    ioloop.run_until_complete(main(**args.__dict__))
    ioloop.close()

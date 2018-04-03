#! /usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio
import logging
import argparse

from src.crawler import run
from src.storage import S


async def main(root_hash: str, reset: bool=False, **kwargs):
    S.set_io_loop(asyncio.get_event_loop())
    if reset:
        await S.drop_all()
    await S.add_video_hash(root_hash)
    await run(**kwargs)

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser(description='Process some args.')
    parser.add_argument('root_hash', action='store', type=str, help='start video hash')
    parser.add_argument('-c', action='store', default=10, type=int, dest='concurrent', help='concurrent level')
    parser.add_argument('-i', action='store', default=10, type=int, dest='max_iterations',
                        help='limit of crawler iterations')
    parser.add_argument('--batch', action='store', default=100, type=int, dest='batch_size',
                        help='limit of urls per iteration')
    parser.add_argument('--reset', action='store_true', help='truncate all data from db')
    args = parser.parse_args()

    ioloop = asyncio.new_event_loop()
    ioloop.run_until_complete(main(**args.__dict__))
    ioloop.close()

#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import asyncio
import logging

from src.storage import S


async def main(limit_nodes: int=100):
    S.set_io_loop(asyncio.get_event_loop())

    # todo depth limit


    # todo fetch nodes w/ limit

    # todo save only already parsed nodes to dot file

    pass


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser(description='Process some args.')
    parser.add_argument('-l', action='store', default=100, type=int, dest='limit_nodes', help='nodes limit')
    args = parser.parse_args()

    ioloop = asyncio.new_event_loop()
    ioloop.run_until_complete(main(**args.__dict__))
    ioloop.close()

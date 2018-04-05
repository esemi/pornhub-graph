#! /usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import asyncio
import logging
from collections import Counter

from src.storage import S


async def main(depth: int):
    S.set_io_loop(asyncio.get_event_loop())

    parsed_nodes = await S.export_graph(depth)
    logging.info('fetch %d parsed videos for %d depth', len(parsed_nodes), depth)

    valid_nodes = set(map(lambda x: x['_id'], parsed_nodes))
    logging.info('found %d valid unique nodes', len(valid_nodes))

    cnt = Counter()
    with open('data/export_graph_%d.dot' % depth, mode='w+') as output_file:
        output_file.write("digraph SEMhub_level_%d {\n" % depth)
        for node in parsed_nodes:
            cnt['nodes'] += 1
            output_file.write("\t%s [label='%s',level='%d']\n" % (node['_id'], node['title'], node['level']))
            for edge in node['rel']:
                cnt['edges_total'] += 1
                if edge in valid_nodes:
                    output_file.write("\t%s -> %s\n" % (node['_id'], edge))
                    cnt['edges'] += 1
        output_file.write("}")
    logging.info('success export %s', cnt)


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser(description='Process some args.')
    parser.add_argument('-d', action='store', default=3, type=int, dest='depth', help='max depth')
    args = parser.parse_args()

    ioloop = asyncio.new_event_loop()
    ioloop.run_until_complete(main(**args.__dict__))
    ioloop.close()

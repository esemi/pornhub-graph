import argparse

import requests


def fetch_current_top(limit: int=10) -> set:
    """
    Fetch current top of videos and add it to queue
    """

    assert limit >= 0
    response = requests.get('https://www.pornhub.com/webmasters/search?ordering=mostviewed&period=alltime')
    response.raise_for_status()
    json_data = response.json()['videos']
    return set(list(map(lambda x: x['video_id'], json_data))[:limit])


def get_default_arg_parser():
    parser = argparse.ArgumentParser(description='Process some args.')
    parser.add_argument('-c', action='store', default=10, type=int, dest='concurrent', help='concurrent level')
    parser.add_argument('-i', action='store', default=10, type=int, dest='max_iterations',
                        help='limit of crawler iterations')
    parser.add_argument('--batch', action='store', default=100, type=int, dest='batch_size',
                        help='limit of urls per iteration')
    parser.add_argument('--reset', action='store_true', help='truncate all data from db')
    return parser

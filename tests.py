import time
import unittest
from collections import Counter

import asynctest

from pyppeteer_v1 import crawl_many_videos, crawl_many_videos_pool

concurrency = 100
task_count_factor = 20

random_videos = {'ph59d38bc435f0f', 'ph590df19b8e7b9', 'ph5a04a7c416bc1', 'ph59ad0a3e49544', 'ph59fcf23b6203e',
                 'ph59c92d603f48b', 'ph59a741939ce82', 'ph5a21ce15a87fb', 'ph59bef16384d20', 'ph5a185d0c6b7a2'}
random_videos = list(random_videos) * task_count_factor


class SpeedTest(asynctest.TestCase):
    use_default_loop = True

    async def test_speed_one_page(self):
        cnt = Counter()
        t = time.time()
        await crawl_many_videos(concurrency, random_videos, cnt)
        end_time = time.time()
        print('One page version result %.2f %s' % (end_time - t, cnt))

    async def test_speed_many_pages(self):
        cnt = Counter()
        t = time.time()
        await crawl_many_videos_pool(concurrency, random_videos, cnt)
        end_time = time.time()
        print('Many pages version result %.2f %s' % (end_time - t, cnt))


if __name__ == '__main__':
    unittest.main()

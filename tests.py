import unittest
from collections import Counter

import asynctest
import time

from pyppeteer_v1 import crawl_many_videos


class SpeedTest(asynctest.TestCase):
    async def test_one_page_version(self):
        cnt = Counter()
        random_videos = {'ph59d38bc435f0f', 'ph590df19b8e7b9', 'ph5a04a7c416bc1', 'ph59ad0a3e49544', 'ph59fcf23b6203e',
                         'ph59c92d603f48b', 'ph59a741939ce82', 'ph5a21ce15a87fb', 'ph59bef16384d20', 'ph5a185d0c6b7a2',
                         'ph59a123b7aae59', 'ph5a03d1b95f345', 'ph5a39c2e3a4012'}
        t = time.time()
        await crawl_many_videos(10, random_videos, cnt)
        end_time = time.time()
        print('One page version result %.2f %s' % (end_time - t, cnt))


if __name__ == '__main__':
    unittest.main()

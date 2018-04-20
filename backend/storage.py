import pymongo
from pymongo.errors import DuplicateKeyError
import motor.motor_asyncio


MONGO_HOST = 'localhost'
MONGO_PORT = 27017
MONGO_DB = 'semhub'


class Storage:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_HOST, MONGO_PORT)
        db = self.client[MONGO_DB]
        self.videos = db.videos

    def set_io_loop(self, loop):
        self.client.io_loop = loop

    async def drop_all(self):
        await self.videos.drop()

    async def mark_video_as_parsed(self, video_hash: str, title: str, relations: set):
        await self.videos.update_one({'_id': video_hash}, {'$set': {'title': title, 'parsed': True,
                                                                    'rel': list(relations)},
                                                           '$inc': {'parse_try': 1}})

    async def mark_video_as_parsed_fail(self, video_hash: str):
        await self.videos.update_one({'_id': video_hash}, {'$inc': {'parse_try': 1}})

    async def update_preview_img(self, video_hash: str, url: str):
        await self.videos.update_one({'_id': video_hash}, {'$set': {'img_src': url}})

    async def get_videos_for_parsing(self, limit: int, max_tries: int) -> list:
        return list(map(lambda x: (x['_id'], x['level']),
                        await self.videos.find({'parsed': False, 'parse_try': {'$lt': max_tries}},
                                               projection=['_id', 'level'],
                                               limit=limit).sort('level', pymongo.ASCENDING).to_list(None)))

    async def get_videos_for_fetch_additional_info(self) -> list:
        return list(map(lambda x: x['_id'], await self.videos.find({'parsed': True, 'img_src': None},
                                                                   projection=['_id']).sort('level', pymongo.ASCENDING).to_list(None)))

    async def add_video_hash(self, video_hash: str, level: int=0) -> bool:
        try:
            await self.videos.insert_one({'_id': video_hash, 'parsed': False, 'parse_try': 0, 'level': level})
            return True
        except DuplicateKeyError:
            await self.videos.update_one({'_id': video_hash}, {'$min': {'level': level}})
            return False

    def export_graph(self, max_level: int):
        return self.videos.find({'parsed': True, 'level': {'$lte': max_level}})\
            .sort('_id', pymongo.ASCENDING).to_list(None)


S = Storage()

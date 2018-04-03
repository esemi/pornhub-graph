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
                                                                    'rel': list(relations)}})

    async def mark_video_as_parsed_fail(self, video_hash: str):
        await self.videos.update_one({'_id': video_hash}, {'$inc': {'parse_try': 1}})

    async def get_videos_for_parsing(self, limit: int, max_tries: int) -> set:
        return set(map(lambda x: x['_id'],
                       await self.videos.find({'parsed': False, 'parse_try': {'$lt': max_tries}}, projection=['_id'],
                                              limit=limit).to_list(None)))

    async def add_video_hash(self, video_hash: str) -> bool:
        video = {'_id': video_hash, 'parsed': False, 'parse_try': 0}
        try:
            await self.videos.insert_one(video)
            return True
        except DuplicateKeyError:
            return False


S = Storage()

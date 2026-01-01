from pymongo import AsyncMongoClient

from ..logging import LOGGER
from config import MONGO_DB_URI

_mongo_async_ = AsyncMongoClient(MONGO_DB_URI)
mongodb = _mongo_async_.Yukki
LOGGER(__name__).info("Connected to your Mongo Database.")

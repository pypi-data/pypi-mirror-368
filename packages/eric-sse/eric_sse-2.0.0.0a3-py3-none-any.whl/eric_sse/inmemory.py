from typing import Iterable

from eric_sse.persistence import KvStorageEngine, ItemNotFound
from eric_sse.repository import ChannelRepository
from eric_sse.entities import AbstractChannel


class InMemoryStorage(KvStorageEngine):

    def __init__(self, objects: dict[str, any] = None):
        self.objects = objects or {}

    objects: dict[str, any] = {}

    def fetch_by_prefix(self, prefix: str) -> Iterable[any]:
        for k, obj in self.objects.items():
            if k.startswith(prefix):
                yield obj

    def fetch_all(self) -> Iterable[any]:
        for obj in self.objects.values():
            yield obj

    def upsert(self, key: str, value: any):
        self.objects[key] = value

    def fetch_one(self, key: str) -> any:
        try:
            return self.objects[key]
        except KeyError:
            raise ItemNotFound(key)

    def delete(self, key: str):
        del InMemoryStorage.objects[key]

class InMemoryChannelRepository(ChannelRepository):
    def __init__(self, channels: dict[str, AbstractChannel] = None):
        super().__init__(storage_engine=InMemoryStorage(objects=channels or {}))


from abc import ABC
from typing import Iterable

from eric_sse.entities import AbstractChannel
from eric_sse.interfaces import ChannelRepositoryInterface, ListenerRepositoryInterface, QueueRepositoryInterface
from eric_sse.listener import MessageQueueListener, PersistableListener
from eric_sse.persistence import ObjectAsKeyValuePersistenceMixin, KvStorageEngine
from eric_sse.queues import Queue, PersistableQueue


class PersistableChannel(AbstractChannel, ObjectAsKeyValuePersistenceMixin, ABC):
    ...


class ChannelRepository(ChannelRepositoryInterface):
    """
    If your concrete repository is a serializable object, you can use this class if correspondant storage engine supports its format

    see :class:`~eric_sse.inmemory.InMemoryChannelRepository`
    """
    def __init__(self, storage_engine: KvStorageEngine):
        self.__storage_engine = storage_engine

    def load_all(self) -> Iterable[PersistableChannel]:
        for obj in self.__storage_engine.fetch_all():
            yield obj

    def load_one(self, key: str) -> PersistableChannel:
        return self.__storage_engine.fetch_one(key)

    def persist(self, persistable: PersistableChannel):
        self.__storage_engine.upsert(persistable.kv_key, persistable)

    def delete(self, key: str):
        self.__storage_engine.delete(key)

class ListenerRepository(ListenerRepositoryInterface):

    def __init__(self, storage_engine: KvStorageEngine):
        self.__storage_engine = storage_engine

    def load_all(self, channel_id: str) -> Iterable[MessageQueueListener]:
        for obj in self.__storage_engine.fetch_all():
            yield obj

    def load_one(self, channel_id: str, key: str) -> PersistableListener:
        return self.__storage_engine.fetch_one(key)

    def persist(self, channel_id: str, listener: PersistableListener):
        self.__storage_engine.upsert(
            listener.kv_key, listener.kv_setup_values_as_dict
        )

    def delete(self, key: str):
        self.__storage_engine.delete(key)

class QueueRepository(QueueRepositoryInterface):
    def __init__(self, storage_engine: KvStorageEngine):
        self.__storage_engine = storage_engine

    def load_one(self, key: str) -> Queue:
        return self.__storage_engine.fetch_one(key)

    def persist(self, queue: PersistableQueue):
        self.__storage_engine.upsert(
            queue.kv_key, queue.kv_setup_values_as_dict
        )

    def delete(self, key: str):
        self.__storage_engine.delete(key)

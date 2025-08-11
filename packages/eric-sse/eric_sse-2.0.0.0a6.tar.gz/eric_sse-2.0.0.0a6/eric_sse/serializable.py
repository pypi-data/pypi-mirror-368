"""
If you have to persist a serializable participant, you can use this module if correspondant storage engine supports its format

see :class:`~eric_sse.inmemory.InMemoryChannelRepository`
"""

from typing import Iterable

from eric_sse.connection import Connection
from eric_sse.interfaces import ChannelRepositoryInterface, ListenerRepositoryInterface, QueueRepositoryInterface, \
    ConnectionRepositoryInterface
from eric_sse.persistence import KvStorageEngine

from eric_sse.entities import AbstractChannel
from eric_sse.listener import MessageQueueListener
from eric_sse.queues import Queue

class ListenerRepository(ListenerRepositoryInterface):

    def __init__(self, storage_engine: KvStorageEngine):
        self.__storage_engine = storage_engine

    @staticmethod
    def build_key(channel_id: str, listener_id: str, separator: str = ':') -> str:
        """Builds a unique key for a channel and a listener joining them by separator"""

        return f'{channel_id}{separator}{listener_id}'

    def load_all(self, channel_id: str) -> Iterable[MessageQueueListener]:
        for obj in self.__storage_engine.fetch_all():
            yield obj

    def load_one(self, channel_id: str, listener_id: str) -> MessageQueueListener:
        key = ListenerRepository.build_key(channel_id, listener_id)
        return self.__storage_engine.fetch_one(key)

    def persist(self, channel_id: str, listener: MessageQueueListener):
        key = ListenerRepository.build_key(channel_id, listener.id)
        self.__storage_engine.upsert(key, listener)

    def delete(self, channel_id: str, listener_id: str):
        key = ListenerRepository.build_key(channel_id, listener_id)
        self.__storage_engine.delete(key)

class QueueRepository(QueueRepositoryInterface):
    def __init__(self, storage_engine: KvStorageEngine):
        self.__storage_engine = storage_engine

    def load_one(self, key: str) -> Queue:
        return self.__storage_engine.fetch_one(key)

    def persist(self, queue: Queue):
        self.__storage_engine.upsert(queue.id, queue)

    def delete(self, key: str):
        self.__storage_engine.delete(key)

class ConnectionRepository(ConnectionRepositoryInterface):

    def __init__(self, storage_engine: KvStorageEngine):
        self.__storage_engine = storage_engine
        self.__listener_repository = ListenerRepository(storage_engine)
        self.__queues_repository = QueueRepository(storage_engine)

    @property
    def listeners_repository(self) -> ListenerRepositoryInterface:
        return self.__listener_repository

    @property
    def queues_repository(self) -> QueueRepositoryInterface:
        return self.__queues_repository

    @staticmethod
    def build_key(channel_id: str, listener_id: str) -> str:
        """Builds a unique key for a channel and a listener, defaults to {channel_id}:{listener_id}"""

        return f'{channel_id}:{listener_id}'

    def load_all(self, channel_id: str) -> Iterable[Connection]:
        for obj in self.__storage_engine.fetch_all():
            yield obj

    def load_one(self, channel_id: str, listener_id: str) -> Connection:
        key = ListenerRepository.build_key(channel_id, listener_id)
        return self.__storage_engine.fetch_one(key)

    def persist(self, channel_id: str, listener: Connection):
        key = ListenerRepository.build_key(channel_id, listener.id)
        self.__storage_engine.upsert(key, listener)

    def delete(self, channel_id: str, listener_id: str):
        key = ListenerRepository.build_key(channel_id, listener_id)
        self.__storage_engine.delete(key)


class ChannelRepository(ChannelRepositoryInterface):
    def __init__(self, storage_engine: KvStorageEngine):
        self.__storage_engine = storage_engine
        self.connection_repository = ConnectionRepository(storage_engine)

    @property
    def connections_repository(self) -> ConnectionRepositoryInterface:
        return self.connection_repository

    def load_all(self) -> Iterable[AbstractChannel]:
        for obj in self.__storage_engine.fetch_all():
            yield obj

    def load_one(self, channel_id: str) -> AbstractChannel:
        return self.__storage_engine.fetch_one(channel_id)

    def persist(self, channel: AbstractChannel):
        self.__storage_engine.upsert(channel.id, channel)

    def delete(self, channel_id: str):
        self.__storage_engine.delete(channel_id)


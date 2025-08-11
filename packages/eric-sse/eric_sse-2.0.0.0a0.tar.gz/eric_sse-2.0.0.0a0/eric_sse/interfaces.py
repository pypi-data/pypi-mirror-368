from abc import ABC, abstractmethod
from typing import Iterable

from eric_sse.entities import AbstractChannel
from eric_sse.connection import Connection
from eric_sse.queues import Queue
from eric_sse.listener import MessageQueueListener


class ChannelRepositoryInterface(ABC):

    @abstractmethod
    def load_all(self) -> Iterable[AbstractChannel]:
        pass

    @abstractmethod
    def load_one(self, key: str) -> AbstractChannel:
        pass

    @abstractmethod
    def persist(self, persistable: AbstractChannel):
        pass

    @abstractmethod
    def delete(self, key: str):
        pass

class ConnectionRepositoryInterface(ABC):

    @abstractmethod
    def load_all(self, channel_id: str) -> Iterable[Connection]:
        pass

    @abstractmethod
    def load_one(self, channel_id: str, key: str) -> Connection:
        pass

    @abstractmethod
    def persist(self, channel_id: str, connection: Connection):
        pass

    @abstractmethod
    def delete(self, key: str):
        pass

class ListenerRepositoryInterface(ABC):

    @abstractmethod
    def load_all(self) -> Iterable[MessageQueueListener]:
        pass

    @abstractmethod
    def load_one(self, channel_id: str, key: str) -> MessageQueueListener:
        pass

    @abstractmethod
    def persist(self, channel_id: str, listener: MessageQueueListener):
        pass

    @abstractmethod
    def delete(self, key: str):
        pass

class QueueRepositoryInterface(ABC):

    @abstractmethod
    def load_one(self, key: str) -> Queue:
        pass

    @abstractmethod
    def persist(self, queue: Queue):
        pass

    @abstractmethod
    def delete(self, key: str):
        pass
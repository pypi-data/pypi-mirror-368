from abc import abstractmethod

from buz.event import Event, Subscriber
from buz.event.middleware import ConsumeMiddleware, ConsumeCallable


class BaseConsumeMiddleware(ConsumeMiddleware):
    def on_consume(self, event: Event, subscriber: Subscriber, consume: ConsumeCallable) -> None:
        self._before_on_consume(event, subscriber)
        consume(event, subscriber)
        self._after_on_consume(event, subscriber)

    @abstractmethod
    def _before_on_consume(self, event: Event, subscriber: Subscriber) -> None:
        pass

    @abstractmethod
    def _after_on_consume(self, event: Event, subscriber: Subscriber) -> None:
        pass

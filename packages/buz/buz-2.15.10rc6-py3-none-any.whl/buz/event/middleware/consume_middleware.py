from abc import abstractmethod
from typing import Callable

from buz.event import Event, Subscriber
from buz.middleware import Middleware

ConsumeCallable = Callable[[Event, Subscriber], None]


class ConsumeMiddleware(Middleware):
    @abstractmethod
    def on_consume(self, event: Event, subscriber: Subscriber, consume: ConsumeCallable) -> None:
        pass

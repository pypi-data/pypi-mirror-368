from abc import abstractmethod

from buz.event import Event
from buz.event.async_subscriber import AsyncSubscriber
from buz.event.middleware.async_consume_middleware import AsyncConsumeMiddleware, AsyncConsumeCallable


class BaseAsyncConsumeMiddleware(AsyncConsumeMiddleware):
    async def on_consume(self, event: Event, subscriber: AsyncSubscriber, consume: AsyncConsumeCallable) -> None:
        await self._before_on_consume(event, subscriber)
        await consume(event, subscriber)
        await self._after_on_consume(event, subscriber)

    @abstractmethod
    async def _before_on_consume(self, event: Event, subscriber: AsyncSubscriber) -> None:
        pass

    @abstractmethod
    async def _after_on_consume(self, event: Event, subscriber: AsyncSubscriber) -> None:
        pass

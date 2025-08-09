from typing import Sequence
from buz.event import Event
from buz.event.async_subscriber import AsyncSubscriber

from buz.event.middleware.async_consume_middleware import AsyncConsumeCallable, AsyncConsumeMiddleware
from buz.middleware import MiddlewareChainBuilder


class AsyncConsumeMiddlewareChainResolver:
    def __init__(
        self,
        middlewares: Sequence[AsyncConsumeMiddleware],
    ):
        self.__middlewares = middlewares
        self.__middleware_chain_builder: MiddlewareChainBuilder[
            AsyncConsumeCallable, AsyncConsumeMiddleware
        ] = MiddlewareChainBuilder(middlewares)

    async def resolve(self, event: Event, subscriber: AsyncSubscriber, consume: AsyncConsumeCallable) -> None:
        chain_callable: AsyncConsumeCallable = self.__middleware_chain_builder.get_chain_callable(
            consume, self.__get_middleware_callable
        )

        await chain_callable(event, subscriber)

    def __get_middleware_callable(
        self, middleware: AsyncConsumeMiddleware, consume_callable: AsyncConsumeCallable
    ) -> AsyncConsumeCallable:
        return lambda event, subscriber: middleware.on_consume(event, subscriber, consume_callable)

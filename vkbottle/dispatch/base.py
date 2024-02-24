from asyncio import gather
from typing import TYPE_CHECKING, Dict

from vkbottle.modules import logger

from .abc import ABCRouter

if TYPE_CHECKING:
    from vkbottle.api.abc import ABCAPI
    from vkbottle.dispatch.dispenser import ABCStateDispenser
    from vkbottle.dispatch.views import ABCView
    from vkbottle.exception_factory import ABCErrorHandler


class Router(ABCRouter):
    async def route(self, event: dict, ctx_api: "ABCAPI") -> None:
        logger.debug("Routing update {}", event)

        tasks = [view.handle_event(
            event, ctx_api, self.state_dispenser
        ) for view in self.views.values() if await view.process_event(event)]

        try:
            await gather(*tasks)
        except Exception as e:
            await self.error_handler.handle(e)

    def construct(
        self,
        views: Dict[str, "ABCView"],
        state_dispenser: "ABCStateDispenser",
        error_handler: "ABCErrorHandler",
    ) -> "Router":
        self.views = views
        self.state_dispenser = state_dispenser
        self.error_handler = error_handler
        return self

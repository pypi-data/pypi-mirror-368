import logging

from fastapi.routing import APIRouter
from globalgenie.app.base import BaseAPIApp
from globalgenie.app.slack.async_router import get_async_router
from globalgenie.app.slack.sync_router import get_sync_router

logger = logging.getLogger(__name__)


class SlackAPI(BaseAPIApp):
    type = "slack"

    def get_router(self) -> APIRouter:
        return get_sync_router(agent=self.agent, team=self.team)

    def get_async_router(self) -> APIRouter:
        return get_async_router(agent=self.agent, team=self.team)

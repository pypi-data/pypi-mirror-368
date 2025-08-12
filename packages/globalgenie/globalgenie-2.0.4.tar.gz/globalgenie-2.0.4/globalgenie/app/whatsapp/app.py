from fastapi.routing import APIRouter
from globalgenie.app.base import BaseAPIApp
from globalgenie.app.whatsapp.async_router import get_async_router
from globalgenie.app.whatsapp.sync_router import get_sync_router


class WhatsappAPI(BaseAPIApp):
    type = "whatsapp"

    def get_router(self) -> APIRouter:
        return get_sync_router(agent=self.agent, team=self.team)

    def get_async_router(self) -> APIRouter:
        return get_async_router(agent=self.agent, team=self.team)

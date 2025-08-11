from __future__ import annotations

import json
from datetime import datetime

from ninja import NinjaAPI, Schema

from django.utils.timezone import now

from allianceauth.framework.tests.test_api_user import (
    get_main_character_from_user,
)
from allianceauth.services.hooks import get_extension_logger

from incursions.api.helpers.sse import SSEClient, SSEEvent
from incursions.api.schema import CharacterSchema
from incursions.app_settings import SSE_SECRET, SSE_SITE_URL
from incursions.models.waitlist import Announcement


class RequestPayloadSchema(Schema):
    message: str
    is_alert: bool
    pages: str | None


class AnnouncementSchema(Schema):
    id: int
    message: str
    is_alert: bool
    pages: str | None
    created_by: CharacterSchema | None
    created_at: datetime
    revoked_by: CharacterSchema | None
    revoked_at: datetime | None


sse_client = SSEClient(SSE_SITE_URL, SSE_SECRET)
logger = get_extension_logger(__name__)
api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    AnnouncementAPIEndpoints(api)


class AnnouncementAPIEndpoints:

    tags = ["Announcements"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/announcements", response={200: list[AnnouncementSchema], 403: dict}, tags=self.tags)
        def list_announcements(request) -> tuple[int, list[AnnouncementSchema] | dict]:
            if not request.user.has_perm("incursions.basic_waitlist"):
                logger.warning(f"Permission denied for listing announcements by user {request.user}")
                return 403, {"error": "Permission denied"}

            announcements = list(Announcement.objects.filter(revoked_at__isnull=True).select_related("created_by", "revoked_by"))
            logger.info(f"Returning {len(announcements)} active announcements to user {request.user}")
            return 200, announcements

        @api.post("/announcements", tags=self.tags, response={200: dict, 403: dict})
        def create_announcement(request, payload: RequestPayloadSchema) -> tuple[int, dict]:
            if not request.user.has_perm("incursions.waitlist_announcements_manage"):
                logger.warning(f"Permission denied for creating announcement by user {request.user}")
                return 403, {"error": "Permission denied"}

            announcement = Announcement.objects.create(
                message=payload.message,
                is_alert=payload.is_alert,
                pages=payload.pages,
                created_by=get_main_character_from_user(request.user),
                # created_at=now(), # auto_now_add
            )
            logger.info(f"Created announcement #{announcement.pk} by user {request.user}")
            sse_client.submit([SSEEvent.new_json(topic="announcements", event="announcement;new", data=json.loads(AnnouncementSchema.from_orm(announcement).model_dump_json()))])
            return 200, {"id": announcement.pk, "status": "Created"}

        @api.put("/announcements/{announcement_id}", response={200: dict, 403: dict, 404: dict}, tags=self.tags)
        def update_announcement(request, announcement_id: int, payload: RequestPayloadSchema) -> tuple[int, dict]:
            if not request.user.has_perm("incursions.waitlist_announcements_manage"):
                logger.warning(f"Permission denied for updating announcement by user {request.user}")
                return 403, {"error": "Permission denied"}

            announcement = Announcement.objects.get(id=announcement_id, revoked_at__isnull=True)
            if not announcement:
                logger.error(f"Announcement #{announcement_id} not found for update")
                return 404, {"error": "Announcement not found"}

            announcement.message = payload.message
            announcement.is_alert = payload.is_alert
            announcement.pages = payload.pages
            announcement.created_by = get_main_character_from_user(request.user)
            announcement.save(update_fields=["message", "is_alert", "pages", "created_by"])

            logger.info(f"Updated announcement #{announcement.pk} by user {request.user}")
            sse_client.submit([SSEEvent.new_json(topic="announcements", event="announcement;updated", data=json.loads(AnnouncementSchema.from_orm(announcement).model_dump_json()))])
            return 200, {"status": "Updated"}

        @api.delete("/announcements/{announcement_id}", response={200: dict, 403: dict, 404: dict}, tags=self.tags)
        def revoke_announcement(request, announcement_id: int) -> tuple[int, dict]:
            if not request.user.has_perm("incursions.waitlist_announcements_manage"):
                logger.warning(f"Permission denied for revoking announcement by user {request.user}")
                return 403, {"error": "Permission denied"}

            announcement = Announcement.objects.get(id=announcement_id, revoked_at__isnull=True)
            if not announcement:
                logger.error(f"Announcement #{announcement_id} not found or already revoked")
                return 404, {"error": "Announcement not found or already revoked"}

            announcement.revoked_by = get_main_character_from_user(request.user)
            announcement.revoked_at = now()
            announcement.save(update_fields=["revoked_by", "revoked_at"])

            logger.info(f"Revoked announcement #{announcement.pk} by user {request.user}")
            sse_client.submit([SSEEvent.new_json(topic="announcements", event="announcement;updated", data=json.loads(AnnouncementSchema.from_orm(announcement).model_dump_json()))])
            return 200, {"status": "Revoked"}

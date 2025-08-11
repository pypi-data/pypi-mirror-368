from __future__ import annotations

from datetime import datetime

from ninja import NinjaAPI, Schema

from allianceauth.eveonline.models import EveCharacter
from allianceauth.framework.api.user import get_main_character_from_user
from allianceauth.services.hooks import get_extension_logger

from incursions.api.schema import CharacterSchema
from incursions.models.waitlist import Badge, CharacterBadges


class BadgeSchema(Schema):
    id: int
    name: str
    letter: str
    type: str
    color: str
    order: int
    member_count: int
    exclude_badge_id: int | None


class CharacterBadgesSchema(Schema):
    badge: BadgeSchema
    character: CharacterSchema
    granted_by: CharacterSchema | None
    granted_at: datetime


class AssignBadgeRequest(Schema):
    character_id: int


logger = get_extension_logger(__name__)

api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    BadgesAPIEndpoints(api)


class BadgesAPIEndpoints:

    tags = ["Badges"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/badges", response={200: list[BadgeSchema], 403: dict}, tags=["Badges"])
        def list_badges(request) -> tuple[int, list[BadgeSchema] | dict]:
            if not request.user.has_perm("incursions.basic_waitlist"):
                logger.warning(f"Permission denied to list badges for user {request.user}")
                return 403, {"error": "Permission denied"}

            badges = Badge.objects.all()
            result = [BadgeSchema.from_orm(b) for b in badges]
            logger.info(f"Returning {len(result)} badges to user {request.user}")
            return 200, result

        @api.get("/badges/{badge_id}/members", response={200: list[CharacterBadgesSchema], 403: dict, 404: dict}, tags=self.tags)
        def get_badge_members(request, badge_id: int) -> tuple[int, list[CharacterBadgesSchema] | dict]:
            if not (request.user.has_perm("incursions.waitlist_badges_view") or request.user.has_perm("incursions.waitlist_badges_manage")):
                logger.warning(f"Permission denied to view badge members for user {request.user}")
                return 403, {"error": "Permission denied"}

            badge = Badge.objects.filter(id=badge_id).first()
            if not badge:
                logger.error(f"Badge {badge_id} not found")
                return 404, {"error": "Badge not found"}

            characters = CharacterBadges.objects.filter(badge=badge).select_related("character", "granted_by", "badge")
            logger.info(f"Returning {characters.count()} badge members for badge {badge_id} to user {request.user}")
            return 200, [CharacterBadgesSchema.from_orm(cb) for cb in characters]

        @api.post("/badges/{badge_id}/members", response={200: dict, 403: dict, 404: dict}, tags=self.tags)
        def assign_badge(request, badge_id: int, payload: AssignBadgeRequest) -> tuple[int, dict]:
            if not request.user.has_perm("incursions.waitlist_badges_manage"):
                logger.warning(f"Permission denied to assign badge by user {request.user}")
                return 403, {"error": "Permission denied"}

            character = EveCharacter.objects.filter(character_id=payload.character_id).first()
            if not character:
                logger.error(f"Character {payload.character_id} not found")
                return 404, {"error": "EveCharacter not found"}

            badge = Badge.objects.filter(id=badge_id).first()
            if not badge:
                logger.error(f"Badge {badge_id} not found")
                return 404, {"error": "Badge not found"}

            if CharacterBadges.objects.filter(character=character, badge=badge).exists():
                logger.warning(f"Character {payload.character_id} already has badge {badge_id}")
                return 400, {"error": "EveCharacter already has this badge"}

            CharacterBadges.objects.create(badge=badge, character=character, granted_by=get_main_character_from_user(request.user))
            logger.info(f"Assigned badge {badge_id} to character {payload.character_id} by user {request.user}")
            return 200, {"status": "Badge assigned"}

        @api.delete("/badges/{badge_id}/members/{character_id}", response={200: dict, 403: dict, 404: dict}, tags=self.tags)
        def revoke_badge(request, badge_id: int, character_id: int) -> tuple[int, dict]:
            if not request.user.has_perm("incursions.waitlist_badges_manage"):
                logger.warning(f"Permission denied to revoke badge by user {request.user}")
                return 403, {"error": "Permission denied"}

            character = EveCharacter.objects.filter(character_id=character_id).first()
            if not character:
                logger.error(f"Character {character_id} not found")
                return 404, {"error": "Character not found"}

            badge = Badge.objects.filter(id=badge_id).first()
            if not badge:
                logger.error(f"Badge {badge_id} not found")
                return 404, {"error": "Badge not found"}

            badge_qs = CharacterBadges.objects.filter(character=character, badge=badge)
            if not badge_qs.exists():
                logger.warning(f"Badge assignment for character {character_id} and badge {badge_id} not found")
                return 404, {"error": "Badge assignment not found"}

            deleted, _ = badge_qs.delete()
            logger.info(f"Revoked badge {badge_id} from character {character_id} by user {request.user}")
            return 200, {"status": "Badge revoked"}

from datetime import datetime, timezone

from ninja import NinjaAPI, Schema

from django.db import transaction

from allianceauth.eveonline.models import EveCharacter
from allianceauth.framework.api.user import get_main_character_from_user
from allianceauth.services.hooks import get_extension_logger

from incursions.api.schema import (
    AllianceSchema, CharacterSchema, CorporationSchema,
)
from incursions.models.waitlist import Ban


class PublicBanSchema(Schema):
    id: int
    entity_name: str
    entity_type: str
    entity_character: CharacterSchema | None
    entity_corporation: CorporationSchema | None
    entity_alliance: AllianceSchema | None
    issued_at: datetime
    issued_by: CharacterSchema | None
    public_reason: str | None
    revoked_at: datetime | None
    revoked_by: CharacterSchema | None


class BanSchema(Schema):
    id: int
    entity_name: str
    entity_type: str
    entity_character: CharacterSchema | None
    entity_corporation: CorporationSchema | None
    entity_alliance: AllianceSchema | None
    issued_at: datetime
    issued_by: CharacterSchema | None
    reason: str
    public_reason: str | None
    revoked_at: datetime | None
    revoked_by: CharacterSchema | None


class UpdateBanSchema(Schema):
    id: int
    entity_type: str
    entity_character: CharacterSchema | None
    entity_corporation: CorporationSchema | None
    entity_alliance: AllianceSchema | None
    reason: str
    public_reason: str | None
    revoked_at: datetime | None


logger = get_extension_logger(__name__)
api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    BansAPIEndpoints(api)


class BansAPIEndpoints:

    tags = ["Bans"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/bans", response={200: list[BanSchema], 403: dict}, tags=self.tags)
        def list_bans(request):
            if not (request.user.has_perm("incursions.waitlist_bans_view") or request.user.has_perm("incursions.waitlist_bans_manage")):
                logger.warning(f"User {request.user} denied listing bans")
                return 403, {"error": "Permission denied"}

            bans = Ban.objects.filter(revoked_at__isnull=True).select_related("entity_character", "entity_corporation", "entity_alliance", "issued_by", "revoked_by")
            logger.info(f"User {request.user} listed {bans.count()} active bans")
            return 200, list(bans)

        @api.post("/bans", response={200: dict, 403: dict}, tags=self.tags)
        def create_ban(request, payload: UpdateBanSchema):
            if not request.user.has_perm("incursions.waitlist_bans_manage"):
                logger.warning(f"User {request.user} denied ban creation")
                return 403, {"error": "Permission denied"}

            with transaction.atomic():
                Ban.objects.create(
                    pk=payload.id,
                    entity_type=payload.entity_type,
                    issued_at=datetime.now(timezone.utc),
                    issued_by=get_main_character_from_user(request.user),
                    entity_character_id=payload.entity_character.pk if payload.entity_character else None,
                    entity_corporation_id=payload.entity_corporation.pk if payload.entity_corporation else None,
                    entity_alliance_id=payload.entity_alliance.pk if payload.entity_alliance else None,
                    reason=payload.reason,
                    public_reason=payload.public_reason,
                    revoked_at=payload.revoked_at,
                    revoked_by=get_main_character_from_user(request.user) if payload.revoked_at else None
                )
            logger.info(f"Ban {payload.id} created by user {request.user}")
            return 200, {"status": "Ban created"}

        @api.get("/bans/{character_id}", response={200: list[BanSchema], 403: dict, 404: dict}, tags=self.tags)
        def character_history(request, character_id: int):
            if not (request.user.has_perm("incursions.waitlist_bans_view") or request.user.has_perm("incursions.waitlist_bans_manage")):
                logger.warning(f"User {request.user} denied access to character ban history for {character_id}")
                return 403, {"error": "Permission denied"}

            if not EveCharacter.objects.filter(character_id=character_id).exists():
                logger.error(f"Character {character_id} not found")
                return 404, {"error": "Character not found"}

            bans = Ban.objects.filter(entity_character__character_id=character_id, entity_type="Character").select_related("entity_character", "entity_corporation", "entity_alliance", "issued_by", "revoked_by")
            logger.info(f"User {request.user} retrieved {bans.count()} bans for character {character_id}")
            return 200, list(bans)

        @api.patch("/bans/{ban_id}", response={200: dict, 403: dict, 404: dict}, tags=self.tags)
        def update_ban(request, ban_id: int, payload: BanSchema):
            if not request.user.has_perm("incursions.waitlist_bans_manage"):
                logger.warning(f"User {request.user} denied ban update")
                return 403, {"error": "Permission denied"}

            try:
                ban = Ban.objects.select_for_update().get(pk=ban_id)
            except Ban.DoesNotExist:
                logger.error(f"Ban {ban_id} not found")
                return 404, {"error": "Ban not found"}

            ban.reason = payload.reason
            ban.public_reason = payload.public_reason
            ban.revoked_at = payload.revoked_at
            ban.revoked_by = get_main_character_from_user(request.user) if payload.revoked_at else None
            ban.issued_by = get_main_character_from_user(request.user)
            ban.issued_at = datetime.now(timezone.utc)
            ban.save(update_fields=["reason", "public_reason", "revoked_at", "revoked_by", "issued_by", "issued_at"])

            logger.info(f"Ban {ban_id} updated by user {request.user}")
            return 200, {"status": "Ban updated"}

        @api.delete("/bans/{ban_id}", response={200: dict, 403: dict, 404: dict}, tags=self.tags)
        def revoke_ban(request, ban_id: int):
            if not request.user.has_perm("incursions.waitlist_bans_manage"):
                logger.warning(f"User {request.user} denied ban revocation")
                return 403, {"error": "Permission denied"}

            try:
                ban = Ban.objects.select_for_update().get(pk=ban_id)
            except Ban.DoesNotExist:
                logger.error(f"Ban {ban_id} not found")
                return 404, {"error": "Ban not found"}

            ban.revoked_at = datetime.now(timezone.utc)
            ban.revoked_by = get_main_character_from_user(request.user)
            ban.save(update_fields=["revoked_at", "revoked_by"])

            logger.info(f"Ban {ban_id} revoked by user {request.user}")
            return 200, {"status": "Ban revoked"}

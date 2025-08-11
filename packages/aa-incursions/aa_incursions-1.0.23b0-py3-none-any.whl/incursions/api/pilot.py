from aadiscordbot.cogs.utils.exceptions import NotAuthenticated
from aadiscordbot.utils.auth import get_discord_user_id
from ninja import NinjaAPI, Schema

from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from allianceauth.eveonline.models import EveCharacter
from allianceauth.framework.api.evecharacter import get_user_from_evecharacter
from allianceauth.framework.api.user import get_all_characters_from_user
from allianceauth.services.hooks import get_extension_logger

from incursions.api.badges import BadgeSchema
from incursions.api.bans import PublicBanSchema
from incursions.api.schema import CharacterSchema
from incursions.models.waitlist import Ban


class PilotInfoSchema(Schema):
    character: CharacterSchema
    badges: list[BadgeSchema]
    active_bans: list[PublicBanSchema] | None


class PilotDiscordSchema(Schema):
    character: CharacterSchema
    discord_username: str


logger = get_extension_logger(__name__)
api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    PilotAPIEndpoints(api)


class PilotAPIEndpoints:

    tags = ["Pilot"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/pilot/info", response={200: PilotInfoSchema, 403: dict, 404: dict}, tags=self.tags)
        def pilot_info(request, character_id: int):
            if not (character_id in [c.character_id for c in get_all_characters_from_user(request.user)] or request.user.has_perm("incursions.waitlist_pilot_view")):
                logger.warning(f"User {request.user} denied access to pilot info for character {character_id}")
                return 403, {"error": "Permission denied"}

            try:
                character = EveCharacter.objects.prefetch_related("incursions_badge").get(character_id=character_id)
            except EveCharacter.DoesNotExist:
                logger.warning(f"User {request.user} requested pilot info for non-existent character {character_id}")
                return 404, {"error": "Pilot not found"}

            bans = Ban.objects.filter(
                Q(revoked_at__isnull=True) | Q(revoked_at__gt=now()),
                entity_character_id=character.pk,
            )

            logger.info(f"User {request.user} fetched pilot info for character {character_id}")
            return 200, PilotInfoSchema(
                character=CharacterSchema.from_orm(character),
                badges=[BadgeSchema.from_orm(cb.badge) for cb in character.incursions_badge.all()],
                active_bans=[PublicBanSchema.from_orm(ban) for ban in bans],
            )

        @api.get("/pilot/discord", response={200: PilotDiscordSchema, 403: dict, 404: dict}, tags=self.tags)
        def pilot_discord(request, character_id: int):
            if not (character_id in [c.character_id for c in get_all_characters_from_user(request.user)] or request.user.has_perm("incursions.waitlist_pilot_view")):
                logger.warning(f"User {request.user} denied access to discord info for character {character_id}")
                return 403, {"error": "Permission denied"}

            try:
                character = EveCharacter.objects.get(character_id=character_id)
            except EveCharacter.DoesNotExist:
                logger.warning(f"User {request.user} requested pilot info for non-existent character {character_id}")
                return 404, {"error": "Pilot not found"}

            try:
                discord_uid = get_discord_user_id(get_user_from_evecharacter(character))
            except NotAuthenticated:
                logger.warning(f"User {request.user} requested discord info for character {character_id} but no discord user found")
                return 404, {"error": "Discord user not found"}

            logger.info(f"User {request.user} fetched pilot info for character {character_id}")
            return 200, PilotDiscordSchema(
                character=CharacterSchema.from_orm(character),
                discord_username=f"<@{discord_uid}>",
            )

        @api.get("/pilot/alts", response={200: list[CharacterSchema], 403: dict}, tags=self.tags)
        def alt_info(request, character_id: int):
            character = get_object_or_404(EveCharacter.objects.only("pk"), character_id=character_id)
            if not (character in get_all_characters_from_user(request.user) or request.user.has_perm("incursions.waitlist_alts_view")):
                logger.warning(f"User {request.user} denied access to alts for character {character_id}")
                return 403, {"error": "Permission denied"}

            character = get_object_or_404(EveCharacter.objects.only("pk", "character_id"), character_id=character_id)
            user = get_user_from_evecharacter(character)
            alts = get_all_characters_from_user(user)
            filtered_alts = [alt for alt in alts if alt.character_id != character_id]

            logger.info(f"User {request.user} fetched {len(filtered_alts)} alts for character {character_id}")
            return [CharacterSchema.from_orm(alt) for alt in filtered_alts]

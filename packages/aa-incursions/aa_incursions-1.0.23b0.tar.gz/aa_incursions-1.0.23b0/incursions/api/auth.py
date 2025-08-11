from __future__ import annotations

from ninja import NinjaAPI, Schema

from allianceauth.framework.api.user import (
    get_all_characters_from_user, get_main_character_from_user,
)
from allianceauth.services.hooks import get_extension_logger

from incursions.api.schema import CharacterSchema


class WhoamiResponse(Schema):
    main_character_id: int
    access: list[str]
    characters: list[CharacterSchema]


logger = get_extension_logger(__name__)
api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    AuthAPIEndpoints(api)


class AuthAPIEndpoints:

    tags = ["Auth"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/auth/whoami", response={200: WhoamiResponse, 404: dict}, tags=self.tags)
        def whoami(request) -> tuple[int, WhoamiResponse | dict]:
            user = request.user
            logger.debug(f"Authenticating user: {user}")

            try:
                main_character = get_main_character_from_user(user)
            except Exception as e:
                logger.warning("Main character fetch failed", exc_info=e)
                return 404, {"error": "User has no Main Character Set"}

            access_levels: list[str] = [perm for perm in user.get_all_permissions() if perm.startswith("incursions.")]
            characters = get_all_characters_from_user(user)
            character_schemas = [CharacterSchema.from_orm(alt) for alt in characters]

            logger.info(f"User {user} authenticated with {len(character_schemas)} characters")
            return 200, WhoamiResponse(main_character_id=main_character.character_id, access=access_levels, characters=character_schemas)

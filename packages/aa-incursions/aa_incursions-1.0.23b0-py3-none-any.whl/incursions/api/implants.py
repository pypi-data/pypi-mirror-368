from ninja import NinjaAPI, Schema

from django.shortcuts import get_object_or_404

from allianceauth.eveonline.models import EveCharacter
from allianceauth.framework.api.user import get_all_characters_from_user
from allianceauth.services.hooks import get_extension_logger

from incursions.providers import get_character_implants


class ImplantsResponse(Schema):
    implants: list[int]


logger = get_extension_logger(__name__)
api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    ImplantsAPIEndpoints(api)


class ImplantsAPIEndpoints:

    tags = ["Implants"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/implants", response={200: ImplantsResponse, 403: dict}, tags=self.tags)
        def list_implants(request, character_id: int):
            character = get_object_or_404(EveCharacter.objects.only("pk"), character_id=character_id)

            if not (character in get_all_characters_from_user(request.user) or request.user.has_perm("incursions.waitlist_implants_view")):
                logger.warning(f"User {request.user} denied access to implants for character {character_id}")
                return 403, {"error": "Permission denied"}

            implants, _ = get_character_implants(character_id)
            logger.info(f"Implants returned for character {character_id} by user {request.user}")

            return ImplantsResponse(implants=implants)

from ninja import NinjaAPI, Schema

from allianceauth.eveonline.models import EveCharacter
from allianceauth.services.hooks import get_extension_logger

from incursions.api.schema import CharacterSchema
from incursions.providers import search_esi


class SearchResponse(Schema):
    query: str
    results: list[CharacterSchema]


class EsiSearchRequest(Schema):
    search: str
    category: str = "character"
    strict: bool = False


class EsiSearchResponse(Schema):
    character: list[int] | None = None
    corporation: list[int] | None = None
    alliance: list[int] | None = None


logger = get_extension_logger(__name__)
api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    SearchAPIEndpoints(api)


class SearchAPIEndpoints:

    tags = ["Search"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/search", response={200: SearchResponse, 403: dict}, tags=self.tags)
        def query(request, query: str):
            if not (request.user.has_perm("incursions.waitlist_search") or request.user.has_perm("incursions.waitlist_esi_search")):
                logger.warning(f"User {request.user} denied search for query '{query}'")
                return 403, {"error": "Permission denied"}

            characters = list(EveCharacter.objects.only("character_id", "character_name", "corporation_id", "alliance_id").filter(character_name__icontains=query))
            logger.info(f"User {request.user} performed search query '{query}' and found {len(characters)} results")
            return SearchResponse(query=query, results=characters)

        @api.post("/search", response={200: list[int], 403: dict}, tags=self.tags)
        def esi_search(request, payload: EsiSearchRequest):
            if not request.user.has_perm("incursions.waitlist_esi_search"):
                logger.warning(f"User {request.user} denied ESI search for category '{payload.category}' and search '{payload.search}'")
                return 403, {"error": "Permission denied"}

            if payload.category == "character":
                result, _ = search_esi(request.user.main_character.character_id, payload.search, payload.category, payload.strict)
                logger.info(f"User {request.user} performed ESI search for '{payload.search}' and got {len(result.get(payload.category, []))} results")
                return [x for x in result.get(payload.category, [])]

            logger.warning(f"Unsupported ESI category '{payload.category}' requested by user {request.user}")
            return 403, {"error": "Unsupported search category"}

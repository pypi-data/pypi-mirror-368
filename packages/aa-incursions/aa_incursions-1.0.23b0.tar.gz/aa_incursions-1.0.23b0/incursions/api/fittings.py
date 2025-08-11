from ninja import NinjaAPI, Schema

from allianceauth.services.hooks import get_extension_logger

from incursions.models.waitlist import (
    ApprovedFitting, WaitlistCategory, WaitlistCategoryRule,
)


class DNAFittingSchema(Schema):
    name: str
    dna: str
    tier: str
    implant_set: str


class FittingNoteSchema(Schema):
    name: str
    description: str | None


class FittingResponse(Schema):
    fittingdata: list[DNAFittingSchema] | None
    notes: list[FittingNoteSchema] | None
    logi_rules: list[int] | None  # Im hoping to deprecate this entirely, its dumb


logger = get_extension_logger(__name__)
api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    FittingsAPIEndpoints(api)


class FittingsAPIEndpoints:

    tags = ["Fittings"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/fittings", response={200: FittingResponse, 403: dict, 404: dict}, tags=self.tags)
        def fittings(request):
            if not request.user.has_perm("incursions.basic_waitlist"):
                logger.warning(f"User {request.user} denied access to fittings")
                return 403, {"error": "Permission denied"}

            fittings = ApprovedFitting.objects.select_related("implants", "ship")

            logi_category, created = WaitlistCategory.objects.get_or_create(name="LOGI")
            if created:
                logger.info("LOGI category was created automatically")

            logi_rules = list(WaitlistCategoryRule.objects.filter(waitlist_category_id=logi_category.pk).values_list("ship__type_id", flat=True))

            logger.info(f"User {request.user} fetched {len(fittings)} fittings and {len(logi_rules)} logi rules")
            return 200, FittingResponse(
                fittingdata=fittings,
                notes=fittings,  # ARIEL, FittingSortDisplay expects a list of notes and matches them on the ship name. Passing this here should get pydantic-ed to something approximately useful
                logi_rules=logi_rules
            )

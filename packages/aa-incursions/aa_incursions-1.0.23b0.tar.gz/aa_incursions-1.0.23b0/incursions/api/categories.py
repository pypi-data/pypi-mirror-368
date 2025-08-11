from ninja import NinjaAPI, Schema

from allianceauth.services.hooks import get_extension_logger

from incursions.models.waitlist import WaitlistCategory


class CategorySchema(Schema):
    id: int
    name: str


class CategoriesResponse(Schema):
    categories: list[CategorySchema]


api = NinjaAPI()
logger = get_extension_logger(__name__)


def setup(api: NinjaAPI) -> None:
    CategoriesAPIEndpoints(api)


class CategoriesAPIEndpoints:

    tags = ["Categories"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/categories", response={200: CategoriesResponse, 403: dict}, tags=self.tags)
        def list_categories(request):
            if not request.user.has_perm("incursions.basic_waitlist"):
                logger.warning(f"User {request.user} denied access to category list")
                return 403, {"error": "Permission denied"}

            categories = list(WaitlistCategory.objects.only("pk", "name"))
            logger.info(f"User {request.user} fetched {len(categories)} categories")
            return 200, CategoriesResponse(categories=list(CategorySchema.from_orm(cat) for cat in categories))

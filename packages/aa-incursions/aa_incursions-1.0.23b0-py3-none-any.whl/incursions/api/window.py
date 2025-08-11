from ninja import NinjaAPI, Schema

from allianceauth.services.hooks import get_extension_logger

from incursions.providers import open_window_information


class OpenWindowRequest(Schema):
    character_id: int
    target_id: int


logger = get_extension_logger(__name__)

api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    WindowAPIEndpoints(api)


class WindowAPIEndpoints:

    tags = ["Window"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.post("/open_window", tags=self.tags)
        def open_window(request, payload: OpenWindowRequest):
            if not request.user.has_perm("incursions.waitlist_esi_show_info"):
                return 403, {"error": "Permission denied"}

            result, _ = open_window_information(payload.character_id, payload.target_id)
            return result

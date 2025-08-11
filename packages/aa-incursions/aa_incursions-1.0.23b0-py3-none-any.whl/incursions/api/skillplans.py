from enum import Enum

from ninja import Field, NinjaAPI, Schema

from allianceauth.services.hooks import get_extension_logger

from incursions.api.schema import HullSchema


class SkillLevelEnum(str, Enum):
    I = "I"  # noqa: E741
    II = "II"
    III = "III"
    IV = "IV"
    V = "V"


class BaseSkillPlanLevel(Schema):
    type: str


class FitLevel(Schema):
    type: str = "fit"
    ship: str
    fit: str


class SkillsLevel(Schema):
    type: str = "skills"
    from_: str = Field(..., alias="from")
    tier: str


class SkillLevelEntry(Schema):
    type: str = "skill"
    from_: str = Field(..., alias="from")
    level: SkillLevelEnum


class TankLevel(Schema):
    type: str = "tank"
    from_: str = Field(..., alias="from")


class SkillPlanSchema(Schema):
    name: str
    description: str
    alpha: bool = False
    plan: list[FitLevel | SkillsLevel | SkillLevelEntry | TankLevel] = Field(..., discriminator="type")


class SkillPlansResponsePlanSchema(Schema):
    source: str | None
    levels: list[tuple[int, int]] | None
    ships: list[HullSchema] | None


class SkillPlansResponse(Schema):
    plans: list[SkillPlansResponsePlanSchema]


logger = get_extension_logger(__name__)
api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    SkillPlansAPIEndpoints(api)


class SkillPlansAPIEndpoints:

    tags = ["Skill Plans"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/skills/plans", response={200: SkillPlansResponse, 403: dict}, tags=self.tags)
        def get_skill_plans(request) -> SkillPlansResponse | tuple[int, dict]:
            if not request.user.has_perm("incursions.basic_waitlist"):
                logger.warning(f"User {request.user} denied access to skill plans")
                return 403, {"error": "Permission denied"}

            plans: list[SkillPlansResponsePlanSchema] = [
                SkillPlansResponsePlanSchema(
                    source=None,
                    levels=None,
                    ships=None,
                )
            ]

            logger.info(f"User {request.user} fetched {len(plans)} skill plan(s)")
            return SkillPlansResponse(plans=plans)

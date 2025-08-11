from corptools.models import EveItemType
from ninja import NinjaAPI, Schema

from allianceauth.services.hooks import get_extension_logger

from incursions.api.schema import CharacterSchema, HullSchema
from incursions.models.waitlist import FittingHistory, FleetActivity

logger = get_extension_logger(__name__)
api = NinjaAPI()


class ActivityEntrySchema(Schema):
    ship: HullSchema
    logged_at: int
    time_in_fleet: int


class ActivitySummaryEntrySchema(Schema):
    ship: HullSchema
    time_in_fleet: int


class ActivityResponse(Schema):
    activity: list[ActivityEntrySchema]
    summary: list[ActivitySummaryEntrySchema]


class FleetCompEntrySchema(Schema):
    ship: HullSchema
    character: CharacterSchema
    logged_at: int
    time_in_fleet: int
    is_boss: bool


class HistoryFleetCompResponse(Schema):
    fleets: dict[int, list[FleetCompEntrySchema]]


class XupHistoryLineSchema(Schema):
    logged_at: int
    dna: str
    implants: list[int]
    ship: HullSchema


class XupHistorySchema(Schema):
    xups: list[XupHistoryLineSchema]


class SkillHistoryResponseLineSchema(Schema):
    skill_id: int
    old_level: int
    new_level: int
    logged_at: int
    name: str


class SkillHistoryResponse(Schema):
    history: list[SkillHistoryResponseLineSchema]
    ids: dict[str, int]


def setup(api: NinjaAPI) -> None:
    HistoryAPIEndpoints(api)


class HistoryAPIEndpoints:

    tags = ["History"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/history/fleet", response=ActivityResponse, tags=self.tags)
        def fleet_history(request, character_id: int):
            if not request.user.has_perm("incursions.waitlist_history_view"):
                logger.warning(f"User {request.user} denied access to fleet history for character {character_id}")
                return 403, {"error": "Permission denied"}

            activities = FleetActivity.objects.filter(character_id=character_id).select_related("ship").order_by("-first_seen")
            time_by_ship: dict[int, int] = {}
            activity_entries: list[ActivityEntrySchema] = []

            for act in activities:
                time_in_fleet = act.last_seen - act.first_seen
                ship_id = act.ship.type_id
                ship_name = act.ship.name
                time_by_ship[ship_id] = time_by_ship.get(ship_id, 0) + time_in_fleet

                activity_entries.append(ActivityEntrySchema(
                    ship=HullSchema(id=ship_id, name=ship_name),
                    logged_at=act.first_seen,
                    time_in_fleet=time_in_fleet,
                ))

            summary_entries: list[ActivitySummaryEntrySchema] = [
                ActivitySummaryEntrySchema(ship=HullSchema(id=ship_id, name=EveItemType.objects.only("name").get(pk=ship_id).name), time_in_fleet=total_time)
                for ship_id, total_time in time_by_ship.items()
            ]
            summary_entries.sort(key=lambda s: s.time_in_fleet, reverse=True)

            logger.info(f"Fleet history returned for character {character_id} with {len(activity_entries)} entries")
            return {"activity": activity_entries, "summary": summary_entries}

        @api.get("/history/fleet-comp", response=HistoryFleetCompResponse, tags=self.tags)
        def fleet_comp(request, time: int):
            if not request.user.has_perm("incursions.waitlist_history_view"):
                logger.warning(f"User {request.user} denied access to fleet composition at time {time}")
                return 403, {"error": "Permission denied"}

            comp_entries = FleetActivity.objects.select_related("character", "ship", "fleet", "fleet__boss").filter(first_seen__lte=time, last_seen__gte=time)
            fleets: dict[int, list[FleetCompEntrySchema]] = {}

            for entry in comp_entries:
                fleet_id = entry.fleet.pk
                is_boss = entry.fleet.boss_id == entry.character.pk
                fleets.setdefault(fleet_id, []).append(FleetCompEntrySchema(
                    ship=HullSchema.from_orm(entry.ship),
                    character=CharacterSchema.from_orm(entry.character),
                    logged_at=entry.first_seen,
                    time_in_fleet=entry.last_seen - entry.first_seen,
                    is_boss=is_boss,
                ))

            logger.info(f"Fleet composition at {time} returned with {sum(len(v) for v in fleets.values())} members")
            return {"fleets": fleets}

        @api.get("/history/xup", response=XupHistorySchema, tags=self.tags)
        def xup_history(request, character_id: int):
            if not request.user.has_perm("incursions.waitlist_history_view"):
                logger.warning(f"User {request.user} denied access to XUP history for character {character_id}")
                return 403, {"error": "Permission denied"}

            xup_lines: list[XupHistoryLineSchema] = []
            fittings = FittingHistory.objects.filter(character_id=character_id).select_related("fit__ship", "implant_set").order_by("-pk")

            for xup in fittings:
                try:
                    implants_list = [int(i) for i in xup.implant_set.implants.split(':') if i]
                except Exception:
                    implants_list = []

                ship_schema = HullSchema().from_orm(xup.fit.ship)
                xup_lines.append(XupHistoryLineSchema(logged_at=xup.logged_at, dna=xup.fit.dna, implants=implants_list, ship=ship_schema))

            logger.info(f"XUP history returned for character {character_id} with {len(xup_lines)} entries")
            return {"xups": xup_lines}

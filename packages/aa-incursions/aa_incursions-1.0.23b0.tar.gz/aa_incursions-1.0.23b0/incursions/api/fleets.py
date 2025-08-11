from enum import Enum

from corptools.models import EveItemType
from ninja import NinjaAPI, Schema

from django.db import transaction
from django.http import Http404
from django.utils import timezone

from allianceauth.eveonline.models import EveCharacter
from allianceauth.framework.api.user import get_all_characters_from_user
from allianceauth.services.hooks import get_extension_logger

from incursions.api.schema import CharacterSchema, HullSchema
from incursions.models.waitlist import (
    ActiveFleet, Fleet, FleetSquad, WaitlistCategory,
)
from incursions.providers import (
    get_characters_character_id_fleet, kick_all_fleet_members,
)


class RoleEnum(str, Enum):
    FC = "fleet_commander"
    SC = "squad_commander"
    WC = "squad_member"
    MEMBER = "wing_commander"


class FleetStatusFleetSchema(Schema):
    id: int
    boss: CharacterSchema


class FleetStatusResponse(Schema):
    fleets: list[FleetStatusFleetSchema] | None


class FleetInfoSquadSchema(Schema):
    id: int
    name: str


class FleetInfoWingSchema(Schema):
    id: int
    name: str
    squads: list[FleetInfoSquadSchema]


class FleetInfoResponse(Schema):
    fleet_id: int
    wings: list[FleetInfoWingSchema]


class FleetMemberSchema(Schema):
    character_id: int
    character_name: str | None = None
    ship: HullSchema
    role: RoleEnum


class FleetCompSquadMembersSchema(Schema):
    id: int
    name: str
    members: list[FleetMemberSchema]
    boss: FleetMemberSchema | None = None


class FleetCompWingSchema(Schema):
    id: int
    name: str
    squads: list[FleetCompSquadMembersSchema]
    boss: FleetMemberSchema | None = None


class FleetCompResponse(Schema):
    id: int | None
    wings: list[FleetCompWingSchema] | None
    members: list[FleetMemberSchema] | None
    boss: FleetMemberSchema | None = None


class FleetMembersMemberSchema(Schema):
    character_id: int
    character_name: str | None = None
    ship: HullSchema
    wl_category: str | None = None
    category: str | None = None
    role: RoleEnum


class FleetMembersResponse(Schema):
    members: list[FleetMembersMemberSchema]


class RegisterRequest(Schema):
    character_id: int
    fleet_id: int
    assignments: dict[str, tuple[int, int]]


logger = get_extension_logger(__name__)
api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    FleetAPIEndpoints(api)


class FleetAPIEndpoints:

    tags = ["Fleets"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/fleet/status", response={200: FleetStatusResponse, 403: dict}, tags=self.tags)
        def fleet_status(request) -> tuple[int, dict]:
            # Called regularly
            if not request.user.has_perm("incursions.basic_waitlist"):
                logger.warning(f"User {request.user} denied access to fleet status")
                return 403, {"error": "Permission denied"}

            try:
                active_fleet = ActiveFleet.get_solo()
                fleet = active_fleet.fleet
                if fleet is None:
                    raise ActiveFleet.DoesNotExist
                logger.info(f"User {request.user} retrieved active fleet {fleet.pk if fleet else None}")
                return 200, FleetStatusResponse(fleets=[fleet])
            except (ActiveFleet.DoesNotExist, Fleet.DoesNotExist):
                logger.info(f"No active fleet for user {request.user}")
                return 200, FleetStatusResponse(fleets=None)

        @api.get("/fleet/info", response={200: FleetInfoResponse, 403: dict}, tags=self.tags)
        def fleet_info(request, character_id: int) -> tuple[int, dict]:
            # Called only by Register, loads extra DB info to then register a fleet later
            if not request.user.has_perm("incursions.waitlist_manage_waitlist"):
                logger.warning(f"User {request.user} denied access to fleet info")
                return 403, {"error": "Permission denied"}

            # ARIEL check if request.body.character_id is owned by request.user
            # Recheck this
            if EveCharacter.objects.get(character_id=character_id) not in get_all_characters_from_user(request.user):
                logger.warning(f"User {request.user} attempted to load info on a fleet with different character ID")
                return 403, {"error": "Permission denied"}

            esi_fleet = get_characters_character_id_fleet(character_id=character_id)

            if not esi_fleet:
                logger.error(f"Fleet not found for character {character_id}")
                raise Http404("Fleet not found")

            try:
                boss = EveCharacter.objects.get(character_id=character_id)
            except EveCharacter.DoesNotExist:
                boss = EveCharacter.objects.create_character(character_id=character_id)

            fleet, created = Fleet.objects.update_or_create(
                pk=esi_fleet.get("fleet_id"),
                defaults={
                    "boss": boss,
                    "open": True,
                    "closed": None,
                    "is_updating": True,
                    "last_updated": timezone.now(),
                }
            )

            fleet_wings = fleet.get_fleets_fleet_id_wings()
            wings = [
                FleetInfoWingSchema(
                    id=wing.get("id"),
                    name=wing.get("name"),
                    squads=[FleetInfoSquadSchema(id=s.get("id"), name=s.get("name")) for s in wing.get("squads", [])],
                )
                for wing in fleet_wings
            ]
            logger.info(f"Fleet info fetched for fleet {fleet.pk} by user {request.user}")
            return FleetInfoResponse(fleet_id=fleet.pk, wings=wings)

        @api.get("/fleet/fleetcomp", response={200: FleetCompResponse, 403: dict}, tags=self.tags)
        # FC FleetMembers (yes shitty naming)
        # Used for the full wing/squad/ship breakdown of the fleet
        #
        # Character ID is not used currently, as we only have one fleet at a time
        # Will be used to distinguish between multiple fleets in the future
        def fleet_composition(request, character_id: int) -> tuple[int, dict]:
            if not request.user.has_perm("incursions.waitlist_fleet_view"):
                logger.warning(f"User {request.user} denied access to fleet composition")
                return 403, {"error": "Permission denied"}

            try:
                active_fleet = ActiveFleet.get_solo()
                fleet = active_fleet.fleet
                if fleet is None:
                    raise ActiveFleet.DoesNotExist
                logger.info(f"User {request.user} retrieved active fleet {fleet.pk if fleet else None}")
            except (ActiveFleet.DoesNotExist, Fleet.DoesNotExist):
                logger.info(f"No active fleet for user {request.user}")
                return 404, {"error": "No active fleet found"}

            fleet_members = fleet.get_fleet_members()
            fleet_wings = fleet.get_fleets_fleet_id_wings()
            wings: list[FleetCompWingSchema] = []
            members: list[FleetMemberSchema] = []
            fleet_boss: FleetMemberSchema | None = None

            for wing in fleet_wings:
                squads: list[FleetCompSquadMembersSchema] = []
                wing_boss: FleetMemberSchema | None = None
                for squad in wing.get("squads", []):
                    squad_members: list[FleetMemberSchema] = []
                    squad_boss: FleetMemberSchema | None = None
                    for fm in fleet_members:  # For Each Wing+Squad, Loop through all fleet members and act on match
                        if fm.get("wing_id") == wing.get("id") and fm.get("squad_id") == squad.get("id"):
                            try:
                                character = EveCharacter.objects.only("character_name").get(character_id=fm.get("character_id"))
                                ship = EveItemType.objects.only("name").get(type_id=fm.get("ship_type_id"))
                            except EveCharacter.DoesNotExist:
                                EveCharacter.objects.create_character(character_id=fm.get("character_id"))
                                return 503, {"error": "Unknown Character  found, please try again later."}
                            except EveItemType.DoesNotExist:
                                EveItemType.objects.get_or_create_from_esi(fm.get("ship_type_id"))
                                return 503, {"error": "Unknown Ship found, please try again later"}
                            if fm.get("role") == "fleet_commander":
                                fleet_boss = FleetMemberSchema(character_id=fm.get("character_id"), character_name=character.character_name, ship=HullSchema(id=ship.pk, name=ship.name), role=fm.get("role"))
                            elif fm.get("role") == "wing_commander":
                                wing_boss = FleetMemberSchema(character_id=fm.get("character_id"), character_name=character.character_name, ship=HullSchema(id=ship.pk, name=ship.name), role=fm.get("role"),)
                            elif fm.get("role") == "squad_commander":
                                squad_boss = FleetMemberSchema(character_id=fm.get("character_id"), character_name=character.character_name, ship=HullSchema(id=ship.pk, name=ship.name), role=fm.get("role"),)
                                squad_members.append(FleetMemberSchema(character_id=fm.get("character_id"), character_name=character.character_name, ship=HullSchema(id=ship.pk, name=ship.name), role=fm.get("role"),))
                            else:
                                squad_members.append(FleetMemberSchema(character_id=fm.get("character_id"), character_name=character.character_name, ship=HullSchema(id=ship.pk, name=ship.name), role=fm.get("role"),))
                            members.append(FleetMemberSchema(  # Always append everyone to the master members list, used in frontend to reduce code
                                character_id=fm.get("character_id"),
                                name=character.character_name,
                                ship=HullSchema(id=ship.pk, name=ship.name),
                                role=fm.get("role"),
                            ))
                    squads.append(FleetCompSquadMembersSchema(id=squad.get("id"),name=squad.get("name"), members=squad_members, boss=squad_boss if squad_boss else None))
                wings.append(FleetCompWingSchema(id=wing.get("id"), name=wing.get("name"), squads=squads, boss=wing_boss if wing_boss else None))

            logger.info(f"Fleet composition fetched for fleet {fleet.pk} by user {request.user}")
            return 200, FleetCompResponse(wings=wings, id=fleet.pk, member=members, boss=fleet_boss if fleet_boss else None, members=members),

        @api.get("/fleet/members", response=FleetMembersResponse, tags=self.tags)
        # Waitlist useFleetComposition
        # Used for Waitlist Category Headers, simple fetch, number of ships, etc
        #
        # Character ID is not used currently, as we only have one fleet at a time
        # Will be used to distinguish between multiple fleets in the future
        def fleet_members(request, character_id: int) -> tuple[int, dict]:
            if not request.user.has_perm("incursions.waitlist_fleet_view"):
                logger.warning(f"User {request.user} denied access to fleet members")
                return 403, {"error": "Permission denied"}

            try:
                active_fleet = ActiveFleet.get_solo()
                fleet = active_fleet.fleet
                if fleet is None:
                    raise ActiveFleet.DoesNotExist
                logger.info(f"User {request.user} retrieved active fleet {fleet.pk if fleet else None}")
            except (ActiveFleet.DoesNotExist, Fleet.DoesNotExist):
                logger.info(f"No active fleet for user {request.user}")
                return 404, {"error": "No active fleet found"}

            fleet_members = fleet.get_fleet_members()
            wings = {w.get("id"): w.get("name") for w in fleet.get_fleets_fleet_id_wings()}
            members: list[FleetMembersMemberSchema] = []

            for fm in fleet_members:
                try:
                    char = EveCharacter.objects.only("character_name").get(character_id=fm.get("character_id"))
                    ship = EveItemType.objects.only("name").get(type_id=fm.get("ship_type_id"))
                    squad = FleetSquad.objects.only("category").get(squad_id=fm.get("squad_id"))
                except FleetSquad.DoesNotExist:
                    continue
                # These are intentionally just excepts, not get_or_create, i want this api to be performant for EVE reasons, but failing is fine
                except EveCharacter.DoesNotExist:
                    EveCharacter.objects.create_character(character_id=fm.get("character_id"))
                    return 503, {"error": "Unknown Character  found, please try again later."}
                except EveItemType.DoesNotExist:
                    EveItemType.objects.get_or_create_from_esi(fm.get("ship_type_id"))
                    return 503, {"error": "Unknown Ship found, please try again later"}

                members.append(FleetMembersMemberSchema(
                    character_id=fm.get("character_id"),
                    character_name=char.character_name,
                    ship=HullSchema(id=ship.pk, name=ship.name),
                    wl_category=squad.category.name,
                    category=f"{wings.get(fm.get('wing_id'))} - {fm.get('squad_name')}",
                    role=fm.get("role"),
                ))

            logger.info(f"Fleet members listed for fleet {fleet.pk} by user {request.user}")
            return FleetMembersResponse(members=members)

        @api.post("/fleet/register", tags=self.tags)
        def register_fleet(request, body: RegisterRequest) -> tuple[int, dict]:
            if not request.user.has_perm("incursions.waitlist_manage_waitlist"):
                logger.warning(f"User {request.user} denied fleet registration")
                return 403, {"error": "Permission denied"}

            # ARIEL check if request.body.character_id is owned by request.user
            # Recheck this
            if EveCharacter.objects.get(character_id=body.character_id) not in get_all_characters_from_user(request.user):
                logger.warning(f"User {request.user} attempted to register fleet with different character ID")
                return 403, {"error": "Permission denied"}

            with transaction.atomic():
                fleet, _ = Fleet.objects.select_for_update().update_or_create(
                    pk=body.fleet_id,
                    defaults={
                        "boss": EveCharacter.objects.get(character_id=body.character_id),
                        "open": True,
                        "closed": None,
                        "is_updating": True,
                        "last_updated": timezone.now(),
                    },
                )

                active_fleet = ActiveFleet.get_solo()
                active_fleet.fleet = fleet
                active_fleet.save(update_fields=["fleet"])

                for category, (wing_id, squad_id) in body.assignments.items():
                    cat = WaitlistCategory.objects.get(pk=category)
                    FleetSquad.objects.update_or_create(
                        fleet=fleet,
                        category=cat,
                        defaults={"wing_id": wing_id, "squad_id": squad_id},
                    )

            logger.info(f"Fleet {fleet.pk} registered and squads assigned by user {request.user}")
            return "OK"

        @api.post("/fleet/close", response={200: str, 403: dict, 404: dict}, tags=self.tags)
        def close_fleet(request, boss_character_id: int) -> tuple[int, dict]:
            if not request.user.has_perm("incursions.waitlist_manage_waitlist"):
                logger.warning(f"User {request.user} denied closing fleet")
                return 403, {"error": "Permission denied"}

            active_fleet = ActiveFleet.get_solo().fleet
            if active_fleet is None:
                logger.warning(f"User {request.user} attempted to close a fleet but no active fleet was found")
                return 404, {"error": "No active fleet found"}

            active_fleet.open = False
            active_fleet.closed = timezone.now()
            active_fleet.is_updating = False
            active_fleet.last_updated = timezone.now()
            active_fleet.save(update_fields=["open", "closed", "is_updating", "last_updated"])

            count = kick_all_fleet_members(boss_character_id=active_fleet.boss.character_id, fleet_id=active_fleet.pk)
            logger.info(f"User {request.user} closed fleet {active_fleet.pk} and kicked {count} members")
            return 200, f"Kicked {count} Fleet Members"

import json
from datetime import datetime

from corptools.models import EveItemType
from ninja import NinjaAPI, Schema

from django.db import transaction
from django.db.models import Count, Prefetch
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from allianceauth.eveonline.models import EveCharacter
from allianceauth.framework.api.evecharacter import (
    get_main_character_from_evecharacter,
)
from allianceauth.framework.api.user import (
    get_all_characters_from_user, get_main_character_from_user,
)
from allianceauth.services.hooks import get_extension_logger

from incursions.api.badges import BadgeSchema
from incursions.api.helpers.fittings import FittingParser
from incursions.api.helpers.sse import SSEClient, SSEEvent
from incursions.api.schema import CharacterSchema, HullSchema
from incursions.app_settings import SSE_SECRET, SSE_SITE_URL
from incursions.models.waitlist import (
    ActiveFleet, ApprovedFitting, CharacterBadges, Fitting, FleetSquad,
    ImplantSet, Waitlist, WaitlistCategory, WaitlistCategoryRule,
    WaitlistEntry, WaitlistEntryFit,
)
from incursions.providers import get_character_implants, invite_to_fleet

logger = get_extension_logger(__name__)
sse_client = SSEClient(SSE_SITE_URL, SSE_SECRET)


# Schemas
class WaitlistEntryFitSchema(Schema):
    id: int
    approved: bool
    category: str
    dna: str
    ship: HullSchema
    character: CharacterSchema
    hours_in_fleet: int
    review_comment: str | None = None
    implants: list[int]
    fit_analysis: dict | None = None
    is_alt: bool
    messagexup: str | None = None
    badges: list[BadgeSchema]


class WaitlistEntrySchema(Schema):
    id: int
    main_character: CharacterSchema | None = None
    joined_at: datetime
    can_remove: bool
    fits: list[WaitlistEntryFitSchema]


class WaitlistResponse(Schema):
    open: bool
    waitlist: list[WaitlistEntrySchema] | None = None
    categories: list[str]


class XupRequest(Schema):
    waitlist_id: int
    character_id: int
    eft: str
    is_alt: bool
    messagexup: str


class RemoveWaitlistEntryRequest(Schema):
    id: int


class RemoveWaitlistEntryFitRequest(Schema):
    id: int


class InviteRequest(Schema):
    id: int


class ApproveRequest(Schema):
    id: int


class RejectRequest(Schema):
    id: int
    review_comment: str


class SetOpenRequest(Schema):
    open: bool
    waitlist_id: int


class EmptyWaitlistRequest(Schema):
    waitlist_id: int


class WaitlistUpdateSchema(Schema):
    waitlist_id: int


api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    WaitlistAPIEndpoints(api)


class WaitlistAPIEndpoints:
    tags = ["Waitlist"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/waitlist", response={200: WaitlistResponse, 403: dict, 404: dict}, tags=self.tags)
        def get_waitlist(request: HttpRequest) -> WaitlistResponse | tuple[int, dict]:
            logger.info("Fetching waitlist for user %s", request.user)
            if not request.user.has_perm("incursions.basic_waitlist"):
                logger.warning("User %s does not have permission incursions.basic_waitlist", request.user)
                return 403, {"error": "Permission denied"}

            waitlist = Waitlist.get_solo()
            categories: list[str] = list(WaitlistCategory.objects.values_list("name", flat=True))
            request_main_character = get_main_character_from_user(request.user)

            context_manager: bool = request.user.has_perm("incursions.waitlist_manage_waitlist")
            context_wl_approver: bool = context_manager or request.user.has_perm("incursions.waitlist_manage_waitlist_approve_fits")
            context_implants: bool = context_wl_approver or request.user.has_perm("incursions.waitlist_implants_view")
            context_stats: bool = context_wl_approver or request.user.has_perm("incursions.waitlist_stats_view")
            context_quantity: bool = context_wl_approver or request.user.has_perm("incursions.waitlist_context_a")
            context_ship: bool = context_wl_approver or request.user.has_perm("incursions.waitlist_context_b")
            context_time: bool = context_wl_approver or request.user.has_perm("incursions.waitlist_context_c")
            context_name: bool = context_wl_approver or request.user.has_perm("incursions.waitlist_context_d")

            if not waitlist.is_open:
                logger.info("Waitlist is closed.")
                return WaitlistResponse(open=False, waitlist=None, categories=categories)

            waitlist_entries = WaitlistEntry.objects.filter(waitlist=waitlist).select_related("main_character", "waitlist")

            response_waitlist: list[WaitlistEntrySchema] = []
            for waitlist_entry in waitlist_entries:
                fits_data: list[WaitlistEntryFitSchema] = []
                is_self: bool = request_main_character == waitlist_entry.main_character
                for wl_fit in WaitlistEntryFit.objects.filter(
                    waitlist_entry=waitlist_entry
                ).select_related(
                    "implant_set", "fit", "category", "character"
                ).prefetch_related(
                    Prefetch(
                        "character__incursions_badge",
                        queryset=CharacterBadges.objects.select_related("badge"),
                        to_attr="prefetched_badges"
                    )
                ):

                    if wl_fit.implant_set and wl_fit.implant_set.implants:
                        implants_list = json.loads(wl_fit.implant_set.implants)
                    else:
                        implants_list: list[str] = []

                    fits_data.append(
                        WaitlistEntryFitSchema(
                            id=wl_fit.pk,
                            approved=wl_fit.approved,
                            category=wl_fit.category.name,
                            ship=HullSchema(
                                id=wl_fit.fit.ship.type_id if (is_self or context_wl_approver or context_ship) else 670,  # Capsule for memes (and a real icon)
                                name=wl_fit.fit.ship.name if (is_self or context_wl_approver or context_ship) else "Hidden",
                            ),
                            character=CharacterSchema(
                                character_name=wl_fit.character.character_name if (is_self or context_name) else "Hidden",
                                character_id=wl_fit.character.character_id if (is_self or context_name) else 0,
                                corporation_id=wl_fit.character.corporation_id if (is_self or context_name) else 0,
                            ),
                            hours_in_fleet=wl_fit.cached_time_in_fleet // 3600 if context_stats else 0,
                            review_comment=wl_fit.review_comment if (is_self or context_wl_approver) else None,
                            dna=wl_fit.fit.dna if (is_self or context_wl_approver) else "",
                            implants=implants_list if (is_self or context_wl_approver or context_implants) else [],
                            fit_analysis=wl_fit.fit_analysis if (is_self or context_wl_approver or context_implants) else None,
                            is_alt=wl_fit.is_alt if (is_self or context_wl_approver or context_quantity) else False,
                            messagexup=wl_fit.messagexup if (is_self or context_wl_approver) else None,
                            badges=[BadgeSchema.from_orm(cb.badge) for cb in getattr(wl_fit.character, "prefetched_badges", [])]
                        )
                    )
                response_waitlist.append(
                    WaitlistEntrySchema(
                        id=waitlist_entry.pk,
                        main_character=CharacterSchema(
                            character_name=waitlist_entry.main_character.character_name if (is_self or context_name) else "Hidden",
                            character_id=waitlist_entry.main_character.character_id if (is_self or context_name) else 0,
                        ),
                        joined_at=waitlist_entry.joined_at if (is_self or context_time) else now(),
                        can_remove=True if (is_self or context_wl_approver) else False,
                        fits=fits_data,
                    )
                )
            logger.info("Returning waitlist with %d entries", len(response_waitlist))
            return WaitlistResponse(open=True, waitlist=response_waitlist, categories=categories)

        @api.post("/waitlist/xup", response={200: dict, 403: dict, 404: dict}, tags=self.tags)
        def xup(request: HttpRequest, payload: XupRequest) -> tuple[int, dict]:
            logger.info(
                "Processing xup for waitlist_id: %s and character_id: %s",
                payload.waitlist_id,
                payload.character_id,
            )
            if not request.user.has_perm("incursions.basic_waitlist"):
                logger.warning("User %s lacks basic_waitlist permission", request.user)
                return 403, {"error": "Permission denied"}

            waitlist = Waitlist.get_solo()
            character = get_object_or_404(EveCharacter, character_id=payload.character_id)
            fitting_parser = FittingParser.from_eft(payload.eft)

            fitting, _ = Fitting.objects.get_or_create(
                dna=fitting_parser.to_dna(),
                ship=EveItemType.objects.get_or_create_from_esi(fitting_parser.ship)[0],
            )
            implant_set, _ = ImplantSet.objects.get_or_create(implants=list(get_character_implants(character.character_id)[0]))
            try:
                rule = WaitlistCategoryRule.objects.select_related("waitlist_category").get(ship=fitting.ship)
                waitlist_category = rule.waitlist_category
            except WaitlistCategoryRule.DoesNotExist:
                waitlist_category, _ = WaitlistCategory.objects.get_or_create(name="Sponge")

            try:
                fit_analysis = fitting_parser.to_analysis(doctrine=FittingParser.from_dna(ApprovedFitting.objects.get(ship=fitting.ship).dna))
                # Ariel Badges Add Bad Fit?
            except ApprovedFitting.DoesNotExist:
                fit_analysis = {}
            with transaction.atomic():
                waitlist_entry, _ = WaitlistEntry.objects.get_or_create(main_character=get_main_character_from_evecharacter(character), waitlist=waitlist)
                new_fit, created = WaitlistEntryFit.objects.update_or_create(
                    character=character,
                    waitlist_entry=waitlist_entry,
                    defaults={
                        # "approved": False,
                        "category": waitlist_category,
                        "cached_time_in_fleet": 0,
                        "is_alt": payload.is_alt,  # ARIEL i can probably calculate this on my end, not frontend
                        "messagexup": payload.messagexup,
                        "tags": "",  # ARIEL i can probably calculate this on my end, not frontend
                        "fit": fitting,
                        "implant_set": implant_set,
                        "fit_analysis": fit_analysis if fit_analysis else {},
                    }
                )
            sse_payload = WaitlistUpdateSchema(waitlist_id=waitlist.pk).model_dump()
            sse_client.submit([SSEEvent.new_json(
                topic="waitlist", event="waitlist_update", data=sse_payload
            )])
            boss_char = get_main_character_from_evecharacter(ActiveFleet.get_solo().fleet.boss)

            if created is True:
                sse_client.submit([SSEEvent.new(
                    topic=f"account;{boss_char.character_id}",
                    event="message",
                    data="New x-up in waitlist",
                )])
                logger.info("X-up recorded with fit_id %s", new_fit.pk)
                return 200, {"status": "X-up recorded", "fit_id": new_fit.pk}
            else:
                sse_client.submit([SSEEvent.new(
                    topic=f"account;{boss_char.character_id}",
                    event="message",
                    data="Updated x-up in waitlist",
                )])
                logger.info("X-up updated with fit_id %s", new_fit.pk)
                return 200, {"status": "X-up updated", "fit_id": new_fit.pk}

        @api.post("/waitlist/remove_waitlistentry", response={200: dict, 403: dict}, tags=self.tags)
        def remove_waitlistentry(request: HttpRequest, payload: RemoveWaitlistEntryRequest) -> tuple[int, dict]:
            # Called by Self, this is the big ol remove entry button
            # Drops the whole WL Entry, + all associated fits
            logger.info("Removing waitlist entry x with id %s", payload.id)

            waitlist = Waitlist.get_solo()

            waitlist_entry = WaitlistEntry.objects.filter(pk=payload.id).first()
            if not waitlist_entry:
                logger.warning("Waitlist entry %s does not exist", payload.id)
                return 404, {"error": "Waitlist entry not found"}

            if not (
                waitlist_entry.main_character == get_main_character_from_user(request.user)
                or request.user.has_perm("incursions.waitlist_manage_waitlist")
            ):
                logger.warning("User %s not authorized to remove waitlist entry %s", request.user, payload.id)
                return 403, {"error": "Permission denied"}

            with transaction.atomic():
                waitlist_entry.delete()

            sse_payload = WaitlistUpdateSchema(waitlist_id=waitlist.pk).model_dump()
            sse_client.submit(
                [SSEEvent.new_json(topic="waitlist", event="waitlist_update", data=sse_payload)]
            )
            logger.info("Waitlist entry %s removed", payload.id)
            return 200, {"status": "Waitlist X-Up removed"}

        @api.post("/waitlist/remove_waitlistentryfit", response={200: dict, 403: dict}, tags=self.tags)
        def remove_waitlistentryfit(request: HttpRequest, payload: RemoveWaitlistEntryFitRequest) -> tuple[int, dict]:
            # This means an FC is removing your fit, not usually called by self
            logger.info("Removing fit with id %s", payload.id)
            entryfit = get_object_or_404(WaitlistEntryFit, pk=payload.id)
            waitlist = Waitlist.get_solo()

            if not (entryfit.character in get_all_characters_from_user(request.user) or request.user.has_perm("incursions.waitlist_manage_waitlist")):
                logger.warning("User %s not authorized to remove fit %s", request.user, payload.id)
                return 403, {"error": "Permission denied"}

            with transaction.atomic():
                WaitlistEntryFit.objects.filter(pk=payload.id).delete()
                WaitlistEntry.objects.annotate(fit_count=Count('waitlistentryfit')).filter(fit_count=0).delete()

            sse_payload = WaitlistUpdateSchema(waitlist_id=waitlist.pk).model_dump()
            sse_client.submit([SSEEvent.new_json(topic="waitlist", event="waitlist_update", data=sse_payload)])
            logger.info("Waitlist fit %s removed", payload.id)
            return 200, {"status": "Waitlist X-Up Fit removed"}

        @api.post("/waitlist/invite", response={200: dict, 403: dict}, tags=self.tags)
        def invite(request: HttpRequest, payload: InviteRequest) -> tuple[int, dict]:
            logger.info(f"Inviting waitlist entry fit id:{payload.id}", )
            if not request.user.has_perm("incursions.waitlist_manage_waitlist"):
                logger.warning("User %s not authorized to invite", request.user)
                return 403, {"error": "Permission denied"}

            active_fleet = ActiveFleet.get_solo()

            if active_fleet.fleet.boss not in get_all_characters_from_user(request.user):
                logger.warning("User %s is not fleet boss", request.user)
                return 403, {"error": "Permission denied"}

            waitlist_entry_fit = get_object_or_404(WaitlistEntryFit, pk=payload.id)
            fleet_squad = get_object_or_404(FleetSquad, fleet=active_fleet.fleet, category__name=waitlist_entry_fit.category.name)
            squad_id = fleet_squad.squad_id
            wing_id = fleet_squad.wing_id
            logger.info(f"Inviting character:{waitlist_entry_fit.character.character_id} for waitlist entry fit id:{payload.id}")

            invite_to_fleet(
                boss_character_id=active_fleet.fleet.boss.character_id,
                fleet_id=active_fleet.fleet.pk,
                character_id=waitlist_entry_fit.character.character_id,
                squad_id=squad_id if squad_id else None,
                wing_id=wing_id if wing_id else None,
                role="squad_member",
            )
            sse_client.submit([SSEEvent.new(
                topic=f"account;{get_main_character_from_evecharacter(waitlist_entry_fit.character).character_id}",
                event="wakeup",
                data=f"{active_fleet.fleet.boss.character_name} has invited your {waitlist_entry_fit.fit.ship.name} to fleet.",
            )])
            logger.info(f"Character:{waitlist_entry_fit.character.character_id} invited for waitlist entry:{payload.id}")
            return 200, {"status": f"Character {waitlist_entry_fit.character.character_id} invited to waitlist entry {payload.id}"}

        @api.post("/waitlist/approve", tags=self.tags)
        def approve_fit(request: HttpRequest, payload: ApproveRequest) -> dict:
            logger.info("Approving fit with id %s", payload.id)
            if not (
                request.user.has_perm("incursions.waitlist_manage_waitlist")
                or request.user.has_perm("incursions.waitlist_manage_waitlist_approve_fits")
            ):
                logger.warning("User %s not authorized to approve fit %s", request.user, payload.id)
                return 403, {"error": "Permission denied"}
            with transaction.atomic():
                fit = get_object_or_404(WaitlistEntryFit, pk=payload.id)
                fit.approved = True
                fit.save(update_fields=["approved"])
            sse_payload = WaitlistUpdateSchema(waitlist_id=fit.waitlist_entry.pk).model_dump()
            sse_client.submit(
                [SSEEvent.new_json(topic="waitlist", event="waitlist_update", data=sse_payload)]
            )
            logger.info("Fit %s approved", payload.id)
            return {"status": f"Fit {fit.pk} approved"}

        @api.post("/waitlist/reject", tags=self.tags)
        def reject_fit(request: HttpRequest, payload: RejectRequest) -> tuple[int, dict]:
            logger.info("Rejecting fit with id %s", payload.id)
            if not (
                request.user.has_perm("incursions.waitlist_manage_waitlist")
                or request.user.has_perm("incursions.waitlist_manage_waitlist_approve_fits")
            ):
                logger.warning("User %s not authorized to reject fit %s", request.user, payload.id)
                return 403, {"error": "Permission denied"}
            with transaction.atomic():
                fit = get_object_or_404(WaitlistEntryFit, pk=payload.id)
                fit.approved = False
                fit.review_comment = payload.review_comment
                fit.save(update_fields=["approved", "review_comment"])
            sse_payload = WaitlistUpdateSchema(waitlist_id=fit.waitlist_entry.pk).model_dump()
            sse_client.submit(
                [SSEEvent.new_json(topic="waitlist", event="waitlist_update", data=sse_payload)]
            )
            logger.info("Fit %s rejected", payload.id)
            return 200, {"status": f"Fit {fit.pk} rejected"}

        @api.post("/waitlist/set_open", tags=self.tags)
        def set_open(request: HttpRequest, payload: SetOpenRequest) -> tuple[int, str | dict]:
            logger.info("Setting waitlist %s open state to %s", payload.waitlist_id, payload.open)
            if not request.user.has_perm("incursions.waitlist_manage_waitlist"):
                logger.warning("User %s not authorized to set open state", request.user)
                return 403, {"error": "Permission denied"}

            waitlist = Waitlist.get_solo()
            waitlist.is_open = payload.open
            waitlist.save(update_fields=["is_open"])
            sse_payload = WaitlistUpdateSchema(waitlist_id=waitlist.pk).model_dump()
            sse_client.submit(
                [SSEEvent.new_json(topic="waitlist", event="open", data=sse_payload)]
            )
            sse_client.submit(
                [SSEEvent.new_json(topic="waitlist", event="waitlist_update", data=sse_payload)]
            )
            logger.info("Waitlist %s open state set to %s", payload.waitlist_id, payload.open)
            return 200, f"Waitlist is now {'Open' if payload.open is True else 'Closed'}."

        @api.post("/waitlist/empty", tags=self.tags)
        def empty_waitlist(request: HttpRequest, payload: EmptyWaitlistRequest) -> dict:
            logger.info("Emptying waitlist with id %s", payload.waitlist_id)
            if not request.user.has_perm("incursions.waitlist_manage_waitlist"):
                logger.warning("User %s not authorized to empty waitlist", request.user)
                return 403, {"error": "Permission denied"}

            waitlist = Waitlist.get_solo()

            with transaction.atomic():
                WaitlistEntryFit.objects.filter(waitlist_entry__waitlist=waitlist).delete()
                WaitlistEntry.objects.filter(waitlist=waitlist).delete()
                waitlist.is_open = False
                waitlist.save()

            sse_payload = WaitlistUpdateSchema(waitlist_id=waitlist.pk).model_dump()
            sse_client.submit(
                [SSEEvent.new_json(topic="waitlist", event="waitlist_update", data=sse_payload)]
            )
            logger.info("Waitlist %s emptied", payload.waitlist_id)
            return 200, {"status": "OK"}

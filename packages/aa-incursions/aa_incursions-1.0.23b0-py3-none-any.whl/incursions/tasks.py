from datetime import datetime, timezone

from celery import shared_task
from corptools.models import EveItemType, MapConstellation, MapSystem
from ninja import Schema

from django.db import IntegrityError, transaction
from django.db.models import Count
from django.utils.timezone import now

from allianceauth.eveonline.models import EveCharacter, EveFactionInfo
from allianceauth.services.hooks import get_extension_logger
from allianceauth.services.tasks import QueueOnce

from incursions.api.helpers.sse import SSEClient, SSEEvent
from incursions.api.waitlist import WaitlistUpdateSchema
from incursions.app_settings import SSE_SECRET, SSE_SITE_URL
from incursions.helpers import (
    embed_boss_spawned, embed_ended, embed_established,
    embed_established_addendum, embed_mobilizing, embed_waitlist_state,
    embed_withdrawing,
)
from incursions.models.incursion import (
    Incursion, IncursionInfluence, IncursionsConfig,
)
from incursions.models.waitlist import (
    ActiveFleet, Fleet, FleetActivity, Waitlist, WaitlistEntry,
    WaitlistEntryFit,
)
from incursions.providers import get_incursions_incursions

logger = get_extension_logger(__name__)
sse_client = SSEClient(SSE_SITE_URL, SSE_SECRET)


class NewFleetCompSchema(Schema):
    fleet_id: int


@shared_task(base=QueueOnce)
def update_incursions() -> None:
    incursions, response = get_incursions_incursions()
    actives = []
    for incursion in incursions:
        actives.append(incursion['constellation_id'])
        try:
            # Get, because i need to do more steps than an update_or_create would let me
            # This chunk is purely for when incursions change states.
            # Also incursions have no unique id.... wtf ccp
            i = Incursion.objects.get(
                constellation=MapConstellation.objects.get(constellation_id=incursion['constellation_id']),
                ended_timestamp__isnull=True)
            if incursion['state'] == "established":
                # This is still just an established incursion, nothing to act on
                pass
            elif incursion['state'] == "mobilizing" and i.state != Incursion.States.MOBILIZING:
                i.mobilizing_timestamp = datetime.strptime(
                    str(response.headers['Last-Modified']), '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=timezone.utc)
                i.state = Incursion.States.MOBILIZING
                if i.has_boss == "true":
                    i.has_boss = True
                i.save(update_fields=["mobilizing_timestamp", "state"])
            elif incursion['state'] == "withdrawing" and i.state != Incursion.States.WITHDRAWING:
                i.withdrawing_timestamp = datetime.strptime(
                    str(response.headers['Last-Modified']), '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=timezone.utc)
                i.state = Incursion.States.WITHDRAWING
                if i.has_boss == "true":
                    i.has_boss = True
                i.save(update_fields=["withdrawing_timestamp", "state"])
            else:
                # ????
                pass
            try:
                IncursionInfluence.objects.create(
                    incursion=i,
                    influence=incursion['influence'],
                    timestamp=datetime.strptime(
                        str(response.headers['Last-Modified']), '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=timezone.utc))
            except IntegrityError:
                # If we call this task too often cache will return the same influence
                pass
        except Incursion.DoesNotExist:
            # Create an Incursion, It does not exist.
            i = Incursion.objects.create(
                constellation=MapConstellation.objects.get(constellation_id=incursion['constellation_id']),
                faction=EveFactionInfo.objects.get_or_create(faction_id=incursion['faction_id'])[0],
                has_boss=True if incursion['has_boss'] == "true" else False,
                staging_solar_system=MapSystem.objects.get(system_id=incursion['staging_solar_system_id']),
                state=incursion['state'],
                type=incursion['type'],
                established_timestamp=datetime.strptime(
                    str(response.headers['Last-Modified']), '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=timezone.utc)
            )
            # We need to also set the mobilizing and withdrawing state here
            # This is purely for new installs, bcoz partially complete incursions
            if incursion['state'] == "mobilizing":
                i.mobilizing_timestamp = datetime.strptime(
                    str(response.headers['Last-Modified']), '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=timezone.utc)
                i.save(update_fields=["mobilizing_timestamp"])
            elif incursion['state'] == "withdrawing ":
                i.mobilizing_timestamp = datetime.strptime(
                    str(response.headers['Last-Modified']), '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=timezone.utc)
                i.withdrawing_timestamp = datetime.strptime(
                    str(response.headers['Last-Modified']), '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=timezone.utc)
                i.save(update_fields=["withdrawing_timestamp", "mobilizing_timestamp"])
            try:
                IncursionInfluence.objects.create(
                    incursion=i,
                    influence=incursion['influence'],
                    timestamp=datetime.strptime(
                        str(response.headers['Last-Modified']), '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=timezone.utc))
            except IntegrityError:
                # If we call this task too often cache will return the same influence
                pass

    for ended in Incursion.objects.filter(ended_timestamp__isnull=True).exclude(constellation_id__in=actives):
        # Cant use update here, need to fire signals
        ended.ended_timestamp = datetime.strptime(
            str(response.headers['Last-Modified']), '%a, %d %b %Y %H:%M:%S %Z')
        ended.state = Incursion.States.ENDED
        ended.save(update_fields=["ended_timestamp", "state"])


@shared_task
def incursion_established(incursion_pk: int) -> None:
    incursion = Incursion.objects.get(pk=incursion_pk)
    for webhook in IncursionsConfig.get_solo().status_webhooks.all():
        if incursion.is_high_sec == webhook.security_high:
            webhook.send_embed(embed=embed_established(incursion))
            webhook.send_embed(embed=embed_established_addendum(incursion))
        elif incursion.is_low_sec == webhook.security_low:
            webhook.send_embed(embed=embed_established(incursion))
            webhook.send_embed(embed=embed_established_addendum(incursion))
        elif incursion.is_null_sec == webhook.security_null:
            webhook.send_embed(embed=embed_established(incursion))
            webhook.send_embed(embed=embed_established_addendum(incursion))


@shared_task
def incursion_mobilizing(incursion_pk: int) -> None:
    incursion = Incursion.objects.get(pk=incursion_pk)
    for webhook in IncursionsConfig.get_solo().status_webhooks.all():
        if incursion.is_high_sec == webhook.security_high:
            webhook.send_embed(embed=embed_mobilizing(incursion))
        elif incursion.is_low_sec == webhook.security_low:
            webhook.send_embed(embed=embed_mobilizing(incursion))
        elif incursion.is_null_sec == webhook.security_null:
            webhook.send_embed(embed=embed_mobilizing(incursion))


@shared_task
def incursion_withdrawing(incursion_pk: int) -> None:
    incursion = Incursion.objects.get(pk=incursion_pk)
    for webhook in IncursionsConfig.get_solo().status_webhooks.all():
        if incursion.is_high_sec == webhook.security_high:
            webhook.send_embed(embed=embed_withdrawing(incursion))
        elif incursion.is_low_sec == webhook.security_low:
            webhook.send_embed(embed=embed_withdrawing(incursion))
        elif incursion.is_null_sec == webhook.security_null:
            webhook.send_embed(embed=embed_withdrawing(incursion))


@shared_task
def incursion_ended(incursion_pk: int) -> None:
    incursion = Incursion.objects.get(pk=incursion_pk)
    for webhook in IncursionsConfig.get_solo().status_webhooks.all():
        if incursion.is_high_sec == webhook.security_high:
            webhook.send_embed(embed=embed_ended(incursion))
        elif incursion.is_low_sec == webhook.security_low:
            webhook.send_embed(embed=embed_ended(incursion))
        elif incursion.is_null_sec == webhook.security_null:
            webhook.send_embed(embed=embed_ended(incursion))


@shared_task
def incursion_boss_spawned(incursion_pk: int) -> None:
    incursion = Incursion.objects.get(pk=incursion_pk)
    for webhook in IncursionsConfig.get_solo().status_webhooks.all():
        if incursion.is_high_sec == webhook.security_high:
            webhook.send_embed(embed=embed_boss_spawned(incursion))
        elif incursion.is_low_sec == webhook.security_low:
            webhook.send_embed(embed=embed_boss_spawned(incursion))
        elif incursion.is_null_sec == webhook.security_null:
            webhook.send_embed(embed=embed_boss_spawned(incursion))


@shared_task
def waitlist_state(waitlist_pk: int, is_open: bool) -> None:
    waitlist = Waitlist.get_solo()
    for webhook in IncursionsConfig.get_solo().waitlist_webhooks.all():
        webhook.send_embed(embed=embed_waitlist_state(waitlist=waitlist, is_open=is_open))


@shared_task(base=QueueOnce)
def update_all_fleets() -> None:

    fleet = ActiveFleet.get_solo().fleet
    update_fleet(fleet.pk)


def update_fleet(fleet_id: int) -> None:

    fleet = Fleet.objects.select_related('boss').get(pk=fleet_id)

    if fleet.is_updating is False:
        return

    new_comp_detected = False
    changed_waitlists = False
    waitlist = Waitlist.get_solo()

    # ARIEL: this wants much more error handling of various cases
    # Sometimes ESI is unavailable etc, rn it fails once and shuts down
    try:
        esi_fleet = fleet.get_fleet_members()
        fleet.last_updated = now()
        fleet.save(update_fields=["last_updated"])
    except Exception as e:
        logger.error(f"Fleet {fleet.pk} failed to get fleet esi: {e}")
        fleet.is_updating = False
        fleet.save(update_fields=["is_updating"])
        return

    fleet_members = {m['character_id']: m for m in esi_fleet}
    fleet_member_ids = list(fleet_members.keys())

    old_fleet_members = FleetActivity.objects.filter(fleet=fleet, has_left=False).values_list('character_id', flat=True)

    # Clean waitlist
    with transaction.atomic():
        count, deleted = WaitlistEntryFit.objects.filter(character__character_id__in=fleet_member_ids).delete()
        WaitlistEntry.objects.annotate(fit_count=Count('waitlistentryfit')).filter(fit_count=0).delete()

    if count > 0:
        changed_waitlists = True

    # Update fleet composition
    with transaction.atomic():

        min_required = 5  # ARIEL replace this with a config

        if len(fleet_members) < min_required:
            return

        for char_id, fleet_member in fleet_members.items():
            fa, created = FleetActivity.objects.update_or_create(
                character=EveCharacter.objects.get(character_id=char_id),
                fleet=fleet,
                # ship_id=fleet_member['ship_type_id'],  # Not sure how i want to handle ship swaps
                defaults={
                    "ship": EveItemType.objects.get_or_create_from_esi(eve_id=fleet_member['ship_type_id'])[0],
                    # "first_seen": now(),  # auto_now_add
                    "last_seen": now(),
                    "is_boss": fleet.boss.character_id == char_id,
                    "has_left": False,
                })
            if created:
                new_comp_detected = True

        updated_count = FleetActivity.objects.filter(
            character_id__in=old_fleet_members,
            fleet=fleet
        ).exclude(
            character_id__in=fleet_member_ids
        ).update(
            has_left=True,
            last_seen=now(),
        )
        if updated_count > 0:
            new_comp_detected = True

    # Notify frontend via SSE or signals

    if new_comp_detected:
        sse_payload = NewFleetCompSchema(fleet_id=waitlist.pk).model_dump()
        sse_client.submit([SSEEvent.new_json(topic="fleet_comp", event="comp_update", data=sse_payload)])
    if changed_waitlists:
        sse_payload = WaitlistUpdateSchema(waitlist_id=waitlist.pk).model_dump()
        sse_client.submit([SSEEvent.new_json(topic="waitlist", event="waitlist_update", data=sse_payload)])

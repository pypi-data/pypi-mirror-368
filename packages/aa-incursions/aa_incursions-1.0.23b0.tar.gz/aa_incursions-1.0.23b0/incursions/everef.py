import bz2
import json
import lzma
import os

from corptools.models import MapConstellation, MapSystem

from django.db import IntegrityError
from django.utils import timezone

from allianceauth.eveonline.models import EveFactionInfo
from allianceauth.services.hooks import get_extension_logger

from incursions.models.incursion import Incursion, IncursionInfluence

from .static_data import incursion_constellations

logger = get_extension_logger(__name__)


EVEREF_STAGING_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'data.everef.net/incursions/history/')


def import_staging_history(dir: str = EVEREF_STAGING_FOLDER):
    for entry in sorted(os.scandir(dir), key=lambda e: e.name):
        if entry.name.startswith('incursions-') and entry.is_file():
            with bz2.open(entry) as f:
                data = f.read()
                magic_time = timezone.datetime.strptime(entry.name.removesuffix(".json.bz2").removeprefix(
                    "incursions-"), '%Y-%m-%d_%H-%M-%S').replace(tzinfo=timezone.utc)
                print(magic_time)
                # 2024-04-06_00-00-01
                # %Y-%m-%d_%H-%M-%S
                for incursion in json.loads(data):
                    # [{"constellation_id":20000651,"faction_id":500019,"has_boss":false,"infested_solar_systems":[30004459,30004460,30004461,30004462,30004463,30004464],"influence":0.0,"staging_solar_system_id":30004464,"state":"mobilizing","type":"Incursion"},{"constellation_id":20000520,"faction_id":500019,"has_boss":true,"infested_solar_systems":[30003565,30003566,30003567,30003568,30003569,30003570,30003571,30003572],"influence":1.0,"staging_solar_system_id":30003572,"state":"mobilizing","type":"Incursion"},{"constellation_id":20000173,"faction_id":500019,"has_boss":false,"infested_solar_systems":[30001184,30001185,30001186,30001187,30001182,30001183],"influence":0.0,"staging_solar_system_id":30001186,"state":"mobilizing","type":"Incursion"},{"constellation_id":20000618,"faction_id":500019,"has_boss":false,"infested_solar_systems":[30004224,30004225,30004226,30004227,30004228,30004229,30004222,30004223],"influence":0.32516667656600473,"staging_solar_system_id":30004227,"state":"established","type":"Incursion"}]
                    # I have to apply my own logic to essentially _backdate_ the inserts at a historical point in time.
                    if incursion['state'] == "established":
                        try:
                            i = Incursion.objects.get(
                                established_timestamp__date__gte=magic_time.date() - timezone.timedelta(days=5),
                                established_timestamp__date__lte=magic_time.date() + timezone.timedelta(days=5),
                                constellation=MapConstellation.objects.get(constellation_id=incursion['constellation_id']))
                            continue
                        except Incursion.DoesNotExist:
                            i = Incursion.objects.create(
                                constellation=MapConstellation.objects.get(constellation_id=incursion['constellation_id']),
                                faction=EveFactionInfo.objects.get_or_create(faction_id=incursion['faction_id'])[0],
                                has_boss=True if incursion['has_boss'] == "true" else False,
                                staging_solar_system=MapSystem.objects.get(system_id=incursion['staging_solar_system_id']),
                                state=incursion['state'],
                                type=incursion['type'],
                                established_timestamp=magic_time
                            )
                        except Incursion.MultipleObjectsReturned as e:
                            # I dont know how to handle this, im hoping if i ignore it, the other data makes up for it.
                            logger.exception(e)
                            continue

                    elif incursion['state'] == "mobilizing":
                        try:
                            i = Incursion.objects.get(
                                mobilizing_timestamp__date__gte=magic_time.date() - timezone.timedelta(days=2),
                                mobilizing_timestamp__date__lte=magic_time.date() + timezone.timedelta(days=2),
                                constellation=MapConstellation.objects.get(constellation_id=incursion['constellation_id']))
                            continue
                        except Incursion.DoesNotExist:
                            try:
                                i = Incursion.objects.get(
                                    established_timestamp__date__gte=magic_time.date() - timezone.timedelta(days=7),
                                    established_timestamp__date__lte=magic_time.date(),
                                    constellation=MapConstellation.objects.get(constellation_id=incursion['constellation_id']))
                                i.mobilizing_timestamp = magic_time
                                if i.state is not Incursion.States.ENDED:
                                    i.state = incursion['state']
                                if i.has_boss == "true":
                                    i.has_boss = True
                                i.save()
                            except Incursion.DoesNotExist:
                                print(f"Incursion Not able to be set Mobilizing {magic_time} {incursion}")
                        except Incursion.MultipleObjectsReturned as e:
                            # I dont know how to handle this, im hoping if i ignore it, the other data makes up for it.
                            logger.exception(e)
                            continue
                    elif incursion['state'] == "withdrawing":
                        try:
                            i = Incursion.objects.get(
                                withdrawing_timestamp__date__gte=magic_time.date() - timezone.timedelta(days=1),
                                withdrawing_timestamp__date__lte=magic_time.date(),
                                constellation=MapConstellation.objects.get(constellation_id=incursion['constellation_id']))
                            continue
                        except Incursion.DoesNotExist:
                            try:
                                i = Incursion.objects.get(
                                    established_timestamp__date__gte=magic_time.date() - timezone.timedelta(days=8),
                                    established_timestamp__date__lte=magic_time.date(),
                                    constellation=MapConstellation.objects.get(constellation_id=incursion['constellation_id']))
                                i.withdrawing_timestamp = magic_time
                                if i.state is not Incursion.States.ENDED:
                                    i.state = incursion['state']
                                if i.has_boss == "true":
                                    i.has_boss = True
                                i.save()
                            except Incursion.DoesNotExist:
                                try:
                                    i = Incursion.objects.get(
                                        mobilizing_timestamp__date__gte=magic_time.date() - timezone.timedelta(days=2),
                                        mobilizing_timestamp__date__lte=magic_time.date(),
                                        constellation=MapConstellation.objects.get(constellation_id=incursion['constellation_id']))
                                    i.withdrawing_timestamp = magic_time
                                    if i.state is not Incursion.States.ENDED:
                                        i.state = incursion['state']
                                    if i.has_boss == "true":
                                        i.has_boss = True
                                    i.save()
                                except Incursion.DoesNotExist:
                                    print(f"Incursion Not able to be set Withdrawing {magic_time} {incursion}")
                        except Incursion.MultipleObjectsReturned as e:
                            # I dont know how to handle this, im hoping if i ignore it, the other data makes up for it.
                            logger.exception(e)
                            continue
                try:
                    endeds = Incursion.objects.exclude(
                        state=Incursion.States.ENDED).filter(
                        established_timestamp__lte=magic_time)
                    for ended in endeds:
                        ended.state = Incursion.States.ENDED
                        ended.ended_timestamp = magic_time
                        ended.save()
                except Exception:
                    pass

        elif entry.is_dir():
            import_staging_history(entry.path)


def import_staging_backfill(dir: str = EVEREF_STAGING_FOLDER):
    with lzma.open(os.path.join(EVEREF_STAGING_FOLDER, "backfills/eve-incursions-de-2023-10-12.json.xz")) as f:
        data = f.read()
        for incursion in json.loads(data):
            eve_constellation = MapConstellation.objects.get(constellation_id=incursion['spawn']["constellation"]["id"])
            if incursion['spawn']['endedAt'] is None:
                print(f"Incursion not gracefully ended {incursion}")
                pass
            try:
                i = Incursion.objects.get(
                    established_timestamp__date=timezone.datetime.strptime(
                        str(incursion['spawn']["establishedAt"]), "%Y-%m-%dT%H:%M:%S.%fZ").date(),
                    ended_timestamp__date=timezone.datetime.strptime(
                        str(incursion['spawn']["endedAt"]), "%Y-%m-%dT%H:%M:%S.%fZ").date(),
                    constellation=eve_constellation)
            except Incursion.DoesNotExist:
                try:
                    i = Incursion.objects.create(
                        constellation=eve_constellation,
                        faction=EveFactionInfo.objects.get_or_create(faction_id=500019)[0],
                        staging_solar_system=MapSystem.objects.get(name=incursion_constellations[eve_constellation.name]["Staging"]),
                        state=Incursion.States.ENDED,
                        established_timestamp=timezone.datetime.strptime(
                            str(incursion['spawn']["establishedAt"]), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc),
                        ended_timestamp=timezone.datetime.strptime(
                            str(incursion['spawn']["endedAt"]), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                    )
                except MapSystem.DoesNotExist:
                    logger.error(eve_constellation.name)
            # Save an extra timestamps we can gather from this data
            try:
                if incursion['state'] == "Mobilizing":
                    i.mobilizing_timestamp = timezone.datetime.strptime(
                        str(incursion['date']), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                    i.save()
                elif incursion['state'] == "Withdrawing":
                    i.withdrawing_timestamp = timezone.datetime.strptime(
                        str(incursion['date']), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
                    i.save()
            except Exception as e:
                logger.exception(e)
            # Moving onto IncursionInfluence before we close the loop
            for ilog in incursion["spawn"]["influenceLogs"]:
                try:
                    IncursionInfluence.objects.create(
                        incursion=i,
                        influence=ilog['influence'],
                        timestamp=timezone.datetime.strptime(str(ilog["date"]), "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc))
                except IntegrityError:
                    # We already have this data
                    pass

#   {
#     "id": "1",
#     "date": "2015-02-06T18:13:45.000Z",
#     "state": "Established",
#     "spawn": {
#       "id": "12",
#       "establishedAt": "2015-02-06T18:13:45.000Z",
#       "endedAt": "2015-02-09T16:00:01.000Z",
#       "state": "Ended",
#       "constellation": {
#         "id": "20000011"
#       },
#       "influenceLogs": [
#         {
#           "id": "293702",
#           "date": "2021-10-30T09:00:00.000Z",
#           "influence": 0
#         },
#         {
#           "id": "293707",
#           "date": "2021-10-30T10:00:00.000Z",
#           "influence": 0
#         },
#         {
#           "id": "293712",
#           "date": "2021-10-30T11:00:00.000Z",
#           "influence": 0.048
#         },
#         {
#           "id": "293717",
#           "date": "2021-10-30T12:00:00.000Z",
#           "influence": 0.175333
#         },
#     }
#   },

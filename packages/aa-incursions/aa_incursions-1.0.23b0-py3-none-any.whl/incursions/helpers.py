import logging
from datetime import datetime, timedelta

# from corptools.models import MapSystem
from corptools.models import MapConstellation, MapRegion
from discord import Colour, Embed
from routing.routing import (
    route_check_edencom, route_check_triglavian, route_length,
)

from incursions import __branch__, __version__
from incursions.models.incursion import Focus, Incursion
from incursions.models.waitlist import Waitlist
from incursions.static_data import incursion_constellations

from .app_settings import get_site_url

logger = logging.getLogger(__name__)


def embed_base() -> Embed:
    embed = Embed(title="AA Incursions")
    embed.url = f"{get_site_url()}/incursions/"
    embed.set_thumbnail(
        url="https://images.evetech.net/types/2192/render?size=128")
    embed.set_footer(
        text=f"AA Incursions v{__version__}-{__branch__}: Developed by Ariel Rin")
    embed.timestamp = datetime.now()
    return embed


def embed_established(incursion: Incursion) -> Embed:
    embed = embed_base()
    embed.colour = Colour.green()
    _incursion_constellation = incursion.constellation if incursion.constellation is not None else MapConstellation.objects.get(id=20000054)  # Polaris fallback
    _incursion_region = _incursion_constellation.region if _incursion_constellation.region is not None else MapRegion.objects.get(id=10000004)  # Jove Fallback

    embed.title = f"New {incursion.security_string}: {_incursion_region.name}/{_incursion_constellation.name}"
    embed.description = "PSA: Create and use an Insta-Dock Bookmark when warping to the new dockup. Scout the route ahead including the dockup station."
    embed.add_field(
        name="Region",
        value=f"{_incursion_region.name}",
        inline=True)
    embed.add_field(
        name="Constellation",
        value=f"{_incursion_constellation.name}")
    # newline
    embed.add_field(
        name="Headquarters",
        value=incursion_constellations[_incursion_constellation.name]["Headquarter"])
    embed.add_field(
        name="Assault",
        value=", ".join(incursion_constellations[_incursion_constellation.name]["Assaults"]),
        inline=True)
    embed.add_field(
        name="Vanguard",
        value=", ".join(incursion_constellations[_incursion_constellation.name]["Vanguards"]),
        inline=True)
    # newline
    # try:
    #     embed.add_field(name="Stations in HQ",
    #                     value=f"{MapSystem.objects.get(name=incursion_constellations[incursion.constellation.name]['Headquarter']).eve_stations.count()}", inline=True)
    # except MapSystem.DoesNotExist:
    #     embed.add_field(name="Stations in HQ",
    #                     value="Does not Exist in Static Data, This is the first time this constellation has seen an incursion!", inline=True)
    # embed.add_field(name="HS Island?",
    #                 value=f"{incursion.is_island}", inline=True)
    try:
        embed.add_field(name=f"Jumps from last HQ {Focus.get_solo().incursion.staging_solar_system.name}",
                        value=f"{route_length(incursion.staging_solar_system.system_id, Focus.get_solo().incursion.staging_solar_system.system_id)}", inline=True)
    except AttributeError:
        # Focus isnt Set, dont stress
        pass
    # newline
    embed.add_field(name="Suggested Dockup",
                    value="Not Implemented", inline=True)
    embed.add_field(name="Edencom In Spawn",
                    value="Not Implemented", inline=True)
    embed.add_field(name="Trigs In Spawn",
                    value="Not Implemented", inline=True)
    return embed


def embed_established_addendum(incursion: Incursion) -> Embed:
    embed = embed_base()
    embed.colour = Colour.blue()
    embed.title = f"{incursion.security_string}: {incursion.constellation.region.name}/{incursion.constellation.name}"
    embed.add_field(name="Spawn Time",
                    value=f"<t:{int(incursion.established_timestamp.timestamp())}:R>", inline=True)
    if incursion.is_high_sec:
        embed.add_field(name="Mommy Time",
                        value=f"<t:{int((incursion.established_timestamp + timedelta(days=3)).timestamp())}:R>", inline=True)
    elif incursion.is_low_sec:
        embed.add_field(name="Mommy Time",
                        value=f"<t:{int((incursion.established_timestamp + timedelta(days=1)).timestamp())}:R>", inline=True)
    embed.add_field(name="Despawn Window Starts",
                    value=f"<t:{int((incursion.established_timestamp + timedelta(days=4)).timestamp())}:R>", inline=True)
    embed.add_field(name="Despawn Window Ends",
                    value=f"<t:{int((incursion.established_timestamp + timedelta(days=8)).timestamp())}:R>", inline=True)
    # newline
    embed.add_field(name="Max Established Time",
                    value=f"<t:{int((incursion.established_timestamp + timedelta(days=5)).timestamp())}:R>")
    embed.add_field(name="HQ to Hek",
                    value=f"{route_length(incursion.staging_solar_system.system_id, 30002053)}", inline=True)
    embed.add_field(name="HQ to Dodixie",
                    value=f"{route_length(incursion.staging_solar_system.system_id, 30002659)}", inline=True)
    # newline
    embed.add_field(name="HQ to Rens",
                    value=f"{route_length(incursion.staging_solar_system.system_id, 30002510)}")
    embed.add_field(name="HQ to Jita",
                    value=f"{route_length(incursion.staging_solar_system.system_id, 30000142)}", inline=True)
    embed.add_field(name="HQ to Amarr",
                    value=f"{route_length(incursion.staging_solar_system.system_id, 30002187)}", inline=True)
    # newline
    embed.add_field(name="Gank Pipes In Route", value="Not Implemented")
    try:
        embed.add_field(name="Triglavian In Route",
                        value=str(route_check_triglavian(incursion.staging_solar_system.system_id, Focus.get_solo().incursion.staging_solar_system.system_id)), inline=True)
    except Exception:
        pass
    try:
        embed.add_field(name="Edencom In Route",
                        value=str(route_check_edencom(incursion.staging_solar_system.system_id, Focus.get_solo().incursion.staging_solar_system.system_id)), inline=True)
    except Exception:
        pass
    return embed


def embed_mobilizing(incursion: Incursion) -> Embed:
    embed = embed_base()
    embed.colour = Colour.yellow()
    embed.title = f"Mobilizing {incursion.security_string}: {incursion.constellation.region.name}/{incursion.constellation.name}"
    embed.add_field(name="Estimated Withdrawing Time",
                    value=f"<t:{int((incursion.mobilizing_timestamp + timedelta(days=2)).timestamp())}:R>", inline=False)
    embed.add_field(name="Estimated Despawn Time",
                    value=f"<t:{int((incursion.mobilizing_timestamp + timedelta(days=3)).timestamp())}:R>", inline=False)
    try:
        embed.add_field(name="Max Spawn Stats",
                        value=f'''
                            {incursion.mobilizing_timestamp - incursion.established_timestamp} Uptime
                            {timedelta(days=5) - (incursion.mobilizing_timestamp - incursion.established_timestamp)} Unused
                            {((incursion.mobilizing_timestamp - incursion.established_timestamp) / timedelta(days=5) * 100):.2f}% total possible `Established` time used
                        ''')
    except Exception:
        pass
    embed.add_field(name="Estimated Respawn Window Opens",
                    value=f"<t:{int((incursion.mobilizing_timestamp + timedelta(days=3, hours=12)).timestamp())}:R>", inline=False)
    embed.add_field(name="Estimated Respawn Window Closes",
                    value=f"<t:{int((incursion.mobilizing_timestamp + timedelta(days=3, hours=36)).timestamp())}:R>", inline=False)
    return embed

    # Spawn Mobilizing!
    # Estimated Withdrawing Time
    # Friday, 23 June 2023 21:37 (in a day)
    # Estimated Despawn Time
    # Saturday, 24 June 2023 21:37 (in 2 days)
    # Saturday, June 24, 2023 11:37 (Eve Time)
    # Max Spawn Stats
    # 4 days 2 hours 36 minutes established
    # 21 hours 24 minutes unused
    # 82.17% total possible "established" time used
    # Estimated Respawn Window Opens
    # Sunday, 25 June 2023 09:37 (in 3 days)
    # Estimated Respawn Window Closes
    # Monday, 26 June 2023 09:37 (in 4 days)


def embed_withdrawing(incursion: Incursion) -> Embed:
    embed = embed_base()
    embed.colour = Colour.red()
    embed.title = f"Withdrawing {incursion.security_string}: {incursion.constellation.region.name}/{incursion.constellation.name}"
    embed.add_field(name="Despawn Before",
                    value=f"<t:{int((incursion.withdrawing_timestamp + timedelta(days=1)).timestamp())}:R>", inline=False)
    embed.add_field(name="Estimated Respawn Window Opens",
                    value=f"<t:{int((incursion.withdrawing_timestamp + timedelta(days=1, hours=12)).timestamp())}:R>", inline=False)
    embed.add_field(name="Estimated Respawn Window Closes",
                    value=f"<t:{int((incursion.withdrawing_timestamp + timedelta(days=1, hours=36)).timestamp())}:R>", inline=False)
    return embed

    # Spawn Withdrawing!
    # Despawn Before
    # Saturday, 24 June 2023 21:40 (2 days ago)
    # Saturday, June 24, 2023 11:40 (Eve Time)
    # Estimated Respawn Window Opens
    # Sunday, 25 June 2023 09:40 (a day ago)
    # Estimated Respawn Window Closes
    # Monday, 26 June 2023 09:40 (2 hours ago)


def embed_ended(incursion: Incursion) -> Embed:
    embed = embed_base()
    embed.colour = Colour.red()
    embed.description = "The next spawn will occur in 12-36 hours."
    embed.title = f"Ended {incursion.security_string}: {incursion.constellation.region.name}/{incursion.constellation.name}"
    embed.add_field(name="Spawn Window Opens",
                    value=f"<t:{int((incursion.ended_timestamp + timedelta(days=1)).timestamp())}:R>", inline=False)
    embed.add_field(name="Spawn Window Closes",
                    value=f"<t:{int((incursion.ended_timestamp + timedelta(days=1, hours=12)).timestamp())}:R>", inline=False)

    try:
        embed.add_field(name="Max Spawn Stats",
                        value=f'''
                            {incursion.ended_timestamp - incursion.withdrawing_timestamp} Withdrawing
                            {timedelta(days=1) - (incursion.ended_timestamp - incursion.withdrawing_timestamp)} Unused
                            {((incursion.ended_timestamp - incursion.withdrawing_timestamp) / timedelta(days=1) * 100):.2f}% total possible `Withdrawing` time used
                        ''')
    except Exception:
        pass
    return embed

    # Max Spawn Stats
    # 23 hours 50 minutes withdrawing
    # 10 minutes unused
    # 99.31% total possible "withdrawing" time used


def embed_boss_spawned(incursion: Incursion) -> Embed:
    embed = embed_base()
    embed.colour = Colour.yellow()
    embed.description = "Boss Spawned"
    embed.title = f"Ended {incursion.security_string}: {incursion.constellation.name}"
    return embed


def embed_waitlist_state(waitlist: Waitlist, is_open: bool) -> Embed:
    embed = embed_base()
    embed.colour = Colour.green() if is_open else Colour.red()
    embed.description = "Waitlist Open" if is_open else "Waitlist Closed"
    embed.title = "Waitlist Open" if is_open else "Waitlist Closed"
    return embed

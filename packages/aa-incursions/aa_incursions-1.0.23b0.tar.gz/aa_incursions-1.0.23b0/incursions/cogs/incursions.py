import logging

from corptools.models import MapConstellation, MapRegion, MapSystem
from discord import AutocompleteContext, Option
from discord.commands import SlashCommandGroup
from discord.embeds import Embed
from discord.ext import commands

from django.conf import settings

from incursions import __version__
from incursions.models.incursion import Focus, Incursion

logger = logging.getLogger(__name__)


class Incursions(commands.Cog):
    """
    Incursion Information and Focus Management
    From AA-incursions
    """

    def __init__(self, bot):
        self.bot = bot

    incursion_commands = SlashCommandGroup("incursions", "Incursions", guild_ids=[int(settings.DISCORD_GUILD_ID)])

    async def search_solar_systems(self, ctx: AutocompleteContext) -> list[str]:
        return list(MapSystem.objects.filter(name__icontains=ctx.value).values_list('name', flat=True)[:10])

    async def search_constellations(self, ctx: AutocompleteContext) -> list[str]:
        return list(MapConstellation.objects.filter(name__icontains=ctx.value).values_list('name', flat=True)[:10])

    async def search_regions(self, ctx: AutocompleteContext) -> list[str]:
        return list(MapRegion.objects.filter(name__icontains=ctx.value).values_list('name', flat=True)[:10])

    async def search_incursion_active(self, ctx: AutocompleteContext) -> list[str]:
        return list(Incursion.objects.exclude(state=Incursion.States.ENDED).filter(constellation__name__icontains=ctx.value).values_list('constellation__name', flat=True)[:10])

    @incursion_commands.command(name="about", description="About the Incursion Bot", guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def about(self, ctx):
        """
        All about the bot
        """
        embed = Embed(title="AA Incursions")
        embed.description = "https://gitlab.com/tactical-supremacy/aa-incursions"
        embed.url = "https://gitlab.com/tactical-supremacy/aa-incursions"
        embed.set_thumbnail(url="https://images.evetech.net/types/2192/render?size=128")
        embed.set_footer(
            text="Developed by Ariel Rin")
        embed.add_field(
            name="Version", value=f"{__version__}", inline=False
        )

        return await ctx.respond(embed=embed)

    @incursion_commands.command(name="focus", description="Get information on the current focus", guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def focus(
        self, ctx,
    ):
        incursion_obj = Focus.get_solo().incursion
        incursion_detail_string = f"""
            {incursion_obj.constellation.name} ({incursion_obj.state})
            Established: {incursion_obj.established_timestamp}
            Mobilized: {incursion_obj.mobilizing_timestamp}
            Withdrawing:{incursion_obj.withdrawing_timestamp}
            Boss Spotted: {incursion_obj.has_boss}
            Influence: {incursion_obj.influence}
            """
        return await ctx.respond(incursion_detail_string)

    @incursion_commands.command(name="set_focus", description="Set the current Focus", guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def focus_set(
        self, ctx,
        incursion=Option(str, "Constellation", autocomplete=search_incursion_active),
    ):
        focus = Focus.get_solo()
        focus.incursion_id = Incursion.objects.exclude(
            state=Incursion.States.ENDED).get(constellation__name__icontains=incursion)
        focus.save()
        return await ctx.respond("Focus Set")

    @incursion_commands.command(name="incursions", description="List active incursions", guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def incursions(
        self, ctx,
    ):
        incursion_string = ""
        for incursion in Incursion.objects.exclude(state=Incursion.States.ENDED):
            incursion_string += f"\n{incursion.constellation.name}"
        return await ctx.respond(incursion_string)

    @incursion_commands.command(name="incursion_detail", description="Status of a specific incursion", guild_ids=[int(settings.DISCORD_GUILD_ID)])
    async def incursion_detail(
        self, ctx,
        incursion=Option(str, "Constellation", autocomplete=search_incursion_active),
    ):
        incursion_obj = Incursion.objects.exclude(state=Incursion.States.ENDED).get(
            constellation__name__icontains=incursion)
        incursion_detail_string = f"""
            {incursion_obj.constellation.name} ({incursion_obj.state})
            Established: {incursion_obj.established_timestamp}
            Mobilized: {incursion_obj.mobilizing_timestamp}
            Withdrawing:{incursion_obj.withdrawing_timestamp}
            Boss Spotted: {incursion_obj.has_boss}
            Influence: {incursion_obj.influence}
            """
        return await ctx.respond(incursion_detail_string)


def setup(bot) -> None:
    bot.add_cog(Incursions(bot))

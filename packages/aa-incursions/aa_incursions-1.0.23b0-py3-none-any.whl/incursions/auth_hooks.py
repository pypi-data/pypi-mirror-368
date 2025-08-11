from django.utils.translation import gettext_lazy as _

from allianceauth import hooks
from allianceauth.menu.hooks import MenuItemHook
from allianceauth.services.hooks import UrlHook

from incursions import urls


class IncursionsMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("Incursion Waitlist"),
            "fas fa-skull-crossbones fa-fw",
            "incursions:waitlist",
            navactive=["incursions:waitlist"],
        )

    def render(self, request):
        if request.user.has_perm("incursions.basic_waitlist"):
            return MenuItemHook.render(self, request)
        return ""


@hooks.register('discord_cogs_hook')
def register_cogs() -> list[str]:
    return ["incursions.cogs.incursions"]


@hooks.register("menu_item_hook")
def register_menu() -> IncursionsMenuItem:
    return IncursionsMenuItem()


@hooks.register("url_hook")
def register_urls() -> UrlHook:
    return UrlHook(urls, "incursions", r"^incursions/")

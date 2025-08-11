from ninja import NinjaAPI
from ninja.security import django_auth

from django.conf import settings

from allianceauth.services.hooks import get_extension_logger

from incursions.api import (
    announcements, auth, badges, bans, categories, fittings, fleets, history,
    implants, modules, notes, pilot, search, skills, sse, statistics, waitlist,
    window,
)

logger = get_extension_logger(__name__)

api = NinjaAPI(
    title="AA Incursions API",
    version="0.0.1",
    urls_namespace='incursions:api',
    auth=django_auth,
    csrf=True,
    openapi_url=settings.DEBUG and "/openapi.json" or ""
)

announcements.setup(api)
auth.setup(api)
badges.setup(api)
bans.setup(api)
categories.setup(api)
fittings.setup(api)
fleets.setup(api)
history.setup(api)
implants.setup(api)
modules.setup(api)
notes.setup(api)
pilot.setup(api)
search.setup(api)
# skillplans.setup(api)
skills.setup(api)
sse.setup(api)
statistics.setup(api)
waitlist.setup(api)
window.setup(api)

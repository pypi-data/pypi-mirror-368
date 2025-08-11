import re
from urllib.parse import urlparse, urlunparse

from django.conf import settings


def get_site_url():  # regex sso url
    regex = r"^(.+)\/s.+"
    matches = re.finditer(regex, settings.ESI_SSO_CALLBACK_URL, re.MULTILINE)
    url = "http://"

    for m in matches:
        url = m.groups()[0]  # first match

    return url


INCURSIONS_AUTO_HIGHSEC_FOCUS = getattr(settings, 'INCURSIONS_AUTO_HIGHSEC_FOCUS', True)

INCURSIONS_SCOPES_BASE = ["publicData", "esi-skills.read_skills.v1", "esi-clones.read_implants.v1"]

INCURSIONS_SCOPES_FC = ["esi-fleets.read_fleet.v1", "esi-fleets.write_fleet.v1", "esi-ui.open_window.v1", "esi-search.search_structures.v1"]


def insert_sse_subdomain(site_url: str) -> str:
    parsed = urlparse(site_url)           # e.g. scheme='http', netloc='localhost:8000', path='', etc.
    parts = parsed.netloc.split(':', 1)   # split hostname from port
    host = parts[0]
    port = parts[1] if len(parts) > 1 else None

    # Prepend 'sse.' to the hostname
    new_host = f"sse.{host}"
    new_netloc = f"{new_host}:{port}" if port else new_host

    # Rebuild the full URL
    new_url = urlunparse((
        parsed.scheme,
        new_netloc,
        parsed.path,
        parsed.params,
        parsed.query,
        parsed.fragment
    ))
    return new_url


SSE_SITE_URL = getattr(settings, 'SSE_SITE_URL', insert_sse_subdomain(settings.SITE_URL))

SSE_SECRET = getattr(settings, 'SSE_SECRET', "0000000000000000000000000000000000000000000000000000000000000000")

EVECATEGORY_SHIP = 6
EVECATEGORY_SKILLS = 16
EVECATEGORY_IMPLANTS = 20
EVECATEGORY_DEPLOYABLE = 22
EVECATEGORY_CHARGE = 8
EVECATEGORY_MODULE = 7
EVECATEGORY_SKILLS = 16
EVECATEGORY_IMPLANTS = 20
EVECATEGORY_CHARGE = 8
EVECATEGORY_DEPLOYABLE = 22
EVECATEGORY_DRONE = 18

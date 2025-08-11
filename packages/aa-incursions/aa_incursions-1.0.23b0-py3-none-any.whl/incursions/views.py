from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from allianceauth.services.hooks import get_extension_logger
from esi.decorators import token_required

from incursions import __version__
from incursions.app_settings import (
    INCURSIONS_SCOPES_BASE, INCURSIONS_SCOPES_FC,
)

logger = get_extension_logger(__name__)


@login_required
def waitlist(request) -> HttpResponse:
    return render(request, 'incursions/base-bs5.html', context={"version": __version__, "app_name": "incursions/waitlist", "page_title": "Waitlist"})


# @login_required
# @token_required(scopes=INCURSIONS_SCOPES_BASE)
# def add_char_base(request, token):

#     return redirect('incursions:waitlist')

@login_required
@token_required(scopes=INCURSIONS_SCOPES_BASE + INCURSIONS_SCOPES_FC)
def add_char_fc(request, token):

    return redirect('incursions:waitlist')

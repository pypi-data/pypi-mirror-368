import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from incursions.app_settings import INCURSIONS_AUTO_HIGHSEC_FOCUS
from incursions.models.incursion import Focus, Incursion
from incursions.models.waitlist import Waitlist
from incursions.tasks import (
    incursion_boss_spawned, incursion_ended, incursion_established,
    incursion_mobilizing, incursion_withdrawing, waitlist_state,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Incursion)
def incursion(sender, instance: Incursion, created: bool, *args, **kwargs):
    update_fields = kwargs.pop('update_fields', []) or []

    if created is True:
        incursion_established.apply_async(args=[instance.pk])
        if INCURSIONS_AUTO_HIGHSEC_FOCUS and instance.is_high_sec:
            Focus.get_solo().incursion = instance

    if 'state' in update_fields:
        if instance.state == Incursion.States.ESTABLISHED:
            # This should have been handled above?
            pass
        elif instance.state == Incursion.States.MOBILIZING:
            incursion_mobilizing.apply_async(args=[instance.pk])
        elif instance.state == Incursion.States.WITHDRAWING:
            incursion_withdrawing.apply_async(args=[instance.pk])
        elif instance.state == Incursion.States.ENDED:
            incursion_ended.apply_async(args=[instance.pk])

    if 'has_boss' in update_fields and instance.has_boss is True:
        incursion_boss_spawned.apply_async(args=[instance.pk])


@receiver(post_save, sender=Waitlist)
def waitlist(sender, instance: Waitlist, created:bool, *args, **kwargs):
    update_fields = kwargs.pop('update_fields', []) or []

    if "is_open" in update_fields:
        if instance.is_open is True:
            waitlist_state.apply_async(args=[instance.pk, instance.is_open])
        else:
            waitlist_state.apply_async(args=[instance.pk, instance.is_open])

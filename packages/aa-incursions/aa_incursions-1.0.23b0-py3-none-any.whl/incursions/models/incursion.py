from datetime import timedelta

from corptools.models import MapConstellation, MapSystem
from discord import SyncWebhook
from routing.routing import route_path_nodes
from solo.models import SingletonModel

from django.db import models
from django.utils.translation import gettext_lazy as _

from allianceauth.eveonline.models import EveFactionInfo


class Incursion(models.Model):

    class States(models.TextChoices):
        """"
        Incursion Phases
        """
        ESTABLISHED = 'established', _("Incursion established")  # Up to 5 Days
        MOBILIZING = 'mobilizing', _("Incursion mobilizing")  # 48 Hours
        WITHDRAWING = 'withdrawing', _("Incursion withdrawing")  # 24 Hours
        # Our custom phase to archive finished incursions
        ENDED = 'ended', _("Ended")

    class Types(models.TextChoices):
        """
        I Think this used to be used for Trig Incursions etc, leaving the option in place to expand it later
        """
        INCURSION = 'Incursion', _("Sansha Incursion")

    constellation = models.ForeignKey(MapConstellation, blank=True, null=True, on_delete=models.CASCADE, related_name="+")
    faction = models.ForeignKey(EveFactionInfo, verbose_name=_(
        "The attacking Faction"), on_delete=models.CASCADE)
    has_boss = models.BooleanField(_("Whether the final encounter has boss or not"), default=False)
    infested_solar_systems = models.ManyToManyField(MapSystem, blank=True, related_name="+")
    staging_solar_system = models.ForeignKey(MapSystem, blank=True, null=True, on_delete=models.CASCADE, related_name="+")

    state = models.CharField(
        _("The state of this incursion"),
        max_length=50, choices=States.choices, default=States.ESTABLISHED)
    type = models.CharField(
        _("The type of this incursion"), max_length=50,
        choices=Types.choices, default=Types.INCURSION)

    established_timestamp = models.DateTimeField(
        _("Established"), auto_now=False, auto_now_add=False, blank=True, null=True)
    mobilizing_timestamp = models.DateTimeField(
        _("Mobilizing"), auto_now=False, auto_now_add=False, blank=True, null=True)
    withdrawing_timestamp = models.DateTimeField(
        _("Withdrawing"), auto_now=False, auto_now_add=False, blank=True, null=True)
    ended_timestamp = models.DateTimeField(
        _("Ended"), auto_now=False, auto_now_add=False, blank=True, null=True)

    class Meta:
        default_permissions = ()
        verbose_name = _("Incursion")
        verbose_name_plural = _("Incursions")

    def __str__(self) -> str:
        return f"{self.constellation.name}"

    @property
    def established_utlization(self) -> float | bool:
        if self.established_timestamp and self.mobilizing_timestamp:
            return (self.established_timestamp - self.mobilizing_timestamp) / timedelta(days=5)
        else:
            return False

    @property
    def mobilizing_utlization(self) -> float | bool:
        if self.mobilizing_timestamp and self.withdrawing_timestamp:
            return (self.mobilizing_timestamp - self.withdrawing_timestamp) / timedelta(days=2)
        else:
            return False

    @property
    def security_string(self) -> str:
        if self.is_high_sec:
            return "High-Sec"
        elif self.is_low_sec:
            return "Low-Sec"
        elif self.is_null_sec:
            return "Null-Sec"
        else:
            return "Unknown"

    @property
    def is_island(self) -> bool:
        try:
            for system in route_path_nodes(self.staging_solar_system.system_id, 30000142):
                if system.security_status < 0.50:
                    return True
            return False
        except Exception:
            # wtf
            return True  # WHY NOT

    @property
    def influence(self) -> float:
        try:
            IncursionInfluence.objects.filter(incursion=self).latest("timestamp").influence
        except Exception:
            return float(0)

    @property
    def is_high_sec(self) -> bool:
        return self.staging_solar_system.security_status >= 0.45

    @property
    def is_low_sec(self) -> bool:
        return 0.0 < self.staging_solar_system.security_status < 0.45

    @property
    def is_null_sec(self) -> bool:
        return self.staging_solar_system.security_status <= 0.0


class IncursionInfluence(models.Model):
    incursion = models.ForeignKey(Incursion, verbose_name=_("Incursion"), on_delete=models.CASCADE)
    timestamp = models.DateTimeField(_("Timestamp"), auto_now=False, auto_now_add=False)
    influence = models.FloatField(
        _("Influence of this incursion as a float from 0 to 1"), default=float(0))

    class Meta:
        default_permissions = ()
        verbose_name = _("IncursionInfluence")
        verbose_name_plural = _("IncursionInfluences")
        constraints = [
            models.UniqueConstraint(fields=['incursion', 'timestamp'], name="UniqueIncursionInfluenceLogTimestamp"),
        ]

    def __str__(self) -> str:
        return f"{self.incursion} @ {self.timestamp}"


class Webhook(models.Model):
    """Destinations for Relays"""
    url = models.CharField(max_length=200)
    name = models.CharField(max_length=50)

    security_high = models.BooleanField(_("Notify on High Security Incursions"))
    security_low = models.BooleanField(_("Notify on Low Security Incursions"))
    security_null = models.BooleanField(_("Notify on Null Security Incursions"))

    def __str__(self) -> str:
        return f'"{self.name}"'

    class Meta:
        default_permissions = ()
        verbose_name = _('Destination Webhook')
        verbose_name_plural = _('Destination Webhooks')

    def send_embed(self, embed):
        webhook = SyncWebhook.from_url(self.url)
        webhook.send(embed=embed, username="AA Incursions")


class IncursionsConfig(SingletonModel):
    status_webhooks = models.ManyToManyField(
        Webhook, verbose_name=_("Destination Webhook for Incursion Updates"), related_name="+", blank=True)
    waitlist_webhooks = models.ManyToManyField(
        Webhook, verbose_name=_("Destination Webhook for Waitlist Updates"), related_name="+", blank=True)

    def __str__(self) -> str:
        return "AA Incursions Settings"

    class Meta:
        """
        Meta definitions
        """
        default_permissions = ()
        verbose_name = _("AA Incursions Settings")
        verbose_name_plural = _("AA Incursions Settings")


class Focus(SingletonModel):
    incursion = models.ForeignKey(
        Incursion,
        verbose_name=_("Current Focus"),
        on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self) -> str:
        try:
            return f"Current Focus: {self.incursion}"
        except Exception:
            return "No Focus Set"

    class Meta:
        """
        Meta definitions
        """
        default_permissions = ()
        verbose_name = _("Current Focus")
        verbose_name_plural = _("Current Focus")

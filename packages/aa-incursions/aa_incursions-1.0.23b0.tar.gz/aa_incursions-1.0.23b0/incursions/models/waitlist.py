from corptools.models import EveItemType
from solo.models import SingletonModel

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from allianceauth.eveonline.models import (
    EveAllianceInfo, EveCharacter, EveCorporationInfo,
)

from incursions.providers import get_fleet_members, get_fleets_fleet_id_wings


class Announcement(models.Model):
    message = models.TextField(verbose_name=_("Message"))
    is_alert = models.BooleanField(default=False, verbose_name=_("Is Alert"))
    pages = models.TextField(null=True, blank=True, verbose_name=_("Pages"))

    created_by = models.ForeignKey(EveCharacter, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name=_("Created By"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    revoked_by = models.ForeignKey(EveCharacter, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name=_("Revoked By"))
    revoked_at = models.DateTimeField(default=None, blank=True, null=True, verbose_name=_("Revoked At"))

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Announcement")
        verbose_name_plural = _("Waitlist - Announcements")

    def __str__(self) -> str:
        return f"Announcement #{self.pk}"


class Ban(models.Model):
    class entity_choices(models.TextChoices):
        CHARACTER = 'Character', _('Character')
        CORPORATION = 'Corporation', _('Corporation')
        ALLIANCE = 'Alliance', _('Alliance')

    entity_type = models.CharField(max_length=12, choices=entity_choices.choices, default=entity_choices.CHARACTER, verbose_name=_("Entity Type"))
    entity_character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name=_("Character"))
    entity_corporation = models.ForeignKey(EveCorporationInfo, on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name=_("Corporation"))
    entity_alliance = models.ForeignKey(EveAllianceInfo, on_delete=models.CASCADE, null=True, blank=True, related_name='+', verbose_name=_("Alliance"))
    public_reason = models.CharField(max_length=512, null=True, blank=True, verbose_name=_("Public Reason"))
    reason = models.CharField(max_length=512, verbose_name=_("Internal Reason"))
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Issued At"))
    issued_by = models.ForeignKey(EveCharacter, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name=_("Issued By"))
    revoked_at = models.DateTimeField(blank=True, null=True, default=None, verbose_name=_("Revoked At"))
    revoked_by = models.ForeignKey(EveCharacter, on_delete=models.SET_NULL, null=True, blank=True, related_name='+', verbose_name=_("Revoked By"))

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Ban")
        verbose_name_plural = _("Waitlist - Bans")

    def __str__(self) -> str:
        return f"Ban #{self.pk} on {self.entity_type} {self.pk}"

    @property
    def entity_name(self) -> str:
        if self.entity_type == self.entity_choices.CHARACTER and self.entity_character:
            return self.entity_character.character_name
        if self.entity_type == self.entity_choices.CORPORATION and self.entity_corporation:
            return self.entity_corporation.corporation_name
        if self.entity_type == self.entity_choices.ALLIANCE and self.entity_alliance:
            return self.entity_alliance.alliance_name
        return "Unknown Name"


class Badge(models.Model):

    class color_choices(models.TextChoices):
        RED = "red", _("Red")
        GREEN = "green", _("Green")
        BLUE = "blue", _("Blue")
        YELLOW = "yellow", _("Yellow")
        PURPLE = "purple", _("Purple")
        NEUTRAL = "neutral", _("Neutral")
        CYAN = "cyan", _("Cyan")

    class type_choices(models.TextChoices):
        SHIELD = "shield", _("Shield")

    name = models.CharField(max_length=64, unique=True, verbose_name=_("Badge Name"))
    letter = models.CharField(max_length=1, verbose_name=_("Letter"))
    type = models.CharField(max_length=16, choices=type_choices.choices, default=type_choices.SHIELD, verbose_name=_("Badge Type"))
    color = models.CharField(max_length=16, choices=color_choices.choices, default=color_choices.NEUTRAL, verbose_name=_("Badge Color"))
    order = models.SmallIntegerField(verbose_name=_("Order"), help_text=_("Order in which the badge will be displayed, lower is earlier"))

    exclude_badge = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name='excluded_by', verbose_name=_("Mutually Exclusive With"))

    class Meta:
        # default_permissions = ()
        verbose_name = _("Waitlist - Badge")
        verbose_name_plural = _("Waitlist - Badges")

    def __str__(self) -> str:
        return f"{self.name}"

    @property
    def member_count(self) -> int:
        return CharacterBadges.objects.filter(badge_id=self.pk).count()


class CharacterBadges(models.Model):
    character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE, related_name='incursions_badge', verbose_name=_("Character"))
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, related_name='+', verbose_name=_("Badge"))
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Granted At"))
    granted_by = models.ForeignKey(EveCharacter, on_delete=models.SET_NULL, blank=True, null=True, related_name='+', verbose_name=_("Granted By"))

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Character Badge")
        verbose_name_plural = _("Waitlist - Character Badges")
        unique_together = ("character", "badge")

    def __str__(self) -> str:
        return f"{self.character} has badge {self.badge}"


class CharacterNote(models.Model):
    character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE, related_name='+', verbose_name=_("Character"))
    note = models.TextField(verbose_name=_("Note"))
    author = models.ForeignKey(EveCharacter, null=True, on_delete=models.SET_NULL, related_name='+', verbose_name=_("Author"))
    logged_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Logged At"))

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Character Note")
        verbose_name_plural = _("Waitlist - Character Notes")
        ordering = ['-logged_at']

    def __str__(self) -> str:
        return f"Note #{self.pk} for {self.character}"


class Fitting(models.Model):
    ship = models.ForeignKey(EveItemType, verbose_name=_("Ship"), on_delete=models.CASCADE, related_name='+')
    dna = models.TextField(max_length=1024, unique=True, verbose_name=_("DNA String"))

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Waitlist Fit")
        verbose_name_plural = _("Waitlist - Waitlist Fits")

    def __str__(self) -> str:
        return f"Fitting {self.pk} (Hull: {self.ship})"


class ImplantSet(models.Model):
    implants = models.CharField(max_length=255, unique=True, verbose_name=_("Implant String"))

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Waitlist Implant Set")
        verbose_name_plural = _("Waitlist - Waitlist Implant Sets")

    def __str__(self) -> str:
        return f"ImplantSet #{self.pk}: {self.implants}"


class SkillCheck(models.Model):
    skill = models.ForeignKey(EveItemType, verbose_name=_("Skill"), on_delete=models.CASCADE, related_name='+')
    min = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=3, verbose_name=_("Minimum Required"))
    elite = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=4, verbose_name=_("Elite Level"))
    gold = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(5)], default=5, verbose_name=_("Gold Level"))

    class Meta:
        # default_permissions = ()
        verbose_name = _("Waitlist - Skill Check")
        verbose_name_plural = _("Waitlist - Skill Checks")

    def __str__(self) -> str:
        return f"Skill: {self.skill} - Min: {self.min}, Elite: {self.elite}, Gold: {self.gold}"


class ApprovedImplantSet(models.Model):
    class set_choices(models.TextChoices):
        AMULET = "Amulet", _("Amulet")
        ASCENDENCY = "Ascendancy ", _("Ascendancy ")
        NONE = "None", _("None")

    name = models.CharField(max_length=255, verbose_name=_("Set Name"))
    set = models.CharField(max_length=16, choices=set_choices.choices, default=set_choices.AMULET, verbose_name=_("Set Type"))
    implants = models.CharField(max_length=255, unique=True, verbose_name=_("Implant List"))

    class Meta:
        # default_permissions = ()
        verbose_name = _("Waitlist - Approved Implant Set")
        verbose_name_plural = _("Waitlist - Approved Implant Sets")

    def __str__(self) -> str:
        return self.implants


class ApprovedFitting(models.Model):
    class tier_choices(models.TextChoices):
        BASIC = "Basic", _("Sponge")
        MAINLINE = "Mainline", _("Mainline")
        ALT = "Alt", _("Alt")
        OTHER = "Other", _("Other")

    ship = models.ForeignKey(EveItemType, verbose_name=_("Ship"), on_delete=models.CASCADE, related_name='+')
    name = models.CharField(max_length=25, unique=True, verbose_name=_("Fitting Name"))
    dna = models.TextField(max_length=1024, unique=True, verbose_name=_("DNA String"))
    tier = models.CharField(max_length=16, choices=tier_choices.choices, default=tier_choices.MAINLINE, verbose_name=_("Tier"))
    description = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Description"))
    implants = models.ForeignKey(ApprovedImplantSet, on_delete=models.SET_NULL, related_name='+', null=True, blank=True, verbose_name=_("Implant Set"))

    class Meta:
        # default_permissions = ()
        verbose_name = _("Waitlist - Approved Fitting")
        verbose_name_plural = _("Waitlist - Approved Fittings")

    def __str__(self) -> str:
        return self.name

    def is_logi(self) -> bool:
        return WaitlistCategoryRule.objects.get(ship_id=self.ship_id).waitlist_category.name == "LOGI"

    def implant_set(self) -> str:
        return self.implants.set if self.implants else "None"


class ApprovedSkills(models.Model):
    ship = models.OneToOneField(EveItemType, verbose_name=_("Ship"), on_delete=models.CASCADE, related_name='+')
    skill_checks = models.ManyToManyField(SkillCheck, verbose_name=_("Skill Checks"), related_name='+')

    class Meta:
        # default_permissions = ()
        verbose_name = _("Waitlist - Approved Skills")
        verbose_name_plural = _("Waitlist - Approved Skills")

    def __str__(self) -> str:
        return f"Hull: {self.ship.name}"


class WaitlistCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Category Name"))

    class Meta:
        # default_permissions = ()
        verbose_name = _("Waitlist - Category")
        verbose_name_plural = _("Waitlist - Categories")
        indexes = [models.Index(fields=['name'])]

    def __str__(self) -> str:
        return f"{self.name}"


class WaitlistCategoryRule(models.Model):
    waitlist_category = models.ForeignKey(WaitlistCategory, verbose_name=_("Waitlist Category"), on_delete=models.CASCADE, related_name='+')
    ship = models.OneToOneField(EveItemType, verbose_name=_("Ship"), on_delete=models.CASCADE, related_name='+')

    class Meta:
        # default_permissions = ()
        verbose_name = _("Waitlist - Category Rule")
        verbose_name_plural = _("Waitlist - Category Rules")

    def __str__(self) -> str:
        return f"{self.waitlist_category} - {self.ship}"


# Fleet
class Fleet(models.Model):
    boss = models.ForeignKey(EveCharacter, on_delete=models.CASCADE, related_name='+', verbose_name=_("Fleet Boss"))
    is_updating = models.BooleanField(default=False, verbose_name=_("Is Updating"))
    open = models.BooleanField(default=False, verbose_name=_("Is Open"))

    opened = models.DateTimeField(auto_now_add=True, verbose_name=_("Opened"))
    closed = models.DateTimeField(null=True, blank=True, default=None, verbose_name=_("Closed"))
    last_updated = models.DateTimeField(blank=True, verbose_name=_("Last Updated"))

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Fleet")
        verbose_name_plural = _("Waitlist - Fleets")

    def __str__(self) -> str:
        return f"Fleet #{self.pk}"

    def get_fleet_members(self):
        # /api/members/{character_id} uses me
        # But if i pass it through here I can dump some info to DB while im at it.
        fleet_members = get_fleet_members(self.boss.character_id, self.pk)
        for fleet_member in fleet_members:
            # Save or update fleet members in the DB
            pass
        return fleet_members

    def get_fleets_fleet_id_wings(self):
        # /api/members/{character_id} uses me
        # But if i pass it through here I can dump some info to DB while im at it.
        fleet_wings = get_fleets_fleet_id_wings(self.boss.character_id, self.pk)
        for wing in fleet_wings:
            # Save or update fleet Wings in the DB
            pass
        return fleet_wings


class ActiveFleet(SingletonModel):

    fleet = models.ForeignKey(Fleet, on_delete=models.CASCADE, related_name='+', verbose_name=_("Fleet"), blank=True, null=True)

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Fleet (Active)")

    def __str__(self) -> str:
        return f"Active Fleet {self.fleet}"


class FleetSquad(models.Model):
    fleet = models.ForeignKey(Fleet, on_delete=models.CASCADE, related_name='+', verbose_name=_("Fleet"))
    category = models.ForeignKey(WaitlistCategory, verbose_name=_("Waitlist Category"), on_delete=models.CASCADE, related_name='+')
    wing_id = models.BigIntegerField(verbose_name=_("Wing ID"))
    squad_id = models.BigIntegerField(verbose_name=_("Squad ID"))

    class Meta:
        default_permissions = ()
        unique_together = (('fleet', 'category'),)
        verbose_name = _("Waitlist - Fleet Squad")
        verbose_name_plural = _("Waitlist - Fleet Squad")

    def __str__(self) -> str:
        return f"FleetSquad in Fleet {self.pk}, category {self.category}"


# Waitlist
class Waitlist(SingletonModel):
    name = models.CharField(max_length=255, default="Waitlist", verbose_name=_("Waitlist Name"))
    is_open = models.BooleanField(default=False, verbose_name=_("Is Open"))

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Waitlist")
        verbose_name_plural = _("Waitlist - Waitlist")

    def __str__(self) -> str:
        return f"{self.name}"


class WaitlistEntry(models.Model):
    waitlist = models.ForeignKey(Waitlist, on_delete=models.CASCADE, related_name='+', verbose_name=_("Waitlist"))
    main_character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE, related_name='+', verbose_name=_("Main Character"))
    joined_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, verbose_name=_("Joined At"))

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Waitlist Entry")
        verbose_name_plural = _("Waitlist - Waitlist Entry")

    def __str__(self) -> str:
        return f"WaitlistEntry {self.main_character.character_name}"


class WaitlistEntryFit(models.Model):
    character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE, related_name='+', verbose_name=_("Character"))
    waitlist_entry = models.ForeignKey(WaitlistEntry, on_delete=models.CASCADE, verbose_name=_("Waitlist Entry"))
    fit = models.ForeignKey("Fitting", on_delete=models.CASCADE, related_name='+', verbose_name=_("Fitting"))
    implant_set = models.ForeignKey("ImplantSet", on_delete=models.CASCADE, related_name='+', verbose_name=_("Implant Set"))
    approved = models.BooleanField(default=False, verbose_name=_("Approved"))
    tags = models.CharField(max_length=255, help_text=_("Comma Seperated: Tags are fit specific Badges, such as First/New/Alt/Skills"), verbose_name=_("Tags"))
    category = models.ForeignKey(WaitlistCategory, verbose_name=_("Waitlist Category"), on_delete=models.CASCADE, related_name='+')
    fit_analysis = models.JSONField(null=True, blank=True, verbose_name=_("Fit Analysis"))
    review_comment = models.TextField(null=True, blank=True, verbose_name=_("Review Comment"))
    is_alt = models.BooleanField(default=False, verbose_name=_("Is Alt"))
    messagexup = models.TextField(null=True, blank=True, verbose_name=_("Message XUP"))
    cached_time_in_fleet = models.BigIntegerField(verbose_name=_("Cached Time In Fleet"))

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Waitlist Entry Fit")
        verbose_name_plural = _("Waitlist - Waitlist Entry Fit")

    def __str__(self) -> str:
        return f"WaitlistEntry: {self.waitlist_entry.main_character.character_name} Fit: {self.character.character_name} - {self.fit.ship.name}"


# Historical Activity
class FleetActivity(models.Model):
    fleet = models.ForeignKey(Fleet, verbose_name=_("Fleet"), on_delete=models.CASCADE)
    character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE, related_name='+', verbose_name=_("Character"))
    ship = models.ForeignKey(EveItemType, verbose_name=_("Ship"), on_delete=models.CASCADE, related_name='+')
    is_boss = models.BooleanField(default=False, verbose_name=_("Is Boss"))

    first_seen = models.DateTimeField(auto_now_add=True, verbose_name=_("First Seen"))
    last_seen = models.DateTimeField(verbose_name=_("Last Seen"))
    has_left = models.BooleanField(default=False, verbose_name=_("Has Left"))

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Fleet Activity")
        verbose_name_plural = _("Waitlist - Fleet Activities")

    def __str__(self) -> str:
        return f"FleetActivity #{self.pk} for {self.character}"


class FittingHistory(models.Model):
    character = models.ForeignKey(EveCharacter, on_delete=models.CASCADE, related_name='+', verbose_name=_("Character"))
    fit = models.ForeignKey("Fitting", on_delete=models.CASCADE, related_name='+', verbose_name=_("Fitting"))
    implant_set = models.ForeignKey("ImplantSet", on_delete=models.CASCADE, related_name='+', verbose_name=_("Implant Set"))
    logged_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Logged At"))

    class Meta:
        default_permissions = ()
        verbose_name = _("Waitlist - Fitting History")
        verbose_name_plural = _("Waitlist - Fitting Histories")

    def __str__(self) -> str:
        return f"FitHistory #{self.pk} for {self.character}"

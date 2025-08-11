from corptools.models import EveItemType

from django.contrib import admin
from django.forms import ModelChoiceField

from allianceauth.services.hooks import get_extension_logger

from incursions.app_settings import EVECATEGORY_SHIP, EVECATEGORY_SKILLS
from incursions.models.incursion import (
    Focus, Incursion, IncursionInfluence, IncursionsConfig, Webhook,
)
from incursions.models.waitlist import (
    ActiveFleet, Announcement, ApprovedFitting, ApprovedImplantSet,
    ApprovedSkills, Badge, Ban, CharacterBadges, CharacterNote, Fitting, Fleet,
    FleetSquad, ImplantSet, SkillCheck, Waitlist, WaitlistCategory,
    WaitlistCategoryRule, WaitlistEntry, WaitlistEntryFit,
)

logger = get_extension_logger(__name__)


# Incursions
@admin.register(IncursionsConfig)
class IncursionsConfigAdmin(admin.ModelAdmin):
    filter_horizontal = ["status_webhooks"]


@admin.register(Incursion)
class IncursionAdmin(admin.ModelAdmin):
    list_display = ["constellation", "state", "established_timestamp",
                    "mobilizing_timestamp", "withdrawing_timestamp", "ended_timestamp"]
    list_filter = ["state", "has_boss"]
    filter_horizontal = ["infested_solar_systems"]


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ("name", "url")


@admin.register(IncursionInfluence)
class IncursionInfluenceAdmin(admin.ModelAdmin):
    list_display = ("incursion", "timestamp", "influence")


@admin.register(Focus)
class FocusAdmin(admin.ModelAdmin):
    list_display = ["incursion"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "incursion":
            kwargs["queryset"] = Incursion.objects.exclude(state=Incursion.States.ENDED)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ("message", "is_alert", "created_at", "revoked_at")
    list_filter = ("is_alert",)
    search_fields = ("message",)
    date_hierarchy = "created_at"


@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display = ("pk", "entity_name", "entity_type", "issued_at", "revoked_at")
    list_filter = ("entity_type", "issued_at", "revoked_at")
    search_fields = ("entity_name", "public_reason", "reason")


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ("name", "exclude_badge")
    search_fields = ("name",)


@admin.register(CharacterBadges)
class CharacterBadgesAdmin(admin.ModelAdmin):
    list_display = ("pk", "character", "badge", "granted_at", "granted_by")
    list_filter = ("badge",)
    search_fields = ("character__name", "badge__name")


@admin.register(Fitting)
class FittingAdmin(admin.ModelAdmin):
    list_display = ("pk", "ship", "dna")
    search_fields = ("dna", "ship__name")
    list_select_related = ("ship",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs) -> ModelChoiceField:
        if db_field.name == "ship":
            kwargs["queryset"] = EveItemType.objects.filter(group__category_id=EVECATEGORY_SHIP)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ImplantSet)
class ImplantSetAdmin(admin.ModelAdmin):
    list_display = ("pk", "implants")
    search_fields = ("implants",)


@admin.register(CharacterNote)
class CharacterNoteAdmin(admin.ModelAdmin):
    list_display = ("character", "author", "logged_at")
    search_fields = ("character__name", "author__name", "note")
    list_select_related = ("character", "author")


@admin.register(WaitlistCategory)
class WaitlistCategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(WaitlistCategoryRule)
class WaitlistCategoryRuleAdmin(admin.ModelAdmin):

    def formfield_for_foreignkey(self, db_field, request, **kwargs) -> ModelChoiceField:
        if db_field.name == "ship":
            kwargs["queryset"] = EveItemType.objects.filter(group__category_id=EVECATEGORY_SHIP)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Fleet)
class FleetAdmin(admin.ModelAdmin):
    list_display = ("pk", "boss", "is_updating")
    search_fields = ("boss__name",)
    list_select_related = ("boss",)


@admin.register(FleetSquad)
class FleetSquadAdmin(admin.ModelAdmin):
    list_display = ("pk", "fleet", "category", "wing_id", "squad_id")
    search_fields = ("fleet__id", "category__name")
    list_select_related = ("fleet", "category")


@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "is_open")
    list_filter = ("is_open",)
    search_fields = ("name",)


@admin.register(WaitlistEntryFit)
class WaitlistEntryFitAdmin(admin.ModelAdmin):
    list_display = (
        "pk",
        "character",
        "fit",
        "implant_set",
        "approved",
        "tags",
        "category",
        "cached_time_in_fleet",
        "is_alt",
    )
    list_filter = ("approved", "is_alt", "fit", "implant_set", "category")
    search_fields = ("character__name", "tags", "category__name")
    list_select_related = ("character", "fit", "implant_set", "category")


@admin.register(ApprovedFitting)
class ApprovedFittingAdmin(admin.ModelAdmin):
    list_display = ("pk", "ship", "tier", "implants")
    list_filter = ("tier", "implants",)
    search_fields = ("dna", "ship__name")
    list_select_related = ("ship",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs) -> ModelChoiceField:
        if db_field.name == "ship":
            kwargs["queryset"] = EveItemType.objects.filter(group__category_id=EVECATEGORY_SHIP)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ApprovedImplantSet)
class ApprovedImplantSetAdmin(admin.ModelAdmin):
    list_display = ("pk", "implants")
    search_fields = ("implants",)


@admin.register(ActiveFleet)
class ActiveFleetAdmin(admin.ModelAdmin):
    list_display = ("pk", "fleet")
    search_fields = ("fleet__id", "fleet__boss__character_name")
    list_select_related = ("fleet",)


@admin.register(SkillCheck)
class SkillCheckAdmin(admin.ModelAdmin):
    list_display = ("skill", "min", "elite", "gold")
    search_fields = ("skill__name",)
    ordering = ("skill",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs) -> ModelChoiceField:
        if db_field.name == "skill":
            kwargs["queryset"] = EveItemType.objects.filter(group__category_id=EVECATEGORY_SKILLS)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(ApprovedSkills)
class ApprovedSkillsAdmin(admin.ModelAdmin):
    list_display = ("ship",)
    search_fields = ("ship__name",)
    filter_horizontal = ("skill_checks",)

    def formfield_for_dbfield(self, db_field, request, **kwargs) -> ModelChoiceField:
        if db_field.name == "ship":
            kwargs["queryset"] = EveItemType.objects.filter(group__category_id=EVECATEGORY_SHIP)
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
    list_display = ("pk", "main_character", "joined_at", "waitlist")
    search_fields = ("main_character__character_name",)
    list_filter = ("waitlist",)
    date_hierarchy = "joined_at"
    list_select_related = ("main_character", "waitlist")

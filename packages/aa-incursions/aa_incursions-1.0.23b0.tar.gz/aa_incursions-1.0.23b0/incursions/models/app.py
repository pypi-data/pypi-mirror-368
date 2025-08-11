from django.db import models


class General(models.Model):
    """Meta model for app permissions"""

    class Meta:
        managed = False
        default_permissions = ()
        permissions = (
            ("basic_waitlist", "Waitlist Access"),  # All
            ("waitlist_alts_view", "View - all of a users Alts ! Danger?"),  # Leadership
            ("waitlist_announcements_manage", "Announcements - Manage"),  # Leadership
            ("waitlist_badges_view", "Badges - View"),  # FC
            ("waitlist_badges_manage", "Badges - Manage"),  # Leadership
            ("waitlist_bans_view", "Bans - View"),  # FC
            ("waitlist_bans_manage", "Bans - Manage"),  # Leadership
            ("waitlist_documentation_view", "Documentation - View"),  # Jr FC
            ("waitlist_fleet_view", "Fleet Composition"),  # FC
            ("waitlist_history_view", "Fleet History"),  # Leadership
            ("waitlist_notes_view", "Notes - View"),  # FC
            ("waitlist_notes_manage", "Notes - Manage"),  # Leadership
            ("waitlist_search", "Search"),  # FC
            ("waitlist_stats_view", "Fleet Stats"),  # Leadership
            ("waitlist_skills_view", "Skills"),  # Leadership
            ("waitlist_pilot_view", "Pilot Information"),  # Leadership
            # Add extra context to the Waitlist for Non-FCs
            ("waitlist_context_a", "Context: Number of Pilots"),
            ("waitlist_context_b", "Context: Ship Types"),
            ("waitlist_context_c", "Context: Time in Waitlist"),
            ("waitlist_context_d", "Context: Pilot Names"),
            ("waitlist_implants_view", "Context: Implants"),  # FC

            ("waitlist_manage_waitlist", "Waitlist Manage"),  # FC
            ("waitlist_manage_waitlist_approve_fits", "Waitlist Manage Fits"),  # FC

            # ESI Calls, Limit these maybe?
            ("waitlist_esi_show_info", "Show Info"),
            ("waitlist_esi_search", "Search - ESI"),
        )

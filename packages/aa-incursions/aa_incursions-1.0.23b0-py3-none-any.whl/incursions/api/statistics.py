from collections import defaultdict
from datetime import timedelta

from ninja import NinjaAPI, Schema

from django.db.models import Count, DurationField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncMonth
from django.utils import timezone

from incursions.models.waitlist import FleetActivity, WaitlistEntryFit


def get_fleet_seconds_by_ship_by_month():
    result = defaultdict(lambda: defaultdict(float))
    qs = (
        FleetActivity.objects
        .annotate(month=TruncMonth('first_seen'))
        .annotate(duration=ExpressionWrapper(F('last_seen') - F('first_seen'), output_field=DurationField()))
        .values('month', 'ship__name')
        .annotate(total=Sum('duration'))
    )
    for row in qs:
        month = row['month'].strftime("%Y-%m")
        result[month][row['ship__name']] += row['total'].total_seconds()
    return result


def get_xes_by_ship_by_month():
    result = defaultdict(lambda: defaultdict(float))
    qs = (
        WaitlistEntryFit.objects
        .annotate(month=TruncMonth('waitlist_entry__joined_at'))
        .values('month', 'fit__ship__name')
        .annotate(count=Count('id'))
    )
    for row in qs:
        month = row['month'].strftime("%Y-%m")
        result[month][row['fit__ship__name']] += row['count']
    return result


def get_fleet_seconds_by_month():
    result = defaultdict(float)
    qs = (
        FleetActivity.objects
        .annotate(month=TruncMonth('first_seen'))
        .annotate(duration=ExpressionWrapper(F('last_seen') - F('first_seen'), output_field=DurationField()))
        .values('month')
        .annotate(total=Sum('duration'))
    )
    for row in qs:
        month = row['month'].strftime("%Y-%m")
        result[month] += row['total'].total_seconds()
    return result


def get_pilots_by_month():
    result = defaultdict(int)
    qs = (
        FleetActivity.objects
        .annotate(month=TruncMonth('first_seen'))
        .values('month')
        .annotate(pilots=Count('character', distinct=True))
    )
    for row in qs:
        month = row['month'].strftime("%Y-%m")
        result[month] = row['pilots']
    return result


def get_xes_by_ship_28d():
    result = defaultdict(float)
    since = timezone.now() - timedelta(days=28)
    qs = (
        WaitlistEntryFit.objects
        .filter(waitlist_entry__joined_at__gte=since)
        .values('fit__ship__name')
        .annotate(count=Count('id'))
    )
    for row in qs:
        result[row['fit__ship__name']] += row['count']
    return result


def get_fleet_seconds_by_ship_28d():
    result = defaultdict(float)
    since = timezone.now() - timedelta(days=28)
    qs = (
        FleetActivity.objects
        .filter(first_seen__gte=since)
        .annotate(duration=ExpressionWrapper(F('last_seen') - F('first_seen'), output_field=DurationField()))
        .values('ship__name')
        .annotate(total=Sum('duration'))
    )
    for row in qs:
        result[row['ship__name']] += row['total'].total_seconds()
    return result


def get_x_vs_time_by_ship_28d():
    xes = get_xes_by_ship_28d()
    seconds = get_fleet_seconds_by_ship_28d()
    result = defaultdict(dict)
    for ship in xes:
        result[ship]['xes'] = xes[ship]
        result[ship]['seconds'] = seconds.get(ship, 0)
    return result


def get_time_spent_in_fleet_by_month():
    result = defaultdict(lambda: defaultdict(float))
    qs = (
        FleetActivity.objects
        .annotate(month=TruncMonth('first_seen'))
        .annotate(duration=ExpressionWrapper(F('last_seen') - F('first_seen'), output_field=DurationField()))
        .values('month', 'character__character_name')
        .annotate(total=Sum('duration'))
    )
    for row in qs:
        month = row['month'].strftime("%Y-%m")
        result[month][row['character__character_name']] += row['total'].total_seconds()
    return result


class StatsResponse(Schema):
    fleet_seconds_by_ship_by_month: dict[str, dict[str, float]]
    xes_by_ship_by_month: dict[str, dict[str, float]]
    fleet_seconds_by_month: dict[str, float]
    pilots_by_month: dict[str, float]
    xes_by_ship_28d: dict[str, float]
    fleet_seconds_by_ship_28d: dict[str, float]
    x_vs_time_by_ship_28d: dict[str, dict[str, float]]
    time_spent_in_fleet_by_month: dict[str, dict[str, float]]


api = NinjaAPI()


def setup(api: NinjaAPI) -> None:
    StatisticsAPIEndpoints(api)


class StatisticsAPIEndpoints:

    tags = ["Statistics"]

    def __init__(self, api: NinjaAPI) -> None:

        @api.get("/stats", response={200: StatsResponse, 403: dict}, tags=self.tags)
        def statistics(request):
            if not request.user.has_perm("incursions.waitlist_stats_view"):
                return 403, {"error": "Permission denied"}

            return StatsResponse(
                fleet_seconds_by_ship_by_month=get_fleet_seconds_by_ship_by_month,
                xes_by_ship_by_month=get_xes_by_ship_by_month,
                fleet_seconds_by_month=get_fleet_seconds_by_month,
                pilots_by_month=get_pilots_by_month,
                xes_by_ship_28d=get_xes_by_ship_28d,
                fleet_seconds_by_ship_28d=get_fleet_seconds_by_ship_28d,
                x_vs_time_by_ship_28d=get_x_vs_time_by_ship_28d,
                time_spent_in_fleet_by_month=get_time_spent_in_fleet_by_month
            )

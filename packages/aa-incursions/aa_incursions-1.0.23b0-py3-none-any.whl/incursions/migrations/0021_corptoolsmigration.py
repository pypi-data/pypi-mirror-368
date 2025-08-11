from django.db import migrations


def migrate_incursion_locations(apps, schema_editor):
    Incursion = apps.get_model('incursions', 'Incursion')
    MapConstellation = apps.get_model('corptools', 'MapConstellation')
    MapSystem = apps.get_model('corptools', 'MapSystem')

    for incursion in Incursion.objects.all():
        if incursion.constellation:
            try:
                incursion.migration_constellation = MapConstellation.objects.get(constellation_id=incursion.constellation.id)
            except MapConstellation.DoesNotExist:
                pass

        if incursion.staging_solar_system:
            try:
                incursion.migration_staging_solar_system = MapSystem.objects.get(
                    system_id=incursion.staging_solar_system.id
                )
            except MapSystem.DoesNotExist:
                pass

        incursion.save()

        system_ids = incursion.infested_solar_systems.values_list('id', flat=True)
        mapped_systems = MapSystem.objects.filter(system_id__in=system_ids)
        incursion.migration_infested_solar_systems.set(mapped_systems)


def reverse_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('corptools', '0118_alter_skill_id'),
        ('incursions', '0020_alter_incursion_migration_infested_solar_systems'),
    ]

    operations = [
        migrations.RunPython(migrate_incursion_locations, reverse_migration),
    ]

from django.apps import AppConfig

from . import __version__


class IncursionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = "incursions"
    verbose_name = f'AA Incursions v{__version__}'

    def ready(self) -> None:
        import incursions.models.app  # Nothing Imports this file, so its here
        import incursions.signals  # noqa: F401

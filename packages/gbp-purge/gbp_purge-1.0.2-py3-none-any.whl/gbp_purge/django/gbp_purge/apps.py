"""AppsConfig for gbp-purge"""

from importlib import import_module

from django.apps import AppConfig


class GBPPurgeConfig(AppConfig):
    """AppConfig for gbp-purge"""

    name = "gbp_purge.django.gbp_purge"
    verbose_name = "Gentoo Build Publisher purge plugin"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self) -> None:
        signals = import_module("gbp_purge.signals")
        signals.init()

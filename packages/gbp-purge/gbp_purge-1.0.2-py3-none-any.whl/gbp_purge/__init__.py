"""gbp-purge: Gentoo Build Publisher plugin for purging old builds"""

import importlib.metadata

__version__ = importlib.metadata.version("gbp-purge")

# Plugin definition
plugin = {
    "name": "gbp-purge",
    "version": __version__,
    "description": "A plugin for purging old builds",
    "app": "gbp_purge.django.gbp_purge.apps.GBPPurgeConfig",
}

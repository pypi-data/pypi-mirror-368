"""gbp-purge signal handlers"""

from typing import Any

from gbp_purge.gateway import GBPGateway
from gbp_purge.types import BuildLike
from gbp_purge.worker import tasks


# pylint: disable=unused-argument,import-outside-toplevel
def gbp_build_pulled(*, build: BuildLike, packages: Any, gbp_metadata: Any) -> None:
    """Purge old builds for the machine given by build"""

    gateway = GBPGateway()
    gateway.run_task(tasks.purge_machine, build.machine)


def init() -> None:
    """Initialize"""
    from gentoo_build_publisher import signals

    dispatcher = signals.dispatcher
    dispatcher.bind(postpull=gbp_build_pulled)

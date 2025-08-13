"""Gateway to the Gentoo Build Publisher"""

from __future__ import annotations

import datetime as dt
import logging
from typing import TYPE_CHECKING, Any, Callable, ParamSpec

from gbp_purge.purger import Purger

if TYPE_CHECKING:
    from gentoo_build_publisher.records import BuildRecord  # pragma nocover

logger = logging.getLogger(__name__)
P = ParamSpec("P")


class GBPGateway:
    """The GBP Gateway"""

    # pylint: disable=import-outside-toplevel
    def run_task(
        self, func: Callable[P, Any], *args: P.args, **kwargs: P.kwargs
    ) -> None:
        """Send the given callable (and args to the GBP task worker to run"""
        from gentoo_build_publisher import worker

        worker.run(func, *args, **kwargs)

    def purge(self, machine: str) -> None:
        """Purge old builds for machine"""
        from gentoo_build_publisher import publisher
        from gentoo_build_publisher.worker.tasks import delete_build

        logger.info("Purging builds for %s", machine)
        build_records = publisher.repo.build_records
        purger = Purger(build_records.for_machine(machine), key=_purge_key)

        for record in purger.purge():
            if not (record.keep or publisher.storage.get_tags(record)):
                self.run_task(delete_build, str(record))


def _purge_key(build_record: BuildRecord) -> dt.datetime:
    """Purge key for build records.  Purge on submitted date"""
    submitted = build_record.submitted or dt.datetime.fromtimestamp(0)

    return submitted.replace(tzinfo=None)

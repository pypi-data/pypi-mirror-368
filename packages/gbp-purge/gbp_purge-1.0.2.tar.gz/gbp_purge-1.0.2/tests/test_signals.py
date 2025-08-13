"""tests for gbp_purge.signals"""

import datetime as dt
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gentoo_build_publisher.records import BuildRecord
from unittest_fixtures import Fixtures, given, where

from . import fixtures as tf

# pylint: disable=missing-docstring
time = dt.datetime.fromisoformat


@given(
    testkit.environ,
    tf.now,
    testkit.publisher,
    old_build=testkit.build,
    new_build=testkit.build,
)
@where(
    now=time("2025-02-25 07:00:00"), environ={"BUILD_PUBLISHER_WORKER_BACKEND": "sync"}
)
class SignalsTests(TestCase):
    def test(self, fixtures: Fixtures) -> None:
        publisher = fixtures.publisher
        records = publisher.repo.build_records

        old_build = fixtures.old_build
        old_record = BuildRecord(
            machine=old_build.machine,
            build_id=old_build.build_id,
            submitted=time("2025-02-17 07:00:00+0000"),
        )
        publisher.pull(old_record)

        new_build = fixtures.new_build
        new_record = BuildRecord(
            machine=new_build.machine,
            build_id=new_build.build_id,
            submitted=time("2025-02-25 00:00:00+0000"),
        )
        publisher.pull(new_record)

        machine = old_build.machine
        builds = [str(record) for record in records.for_machine(machine)]
        self.assertEqual([str(new_build)], builds)

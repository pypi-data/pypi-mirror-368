# pylint: disable=missing-docstring
import datetime as dt
from unittest import TestCase

import gbp_testkit.fixtures as testkit
from gbp_testkit.factories import BuildFactory
from gentoo_build_publisher.types import Content
from unittest_fixtures import Fixtures, given

from gbp_purge.gateway import GBPGateway


@given(testkit.build, testkit.publisher)
class PurgeTests(TestCase):
    def test_purge_deletes_old_build(self, fixtures: Fixtures) -> None:
        """Should remove purgeable builds"""
        publisher = fixtures.publisher
        old_build = fixtures.build
        publisher.pull(old_build)
        record = publisher.record(old_build)
        publisher.repo.build_records.save(
            record, submitted=dt.datetime(1970, 1, 1, tzinfo=dt.UTC)
        )

        new_build = BuildFactory()
        publisher.pull(new_build)
        record = publisher.record(new_build)
        publisher.repo.build_records.save(
            record, submitted=dt.datetime(1970, 12, 31, tzinfo=dt.UTC)
        )

        gateway = GBPGateway()
        gateway.purge(old_build.machine)

        self.assertIs(publisher.repo.build_records.exists(old_build), False)

        for item in Content:
            path = publisher.storage.get_path(old_build, item)
            self.assertIs(path.exists(), False, path)

    def test_purge_does_not_delete_old_tagged_builds(self, fixtures: Fixtures) -> None:
        """Should remove purgeable builds"""

        publisher = fixtures.publisher
        repo = publisher.repo
        datetime = dt.datetime
        kept_build = BuildFactory(machine="lighthouse")
        repo.build_records.save(
            publisher.record(kept_build),
            submitted=datetime(1970, 1, 1, tzinfo=dt.UTC),
            keep=True,
        )
        tagged_build = BuildFactory(machine="lighthouse")
        repo.build_records.save(
            publisher.record(tagged_build),
            submitted=datetime(1970, 1, 1, tzinfo=dt.UTC),
        )
        publisher.pull(tagged_build)
        publisher.tag(tagged_build, "prod")
        repo.build_records.save(
            publisher.record(BuildFactory(machine="lighthouse")),
            submitted=datetime(1970, 12, 31, tzinfo=dt.UTC),
        )

        gateway = GBPGateway()
        gateway.purge("lighthouse")

        self.assertIs(repo.build_records.exists(kept_build), True)
        self.assertIs(repo.build_records.exists(tagged_build), True)

    def test_purge_doesnt_delete_old_published_build(self, fixtures: Fixtures) -> None:
        """Should not delete old build if published"""
        publisher = fixtures.publisher
        build = fixtures.build
        repo = publisher.repo

        publisher.publish(build)
        repo.build_records.save(
            publisher.record(build), submitted=dt.datetime(1970, 1, 1, tzinfo=dt.UTC)
        )
        repo.build_records.save(
            publisher.record(BuildFactory()),
            submitted=dt.datetime(1970, 12, 31, tzinfo=dt.UTC),
        )

        gateway = GBPGateway()
        gateway.purge(build.machine)

        self.assertIs(repo.build_records.exists(build), True)

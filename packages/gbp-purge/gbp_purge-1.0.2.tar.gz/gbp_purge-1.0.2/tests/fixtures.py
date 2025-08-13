# pylint: disable=missing-docstring,unused-argument,disable=redefined-outer-name
import datetime as dt
from unittest import mock

from unittest_fixtures import FixtureContext, Fixtures, fixture


@fixture()
def now(
    fixtures: Fixtures, now: dt.datetime | None = None, at: str = "gbp_purge.purger.dt"
) -> FixtureContext[dt.datetime]:
    new = now or dt.datetime.now()

    with mock.patch(at, wraps=dt) as mock_dt:
        mock_dt.datetime.now.return_value = new
        yield new

"""Data structures for gbp-purge"""

from typing import Protocol


class BuildLike(Protocol):  # pylint: disable=too-few-public-methods
    """This is the internal representation of a GBP build.

    Used by the gateway so we don't have to expose the implementation of actual data
    type.
    """

    machine: str
    build_id: str

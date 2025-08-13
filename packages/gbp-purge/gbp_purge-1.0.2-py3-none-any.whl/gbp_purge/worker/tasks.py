"""gbp-purge tasks

Background tasks used by gbp-purge.

These need to be self-contained, meaning they need to be able to be run without global
variables as this is a requirement of all Gentoo Build Publisher background tasks. Hence
the internal imports.
"""

# pylint: disable=import-outside-toplevel


def purge_machine(machine: str) -> None:
    """Background task to purge a given machine"""
    # This probably *doesn't* need to be a background task as publisher.delete() runs as
    # a background task and thus purge() actually runs pretty quickly.
    from gbp_purge.gateway import GBPGateway

    gateway = GBPGateway()

    gateway.purge(machine)

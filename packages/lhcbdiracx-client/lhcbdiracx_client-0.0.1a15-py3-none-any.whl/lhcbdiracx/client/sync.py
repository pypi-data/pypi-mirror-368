from __future__ import absolute_import

__all__ = [
    "SyncLHCbDiracXClient",
    "sync_operations",
]

from ._generated import Dirac
from ._generated import operations as sync_operations


class SyncLHCbDiracXClient(Dirac):
    pass


SyncDiracClient = SyncLHCbDiracXClient

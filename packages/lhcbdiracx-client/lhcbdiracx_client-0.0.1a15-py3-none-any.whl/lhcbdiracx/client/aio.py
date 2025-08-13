from __future__ import absolute_import

__all__ = [
    "AsyncLHCbDiracXClient",
    "async_operations",
]

from ._generated.aio import Dirac
from ._generated.aio import operations as async_operations


class AsyncLHCbDiracXClient(Dirac):
    pass


AsyncDiracClient = AsyncLHCbDiracXClient

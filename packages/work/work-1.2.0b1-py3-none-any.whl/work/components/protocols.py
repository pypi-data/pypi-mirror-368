"""Protocols (interfaces) for typing."""

from typing import Protocol

# pylint: disable=missing-function-docstring


### <MIGRATE-midnight> To be removed in v1.3 ###


class IMigratable(Protocol):
    """Protocol for a migratable object."""

    def migrate_records_touching_midnight(self, end_lower_bound) -> None: ...

    def protocol_empty(self) -> bool: ...


class IFlags(Protocol):
    """Protocol of a `Flags` object."""

    def is_set(self, key: str) -> bool: ...

    def set(self, *flags: str) -> None: ...

    def remove(self, *flags: str) -> None: ...

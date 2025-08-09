from __future__ import annotations

import logging
from enum import Enum

import ida_typeinf
from typing_extensions import TYPE_CHECKING, Iterator, Optional

from .base import DatabaseEntity, InvalidEAError, check_db_open, decorate_all_methods

if TYPE_CHECKING:
    from ida_idaapi import ea_t

    from .database import Database


logger = logging.getLogger(__name__)


class TypeKind(Enum):
    """Type category enumeration."""

    NAMED = 1
    NUMBERED = 2


@decorate_all_methods(check_db_open)
class Types(DatabaseEntity):
    """
    Provides access to type information and manipulation in the IDA database.

    Can be used to iterate over all types in the opened database.

    Args:
        database: Reference to the active IDA database.
    """

    def __init__(self, database: Database):
        super().__init__(database)

    def __iter__(self) -> Iterator[ida_typeinf.tinfo_t]:
        return self.get_all()

    def get_name_at(self, ea: ea_t) -> str | None:
        """
        Retrieves the type information of the item at the given address.

        Args:
            ea: The effective address.

        Returns:
            The type name or None if it does not exist.

        Raises:
            InvalidEAError: If the effective address is invalid.
        """
        if not self.database.is_valid_ea(ea):
            raise InvalidEAError(ea)
        return ida_typeinf.idc_get_type(ea)

    def apply_named_type(self, ea: ea_t, type: str) -> bool:
        """
        Applies a named type to the given address.

        Args:
            ea: The effective address.
            type: The name of the type to apply.

        Returns:
            True if the type was applied successfully, false otherwise.

        Raises:
            InvalidEAError: If the effective address is invalid.
        """
        if not self.database.is_valid_ea(ea):
            raise InvalidEAError(ea)
        return ida_typeinf.apply_named_type(ea, type)

    def get_all(
        self, type_kind: TypeKind = TypeKind.NAMED, type_library: str = ''
    ) -> Iterator[ida_typeinf.tinfo_t]:
        """
        Retrieves a generator over all types in the specified type library.
        """
        if type_library is not None and type_library != '':
            til = ida_typeinf.load_til(type_library)
        else:
            til = ida_typeinf.get_idati()

        if type_kind == TypeKind.NAMED:
            name = ida_typeinf.first_named_type(til, ida_typeinf.NTF_TYPE)
            while name is not None and name != '':
                tinf = til.get_named_type(name)
                if tinf is not None:
                    yield tinf
                name = ida_typeinf.next_named_type(til, name, ida_typeinf.NTF_TYPE)
        elif type_kind == TypeKind.NUMBERED:
            qty = ida_typeinf.get_ordinal_limit(til)
            if 0 < qty < 0xFFFFFFFF:
                for index in range(1, qty):
                    tinf = til.get_numbered_type(index)
                    yield tinf

    def get_names(self, type_library: str = '') -> Iterator[str]:
        """
        Retrieves a generator over all names in the specified type library.
        """
        til = None
        if type_library != '':
            til = ida_typeinf.load_til(type_library)

        name = ida_typeinf.first_named_type(til, ida_typeinf.NTF_TYPE)
        while name is not None and name != '':
            yield name
            name = ida_typeinf.next_named_type(til, name, ida_typeinf.NTF_TYPE)

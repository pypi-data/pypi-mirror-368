# -*- coding: utf-8 -*-
#
# Copyright (c) 2025~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import types
from dataclasses import dataclass
from typing import Type

from ._primitive_symbol import TypedSymbol


@dataclass(frozen=True, slots=True)
class _NamedTypeListKey:
    '''
    Internal use only.
    '''
    type: type


@dataclass(frozen=True, slots=True)
class NamedType[T]:
    '''
    The NamedType can inject into the `**kwargs`.
    '''
    name: str
    type: Type[T]

    def __post_init__(self) -> None:
        if not isinstance(self.type, (type, types.GenericAlias)):
            raise TypeError(self.type)


__all__ = [
    'TypedSymbol',
    'NamedType',
]

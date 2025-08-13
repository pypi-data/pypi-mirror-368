# -*- coding: utf-8 -*-
# 
# Copyright (c) 2025~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import types
from typing import ForwardRef, Type, get_args

# symbol is primitive type, import any modules from . is not allowed.


class _Symbol:
    '''
    Symbol with description.
    '''

    __slots__ = ('_name', )

    def __init__(self, name: str='') -> None:
        self._name = name

    def __str__(self) -> str:
        return f'Symbol({self._name})'

    def __repr__(self) -> str:
        return f'Symbol({self._name!r})'


class TypedSymbol[T](_Symbol):
    '''
    Symbol with type.

    MUST use `TypedSymbol[...](...)` instead of `TypedSymbol(...)` directly.
    '''

    __slots__ = (
        '__orig_class__',
        '_type', # for cached property
    )

    def __str__(self) -> str:
        ta = self._get_type_args()
        tn = self._get_type_args_repr(ta)
        return f'TypedSymbol[{tn}]({self._name})'

    def __repr__(self) -> str:
        ta = self._get_type_args()
        tn = self._get_type_args_repr(ta)
        return f'TypedSymbol[{tn}]({self._name!r})'

    def _get_type_args(self) -> Type[T]:
        if (oc := getattr(self, '__orig_class__', None)) is not None:
            return get_args(oc)[0]
        raise TypeError('TypedSymbol is created without type args')

    @classmethod
    def _get_type_args_repr(cls, o: object) -> str:
        try:
            if isinstance(o, ForwardRef):
                return o.__forward_arg__
            elif isinstance(o, types.UnionType):
                return ' | '.join(cls._get_type_args_repr(x) for x in get_args(o))
            else:
                return getattr(o, '__name__', str(o))
        except AttributeError:
            return str(o)

    def get_type(self) -> type:
        '''
        Get the type of this symbol
        '''
        if not hasattr(self, '_type'):
            self._type = self._get_type_args()
        return self._type

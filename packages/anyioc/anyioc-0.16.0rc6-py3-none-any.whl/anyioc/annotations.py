# -*- coding: utf-8 -*-
# 
# Copyright (c) 2025~2999 - Cologler <skyoflw@gmail.com>
# ----------
# 
# ----------

from dataclasses import dataclass, field
from typing import Callable, Hashable, Iterable

from ._bases import LifeTime
from ._service_info import GetOrDefaultServiceInfo

_UNSET_KEY = object()


@dataclass(frozen=True, slots=True, eq=False)
class InjectBy:
    '''
    Inject args by key.

    Equals:

    ```
    provider.get(key, default) if has_default() else provider[key]
    ```

    For VAR_POSITIONAL parameter, this equals:

    ```
    * provider.get_many(key)
    ```
    '''

    key: Hashable = field(default=_UNSET_KEY)
    default: object = field(default=GetOrDefaultServiceInfo._UNSET)
    # kwonly:
    lifetime: LifeTime = field(default=LifeTime.transient, kw_only=True)
    name: str | None = field(default=None, kw_only=True)

    def __post_init__(self) -> None:
        if self.lifetime == LifeTime.singleton:
            # we don't known which IServiceProvider own this.
            raise ValueError('Singleton lifetime for InjectBy is not allowed.')

        if self.has_key() and self.has_name():
            raise ValueError('key and name cannot use togeter.')

        if not self.has_key() and not self.has_name():
            raise ValueError('Missing key or name.')

    def has_key(self) -> bool:
        return self.key is not _UNSET_KEY

    def has_name(self) -> bool:
        return self.name is not None

    def has_default(self) -> bool:
        return self.default is not GetOrDefaultServiceInfo._UNSET


@dataclass(frozen=True, slots=True, eq=False)
class InjectByGroup:
    '''
    Inject args as tuple group.

    Equals:

    ```
    tuple(provider[k] for k in keys)
    ```

    For VAR_POSITIONAL parameter, this equals:

    ```
    * tuple(provider[k] for k in keys)
    ```
    '''
    keys: Iterable[Hashable]


@dataclass(frozen=True, slots=True, eq=False)
class InjectWithValue:
    '''
    Inject with the fixed value.

    Equals:

    ```
    value
    ```

    For VAR_POSITIONAL parameter, this is not allowed.
    '''
    value: object


@dataclass(frozen=True, slots=True, eq=False)
class InjectFrom:
    '''
    Inject from a callable.
    '''

    func: Callable[..., object]


__all__ = [
    'InjectBy',
    'InjectByGroup',
    'InjectFrom',
    'InjectWithValue',
]

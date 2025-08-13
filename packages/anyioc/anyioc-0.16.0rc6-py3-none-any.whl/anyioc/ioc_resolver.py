# -*- coding: utf-8 -*-
#
# Copyright (c) 2018~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import sys
import types
from collections.abc import Hashable
from contextlib import nullcontext
from threading import RLock
from typing import Any, get_args, get_origin, override

from ._bases import IServiceInfo, IServiceProvider
from ._service_info import FactoryServiceInfo, GetManyServiceInfo, ValueServiceInfo
from ._utils import wrap_signature
from .err import ServiceNotFoundError


class IServiceInfoResolver:
    '''
    the base class for dynamic resolve `IServiceInfo`.
    '''

    def get(self, provider: IServiceProvider, key: Hashable, /) -> IServiceInfo[Any]:
        '''
        Get the `IServiceInfo` from resolver.
        '''
        raise ServiceNotFoundError(key)

    def __add__(self, other: 'IServiceInfoResolver') -> 'IServiceInfoResolver':
        new_resolver = ServiceInfoChainResolver()
        new_resolver.chain.append(self)
        new_resolver.append(other)
        return new_resolver

    def cache(self, *, sync: bool=False) -> 'IServiceInfoResolver':
        '''
        Returns a `IServiceInfoResolver` to cache all `IServiceInfo`s from this `IServiceInfoResolver`.

        All values won't dynamic update after the first resolved.
        '''
        return CacheServiceInfoResolver(self, sync=sync)


class ServiceInfoChainResolver(IServiceInfoResolver):
    '''
    A chained resolver for resolve IServiceInfos from each `IServiceInfoResolver`
    '''

    def __init__(self, *resolvers: IServiceInfoResolver) -> None:
        self.chain = list(resolvers)

    def get(self, provider: IServiceProvider, key: Hashable) -> IServiceInfo[Any]:
        for resolver in self.chain:
            try:
                return resolver.get(provider, key)
            except ServiceNotFoundError:
                pass
        return super().get(provider, key)

    def append(self, other: IServiceInfoResolver) -> None:
        if isinstance(other, ServiceInfoChainResolver):
            self.chain.extend(other.chain)
        else:
            self.chain.append(other)

    def __add__(self, other: 'IServiceInfoResolver') -> 'ServiceInfoChainResolver':
        new_resolver = ServiceInfoChainResolver()
        new_resolver.chain.extend(self.chain)
        new_resolver.append(other)
        return new_resolver


class CacheServiceInfoResolver(IServiceInfoResolver):
    '''
    a helper resolver for cache values from other `IServiceInfoResolver`

    NOTE:
    if a `IServiceInfo` is affect by `provider`, you should not cache it.
    `CacheServiceInfoResolver` only cache by the `key` and ignore the `provider` arguments.
    '''

    def __init__(self, base_resolver: IServiceInfoResolver, *, sync: bool=False) -> None:
        super().__init__()
        self._base_resolver = base_resolver
        self._cache = {}
        self._lock = RLock() if sync else nullcontext()

    def get(self, provider: IServiceProvider, key: Hashable) -> IServiceInfo[Any]:
        try:
            return self._cache[key]
        except KeyError:
            pass
        with self._lock:
            try:
                return self._cache[key]
            except KeyError:
                pass
            service_info = self._base_resolver.get(provider, key)
            self._cache[key] = service_info
            return service_info

    def cache(self, *, sync: bool=False) -> 'IServiceInfoResolver':
        if sync and isinstance(self._lock, nullcontext):
            return CacheServiceInfoResolver(self, sync=sync)
        return self


class ImportServiceInfoResolver(IServiceInfoResolver):
    '''
    Dynamic resolve `IServiceInfo` if the key is a module name.

    - Relative import is not allowed;
    - If the key is `{module_name}`, only lookup modules from `sys.modules`;
    - If the key is `module::{module_name}` (startswith `module::`), the resolver will try to import it;
    '''

    @override
    def get(self, provider: IServiceProvider, key: Hashable, /) -> IServiceInfo[types.ModuleType]:
        if isinstance(key, str) and not key.startswith('.'): # relative import is not allows
            if key.startswith('module::'):
                module_name = key.removeprefix('module::')
                import importlib
                try:
                    module = importlib.import_module(module_name)
                    return ValueServiceInfo(module)
                except (TypeError, ModuleNotFoundError):
                    pass
            else:
                module_name = key
                if module := sys.modules.get(module_name):
                    return ValueServiceInfo(module)
        return super().get(provider, key)


class TypesServiceInfoResolver(IServiceInfoResolver):
    '''
    Dynamic resolve `IServiceInfo` if the key is a type instance.
    '''

    def get(self, provider: IServiceProvider, key: Hashable) -> IServiceInfo[Any]:
        if isinstance(key, type):
            return FactoryServiceInfo(wrap_signature(key))
        return super().get(provider, key)


class TypeNameServiceInfoResolver(IServiceInfoResolver):
    '''
    dynamic resolve `IServiceInfo` if the key is a type name or qualname.
    '''

    def _get_type(self, key: Hashable) -> type | None:
        if isinstance(key, str):
            for klass in object.__subclasses__():
                if getattr(klass, '__name__', None) == key:
                    return klass
                if getattr(klass, '__qualname__', None) == key:
                    return klass
        # None

    def get(self, provider: IServiceProvider, key: Hashable) -> IServiceInfo[Any]:
        klass = self._get_type(str)
        if klass is not None:
            return FactoryServiceInfo(wrap_signature(klass))
        return super().get(provider, key)


class GenericListAsGetManyServiceInfoResolver(IServiceInfoResolver):
    '''
    Dynamic resolve `IServiceInfo` for `list[T]` to `.get_many(T)`
    '''
    def __init__(self,
            for_list: bool=True,
            for_tuple: bool=False,
        ) -> None:
        super().__init__()
        self._for_list = for_list
        self._for_tuple = for_tuple

    @override
    def get(self, provider: IServiceProvider, key: Hashable) -> IServiceInfo[Any]:
        if isinstance(key, types.GenericAlias) and get_origin(key) is list:
            return GetManyServiceInfo(get_args(key)[0])
        return super().get(provider, key)

# -*- coding: utf-8 -*-
# 
# Copyright (c) 2025~2999 - Cologler <skyoflw@gmail.com>
# ----------
# 
# ----------

from contextlib import nullcontext
from threading import RLock
from typing import Any, Hashable, Iterable, final, override

from .._bases import Factory, IServiceInfo, IServiceProvider, LifeTime
from ..symbols import Symbols

_NULL_CONTEXT = nullcontext()


@final
class ProviderServiceInfo(IServiceInfo[IServiceProvider]):
    '''
    Get current `ServiceProvider`.
    '''
    _INSTANCE: 'ProviderServiceInfo'
    __slots__ = ()

    def __repr__(self) -> str:
        return '<(ioc) => ioc>'

    @override
    def get_service(self, provider: IServiceProvider) -> IServiceProvider:
        return provider

    @classmethod
    def get_singleton_instance(cls) -> 'ProviderServiceInfo':
        return cls._INSTANCE

ProviderServiceInfo._INSTANCE = ProviderServiceInfo()


class GetAttrServiceInfo[T, TD](IServiceInfo[T | TD]):
    '''
    Call `getattr()` from current `ServiceProvider`.
    '''

    __slots__ = ('_getattr_args',)
    _UNSET = object()

    def __init__(self, attr_name: str, attr_default: TD=_UNSET) -> None:
        super().__init__()
        self._getattr_args = (attr_name,) if attr_default is self._UNSET else (attr_name, attr_default)

    def __repr__(self) -> str:
        getattr_args = ', '.join(repr(x) for x in self._getattr_args)
        return f'<(ioc) => getattr(ioc, {getattr_args})>'

    @override
    def get_service(self, provider: IServiceProvider) -> T | TD:
        return getattr(provider, *self._getattr_args) # type: ignore


class ValueServiceInfo[T](IServiceInfo[T]):
    '''a `IServiceInfo` use for get fixed value.'''

    __slots__ = ('_value',)

    def __init__(self, value: T) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f'<(_) => {self._value!r}>'

    @override
    def get_service(self, provider: IServiceProvider) -> T:
        return self._value


class BindedServiceInfo(IServiceInfo[object]):
    '''a `IServiceInfo` use for get value from target key.'''

    __slots__ = ('_target_key',)

    def __init__(self, target_key: Hashable) -> None:
        self._target_key = target_key

    def __repr__(self) -> str:
        return f'<(ioc) => ioc[{self._target_key!r}]>'

    @override
    def get_service(self, provider: IServiceProvider) -> object:
        return provider[self._target_key]


class FactoryServiceInfo[T](IServiceInfo[T]):
    __slots__ = ('_factory')

    def __init__(self, factory: Factory[T]) -> None:
        self._factory = factory

    @override
    def get_service(self, provider: IServiceProvider) -> T:
        return self._factory(provider)


class BoundServiceInfo[T](IServiceInfo[T]):
    __slots__ = (
        '_service_info',
        '_service_provider'
    )

    def __init__(self, service_provider: IServiceProvider, service_info: IServiceInfo[T]) -> None:
        self._service_info = service_info
        self._service_provider = service_provider

    def __repr__(self) -> str:
        return f'<Bound {self._service_info!r}>'

    @override
    def get_service(self, provider: IServiceProvider) -> T:
        return self._service_info.get_service(self._service_provider)

    @staticmethod
    def wrap(service_provider: IServiceProvider, service_info: IServiceInfo[T]) -> 'BoundServiceInfo[T]':
        if type(service_info) is BoundServiceInfo:
            service_info = service_info._service_info
        return BoundServiceInfo(service_provider, service_info)


class LifetimeServiceInfo[T](IServiceInfo[T]):
    __slots__ = (
        '_service_info', '_lifetime',
        # for not transient
        '_lock',
        # for singleton
        '_cached_value',
        # for scoped
        '_scoped_key',
    )

    _NOT_ALLOWED_KEYS = frozenset([
        Symbols.cache,
    ])

    def __init__(self, *,
            lifetime: LifeTime,
            service_provider: IServiceProvider | None,
            key: Hashable,
            service_info: IServiceInfo[T],
            scoped_key: Hashable | None = None,
        ) -> None:

        if key in self._NOT_ALLOWED_KEYS:
            raise ValueError(f'Key {key!r} is not allowed')

        if lifetime == LifeTime.singleton:
            assert service_provider is not None
            # service_provider is required when the lifetime is singleton
            service_info = BoundServiceInfo.wrap(service_provider, service_info)
            # the resolved value maybe a None, so we should cache it as a tuple.
            self._cached_value: tuple[T] | None = None

        self._lifetime = lifetime
        self._service_info = service_info
        self._scoped_key = scoped_key if scoped_key is not None else self

        if self._lifetime != LifeTime.transient:
            self._lock = RLock()
        else:
            self._lock = _NULL_CONTEXT

    def __repr__(self) -> str:
        return f'<{self._lifetime} service from {self._service_info!r}>'

    @override
    def get_service(self, provider: IServiceProvider) -> T:
        if self._lifetime is LifeTime.transient:
            return self._create(provider)

        if self._lifetime is LifeTime.scoped:
            return self._from_scoped(provider)

        if self._lifetime is LifeTime.singleton:
            return self._from_singleton(provider)

        raise NotImplementedError(f'what is {self._lifetime}?')

    def _from_scoped(self, provider: IServiceProvider) -> T:
        scoped_key = self._scoped_key
        cache = provider[Symbols.cache]
        try:
            return cache[scoped_key]
        except KeyError:
            pass
        with self._lock:
            try:
                return cache[scoped_key]
            except KeyError:
                pass
            service = self._create(provider)
            cache[scoped_key] = service
            return service

    def _from_singleton(self, provider: IServiceProvider) -> T:
        if (cached_value := self._cached_value) is None:
            with self._lock:
                if (cached_value := self._cached_value) is None:
                    self._cached_value = cached_value = (self._create(provider),)
        return cached_value[0]

    def _create(self, provider: IServiceProvider) -> T:
        '''
        return the finally service instance.
        '''
        return self._service_info.get_service(provider)


class GetOrDefaultServiceInfo[TD](IServiceInfo[object | TD]):
    _UNSET = object()
    __slots__ = ('_key', '_default')

    def __init__(self, key: Hashable, default: TD=_UNSET) -> None:
        self._key = key
        self._default = default

    def __repr__(self) -> str:
        if self.has_default():
            return f'<(ioc) => ioc.get({self._key!r}, {self._default!r})>'
        else:
            return f'<(ioc) => ioc[{self._key!r}]>'

    @override
    def get_service(self, provider: IServiceProvider) -> object | TD:
        return self.get_service_by_key(provider, self._key)

    def get_service_by_key(self, provider: IServiceProvider, key: Hashable) -> object | TD:
        if self.has_default():
            return provider.get(key, self._default)
        else:
            return provider[key]

    def has_default(self) -> bool:
        return self._default is not self._UNSET


class GetManyServiceInfo[T](IServiceInfo[list[T]]):
    '''
    Get many services from single key.
    '''
    __slots__ = ('_key',)

    def __init__(self, key: Hashable) -> None:
        self._key = key

    def __repr__(self) -> str:
        return f'<(ioc) => ioc.get_many({self._key!r})>'

    @override
    def get_service(self, provider: IServiceProvider) -> list[T]:
        return provider.get_many(self._key)


class GetGroupServiceInfo(IServiceInfo[tuple[Any, ...]]):
    __slots__ = ('_keys',)

    def __init__(self, keys: Iterable[Hashable]) -> None:
        super().__init__()
        self._keys = tuple(keys)

    @override
    def get_service(self, provider: IServiceProvider) -> tuple[Any, ...]:
        return tuple(provider[k] for k in self._keys)

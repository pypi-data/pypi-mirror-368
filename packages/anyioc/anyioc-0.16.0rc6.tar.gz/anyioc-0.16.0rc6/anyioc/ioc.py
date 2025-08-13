# -*- coding: utf-8 -*-
#
# Copyright (c) 2018~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import inspect
import types
from collections.abc import Hashable, Mapping
from contextlib import ExitStack, nullcontext
from logging import getLogger
from threading import RLock
from types import MappingProxyType
from typing import Any, Callable, Iterable, Optional, Self, Type, overload, override

from ._bases import AllSupportsContext, IServiceProvider, LifeTime
from ._consts import SERVICEPROVIDER_NAMING_CONVENTION
from ._internal import Disposable, LockedMapping
from ._service_info import (
    BindedServiceInfo,
    GetAttrServiceInfo,
    GetGroupServiceInfo,
    IServiceInfo,
    ProviderServiceInfo,
    ValueServiceInfo,
)
from ._service_info.extra import CallerFrameServiceInfo, create_lifetime_service_info
from ._servicesmap import ServicesMap
from ._utils import wrap_signature as wrap_signature
from .err import ServiceNotFoundError
from .ioc_resolver import ServiceInfoChainResolver
from .keys import NamedType, _NamedTypeListKey
from .symbols import Symbols, TypedSymbol

_NULL_CONTEXT = nullcontext()

_logger = getLogger(__name__)


class ServiceProvider(IServiceProvider):
    def __init__(self,
            auto_enter: bool=False, *,
            # internal uses:
            _services: Optional[ServicesMap[Hashable, IServiceInfo]]=None,
            _parent: Optional['ServiceProvider']=None,
            _use_lock: bool=True,
        ) -> None:

        self._exit_stack = None
        self._scoped_cache = LockedMapping(use_lock=_use_lock)
        self._lock = RLock() if _use_lock else _NULL_CONTEXT
        self._parent = _parent

        assert (_parent is None) is (_services is None)

        if _parent is not None:
            assert _services is not None
            # scope provider
            assert auto_enter is False, 'must be default value'
            self._services = _services
            self._root: ServiceProvider = _parent._root

        else:
            assert _use_lock, 'root provider must use lock'
            # root provider
            self._services = ServicesMap(use_lock=True)
            self._root: ServiceProvider = self

            # serviceinfos
            get_current_provicer = ProviderServiceInfo.get_singleton_instance()
            get_frameinfo = CallerFrameServiceInfo()

            self._services[Symbols.provider] = get_current_provicer
            self._services[Symbols.provider_root] = ValueServiceInfo(self)
            self._services[Symbols.provider_parent] = GetAttrServiceInfo('_parent')
            self._services[Symbols.cache] = GetAttrServiceInfo('_scoped_cache')
            self._services[Symbols.missing_resolver] = ValueServiceInfo(ServiceInfoChainResolver())
            self._services[Symbols.caller_frame] = get_frameinfo

            self.__init_hooks = []
            self.__init_exc = None

            # service alias
            for name in SERVICEPROVIDER_NAMING_CONVENTION:
                self._services[name] = get_current_provicer
            self._services[ServiceProvider] = get_current_provicer
            self._services[IServiceProvider] = get_current_provicer
            self._services[inspect.FrameInfo] = get_frameinfo

            # options
            self._services[Symbols.provider_options] = ValueServiceInfo(MappingProxyType(
                dict(
                    auto_enter=auto_enter
                )
            ))

        assert self._root is not None

    def add_init_hook(self, func: Callable) -> None:
        func = wrap_signature(func)
        if self.__init_hooks is not None:
            with self._lock:
                if self.__init_hooks is not None:
                    self.__init_hooks.append(func)
                    return
        raise RuntimeError('Cannot add init hook after initialized.')

    def __ensure_init_hooks_called(self) -> None:
        if self.__init_hooks is not None or self.__init_exc is not None:
            with self._lock:
                if self.__init_exc is not None:
                    raise self.__init_exc
                if self.__init_hooks is not None:
                    _logger.debug('call init hooks')
                    hooks = self.__init_hooks
                    self.__init_hooks = None

                    disposable = self._services.add(Symbols.at_init, ValueServiceInfo(True))
                    try:
                        for func in hooks:
                            func(self)
                    except Exception as e:
                        self.__init_exc = e
                        raise
                    disposable()
                    self._services.add(Symbols.at_init, ValueServiceInfo(False))

    def _get_service_info(self, key: Hashable) -> IServiceInfo:
        try:
            return self._services[key]
        except KeyError:
            pass
        # load missing resolver and resolve service info.
        resolver = self._services[Symbols.missing_resolver].get_service(self)
        return resolver.get(self, key)

    @overload
    def __getitem__[T](self, key: NamedType[T]) -> T: ...
    @overload
    def __getitem__[T](self, key: TypedSymbol[T]) -> T: ...
    @overload
    def __getitem__(self, key: Hashable) -> object: ...
    @override
    def __getitem__(self, key: Hashable) -> object: # type: ignore
        _logger.debug('get service by key: %r', key)
        self._root.__ensure_init_hooks_called()
        service_info = self._get_service_info(key)
        try:
            return service_info.get_service(self)
        except ServiceNotFoundError as err:
            raise ServiceNotFoundError(key, *err.resolve_chain)

    @overload
    def get[T, TD](self, key: NamedType[T], d: TD=None) -> T | TD: ...
    @overload
    def get[T, TD](self, key: TypedSymbol[T], d: TD=None) -> T | TD: ...
    @overload
    def get(self, key: Hashable, d: object=None) -> object: ...
    @override
    def get(self, key: Hashable, d: object=None) -> object: # type: ignore
        '''
        Get a service by key with default value.
        '''
        try:
            return self[key]
        except ServiceNotFoundError as err:
            if len(err.resolve_chain) == 1:
                return d
            raise

    @overload
    def get_many[T](self, key: NamedType[T]) -> list[T]: ...
    @overload
    def get_many[T](self, key: TypedSymbol[T]) -> list[T]: ...
    @overload
    def get_many(self, key: Hashable) -> list[Any]: ...
    @override
    def get_many(self, key: Hashable) -> list[Any]: # type: ignore
        '''
        Get services by key.

        ### example

        when you registered multi services with the same key,
        you can get them all:

        ``` py
        provider.register_value('a', 1)
        provider.register_value('a', 2)
        assert provider.get_many('a') == [2, 1] # rev order
        ```
        '''
        _logger.debug('Get services by key: %r', key)
        self._root.__ensure_init_hooks_called()
        service_infos: Iterable[IServiceInfo] = self._services.get_many(key)
        try:
            return [si.get_service(self) for si in service_infos]
        except ServiceNotFoundError as err:
            raise ServiceNotFoundError(key, *err.resolve_chain)

    def resolve[R](self, factory: Callable[..., R], *,
            follow: bool = False,
            kwargs: Mapping[str, Any] | None = None
        ) -> R:
        '''
        Resolve the factory direct without register.
        '''
        return wrap_signature(factory, follow=follow, override_kwargs=kwargs)(self)

    @override
    def enter[T](self, context: AllSupportsContext[T]) -> T:
        with self._lock:
            if self._exit_stack is None:
                self._exit_stack = ExitStack()
            return self._exit_stack.enter_context(context)

    def __enter__(self) -> Self:
        return self

    def __exit__(self,
            exc_type: type | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None, /
        ) -> None:
        with self._lock:
            if self._exit_stack is not None:
                self._exit_stack.__exit__(exc_type, exc_val, exc_tb)
                self._exit_stack = None
        _logger.debug('%r is exited.', self)

    def freeze_key(self, key: Hashable) -> None:
        '''
        Freeze key to avoid registering it later.

        Only effective for the current ServiceProvider.
        '''
        self._services.freeze_key(key)

    def register_service_info(self, key: Hashable, service_info: IServiceInfo) -> Disposable:
        '''
        register a `IServiceInfo` by key.
        '''
        if not isinstance(service_info, IServiceInfo):
            raise TypeError('service_info must be instance of IServiceInfo.')
        _logger.debug('register %r with key %r', service_info, key)

        disposable = self._services.add(key, service_info)
        match key:
            case NamedType(type=k):
                disposable += self._services.add(_NamedTypeListKey(k), ValueServiceInfo(key))

        return disposable

    @overload
    def register[T](self, key: NamedType[T], factory: Type[T], lifetime: LifeTime) -> Disposable: ...
    @overload
    def register(self, key: Hashable, factory: Callable[..., Any], lifetime: LifeTime) -> Disposable: ...
    def register(self, key: Hashable, factory: Callable[..., Any], lifetime: LifeTime) -> Disposable:
        '''
        register a service factory by key.

        `factory` accept a function which require one or zero parameter.
        if the count of parameter is 1, pass a `IServiceProvider` as the argument.
        '''
        return self.register_service_info(key, create_lifetime_service_info(self, key, factory, lifetime))

    @overload
    def register_singleton[T](self, key: NamedType[T], factory: Type[T]) -> Disposable: ...
    @overload
    def register_singleton(self, key: Hashable, factory: Callable[..., Any]) -> Disposable: ...
    def register_singleton(self, key: Hashable, factory: Callable[..., Any]) -> Disposable:
        '''
        register a service factory by key.

        `factory` accept a function which require one or zero parameter.
        if the count of parameter is 1, pass a `IServiceProvider` as the argument.
        '''
        return self.register(key, factory, LifeTime.singleton)

    @overload
    def register_scoped[T](self, key: NamedType[T], factory: Type[T]) -> Disposable: ...
    @overload
    def register_scoped(self, key: Hashable, factory: Callable[..., Any]) -> Disposable: ...
    def register_scoped(self, key: Hashable, factory: Callable[..., Any]) -> Disposable:
        '''
        register a service factory by key.

        `factory` accept a function which require one or zero parameter.
        if the count of parameter is 1, pass a `IServiceProvider` as the argument.
        '''
        return self.register(key, factory, LifeTime.scoped)

    @overload
    def register_transient[T](self, key: NamedType[T], factory: Type[T]) -> Disposable: ...
    @overload
    def register_transient(self, key: Hashable, factory: Callable[..., Any]) -> Disposable: ...
    def register_transient(self, key: Hashable, factory: Callable[..., Any]) -> Disposable:
        '''
        register a service factory by key.

        `factory` accept a function which require one or zero parameter.
        if the count of parameter is 1, pass a `IServiceProvider` as the argument.
        '''
        return self.register(key, factory, LifeTime.transient)

    @overload
    def register_value[T](self, key: NamedType[T], value: T) -> Disposable: ...
    @overload
    def register_value(self, key: Hashable, value: object) -> Disposable: ...
    def register_value(self, key: Hashable, value: object) -> Disposable:
        '''
        register a value by key.

        equals `register_transient(key, lambda ioc: value)`
        '''
        return self.register_service_info(key, ValueServiceInfo(value))

    def register_group(self, key: Hashable, keys: Iterable[Hashable]) -> Disposable:
        '''
        Register a group `key` for get other `keys`.

        For example:

        ```
        provider.register_value('str', 'name')
        provider.register_value('int', 1)
        provider.register_group('any', ['str', 'int'])
        assert provider['any'] == ('name', 1)
        ```

        Is equals `register_transient(key, lambda ioc: tuple(ioc[k] for k in keys))`
        '''
        return self.register_service_info(key, GetGroupServiceInfo(keys))

    def register_bind(self, new_key: Hashable, target_key: Hashable) -> Disposable:
        '''
        bind `new_key` to `target_key` so
        you can use `new_key` as key to get value from service provider.

        equals `register_transient(new_key, lambda ioc: ioc[target_key])`
        '''
        return self.register_service_info(new_key, BindedServiceInfo(target_key))

    @override
    def scope(self, *, use_lock: bool=False) -> 'ServiceProvider':
        '''
        Create a scoped service provider for get scoped services.

        By default, scoped IServiceProvider is not thread safely,
        set `use_lock` to `True` can change this.
        '''
        ssp = ServiceProvider(
            _services=self._services.scope(use_lock=use_lock),
            _parent=self,
            _use_lock=use_lock,
        )
        return self.enter(ssp)


__all__ = ['ServiceProvider']

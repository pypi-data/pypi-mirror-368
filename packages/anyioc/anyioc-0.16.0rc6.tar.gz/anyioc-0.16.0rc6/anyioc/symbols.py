# -*- coding: utf-8 -*-
#
# Copyright (c) 2018~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------


import inspect
from typing import TYPE_CHECKING, Any

from ._bases import IServiceProvider
from ._internal import LockedMapping, ProviderOptions
from ._primitive_symbol import TypedSymbol

if TYPE_CHECKING:
    from . import ioc_resolver  # noqa: F401


class Symbols:
    '''
    The symbols for ServiceProvider internal uses.

    All keys are predefined in `ServiceProvider`.
    overwrite those keys will break the expected behavior.
    '''

    # current scoped `IServiceProvider`
    provider = TypedSymbol[IServiceProvider]('provider')

    # the root `IServiceProvider`
    provider_root = TypedSymbol[IServiceProvider]('provider_root')

    # the parent of current `IServiceProvider`, or `None` for the root `IServiceProvider`.
    provider_parent = TypedSymbol[IServiceProvider | None]('provider_parent')

    # the cache dict to store scoped instances
    cache = TypedSymbol[LockedMapping[Any, Any]]('cache')

    # the missing resolver from `IServiceProvider`
    missing_resolver = TypedSymbol['ioc_resolver.ServiceInfoChainResolver']('missing_resolver')

    # get frame info of caller
    caller_frame = TypedSymbol[inspect.FrameInfo]('caller_frame')

    # the options for the `ServiceProvider`, value is a dict like object.
    provider_options = TypedSymbol[ProviderOptions]('provider_options')

    # is current stage of the `IServiceProvider` is initializing
    at_init = TypedSymbol[bool]('at_init')

    dependent = TypedSymbol[object | None]('dependent')


__all__ = ['Symbols']

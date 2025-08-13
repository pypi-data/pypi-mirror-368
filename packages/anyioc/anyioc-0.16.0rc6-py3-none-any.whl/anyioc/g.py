# -*- coding: utf-8 -*-
#
# Copyright (c) 2018~2999 - Cologler <skyoflw@gmail.com>
# ----------
# a global ioc
# ----------

import importlib
import importlib.util
from logging import getLogger
from typing import Optional

from ._internal import Disposable, LockedMapping
from ._utils import dispose_at_exit, get_frameinfos, get_module_name
from .ioc import ServiceProvider

_logger = getLogger(__name__)


ioc = ServiceProvider()
dispose_at_exit(ioc)

# scoped global ioc

_module_providers = LockedMapping[str, tuple[ServiceProvider, Disposable]](use_lock=True)

def _is_module_exists(module_name: str) -> bool:
    try:
        return importlib.util.find_spec(module_name) is not None
    except ModuleNotFoundError:
        return False

def _get_module_provider(module_name: str) -> ServiceProvider:
    'Get or create module provider'

    def init_hook(provider: ServiceProvider) -> None:
        # auto init ioc
        initioc_module_name = module_name + '.init_ioc'
        _logger.debug('Looking for init_ioc module: %s', initioc_module_name)
        if _is_module_exists(initioc_module_name):
            _logger.debug('Found module %s', initioc_module_name)
            init_ioc = importlib.import_module(initioc_module_name)
            conf_ioc = getattr(init_ioc, 'conf_ioc', None)
            if conf_ioc is not None:
                _logger.debug('Found conf_ioc function, call it now...')
                conf_ioc(provider)
            else:
                _logger.debug('No such function named conf_ioc')
        else:
            _logger.debug('No module call %s', initioc_module_name)

    with _module_providers.lock:
        if (value := _module_providers.get(module_name)) is None:
            provider = ServiceProvider()
            disposable = dispose_at_exit(provider)
            value = (provider, disposable)
            _module_providers[module_name] = value
            provider.add_init_hook(init_hook)
        return value[0]

def get_module_provider(module_name: Optional[str]=None) -> ServiceProvider:
    '''
    get the module scoped singleton `ServiceProvider`.

    if `module_name` is `None`, use caller module name.

    if module `{module_name}.init_ioc` exists and it has a attr `conf_ioc`, will auto config like:

    ``` py
    (importlib.import_module(module_name + '.init_ioc')).conf_ioc(module_provider)
    ```
    '''
    if module_name is None:
        module_name = get_module_name(get_frameinfos(context=0, exclude_anyioc_frames=True)[0])

    if not isinstance(module_name, str):
        raise TypeError

    return _get_module_provider(module_name)

def get_pkgroot_provider(pkgroot: Optional[str]=None) -> ServiceProvider:
    '''
    get the package root scoped singleton `ServiceProvider`.

    if `pkgroot` is `None`, use caller package root.

    for example, `get_pkgroot_provider('A.B.C.D')` is equals `get_module_provider('A')`
    '''
    if pkgroot is None:
        pkgroot = get_module_name(get_frameinfos(context=0, exclude_anyioc_frames=True)[0])

    if not isinstance(pkgroot, str):
        raise TypeError

    pkgroot = pkgroot.partition('.')[0]
    return _get_module_provider(pkgroot)

def reset() -> None:
    '''
    Clear all module (or pkgroot) providers.
    '''
    with _module_providers.lock:
        cloned = list(_module_providers.values())
        _module_providers.clear()
    for item in cloned:
        item[1]() # dispose

# keep old func names:

get_namespace_provider = get_pkgroot_provider

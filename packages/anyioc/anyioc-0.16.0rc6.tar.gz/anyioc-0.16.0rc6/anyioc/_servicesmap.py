# -*- coding: utf-8 -*-
#
# Copyright (c) 2020~2999 - Cologler <skyoflw@gmail.com>
# ----------
#
# ----------

from collections.abc import Generator, Hashable
from contextlib import nullcontext
from logging import getLogger
from threading import Lock
from typing import Any

from ._internal import Disposable

_NULL_CONTEXT = nullcontext()
_logger = getLogger(__name__)

class ServicesMap[TK: Hashable, TV]:
    def __init__(self, *maps: dict[TK, list[tuple[TV]]], use_lock: bool=True) -> None:
        self._lock = Lock() if use_lock else _NULL_CONTEXT
        self._frozen_keys = set()
        self.maps: list[dict[TK, list[tuple[TV]]]] = list(maps) or [{}]

    def resolve(self, key: TK) -> Generator[TV, Any, None]:
        '''
        Resolve values with reversed order.
        '''
        with self._lock:
            for mapping in self.maps:
                yield from (t[0] for t in reversed(mapping.get(key, ())))

    def add(self, key: TK, value: TV) -> Disposable:

        with self._lock:
            if key in self._frozen_keys:
                raise RuntimeError(f'Key {key!r} is frozen.')

            record = (value,) # ensure dispose the right value
            vec = self.maps[0].setdefault(key, [])
            inserted_index = len(vec) # no insert func, so we can cache this index
            vec.append(record)

        def dispose() -> None:
            try:
                with self._lock:
                    # in most case, the del is del from end.
                    for i in range(min(inserted_index, len(vec) - 1), -1, -1):
                        if vec[i] is record:
                            del vec[i]
            except ValueError:
                _logger.warning('dispose() is called after the key be removed.')

        return Disposable(dispose)

    def freeze_key(self, key: TK) -> None:
        with self._lock:
            self._frozen_keys.add(key)

    def __setitem__(self, key: TK, value: TV) -> None:
        self.add(key, value)

    def __getitem__(self, key: TK) -> TV:
        'get item or raise `KeyError`` if not found'
        for value in self.resolve(key):
            return value
        raise KeyError(key)

    def get[TD](self, key: TK, default: TD=None) -> TV | TD:
        'get item or `default` if not found'
        for value in self.resolve(key):
            return value
        return default

    def get_many(self, key: TK) -> list[TV]:
        'get items as list'
        return list(self.resolve(key))

    def scope(self, use_lock: bool=False) -> 'ServicesMap':
        return self.__class__({}, *self.maps, use_lock=use_lock)

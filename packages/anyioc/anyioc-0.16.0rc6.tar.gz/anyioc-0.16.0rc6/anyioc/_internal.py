# -*- coding: utf-8 -*-
# 
# Copyright (c) 2025~2999 - Cologler <skyoflw@gmail.com>
# ----------
# 
# ----------

import types
from collections.abc import Hashable, Iterator, MutableMapping
from contextlib import AbstractContextManager, nullcontext
from threading import RLock
from typing import Callable, TypedDict

from typing_extensions import ReadOnly

_NULL_CONTEXT = nullcontext()

class ProviderOptions(TypedDict):
    auto_enter: ReadOnly[bool]


class LockedMapping[TK: Hashable, TV](MutableMapping[TK, TV]):
    def __init__(self, use_lock: bool) -> None:
        super().__init__()
        self._dict: dict[TK, TV] = dict()
        # The lock may be acquired multiple times,
        # as it is used to prevent repeated calls.
        self._lock = RLock() if use_lock else _NULL_CONTEXT

    @property
    def lock(self) -> AbstractContextManager:
        return self._lock

    def __iter__(self) -> Iterator[TK]:
        with self._lock:
            return iter(self._dict)

    def __len__(self) -> int:
        with self._lock:
            return len(self._dict)

    def __getitem__(self, key: TK) -> TV:
        with self._lock:
            return self._dict[key]

    def __setitem__(self, key: TK, value: TV) -> None:
        with self._lock:
            self._dict[key] = value

    def __delitem__(self, key: TK) -> None:
        with self._lock:
            del self._dict[key]


class Disposable:
    __slots__ = ('dispose',)

    def __init__(self, dispose: Callable[[], None]) -> None:
        self.dispose = dispose

    def __call__(self) -> None:
        if dispose := self.dispose:
            self.dispose = None
            dispose()

    def __enter__(self) -> 'Disposable':
        return self

    def __exit__(self,
            exc_type: type | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None, /
        ) -> None:
        if dispose := self.dispose:
            self.dispose = None
            dispose()

    def __add__(self, other: 'Disposable') -> 'Disposable':
        if isinstance(other, Disposable):
            def dispose() -> None:
                self()
                other()
            return Disposable(dispose)
        return NotImplemented

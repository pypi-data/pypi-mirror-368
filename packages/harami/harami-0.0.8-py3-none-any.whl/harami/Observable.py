# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
from types import MethodType
from typing import Generic, Optional, TypeVar

from .EventArgs import EventArgs
from .Observer import Observer


T = TypeVar('T')

class Observable(Generic[T]):

    __observers:set[Observer]
    __state:T|None

    def __init__(self):
        """
        Create an Observable[T].
        """
        self.__observers = set()
        self.__state = None

    def __call__(self, *state:Optional[T]) -> T|None:
        if len(state) > 1 and isinstance(state[1], EventArgs):
            self.state = state[1]            
        elif len(state) > 0:
            self.state = state[0]
        else:
            return self.state

    def __iadd__(self, observer:Observer) -> 'Observable':
        return self.attach(observer)

    def __isub__(self, observer:Observer) -> 'Observable':
        return self.detach(observer)

    @property
    def state(self) -> T|None:
        """
        The most-recent state of the Observable.
        """
        return self.__state
    @state.setter
    def state(self, state:T|None) -> None:
        self.notify(state)

    def attach(self, observer:Observer) -> 'Observable':
        """
        Attach an Observer.

        :param Observer observer: A callable that accepts two parameters, the first parameter is the value being observed and the second parameter is the prior value.
        ---
        If the same Observer is attached multiple times only one subscription is created, and the Observer is only activated once per value change.
        """
        self.__observers.add(observer)
        return self

    def detach(self, observer:Observer) -> 'Observable':
        """
        Detach an Observer.

        :param Observer observer: An Observer that was previously attached to this Observable.
        """
        try:
            self.__observers.remove(observer)
        except KeyError:
            pass
        return self

    def notify(self, state:T|None) -> None:
        """
        Notifies attached Observers of a state change.
        """
        self.__state = state
        for observer in self.__observers:
            x = None
            if hasattr(observer, '__code__'):
                # best attempt to support non-standard observers:
                #
                # 1) observers which accept no args
                # 2) observers which have more than one arg
                #
                # "officially" harami only "supports" single-arg observers.
                argCount = observer.__code__.co_argcount
                if type(observer) is MethodType:
                    argCount -= 1
                args = []
                if argCount > 0:
                    args.append(state)
                    argCount -= 1
                while argCount > 0:
                    args.append(None)
                x = observer(*args)
            else:
                # brute attempt to dispatch
                x = observer(state)
            if x is not None and asyncio.coroutines.iscoroutine(x):
                asyncio.create_task(x)

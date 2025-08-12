# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

import asyncio
from types import FunctionType, MethodType
from typing import Any, Callable, ForwardRef, cast

from .EventArgs import EventArgs
from .EventHandler import EventHandler

Observable = ForwardRef('Observable')

class EventSource:

    __eventargs:type
    __func:MethodType|FunctionType|None
    __handlers:set[EventHandler]

    def __init__(self, func:MethodType|FunctionType|None, eventargs:type = EventArgs):
        self.__eventargs = eventargs
        self.__func = func
        self.__handlers = set()

    def __call__(self, *args, **kwargs) -> Any:
        result = None if self.__func is None else self.__func(*args, **kwargs)
        for handler in self.__handlers:
            eventargs = self.__eventargs
            sender = args[0] if len(args) > 0 else None
            # event args passing allows for some flexibility to developers:
            # if no args provided to Event Source, send `EventArgs.empty` (useful for generic state change events)
            # otherwise..
            # if the first arg provided is an `EventArgs` subclass, passthrough as-is (and ignore all other args)
            # otherwise..
            # if non-EventArgs args are provided pass them to constructor for the `@event(x)` specified `EventArgs` type `x`
            # except when..
            # no EventArgs type was defined via @event(), pass `EventArgs.empty`
            e:EventArgs = EventArgs.empty if len(args) <= 1 else cast(EventArgs, args[1]) if len(args) > 1 and args[1] is object and issubclass(args[1], EventArgs) else eventargs(*args[1:], **kwargs) if eventargs is not None else EventArgs.empty
            x = handler(sender, e)
            if x is not None and asyncio.coroutines.iscoroutine(x):
                asyncio.create_task(x)
        return result
    
    def __get__(self, instance:Any, owner:Any = None):
        if instance is None:
            return owner
        else:
            return MethodType(self, instance)
    
    def __iadd__(self, handler:EventHandler|Observable) -> 'EventSource':
        return self.addHandler(handler)

    def __isub__(self, handler:EventHandler|Observable) -> 'EventSource':
        return self.removeHandler(handler)

    @property
    def hasHandlers(self) -> bool:
        return len(self.__handlers) > 0

    def addHandler(self, handler:EventHandler|Observable) -> 'EventSource':
        self.__handlers.add(handler)
        return self

    def removeHandler(self, handler:EventHandler|Observable) -> 'EventSource':
        self.__handlers.remove(handler)
        return self

    def wrap(self, func:MethodType|FunctionType) -> Callable[[Any], Any]:
        self.__func = func
        return self


def event(eventargs = None) -> Callable:
    global EventSource
    if eventargs is None:
        return EventSource
    elif isinstance(eventargs, MethodType) or isinstance(eventargs, FunctionType):
        return EventSource(eventargs, EventArgs)
    else:
        return (EventSource(None, eventargs)).wrap

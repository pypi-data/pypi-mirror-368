# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Any


class EventArgs:
    empty:'EventArgs'
    args:tuple[Any, ...]
    kwargs:dict[str, Any]
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
    def getByNameOrIndex(self, name:str, index:int) -> Any:
        d = self.kwargs.get(name, None)
        return d if d is not None else self.args[index]
EventArgs.empty = EventArgs()

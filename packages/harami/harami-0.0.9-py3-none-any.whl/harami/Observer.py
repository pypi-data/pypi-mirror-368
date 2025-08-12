# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from types import CoroutineType
from typing import Any, Callable


type Observer = Callable[[Any], None|CoroutineType[Any,Any,None]]

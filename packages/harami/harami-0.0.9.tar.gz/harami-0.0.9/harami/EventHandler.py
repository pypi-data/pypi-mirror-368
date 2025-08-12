# SPDX-FileCopyrightText: Copyright (C) Shaun Wilson
# SPDX-License-Identifier: MIT

from typing import Callable

from .EventArgs import EventArgs


type EventHandler = Callable[[object, EventArgs], None]

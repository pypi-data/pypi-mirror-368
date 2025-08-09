# `encrustable` - basic components of Rust's type system magic
# Copyright (C) 2025 Artur Ciesielski <artur.ciesielski@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, eq=True)
class Panic(Exception):
    """
    A `Panic` is an error raised when the type system assumptions are
    somehow violated. It's a standard Python `Exception` and can be caught
    at the boundary. The error message (custom if provided, or default)
    can be extracted by casting the error to `str`.
    """

    message: str | None = None
    """A custom panic message, if provided."""

    def __str__(self) -> str:
        return self.message or "panic!"

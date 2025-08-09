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

from encrustable import Err, Nothing, Ok, Option, Panic, Result, Some


def get_some(v: int) -> Option[int]:
    return Some(v)


def get_nothing() -> Option[int]:
    return Nothing()


def get_ok(v: int) -> Result[int, Exception]:
    return Ok(v)


def get_err(e: Exception) -> Result[int, Exception]:
    return Err(e)


def try_unwrap[T, E: Exception](v: Option[T] | Result[T, E]) -> None:
    try:
        unwrapped = v.unwrap()
        print(f"- {repr(v)} unwrap: {repr(unwrapped)}")
    except Panic as p:
        print(f"- {repr(v)} unwrap: {str(p)}\n  cause: {repr(p.__cause__)}")


def try_expect[T, E: Exception](v: Option[T] | Result[T, E]) -> None:
    try:
        unwrapped = v.expect("no valid value")
        print(f"- {repr(v)} expect: {repr(unwrapped)}")
    except Panic as p:
        print(f"- {repr(v)} expect: {str(p)}\n  cause: {repr(p.__cause__)}")


if __name__ == "__main__":
    try_unwrap(get_some(1))
    try_expect(get_some(1))

    try_unwrap(get_nothing())
    try_expect(get_nothing())

    try_unwrap(get_ok(1))
    try_expect(get_ok(1))

    try_unwrap(get_err(Exception()))
    try_expect(get_err(Exception()))

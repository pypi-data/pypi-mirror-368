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

from __future__ import annotations

from collections.abc import Callable, Generator
from dataclasses import dataclass
from typing import TYPE_CHECKING, Never, Protocol, final

from encrustable.panic import Panic

if TYPE_CHECKING:  # pragma: nocover
    from encrustable.option import Option


class ResultProto[T, E: Exception](Protocol):
    """
    This is a common protocol for the `Ok` and `Err` variants that defines
    all available operations for `Result`s.
    """

    def __iter__(self) -> Generator[T]:  # pragma: nocover
        """
        Returns a one-time-use iterator object that will yield
        a single value if `Ok`, otherwise no values.
        """
        ...

    def __or__[V](self, fn: Callable[[T], V]) -> Result[V, E]:
        """
        This implements pipe operator `|` as a convenient alias to the `.map` method.
        """
        return self.map(fn)

    def is_ok(self) -> bool:  # pragma: nocover
        """
        Returns `True` if `Ok`, otherwise `False`.
        """
        ...

    def is_ok_and(self, p: Callable[[T], bool]) -> bool:  # pragma: nocover
        """
        Returns `True` if `Ok` and the predicate `p` returns `True` when applied to
        the contained value, otherwise `False`.
        """
        ...

    def is_err(self) -> bool:  # pragma: nocover
        """
        Returns `True` if `Err`, otherwise `False`.
        """
        ...

    def is_err_and(self, p: Callable[[E], bool]) -> bool:  # pragma: nocover
        """
        Returns `True` if `Err` and the predicate `p` returns `True` when applied to
        the contained error, otherwise `False`.
        """
        ...

    def and_[V](self, r: Result[V, E]) -> Result[V, E]:  # pragma: nocover
        """
        Returns the `Result` in `r` if `Ok`, otherwise the `Err` variant with the
        contained error.

        Note: `and` is a reserved Python keyword, so the method is called `and_`.
        """
        ...

    def and_then[V](
        self, f: Callable[[], Result[V, E]]
    ) -> Result[V, E]:  # pragma: nocover
        """
        Returns the result of calling the factory in `f` if `Ok`, otherwise the
        `Err` variant with the contained error.
        """
        ...

    def or_[F: Exception](self, r: Result[T, F]) -> Result[T, F]:  # pragma: nocover
        """
        Returns `self` if `Some`, otherwise the `Option` in `o`.

        Note: `or` is a reserved Python keyword, so the method is called `or_`.
        """
        ...

    def or_else[F: Exception](
        self, f: Callable[[], Result[T, F]]
    ) -> Result[T, F]:  # pragma: nocover
        """
        Returns `self` if `Some`, otherwise the result of calling the factory in `f`.
        """
        ...

    def inspect(self, fn: Callable[[T], None]) -> Result[T, E]:  # pragma: nocover
        """
        Returns `self` after applying the function `fn` to the contained value if `Ok`.
        """
        ...

    def inspect_err(self, fn: Callable[[E], None]) -> Result[T, E]:  # pragma: nocover
        """
        Returns `self` after applying the function `fn` to the contained error if `Err`.
        """
        ...

    def unwrap(self) -> T:  # pragma: nocover
        """
        Returns the contained value if `Ok`, otherwise raises a `Panic`.
        """
        ...

    def unwrap_err(self) -> E:  # pragma: nocover
        """
        Returns the contained error if `Err`, otherwise raises a `Panic`.
        """
        ...

    def unwrap_or(self, t: T) -> T:  # pragma: nocover
        """
        Returns the contained value if `Ok`, otherwise the value `t`.
        """
        ...

    def unwrap_or_else(self, f: Callable[[], T]) -> T:  # pragma: nocover
        """
        Returns the contained value if `Ok`, otherwise the result of
        calling the factory in `f`.
        """
        ...

    def expect(self, m: str) -> T:  # pragma: nocover
        """
        Returns the contained value if `Ok`, otherwise raises a `Panic`
        with a custom message.
        """
        ...

    def expect_err(self, m: str) -> E:  # pragma: nocover
        """
        Returns the contained error if `Err`, otherwise raises a `Panic`
        with a custom message.
        """
        ...

    def map[V](self, fn: Callable[[T], V]) -> Result[V, E]:  # pragma: nocover
        """
        Returns a new `Result` containing the result of application of the function in
        `fn` to the contained value if `Ok`, otherwise the `Result` untouched.
        """
        ...

    def map_err[F: Exception](
        self, fn: Callable[[E], F]
    ) -> Result[T, F]:  # pragma: nocover
        """
        Returns a new `Result` containing the result of application of the function in
        `fn` to the contained error if `Err`, otherwise the `Result` untouched.
        """
        ...

    def map_or[V](self, v: V, fn: Callable[[T], V]) -> V:  # pragma: nocover
        """
        Returns the result of application of the function in `fn` to the contained
        value if `Ok`, otherwise the value in `v`.
        """
        ...

    def map_or_else[V](
        self, v: Callable[[], V], fn: Callable[[T], V]
    ) -> V:  # pragma: nocover
        """
        Returns the result of application of the function in `fn` to the contained
        value if `Ok`, otherwise the result of calling the factory in `v`.
        """
        ...

    def ok(self) -> Option[T]:  # pragma: nocover
        """
        Converts this `Result` to an `Option[T]` - returns `Some` with the contained
        value if `Ok`, otherwise `Nothing` (contained error is discarded).
        """
        ...

    def err(self) -> Option[E]:  # pragma: nocover
        """
        Converts this `Result` to an `Option[E]` - returns `Some` with the contained
        error if `Err`, otherwise `Nothing`.
        """
        ...

    def flatten[V, F: Exception](self: Result[Result[V, F], F]) -> Result[V, F]:
        """
        Converts a `Result[Result[T, E], E]` to a flat `Result[T, E]`.
        """
        match self:
            case Ok(r):
                match r:
                    case Ok(v):
                        return Ok(v)
                    case Err(e):  # pragma: nobranch
                        return Err(e)
            case Err(e):  # pragma: nobranch
                return Err(e)

    def transpose[V, F: Exception](self: Result[Option[V], F]) -> Option[Result[V, F]]:
        """
        Converts a `Result[Option[T], E]` to an `Option[Result[T, E]]`.
        """
        from encrustable.option import Nothing, Some

        match self:
            case Ok(o):
                match o:
                    case Some(v):
                        return Some(Ok(v))
                    case Nothing():  # pragma: nobranch
                        return Nothing()
            case Err(e):  # pragma: nobranch
                return Some(Err(e))


@final
@dataclass(frozen=True, eq=True)
class Ok[T, E: Exception](ResultProto[T, E]):
    """
    This represents the variant that holds a result of a successful computation.
    """

    v: T

    def __iter__(self) -> Generator[T]:
        yield self.v

    def is_ok(self) -> bool:
        return True

    def is_ok_and(self, p: Callable[[T], bool]) -> bool:
        return p(self.v)

    def is_err(self) -> bool:
        return False

    def is_err_and(self, p: Callable[[E], bool]) -> bool:
        return False

    def and_[V](self, r: Result[V, E]) -> Result[V, E]:
        return r

    def and_then[V](self, f: Callable[[], Result[V, E]]) -> Result[V, E]:
        return f()

    def or_[F: Exception](self, r: Result[T, F]) -> Result[T, F]:
        return Ok(self.v)

    def or_else[F: Exception](self, f: Callable[[], Result[T, F]]) -> Result[T, F]:
        return Ok(self.v)

    def inspect(self, fn: Callable[[T], None]) -> Result[T, E]:
        fn(self.v)
        return self

    def inspect_err(self, fn: Callable[[E], None]) -> Result[T, E]:
        return self

    def unwrap(self) -> T:
        return self.v

    def unwrap_err(self) -> Never:
        raise Panic(str(self))

    def unwrap_or(self, t: T) -> T:
        return self.v

    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        return self.v

    def expect(self, m: str) -> T:
        return self.v

    def expect_err(self, m: str) -> Never:
        raise Panic(m)

    def map[V](self, fn: Callable[[T], V]) -> Result[V, E]:
        return Ok(fn(self.v))

    def map_err[F: Exception](self, fn: Callable[[E], F]) -> Result[T, F]:
        return Ok(self.v)

    def map_or[V](self, v: V, fn: Callable[[T], V]) -> V:
        return fn(self.v)

    def map_or_else[V](self, v: Callable[[], V], fn: Callable[[T], V]) -> V:
        return fn(self.v)

    def ok(self) -> Option[T]:
        from encrustable.option import Some

        return Some(self.v)

    def err(self) -> Option[E]:
        from encrustable.option import Nothing

        return Nothing()


@final
@dataclass(frozen=True, eq=True)
class Err[T, E: Exception](ResultProto[T, E]):
    """
    This represents the variant that holds an error that occured during a computation.
    """

    e: E

    def __iter__(self) -> Generator[T]:
        return
        yield

    def __or__[V](self, fn: Callable[[T], V]) -> Result[V, E]:
        return Err(self.e)

    def is_ok(self) -> bool:
        return False

    def is_ok_and(self, p: Callable[[T], bool]) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def is_err_and(self, p: Callable[[E], bool]) -> bool:
        return p(self.e)

    def and_[V](self, r: Result[V, E]) -> Result[V, E]:
        return Err(self.e)

    def and_then[V](self, f: Callable[[], Result[V, E]]) -> Result[V, E]:
        return Err(self.e)

    def or_[F: Exception](self, r: Result[T, F]) -> Result[T, F]:
        return r

    def or_else[F: Exception](self, f: Callable[[], Result[T, F]]) -> Result[T, F]:
        return f()

    def inspect(self, fn: Callable[[T], None]) -> Result[T, E]:
        return self

    def inspect_err(self, fn: Callable[[E], None]) -> Result[T, E]:
        fn(self.e)
        return self

    def unwrap(self) -> Never:
        raise Panic() from self.e

    def unwrap_err(self) -> E:
        return self.e

    def unwrap_or(self, t: T) -> T:
        return t

    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        return f()

    def expect(self, m: str) -> Never:
        raise Panic(m) from self.e

    def expect_err(self, m: str) -> E:
        return self.e

    def map[V](self, fn: Callable[[T], V]) -> Result[V, E]:
        return Err(self.e)

    def map_err[F: Exception](self, fn: Callable[[E], F]) -> Result[T, F]:
        return Err(fn(self.e))

    def map_or[V](self, v: V, fn: Callable[[T], V]) -> V:
        return v

    def map_or_else[V](self, v: Callable[[], V], fn: Callable[[T], V]) -> V:
        return v()

    def ok(self) -> Option[T]:
        from encrustable.option import Nothing

        return Nothing()

    def err(self) -> Option[E]:
        from encrustable.option import Some

        return Some(self.e)


type Result[T, E: Exception] = Ok[T, E] | Err[T, E]

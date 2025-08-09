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
    from encrustable.result import Result


class OptionProto[T](Protocol):
    """
    This is a protocol base for the `Some` and `Nothing` variants that defines
    all available operations for `Option`s.
    """

    def __iter__(self) -> Generator[T]:  # pragma: nocover
        """
        Returns a one-time-use iterator object that will yield
        a single value if `Some`, otherwise no values.
        """
        ...

    def __or__[V](self, fn: Callable[[T], V]) -> Option[V]:
        """
        This implements pipe operator `|` as a convenient alias to the `.map` method.
        """
        return self.map(fn)

    def is_some(self) -> bool:  # pragma: nocover
        """
        Returns `True` if `Some`, otherwise `False`.
        """
        ...

    def is_some_and(self, p: Callable[[T], bool]) -> bool:  # pragma: nocover
        """
        Returns `True` if `Some` and the predicate `p` returns `True` when applied to
        the contained value, otherwise `False`.
        """
        ...

    def is_nothing(self) -> bool:  # pragma: nocover
        """
        Returns `True` if `Nothing`, otherwise `False`.
        """
        ...

    def is_nothing_or(self, p: Callable[[T], bool]) -> bool:  # pragma: nocover
        """
        Returns `True` if `Nothing` or the predicate `p` returns `True` when applied to
        the contained value, otherwise `False`.
        """
        ...

    def and_[V](self, o: Option[V]) -> Option[V]:  # pragma: nocover
        """
        Returns the `Option` in `o` if `Some`, otherwise `Nothing`.

        Note: `and` is a reserved Python keyword, so the method is called `and_`.
        """
        ...

    def and_then[V](self, f: Callable[[], Option[V]]) -> Option[V]:  # pragma: nocover
        """
        Returns the result of calling the factory in `f` if `Some`, otherwise `Nothing`.
        """
        ...

    def or_(self, o: Option[T]) -> Option[T]:  # pragma: nocover
        """
        Returns `self` if `Some`, otherwise the `Option` in `o`.

        Note: `or` is a reserved Python keyword, so the method is called `or_`.
        """
        ...

    def or_else(self, f: Callable[[], Option[T]]) -> Option[T]:  # pragma: nocover
        """
        Returns `self` if `Some`, otherwise the result of calling the factory in `f`.
        """
        ...

    def or_none(self) -> T | None:  # pragma: nocover
        """
        Returns the contained value if `Some`, otherwise `None`.
        """
        ...

    def xor(self, o: Option[T]) -> Option[T]:  # pragma: nocover
        """
        Returns the `Some` variant with the contained value if exactly one of `self`
        and `o` is `Some`, otherwise `Nothing`.
        """
        ...

    def filter(self, p: Callable[[T], bool]) -> Option[T]:  # pragma: nocover
        """
        Returns `self` if `Some` and the predicate `p` returns `True` when applied to
        the contained value, otherwise `Nothing`.
        """
        ...

    def inspect(self, fn: Callable[[T], None]) -> Option[T]:  # pragma: nocover
        """
        Returns `self` after applying the function `fn` to the contained value
        if `Some`.
        """
        ...

    def unwrap(self) -> T:  # pragma: nocover
        """
        Returns the contained value if `Some`, otherwise raises a `Panic`.
        """
        ...

    def unwrap_or(self, t: T) -> T:  # pragma: nocover
        """
        Returns the contained value if `Some`, otherwise the value `t`.
        """
        ...

    def unwrap_or_else(self, f: Callable[[], T]) -> T:  # pragma: nocover
        """
        Returns the contained value if `Some`, otherwise the result of
        calling the factory in `f`.
        """
        ...

    def expect(self, m: str) -> T:  # pragma: nocover
        """
        Returns the contained value if `Some`, otherwise raises a `Panic`
        with a custom message.
        """
        ...

    def map[V](self, fn: Callable[[T], V]) -> Option[V]:  # pragma: nocover
        """
        Returns a new `Result` containing the result of application of the function in
        `fn` to the contained value if `Some`, otherwise `Nothing`.
        """
        ...

    def map_or[V](self, v: V, fn: Callable[[T], V]) -> V:  # pragma: nocover
        """
        Returns the result of application of the function in `fn` to the contained
        value if `Some`, otherwise the value in `v`.
        """
        ...

    def map_or_else[V](
        self, v: Callable[[], V], fn: Callable[[T], V]
    ) -> V:  # pragma: nocover
        """
        Returns the result of application of the function in `fn` to the contained
        value if `Some`, otherwise the result of calling the factory in `v`.
        """
        ...

    def ok_or[E: Exception](self, e: E) -> Result[T, E]:  # pragma: nocover
        """
        Converts this `Option` to a `Result[T, E]` - returns an `Ok` with the contained
        value if `Some`, otherwise an `Err` with the error `e`.
        """
        ...

    def ok_or_else[E: Exception](
        self, f: Callable[[], E]
    ) -> Result[T, E]:  # pragma: nocover
        """
        Converts this `Option` to a `Result[T, E]` - returns an `Ok` with the contained
        value if `Some`, otherwise an `Err` containing the result of calling the
        factory in `f`.
        """
        ...

    def zip[V](self, o: Option[V]) -> Option[tuple[T, V]]:  # pragma: nocover
        """
        Returns an `Option[(T, V)]` resulting from zipping contained values in this
        `Option` together with another `Option[V]` into a pair (2-tuple) of values.

        Returns `Nothing` if either `self` or `o` is `Nothing`.
        """
        ...

    def zip_with[V, R](self, o: Option[V], f: Callable[[T, V], R]) -> Option[R]:
        """
        Returns an `Option` of a value of type `R` resulting from zipping this option
        together with another `Option[V]` and applying a two-argument function `f`
        on the resulting pair of values.

        Returns `Nothing` if either `self` or `o` is `Nothing`.
        """
        return self.zip(o).map(lambda pair: f(pair[0], pair[1]))

    def flatten[O](self: Option[Option[O]]) -> Option[O]:
        """
        Converts an `Option[Option[T]]` to a flat `Option[T]`.
        """
        match self:
            case Some(o):
                match o:
                    case Some(v):
                        return Some(v)
                    case Nothing():  # pragma: nobranch
                        return Nothing()
            case Nothing():  # pragma: nobranch
                return Nothing()

    def transpose[V, F: Exception](self: Option[Result[V, F]]) -> Result[Option[V], F]:
        """
        Converts an `Option[Result[T, E]]` to a `Result[Option[T], E]`.
        """
        from encrustable.result import Err, Ok

        match self:
            case Some(r):
                match r:
                    case Ok(v):
                        return Ok(Some(v))
                    case Err(e):  # pragma: nobranch
                        return Err(e)
            case Nothing():  # pragma: nobranch
                return Ok(Nothing())


@final
@dataclass(frozen=True, eq=True)
class Some[T](OptionProto[T]):
    """
    This represents the variant that holds a value.
    """

    v: T

    def __iter__(self) -> Generator[T]:
        yield self.v

    def is_some(self) -> bool:
        return True

    def is_some_and(self, p: Callable[[T], bool]) -> bool:
        return p(self.v)

    def is_nothing(self) -> bool:
        return False

    def is_nothing_or(self, p: Callable[[T], bool]) -> bool:
        return p(self.v)

    def and_[V](self, o: Option[V]) -> Option[V]:
        return o

    def and_then[V](self, f: Callable[[], Option[V]]) -> Option[V]:
        return f()

    def or_(self, o: Option[T]) -> Option[T]:
        return self

    def or_else(self, f: Callable[[], Option[T]]) -> Option[T]:
        return self

    def or_none(self) -> T | None:
        return self.v

    def xor(self, o: Option[T]) -> Option[T]:
        return self if o.is_nothing() else Nothing()

    def filter(self, p: Callable[[T], bool]) -> Option[T]:
        return self if p(self.v) else Nothing()

    def inspect(self, fn: Callable[[T], None]) -> Option[T]:
        fn(self.v)
        return self

    def unwrap(self) -> T:
        return self.v

    def unwrap_or(self, t: T) -> T:
        return self.v

    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        return self.v

    def expect(self, m: str) -> T:
        return self.v

    def map[V](self, fn: Callable[[T], V]) -> Option[V]:
        return Some(fn(self.v))

    def map_or[V](self, v: V, fn: Callable[[T], V]) -> V:
        return fn(self.v)

    def map_or_else[V](self, v: Callable[[], V], fn: Callable[[T], V]) -> V:
        return fn(self.v)

    def ok_or[E: Exception](self, e: E) -> Result[T, E]:
        from encrustable.result import Ok

        return Ok(self.v)

    def ok_or_else[E: Exception](self, f: Callable[[], E]) -> Result[T, E]:
        from encrustable.result import Ok

        return Ok(self.v)

    def zip[V](self, o: Option[V]) -> Option[tuple[T, V]]:
        return Some((self.v, o.unwrap())) if o.is_some() else Nothing()


@final
@dataclass(frozen=True, eq=True)
class Nothing[T](OptionProto[T]):
    """
    This represents the empty variant.
    """

    def __iter__(self) -> Generator[T]:
        return
        yield

    def __or__[V](self, fn: Callable[[T], V]) -> Option[V]:
        return Nothing()

    def is_some(self) -> bool:
        return False

    def is_some_and(self, p: Callable[[T], bool]) -> bool:
        return False

    def is_nothing(self) -> bool:
        return True

    def is_nothing_or(self, p: Callable[[T], bool]) -> bool:
        return True

    def and_[V](self, o: Option[V]) -> Option[V]:
        return Nothing()

    def and_then[V](self, f: Callable[[], Option[V]]) -> Option[V]:
        return Nothing()

    def or_(self, o: Option[T]) -> Option[T]:
        return o

    def or_else(self, f: Callable[[], Option[T]]) -> Option[T]:
        return f()

    def or_none(self) -> T | None:
        return None

    def xor(self, o: Option[T]) -> Option[T]:
        return o

    def filter(self, p: Callable[[T], bool]) -> Option[T]:
        return Nothing()

    def inspect(self, fn: Callable[[T], None]) -> Option[T]:
        return self

    def unwrap(self) -> Never:
        raise Panic()

    def unwrap_or(self, t: T) -> T:
        return t

    def unwrap_or_else(self, f: Callable[[], T]) -> T:
        return f()

    def expect(self, m: str) -> Never:
        raise Panic(m)

    def map[V](self, fn: Callable[[T], V]) -> Option[V]:
        return Nothing()

    def map_or[V](self, v: V, fn: Callable[[T], V]) -> V:
        return v

    def map_or_else[V](self, v: Callable[[], V], fn: Callable[[T], V]) -> V:
        return v()

    def ok_or[E: Exception](self, e: E) -> Result[T, E]:
        from encrustable.result import Err

        return Err(e)

    def ok_or_else[E: Exception](self, f: Callable[[], E]) -> Result[T, E]:
        from encrustable.result import Err

        return Err(f())

    def zip[V](self, o: Option[V]) -> Option[tuple[T, V]]:
        return Nothing()


type Option[T] = Some[T] | Nothing[T]

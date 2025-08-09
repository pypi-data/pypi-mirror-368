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

import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from encrustable import Err, Ok, Result


@dataclass(frozen=True, eq=True)
class FileReadError(Exception):
    file_name: Path
    original_error: Exception | None = field(default=None, kw_only=True, repr=False)


class FileNotFound(FileReadError):
    pass


class FileNotReadable(FileReadError):
    pass


class FileEmpty(FileReadError):
    pass


# this function can fail in many different ways:
#   - file does not exist
#   - file is not readable (because of permissions)
#   - file is empty (so no first line)
#   - we can even have a catch-all generic exception handler if we want to
# we encode this scenario as a Result
def read_first_line_from_file(file_name: Path) -> Result[str, FileReadError]:
    try:
        with file_name.open("r") as file:
            if (line := file.readline().strip()) == "":
                return Err(FileEmpty(file_name))
            return Ok(line)
    except FileNotFoundError as e:
        return Err(FileNotFound(file_name, original_error=e))
    except PermissionError as e:
        return Err(FileNotReadable(file_name, original_error=e))
    except Exception as e:
        return Err(FileReadError(file_name, original_error=e))


# we have a regular function that cannot fail
# given a valid string it will give us up to 20 characters from the beginning
def trim_str_above_20_len(line: str) -> str:
    return line.strip()[:20]


# now we can combine them and we can skip any error checking midway
# we will only check the result at the end using pattern matching
def print_first_line_from_file(file_name: Path) -> None:
    match read_first_line_from_file(file_name) | trim_str_above_20_len:
        case Ok(line):
            print(f"- First line (up to 20 chars) from '{file_name}': {line}")
        case Err(err):
            print(
                f"- Could not read first line from '{str(file_name)[:20]}'\n"
                f"  error: {repr(err)}\n"
                f"  original error: {repr(err.original_error)}"
            )


# execute the example for a couple of filenames
if __name__ == "__main__":
    print_first_line_from_file(Path("/etc/passwd"))
    print_first_line_from_file(Path("/does-not-exist.yaml"))
    print_first_line_from_file(Path("/root/file.yaml"))
    with tempfile.NamedTemporaryFile("w") as f:
        print_first_line_from_file(Path(f.name))

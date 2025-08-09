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

from typing import NewType

from encrustable import Nothing, Option, Some

# we use the newtype pattern to squeeze the most ouf of our type checker
Username = NewType("Username", str)
PasswdFileLine = NewType("PasswdFileLine", str)
ParsedPasswdEntry = NewType("ParsedPasswdEntry", list[str])
ShellPath = NewType("ShellPath", str)


# we assume the passwd file exists, is readable and consists of valid lines, so we have
# a function that can fail in exactly one way (the user is not in the passwd file)
# we encode this scenario as an Option
def get_user_entry(username: Username) -> Option[PasswdFileLine]:
    with open("/etc/passwd", "r") as passwd_file:
        for line in passwd_file:
            parts: list[str] = line.split(":")
            if parts[0] == username:
                return Some(PasswdFileLine(line.strip()))
        return Nothing()


# we have a regular function that cannot fail
# assuming it receives a valid passwd file line
def parse_user_entry(entry: PasswdFileLine) -> ParsedPasswdEntry:
    return ParsedPasswdEntry(entry.split(":"))


# we have another regular function that cannot fail
# assuming it receives a valid parsed passwd entry
def get_shell_name(parsed_entry: ParsedPasswdEntry) -> ShellPath:
    return ShellPath(parsed_entry[6])


# now we can combine them and we can skip any error checking midway
# we will only check the result at the end using pattern matching
def print_user_shell(username: Username) -> None:
    match get_user_entry(username) | parse_user_entry | get_shell_name:
        # the result is of the type `Option[ShellPath]`
        case Some(s):
            print(f"- user '{username}' has shell set to '{s}'")
        case Nothing():
            print(f"- user '{username}' not found in the '/etc/passwd' file")


# execute the example for two users, "root" and "anchovies"
if __name__ == "__main__":
    print_user_shell(Username("root"))
    print_user_shell(Username("anchovies"))

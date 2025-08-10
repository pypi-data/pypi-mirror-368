# -*- coding: utf-8 -*-

"""common constants and functions"""

import logging

from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime
from getpass import getuser
from os import DirEntry, sep
from pathlib import Path
from platform import node
from typing import Literal, Self


EMPTY = ""
LF = "\n"
PACKAGE = "uvartage"
POSIX = "posix"
UTF_8 = "utf-8"

ENV_DEFAULT_REPOSITORY = "UVARTAGE_DEFAULT_REPOSITORY"


@dataclass(frozen=True)
class DirectoryEntry:
    """New Directory entry class with constructors from a DirEntry or a Path"""

    name: str
    entry_type: Literal["-", "d", "l"]
    size: int
    last_changed: str
    target: str | None = None

    @property
    def hidden(self) -> bool:
        """returns true if the file or dir is hidden"""
        return self.name.startswith(".")

    def sort_name(self) -> str:
        """return name"""
        return self.name

    def sort_last_changed(self) -> str:
        """return last chnaged time"""
        return self.last_changed

    def __str__(self) -> str:
        """return name"""
        return "  ".join(
            (
                f"{self.entry_type:.<10s}",
                f"{self.size:>10d}",
                self.last_changed,
                f"{self.name} → {self.target}" if self.entry_type == "l" else self.name,
            )
        )

    def display(self, long_format: bool = False) -> str:
        """self display"""
        if long_format:
            return str(self)
        #
        return self.name

    @classmethod
    def from_entry(cls, entry: DirEntry | Path, full_path: bool = False) -> Self:
        """Store attributes"""
        if isinstance(entry, Path):
            stat = entry.lstat()
        elif isinstance(entry, DirEntry):
            stat = entry.stat(follow_symlinks=False)
        else:
            raise TypeError("Must be a DirEntry or Path instance")
        #
        last_changed = datetime.fromtimestamp(stat.st_mtime_ns / 1e9).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        name = str(entry) if full_path else entry.name
        if entry.is_dir():
            return cls(f"{name}{sep}", "d", stat.st_size, last_changed)
        #
        if entry.is_symlink():
            return cls(
                name,
                "l",
                stat.st_size,
                last_changed,
                target=str(Path(entry).readlink()),
            )
        #
        return cls(name, "-", stat.st_size, last_changed)


def complete_paths(text: str, line: str, begidx: int, unused_endidx: int) -> list[str]:
    """Completion for paths on the command line"""
    results: list[str] = []
    if text.startswith("-"):
        # no completion for options
        return results
    #
    if text == "..":
        results.append("../")
        return results
    #
    pattern = f"{text}*"
    basepath = Path()
    if begidx > 0:
        preceding_argument = line[:begidx].split()[-1]
        if preceding_argument[-1] == sep:
            basepath = Path(preceding_argument)
        #
    #
    for found_path in basepath.glob(pattern):
        found_name = found_path.name
        if found_path.is_dir():
            results.append(f"{found_name}{sep}")
        else:
            results.append(found_name)
        #
    #
    return results


def enforce_str(source) -> str:
    """Return source if it is a str instance, or raise a TypeError"""
    if isinstance(source, str):
        return source
    #
    raise TypeError(f"Expected {source!r} to be of type str")


def get_prompt() -> str:
    """Return a prompt including user@host along with the current workdir"""
    return f"«{PACKAGE}» [{getuser()}@{node()} {Path.cwd().name}] "


def get_existing_paths(*files_or_dirs: str) -> list[Path]:
    """Return a list of existing paths from file_or_dirs
    after username and wildcard expansion
    """
    existing_paths: list[Path] = []
    error_messages: list[str] = []
    for single_pattern in files_or_dirs:
        if any((wildcard in single_pattern for wildcard in "?*")):
            if single_pattern.startswith(sep):
                basepath = Path(sep)
                single_pattern = single_pattern[1:]
            else:
                basepath = Path()
            #
            matched_paths = list(basepath.glob(single_pattern))
            if not matched_paths:
                error_messages.append(f"{single_pattern} not found")
            #
            existing_paths.extend(matched_paths)
        else:
            current_path = Path(single_pattern)
            if current_path.exists():
                existing_paths.append(current_path)
            else:
                error_messages.append(f"{single_pattern} does not exist")
            #
        #
    #
    if error_messages and not existing_paths:
        raise ValueError(LF.join(error_messages))
    #
    return existing_paths


def iter_paths_list(
    *files_or_dirs: str,
    long_format: bool = False,
    show_all: bool = False,
    sort_by_time: bool = False,
    sort_reverse: bool = False,
) -> Iterator[str]:
    """Iterate over paths"""
    existing_paths: list[Path] = get_existing_paths(*files_or_dirs)
    if not existing_paths:
        existing_paths.append(Path("."))
    #
    sort_key = DirectoryEntry.sort_name
    if sort_by_time:
        sort_key = DirectoryEntry.sort_last_changed
        sort_reverse = not sort_reverse
    #
    for candidate_path in existing_paths:
        output_entries: list[DirectoryEntry] = []
        if candidate_path.is_dir():
            entries = [
                DirectoryEntry.from_entry(dir_entry)
                for dir_entry in candidate_path.glob("*")
            ]
            for entry in sorted(entries, key=sort_key, reverse=sort_reverse):
                if show_all or not entry.hidden:
                    output_entries.append(entry)
                #
            #
            yield f"--- Contents of {candidate_path}:"
            for entry in output_entries:
                yield entry.display(long_format=long_format)
            #
            yield EMPTY
        else:
            try:
                yield DirectoryEntry.from_entry(candidate_path, full_path=True).display(
                    long_format=long_format
                )
            except OSError as error:
                logging.error(str(error))
            #
        #
    #


def log_multiline(message: str, level: int = logging.INFO) -> None:
    """Log message, using multiple log calls if necessary for multimple lines"""
    for line in message.splitlines():
        logging.log(level, line)
    #

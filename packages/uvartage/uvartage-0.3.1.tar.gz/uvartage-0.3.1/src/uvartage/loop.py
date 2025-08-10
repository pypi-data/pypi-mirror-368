# -*- coding: utf-8 -*-

"""uvartage cmd loop implementation"""

import logging

from argparse import ArgumentParser, Namespace, REMAINDER
from cmd import Cmd
from fnmatch import filter as fnmatch_filter
from getpass import getpass
from os import chdir, environ, getcwd
from pathlib import Path
from shlex import split
from subprocess import run
from sys import stderr

from . import backends
from .commons import (
    EMPTY,
    complete_paths,
    get_prompt,
    iter_paths_list,
    log_multiline,
)


class OptionError(Exception):
    """Raised if the OptionParser would exit"""


class DefusedArgumentParser(ArgumentParser):
    """Defused argument parser not exiting the whoöe loop on wrong options"""

    def exit(self, status=0, message=None):
        """Do not exit the program, raise an OptionError instead"""
        if message:
            stderr.write(message)
        #
        raise OptionError(status)

    @classmethod
    def get_list_arguments(cls, arg: str) -> Namespace:
        """Return parsed arguments for the list command"""
        parser = cls(prog="list", description="Print directory contents")
        parser.add_argument(
            "-l",
            "--long",
            action="store_true",
            help="long format (including size and last changed date)",
        )
        parser.add_argument(
            "-a",
            "--all",
            action="store_true",
            help="all files (by default, hidden files are not listed)",
        )
        parser.add_argument(
            "-r", "--reverse", action="store_true", help="reverse sort order"
        )
        parser.add_argument(
            "-t", "--time", action="store_true", help="sort by time instead of by name"
        )
        parser.add_argument(
            "files_or_dirs", nargs=REMAINDER, help="the file(s) or dir(s) to list"
        )
        return parser.parse_args(split(arg))


class Loop(Cmd):
    """Command loop"""

    _masked = "[masked]"
    _masked_entered_password = "[masked: entered password]"
    _default_index_key = "primary"
    _extra_index_key_base = "extra"

    def __init__(
        self,
        ca_file: Path | None,
        hostname_argument: str,
        repositories: list[str],
        default_username: str,
    ) -> None:
        """Initialize with the provided arguments"""
        if not repositories:
            raise ValueError("At least one repository is required")
        #
        self._environment = dict(environ)
        if isinstance(ca_file, Path):
            ca_full_path = ca_file.resolve()
            if not ca_full_path.is_file():
                raise ValueError(f"{ca_full_path} does not exist or is not a file")
            #
            self._environment.update(SSL_CERT_FILE=str(ca_full_path))
        elif "SSL_CERT_FILE" not in self._environment:
            logging.warning(
                "Neither the environment variable SSL_CERT_FILE has been set,"
                " nor a CA file through --ca-file."
            )
            logging.warning(
                "You might encounter problems if using a non-standard"
                " (i.e. organization internal) certificate authority."
            )
        #
        self._backend = backends.get_backend(
            backends.SupportedBackendType.ARTIFACTORY,
            hostname_argument,
            default_username,
        )
        self._password = getpass(
            f"Please enter the password for {self._backend.username}"
            f" on {self._backend.hostname} (input is hidden): "
        )
        if not self._password:
            raise ValueError("Stopping due to empty password input")
        #
        self._password_masked: set[str] = set()
        self._extra_indexes: list[str] = []
        for index_number, index_repository in enumerate(repositories):
            self.add_index(index_number, index_repository)
        #
        if self._extra_indexes:
            self._environment.update(UV_INDEX=" ".join(self._extra_indexes))
        #
        self.prompt = get_prompt()
        super().__init__()

    def add_index(self, index_number: int, index_repository: str) -> None:
        """Add one index"""
        index_url = self._backend.get_index_url(index_repository)
        if not index_number:
            index_key = self._default_index_key
        elif index_number > 0:
            index_key = f"{self._extra_index_key_base}{index_number}"
        else:
            raise ValueError(f"Invalid index number {index_number}")
        #
        index_envvalue = f"{index_key}={index_url}"
        if index_number:
            self._extra_indexes.append(index_envvalue)
        else:
            self._environment.update(UV_DEFAULT_INDEX=index_envvalue)
        #
        index_cred_prefix = f"UV_INDEX_{index_key.upper()}"
        self._password_masked.add(f"{index_cred_prefix}_PASSWORD")
        self._environment.update(
            {
                f"{index_cred_prefix}_USERNAME": self._backend.username,
                f"{index_cred_prefix}_PASSWORD": self._password,
            }
        )

    def execute_command(
        self,
        command: str,
        *additional_args: str,
        arg: str = EMPTY,
    ) -> None:
        """execute command through subprocess.run() in the set environment,
        without outputcapture or check
        """
        full_command = [command] + list(additional_args) + split(arg)
        logging.warning("Running command: %r", full_command)
        run(full_command, env=self._environment, check=False)

    def do_cd(self, arg) -> None:
        """Change directory"""
        if not arg:
            arg = self._environment["HOME"]
        #
        chdir(arg)
        self.prompt = get_prompt()

    def do_env(self, arg) -> None:
        """Print the environment variables"""
        if not arg:
            arg = "*"
        #
        for key in sorted(fnmatch_filter(self._environment, arg)):
            if key in self._password_masked:
                print(f"{key}={self._masked_entered_password}")
            elif any(to_mask in key.lower() for to_mask in ("password", "token")):
                print(f"{key}={self._masked}")
            else:
                print(f"{key}={self._environment[key]}")
            #
        #

    def complete_sh(
        self, text: str, line: str, begidx: int, unused_endidx: int
    ) -> list[str]:
        """Completion for the sh command"""
        return complete_paths(text, line, begidx, unused_endidx)

    def do_sh(self, arg) -> None:
        """Run an arbitrary command through the shell"""
        logging.warning("Running command with shell=True: %r", arg)
        run(arg, env=self._environment, check=False, shell=True)

    def do_git(self, arg) -> None:
        """Run git with the provided arguments"""
        self.execute_command("git", arg=arg)

    def complete_list(
        self, text: str, line: str, begidx: int, unused_endidx: int
    ) -> list[str]:
        """Completion for the list command"""
        return complete_paths(text, line, begidx, unused_endidx)

    def do_list(self, arg) -> None:
        """Print directory contents (emulation)"""
        try:
            args = DefusedArgumentParser.get_list_arguments(arg)
        except OptionError:
            return
        #
        try:
            for line in iter_paths_list(
                *args.files_or_dirs,
                long_format=args.long,
                show_all=args.all,
                sort_reverse=args.reverse,
                sort_by_time=args.time,
            ):
                print(line)
            #
        except ValueError as error:
            log_multiline(str(error), level=logging.ERROR)
            return
        #

    def do_ls(self, arg) -> None:
        """Deprecated POSIX platform only external ls command"""
        del arg
        logging.warning(
            "'ls' is not supported anymore – please use the list command (or 'sh ls ...')"
        )

    def do_pwd(self, unused_arg) -> None:
        """Print working directory"""
        if unused_arg:
            logging.warning("Ignored argument(s) %r", unused_arg)
        #
        print(getcwd())

    def do_uv(self, arg) -> None:
        """Run uv with the provided arguments"""
        self.execute_command("uv", arg=arg)

    def do_uvx(self, arg) -> None:
        """Run uvx with the provided arguments"""
        self.execute_command("uvx", arg=arg)

    # pylint: disable=invalid-name ; required to support EOF character
    def do_EOF(self, unused_arg) -> bool:
        """Exit the REPL by EOF (eg. Ctrl-D on Unix)"""
        print()
        if unused_arg:
            logging.warning("Ignored argument(s) %r", unused_arg)
        #
        logging.info("bye")
        return True

    def emptyline(self) -> bool:
        """do nothing on empty input"""
        return False

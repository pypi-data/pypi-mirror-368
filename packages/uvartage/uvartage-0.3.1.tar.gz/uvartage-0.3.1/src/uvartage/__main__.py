# -*- coding: utf-8 -*-

"""uvartage command line interface"""

import argparse
import getpass
import importlib.metadata
import logging
import os
import pathlib
import sys
import tomllib

from .backends import SupportedBackendType
from .commons import PACKAGE, UTF_8, ENV_DEFAULT_REPOSITORY
from .loop import Loop


def get_project_file_contents(project_file_name: str) -> str:
    """Return the contents of a project file two directories up"""
    project_directory_path = pathlib.Path(__file__).resolve().parent.parent.parent
    project_file_path = project_directory_path / project_file_name
    return project_file_path.read_text(encoding=UTF_8)


def get_metadata_version(metadata_file_name: str = "pyproject.toml") -> str:
    """get version information from metadata_file up_dirs directories above"""
    metadata = tomllib.loads(get_project_file_contents(metadata_file_name))
    version = metadata["project"]["version"]
    return f"{version} (read directly from {metadata_file_name})"


def get_arguments(*args: str, test_context: bool = False) -> argparse.Namespace:
    """Parse commandline arguments"""
    try:
        version = importlib.metadata.version(PACKAGE)
    except importlib.metadata.PackageNotFoundError:
        version = get_metadata_version()
    #
    parser = argparse.ArgumentParser(
        prog=PACKAGE,
        description="Wrapper for uv with artifact storage in airgapped environments",
    )
    parser.set_defaults(loglevel=logging.WARNING, user=getpass.getuser())
    parser.add_argument(
        "--version", action="version", version=version, help="print version and exit"
    )
    parser.add_argument(
        "-v ",
        "--verbose",
        action="store_const",
        const=logging.INFO,
        dest="loglevel",
        help="show more messages",
    )
    parser.add_argument(
        "--backend",
        type=SupportedBackendType,
        # see https://stackoverflow.com/a/46385352>
        choices=list(SupportedBackendType),
        default=SupportedBackendType.ARTIFACTORY,
        help="the artifact storage backend type"
        " (default and currently the only supported backend: %(default)s)",
    )
    parser.add_argument(
        "--ca-file",
        type=pathlib.Path,
        help="a CA cert bundle file to be provided via SSL_CERT_FILE.",
    )
    parser.add_argument(
        "--user",
        help="username for the artifact storage backend if the hostname is"
        " not explicitly specified as USER@HOSTNAME; default is %(default)r.",
    )
    parser.add_argument(
        "hostname",
        metavar="[USER@]HOSTNAME",
        help="the artifact storage hostname, or user and hostname combined by '@'.",
    )
    parser.add_argument(
        "repositories",
        nargs=argparse.REMAINDER,
        help="the package repositories (default first)."
        " If not at least one repository name is provided, the value of the"
        f" environment variable {ENV_DEFAULT_REPOSITORY} will be used.",
    )
    if args or test_context:
        arguments = parser.parse_args(list(args))
    else:
        arguments = parser.parse_args()
    #
    logging.basicConfig(format="| %(message)s", level=arguments.loglevel)
    return arguments


def main() -> int:
    """Execute the loop and return a zero returncode"""
    arguments = get_arguments()
    if not arguments.repositories:
        try:
            default_repository = os.environ[ENV_DEFAULT_REPOSITORY]
        except KeyError:
            logging.critical(
                "If no repository names are provided on the command line,"
                " a default repository name has to be specified via"
                " environment variable %r.",
                ENV_DEFAULT_REPOSITORY,
            )
            return 1
        #
        arguments.repositories.append(default_repository)
    #
    repl = Loop(
        ca_file=arguments.ca_file,
        hostname_argument=arguments.hostname,
        repositories=arguments.repositories,
        default_username=arguments.user,
    )
    # Do not exit on KeyboardInterrupt
    repeat = True
    intro = "Welcome to the uv wrapper shell. Type help or ? to list commands.\n"
    while repeat:
        try:
            repl.cmdloop(intro=intro)
        except ValueError as error:
            logging.critical(str(error))
            return 1
        #
        except KeyboardInterrupt:
            # silent REPL restart
            print("^C")
            intro = ""
            continue
        #
        repeat = False
    #
    return 0


if __name__ == "__main__":
    sys.exit(main())

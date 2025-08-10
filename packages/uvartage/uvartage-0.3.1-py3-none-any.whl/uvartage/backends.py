# -*- coding: utf-8 -*-

"""uvartage: wrapper for uv with artifact storage in airgapped environments"""

import urllib.parse

from enum import Enum

from .commons import EMPTY, enforce_str


class SupportedBackendType(str, Enum):
    """Supported Backend types"""

    ARTIFACTORY = "artifactory"

    def __str__(self):
        """required for proper argparse display,
        compare <https://stackoverflow.com/a/46385352>
        """
        return self.value


class BackendBase:
    """Backend base class"""

    api_path = "/"
    scheme = "https"

    def __init__(self, hostname_argument: str, default_username: str) -> None:
        """Store the URL parts and the username"""
        try:
            self.__username, self.__hostname = hostname_argument.split("@")
        except ValueError:
            self.__username = default_username
            self.__hostname = hostname_argument
        #
        self.__api_base_url = enforce_str(
            urllib.parse.urlunsplit(
                (self.scheme, self.__hostname, self.api_path, EMPTY, EMPTY)
            )
        )

    @property
    def hostname(self) -> str:
        """hostname property"""
        return self.__hostname

    @property
    def username(self) -> str:
        """Username property"""
        return self.__username

    @property
    def api_base_url(self) -> str:
        """API base URL"""
        return self.__api_base_url

    def get_index_url(self, repository_name: str) -> str:
        """Index URL for the provided repository name"""
        return f"{self.__api_base_url}{repository_name}/simple"


class Artifactory(BackendBase):
    """Artifactory backend"""

    api_path = "/artifactory/api/pypi/"


def get_backend(
    backend_type: SupportedBackendType, hostname_argument: str, default_username: str
) -> BackendBase:
    """Return the backend for backend_type ans hostname_argument"""
    match backend_type:
        case SupportedBackendType.ARTIFACTORY:
            return Artifactory(hostname_argument, default_username)
        #
    #
    raise ValueError(f"Unsupported backend {backend_type!r}")

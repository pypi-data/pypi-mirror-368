#!/usr/bin/env python3

# Standard libraries
from typing import Union

# Modules libraries
from gitlab import Gitlab
from gitlab.v4.objects import Project

# GitLabFeature class, pylint: disable=too-many-public-methods
class GitLabFeature:

    # Members
    __gitlab: Gitlab

    # Constructor
    def __init__(
        self,
        url: str,
        private_token: str,
        job_token: str,
        ssl_verify: Union[bool, str] = True,
    ) -> None:

        # Create GitLab client
        if private_token:
            self.__gitlab = Gitlab(
                url=url,
                private_token=private_token,
                ssl_verify=ssl_verify,
            )
        elif job_token:
            self.__gitlab = Gitlab(
                url=url,
                job_token=job_token,
                ssl_verify=ssl_verify,
            )
        else:
            self.__gitlab = Gitlab(
                url=url,
                ssl_verify=ssl_verify,
            )

        # Authenticate if available
        if self.__gitlab.private_token or self.__gitlab.oauth_token:
            self.__gitlab.auth()

    # Project
    def project(self, criteria: str) -> Project:
        return self.__gitlab.projects.get(criteria)

    # URL
    @property
    def url(self) -> str:
        return str(self.__gitlab.api_url)

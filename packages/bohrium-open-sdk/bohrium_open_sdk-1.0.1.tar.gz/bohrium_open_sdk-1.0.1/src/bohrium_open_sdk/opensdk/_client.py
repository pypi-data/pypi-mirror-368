from __future__ import annotations

import os
from typing import Optional, Union

from httpx import URL, Client, Timeout
from typing_extensions import override

from . import resources
from ._base_client import DEFAULT_MAX_RETRIES, SyncAPIClient
from ._constants import DEFAULT_API_PREFIX
from ._exceptions import AccessKeyError
from ._version import __version__


class OpenSDK(SyncAPIClient):
    # resources
    job: resources.Job
    app: resources.App
    user: resources.User

    # client options
    access_key: str
    user_token: str
    project_id: Union[int, None]
    tiefblue_base_url: str
    app_key: str

    def __init__(
        self,
        *,
        access_key: Optional[str] = None,
        app_key: Optional[str] = None,
        base_url: Optional[Union[str, URL]] = None,
        tiefblue_base_url: Optional[str] = None,
        project_id: Optional[int] = None,
        timeout: Optional[Union[float, Timeout]] = 300,
        max_retries: Optional[int] = DEFAULT_MAX_RETRIES,
        api_prefix: Optional[Union[str, None]] = DEFAULT_API_PREFIX,
        http_client: Optional[Client] = None,
    ) -> None:

        # initialize project_id
        if project_id is None:
            project_id = os.environ.get("BOHRIUM_PROJECT_ID")
        self.project_id = project_id

        if base_url is None:
            base_url = os.environ.get("BOHRIUM_OPEN_SDK_BASE_URL")

        if base_url is None:
            base_url = "https://openapi.dp.tech"

        if tiefblue_base_url is None:
            tiefblue_base_url = os.environ.get("TIEFBLUE_BASE_URL")

        if tiefblue_base_url is None:
            # default is tiefblue nas
            tiefblue_base_url = "https://tiefblue-nas.dp.tech"

        self.tiefblue_base_url = tiefblue_base_url

        self.api_prefix = api_prefix
        self.app_key = app_key

        # initialize ak by user_token
        # TODO: Bohrium Oauth support ak and scope remove this logic
        self.access_key = access_key
        if access_key is None:
            access_key = os.environ.get("BOHRIUM_OPEN_SDK_ACCESS_KEY")
            self.access_key = access_key

        if self.access_key is None:
            raise AccessKeyError(
                "The api_key client option must be set either by passing api_key to the client or by setting the BOHRIUM_OPEN_SDK_ACCESS_KEY environment variable"
            )

        super().__init__(
            _version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=self.default_headers,
        )

        self.job = resources.Job(self)
        self.user = resources.User(self)
        self.app = resources.App(self)
        self.app_db = resources.AppDB(self)

    @property
    @override
    def default_headers(self) -> dict[str, str]:
        default_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-access-key": self.access_key,
            "accessKey": self.access_key,
        }
        if self.app_key:
            default_headers["x-app-key"] = self.app_key
        return default_headers


class SyncHttpxClientWrapper(Client):
    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass

import logging

from bohrium_open_sdk.opensdk._resource import SyncAPIResource
from bohrium_open_sdk.opensdk._response import APIResponse


log = logging.getLogger(__name__)


class User(SyncAPIResource):

    def get_info(self):
        response = self._client.get("openapi/v1/ak/user")
        return APIResponse(response).json

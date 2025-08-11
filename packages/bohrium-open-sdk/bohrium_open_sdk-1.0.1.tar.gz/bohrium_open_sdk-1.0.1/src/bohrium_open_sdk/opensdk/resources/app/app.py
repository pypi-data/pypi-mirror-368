from bohrium_open_sdk.opensdk.resources.app.app_job import AppJob
from bohrium_open_sdk.opensdk._resource import SyncAPIResource
from bohrium_open_sdk.opensdk._response import APIResponse


class App(SyncAPIResource):
    job: AppJob

    def __init__(self, _client) -> None:
        self.job = AppJob(_client)
        super().__init__(_client)

    def get_app_info(self, app_key: str):
        response = self._client.get(
            "/openapi/v1/square/app/schema", params={"appKey": app_key}
        )
        return APIResponse(response).json

    def get_upload_token(self, file_name: str = ""):
        url = f"/openapi/v1/square/app/admin/upload/token?appKey={self._client.app_key}&type=other&fileName={file_name}"
        response = self._client.get(url)
        if response.status_code != 200:
            raise Exception(f"get upload token failed: {response.text}")
        return APIResponse(response).json

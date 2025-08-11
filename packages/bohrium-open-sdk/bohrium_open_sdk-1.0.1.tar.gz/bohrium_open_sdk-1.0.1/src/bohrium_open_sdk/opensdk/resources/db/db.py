# -*- coding: UTF-8 -*-

from typing import Optional, Tuple, List

from bohrium_open_sdk.opensdk._resource import SyncAPIResource
from bohrium_open_sdk.opensdk._response import APIResponse


class AppDB(SyncAPIResource):

    def __init__(self, _client) -> None:
        super().__init__(_client)

    def insert(self, data) -> List:
        response = self._client.post("/openapi/v1/db/app/data/insert", json=data)
        data: dict = APIResponse(response).json
        if data.get("code", None) != 0:
            raise Exception(f"insert failed: {data}")

        return data["data"]["ids"]

    def delete(self, data) -> int:
        response = self._client.delete("/openapi/v1/db/app/data", json=data)
        data: dict = APIResponse(response).json
        if data.get("code", None) != 0:
            raise Exception(f"delete failed: {data}")

        return data["data"]["deletedCount"]

    def update(self, data) -> Tuple[int, Optional[str]]:
        response = self._client.post("/openapi/v1/db/app/data/update", json=data)
        data: dict = APIResponse(response).json
        if data.get("code", None) != 0:
            raise Exception(f"update failed: {data}")

        return data["data"]["modifyCount"], data["data"]["result"] or None

    def query(self, data) -> Tuple[int, List]:
        response = self._client.post("/openapi/v1/db/app/data/list", json=data)
        data: dict = APIResponse(response).json
        if data.get("code", None) != 0:
            raise Exception(f"query failed: {data}")

        return data["data"]["count"], data["data"]["list"] or []

    def queryv2(self, data) -> Tuple[int, List]:
        response = self._client.post("/openapi/v1/db/app/data/listv2", json=data)
        data: dict = APIResponse(response).json
        if data.get("code", None) != 0:
            raise Exception(f"query v2 failed: {data}")

        return data["data"]["count"], data["data"]["list"] or []

    def count(self, data) -> int:
        response = self._client.post("/openapi/v1/db/app/data/count", json=data)
        data: dict = APIResponse(response).json
        if data.get("code", None) != 0:
            raise Exception(f"count failed: {data}")

        return data["data"]["count"]

    def create_table(self, data) -> str:
        response = self._client.post("/openapi/v1/db/app/table/create", json=data)
        data: dict = APIResponse(response).json
        if data.get("code", None) != 0:
            raise Exception(f"create_table failed: {data}")

        return data["data"]["tableId"]

    def create_table_v2(self, data) -> str:
        response = self._client.post("/openapi/v1/db/app/table", json=data)
        data: dict = APIResponse(response).json
        if data.get("code", None) != 0:
            raise Exception(f"create_table_v2 failed: {data}")

        return data["data"]["tableAk"]

    def delete_table(self, data) -> bool:
        response = self._client.delete("/openapi/v1/db/app/table", json=data)
        data: dict = APIResponse(response).json
        if data.get("code", None) != 0:
            raise Exception(f"delete_table failed: {data}")
        return data["data"]["result"]

    def get_common_db_file_token(self, file_name: str = ""):
        url = f"/openapi/v1/db/app/file/token?fileName={file_name}"
        response = self._client.get(url)
        if response.status_code != 200:
            raise Exception(f"get upload token failed: {response.text}")
        return APIResponse(response).json

    def get_table_detail(self, table_ak: str = ""):
        url = f"/openapi/v1/db/app/table?tableAk={table_ak}"
        response = self._client.get(url)
        if response.status_code != 200:
            raise Exception(f"get table detail failed: {response.text}")
        result = APIResponse(response).json
        if result.get("code", None) != 0:
            raise Exception(f"get table detail failed: {result}")
        return result["data"]

    def tables(self, db_ak: str = ""):
        url = f"/openapi/v1/db/app/table/list?dbAk={db_ak}"
        response = self._client.get(url)
        if response.status_code != 200:
            raise Exception(f"get tables detail failed: {response.text}")
        result = APIResponse(response).json
        if result.get("code", None) != 0:
            raise Exception(f"get tables detail failed: {result}")
        return result["data"]

    def alter_table(self, data):
        response = self._client.post("/openapi/v1/db/app/table/alter", json=data)
        data: dict = APIResponse(response).json
        if data.get("code", None) != 0:
            raise Exception(f"alter_table failed: {data}")
        return data["data"]["result"]

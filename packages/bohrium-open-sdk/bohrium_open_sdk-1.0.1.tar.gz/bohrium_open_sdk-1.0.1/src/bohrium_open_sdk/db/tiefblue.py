from bohrium_open_sdk.opensdk._tiefblue_client import Tiefblue as _Tiefblue
from bohrium_open_sdk.opensdk._base_client import BaseClient
from httpx import URL
from typing import Optional, Union
from bohrium_open_sdk import UploadInputItem
import io
from bohrium_open_sdk import OpenSDK
import os
from glom import glom


class Tiefblue(BaseClient):
    def __init__(
        self,
        base_url="https://openapi.test.dp.tech",
        tiefblue_url: Optional[Union[str, URL]] = None,
        access_key="",
        app_key="",
        timeout=60,
    ) -> None:
        self.tiefblue = _Tiefblue(base_url=tiefblue_url)
        self.client = OpenSDK(
            base_url=base_url, access_key=access_key, app_key=app_key, timeout=timeout
        )

    def get_upload_token(self, file_name: str = ""):
        # return self.client.app.get_upload_token(file_name)
        return self.client.app_db.get_common_db_file_token(file_name)

    def check_upload_file_params(self, file_name, file):
        if not file_name:
            raise Exception("file_name is required")
        if not file:
            raise Exception("file is required")

    def upload_file(
        self,
        file_name: str = "",
        file_path: str = "",
        overwrite: bool = False,
    ) -> {}:
        """
        file_name: str, required 存储的文件名
        file_path: str, required 要上传文件的本地路径
        overwrite: bool, optional 是否覆盖同名文件，默认为 False

        请捕获异常并处理
        """
        self.check_upload_file_params(file_name, file_path)
        # file_path是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"file_path {file_path} not exists")
        if os.path.isdir(file_path):
            raise IsADirectoryError(f"file_path {file_path} is a directory")

        token = self.get_upload_token(file_name)

        if token.get("code") != 0:
            raise Exception(f"get upload token failed: {token}")

        resp = self._upload_file(token.get("data"), file_path, overwrite)
        if resp.get("code") != 0:
            return resp
        resp["data"]["name"] = file_name
        return resp

    def upload_file_bytes(
        self,
        file_name: str = "",
        file_bytes: bytes = b"",
        overwrite: bool = False,
    ) -> {}:
        """
        file_name: str, required 存储的文件名
        file_bytes: bytes, required 要上传的文件的二进制数据
        overwrite: bool, optional 是否覆盖同名文件，默认为 False

        请捕获异常并处理
        """
        self.check_upload_file_params(file_name, file_bytes)

        token = self.get_upload_token(file_name)

        if token.get("code") != 0:
            raise Exception(f"get upload token failed: {token}")

        resp = self._upload_file_bytes(token.get("data"), file_bytes, overwrite)
        if resp.get("code") != 0:
            return resp
        resp["data"]["name"] = file_name
        return resp

    def delete_file(self, file_name: str = ""):
        """
        file_name: str, required 要删除的文件名

        return: bool, 是否删除成功
        请捕获异常并处理
        """
        if not file_name:
            raise Exception("file_name is required")
        token = self.get_upload_token(file_name)
        if token.get("code") != 0:
            raise Exception(f"delete file failed: {token}")
        params = self.tiefblue.decode_base64(
            token.get("data").get(self.tiefblue.TIEFBLUE_HEADER_KEY)
        )
        path = params.get("path", "")
        headers = {
            self.tiefblue.TIEFBLUE_HEADER_KEY: token.get("data").get(
                self.tiefblue.TIEFBLUE_HEADER_KEY
            ),
            self.tiefblue.AUTH_HEADER_KEY: token.get("data").get(
                self.tiefblue.AUTH_HEADER_KEY
            ),
        }
        meta_resp = self.tiefblue.meta(path=path, headers=headers)

        if meta_resp.get("code") != 0:
            raise Exception(f"upload failed pre to get meta failed: {meta_resp}")

        if glom(meta_resp, "data.exist") is False:
            return True
        delete_resp = self.tiefblue.delete_file(path=path, headers=headers)
        return delete_resp.get("code") == 0

    def get_download_url(
        self,
        file_name: str = "",
    ):
        if not file_name:
            raise Exception("file_name is required")
        token = self.get_upload_token(file_name)
        if token.get("code") != 0:
            raise Exception(f"get download url failed: {token}")
        return self._get_download_url(token.get("data"))

    def build_upload_params(self, token_params: dict = {}, overwrite: bool = False):
        # path
        params = self.tiefblue.decode_base64(
            token_params.get(self.tiefblue.TIEFBLUE_HEADER_KEY)
        )

        path = params.get("path", "")
        # 检查 path 是否为空
        if not path:
            raise ValueError(f"get Path from token is empty or not provided")
        orgin_file_name = path.split("/")[-1] if "/" in path else path

        headers = {
            self.tiefblue.TIEFBLUE_HEADER_KEY: token_params.get(
                self.tiefblue.TIEFBLUE_HEADER_KEY
            ),
            self.tiefblue.AUTH_HEADER_KEY: token_params.get(
                self.tiefblue.AUTH_HEADER_KEY
            ),
        }
        meta_resp = self.tiefblue.meta(path=path, headers=headers)

        if meta_resp.get("code") != 0:
            raise Exception(f"upload failed pre to get meta failed: {meta_resp}")

        if glom(meta_resp, "data.exist") and not overwrite:
            raise FileExistsError(f"file {orgin_file_name} already exists")
        return path, orgin_file_name, headers

    def _upload_file(
        self, token_params: dict = {}, file_path: str = "", overwrite: bool = False
    ) -> {}:
        path, _, headers = self.build_upload_params(token_params, overwrite)
        # 上传文件
        file = UploadInputItem(src=file_path)
        return self.tiefblue.upload_from_file_multi_part(
            object_key=path,
            custom_headers=headers,
            file_path=str(file.src),
            progress_bar=True,
        )

    def _upload_file_bytes(
        self,
        token_params: dict = {},
        file_bytes: bytes = b"",
        overwrite: bool = False,
    ) -> {}:
        path, file_name, headers = self.build_upload_params(token_params, overwrite)
        # 上传文件
        return self.tiefblue.upload_from_byte_multi_part(
            object_key=path,
            custom_headers=headers,
            file_name=file_name,
            file_stream=io.BytesIO(file_bytes),
            progress_bar=True,
        )

    def _get_download_url(self, token_params: dict = {}):
        # path
        params = self.tiefblue.decode_base64(
            token_params.get(self.tiefblue.TIEFBLUE_HEADER_KEY)
        )
        path = params.get("path", "")
        # 检查 path 是否为空
        if not path:
            raise ValueError(f"get Path from token is empty or not provided")
        orgin_file_name = path.split("/")[-1] if "/" in path else path

        headers = {
            self.tiefblue.TIEFBLUE_HEADER_KEY: token_params.get(
                self.tiefblue.TIEFBLUE_HEADER_KEY
            ),
            self.tiefblue.AUTH_HEADER_KEY: token_params.get(
                self.tiefblue.AUTH_HEADER_KEY
            ),
        }

        meta_resp = self.tiefblue.meta(path=path, headers=headers)
        if meta_resp.get("code") != 0:
            raise Exception(
                f"get download url failed pre to get meta failed: {meta_resp}"
            )
        if not glom(meta_resp, "data.exist"):
            raise Exception(f"file {orgin_file_name} not exists")

        return self.tiefblue.get_download_url(path=path, headers=headers)

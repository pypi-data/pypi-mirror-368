import base64
import json
import logging
import os
import time
from pathlib import Path
from typing import Mapping, Optional, Union, cast
import io

import requests
from httpx import URL, Client, Limits, Timeout
from tqdm import tqdm

from ._base_client import BaseClient, SyncHttpxClientWrapper
from ._constants import (
    DEFAULT_CONNECTION_LIMITS,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIEFBLUE_TIMEOUT,
)
from ._response import APIResponse

_DEFAULT_CHUNK_SIZE = 50 * 1024 * 1024
_DEFAULT_ITERATE_MAX_OBJECTS = 50

logger = logging.getLogger(__name__)


class Parameter(object):
    contentType: str
    contentEncoding: str
    contentLanguage: str
    contentDisposition: str
    cacheControl: str
    acl: str
    expires: str
    userMeta: dict
    predefinedMeta: str


class Tiefblue(BaseClient[Client]):
    TIEFBLUE_HEADER_KEY = "X-Storage-Param"
    AUTH_HEADER_KEY = "Authorization"
    _client: Client

    def __init__(
        self,
        base_url: Optional[Union[str, URL]] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        timeout: Union[float, Timeout, None] = DEFAULT_TIEFBLUE_TIMEOUT,
        limits: Limits = DEFAULT_CONNECTION_LIMITS,
        _version: Optional[str] = None,
        custom_headers: Optional[Mapping[str, str]] = None,
    ) -> None:

        if base_url is None:
            base_url = os.environ.get("TIEFBLUE_BASE_URL")

        if base_url is None:
            base_url = "https://tiefblue.dp.tech"

        super().__init__(
            _version=_version,
            limits=limits,
            # cast to a valid type because mypy doesn't understand our type narrowing
            timeout=cast(Timeout, timeout),
            base_url=base_url,
            max_retries=max_retries,
            custom_headers=custom_headers,
        )
        self._client = SyncHttpxClientWrapper(
            base_url=base_url,
            # cast to a valid type because mypy doesn't understand our type narrowing
            timeout=cast(Timeout, timeout),
            limits=limits,
            follow_redirects=True,
        )

    def encode_base64(self, parameter: dict = {}) -> str:
        j = json.dumps(parameter)
        return base64.b64encode(j.encode()).decode()

    def _write(
        self,
        object_key: str,
        data: str = "",
        headers: dict = {},
        parameter: dict = {},
    ):
        param = {"path": object_key}

        if parameter:
            param["option"] = parameter.__dict__

        headers[self.TIEFBLUE_HEADER_KEY] = self.encode_base64(param)
        resp = self._client.post("/api/upload/binary", headers=headers, data=data)

        return APIResponse(resp).json

    def read(self, object_key: str = "", token: str = "", ranges: str = "") -> None:

        url = f"/api/download/{object_key}"
        self.client.token = token
        res = self.client.get(url, host=self.host, stream=True)
        return res

    def meta(self, path: str = "", headers: dict = {}) -> dict:
        url = f"/api/meta/{path}"
        response = self._client.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"get meta failed: {response.text}")
        return APIResponse(response).json

    def delete_file(self, path: str = "", headers: dict = {}):
        url = f"/api/delete/{path}"
        response = self._client.delete(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"delete file failed: {response.text}")
        return APIResponse(response).json

    def get_download_url(self, path: str = "", headers: dict = {}):
        import http.client
        from urllib.parse import urlparse, quote

        _base_url = str(self._base_url)
        if not _base_url.endswith("/"):
            _base_url += "/"
        url = f"{_base_url}api/download/{quote(path)}"
        parsed_url = urlparse(url)

        if parsed_url.scheme == "https":
            connection = http.client.HTTPSConnection(parsed_url.netloc)
        else:
            connection = http.client.HTTPConnection(parsed_url.netloc)

        full_path = parsed_url.path
        if parsed_url.query:
            full_path += "?" + parsed_url.query

        connection.request("GET", full_path, headers=headers)
        response = connection.getresponse()

        if response.status in [301, 302, 307, 308]:  # 处理所有常见的重定向状态码
            redirect_url = response.getheader("Location")
            return redirect_url
        else:
            response_content = response.read().decode("utf-8")
            raise Exception(
                f"get download {parsed_url.scheme}://{parsed_url.netloc}{full_path} failed, "
                f"status: {response.status}, response: {response_content}"
            )

    def upload_from_file(
        self,
        object_key: str = "",
        file_path: str = "",
        token: str = "",
        parameter: dict = None,
    ) -> None:
        if not os.path.exists(file_path):
            raise FileNotFoundError
        if os.path.isdir(file_path):
            raise IsADirectoryError
        _, disposition = os.path.split(file_path)
        if parameter is None:
            parameter = Parameter()
        parameter.contentDisposition = f'attachment; filename="{disposition}"'
        with open(file_path, "rb") as fp:
            res = self._write(
                object_key=object_key, data=fp.read(), parameter=parameter
            )
            return res

    def init_upload_by_part(self, object_key: str, parameter=None):
        data = {"path": object_key}
        if parameter is not None:
            data["option"] = parameter.__dict__
        url = "/api/upload/multipart/init"
        return self._client.post(url, host=self.host, json=data)

    def upload_by_part(
        self, object_key: str, initial_key: str, chunk_size: int, number: int, body
    ):
        param = {
            "initialKey": initial_key,
            "number": number,
            "partSize": chunk_size,
            "objectKey": object_key,
        }
        headers = {}
        headers[self.TIEFBLUE_HEADER_KEY] = self._dump_parameter(param)
        url = "/api/upload/multipart/upload"
        resp = self._client.post(url, host=self.host, data=body, headers=headers)
        return resp

    def complete_upload_by_part(self, object_key, initial_key, part_string):
        data = {
            "path": object_key,
            "initialKey": initial_key,
            "partString": part_string,
        }
        url = "/api/upload/multipart/complete"
        resp = self.client.post(url, host=self.host, json=data)
        return APIResponse(resp).json

    def upload_from_file_multi_part(
        self,
        *,
        object_key: Union[str, Path],
        file_path: Union[str, Path],
        custom_headers: Optional[Mapping[str, str]] = None,
        chunk_size: int = _DEFAULT_CHUNK_SIZE,
        parameter=None,
        progress_bar=False,
        need_parse=False,
    ) -> {}:
        if isinstance(file_path, Path):
            if not file_path.exists():
                raise FileNotFoundError
        elif not os.path.exists(file_path):
            raise FileNotFoundError
        if os.path.isdir(file_path):
            raise IsADirectoryError
        object_key = str(object_key)
        if need_parse:
            _, _, object_key = self._parse_ap_name_and_tag(object_key)
        size = os.path.getsize(file_path)
        _, disposition = os.path.split(file_path)
        if parameter is None:
            parameter = Parameter()
        parameter.contentDisposition = f'attachment; filename="{disposition}"'
        bar_format = "{l_bar}{bar}| {n:.02f}/{total:.02f} %  [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
        with open(file_path, "r") as f:
            pbar = tqdm(
                total=100,
                desc=f"Uploading {disposition}",
                smoothing=0.01,
                bar_format=bar_format,
                disable=not progress_bar,
            )
            f.seek(0)
            if size < _DEFAULT_CHUNK_SIZE * 2:
                resp = self._write(
                    object_key=object_key,
                    data=f.buffer,
                    parameter=parameter,
                    headers=custom_headers,
                )
                pbar.update(100)
                pbar.close()
                return resp
            chunks = split_size_by_part_size(size, chunk_size)
            initial_key = self.init_upload_by_part(object_key, parameter).get(
                "initialKey"
            )
            part_string = []
            for c in chunks:
                f.seek(c.Offset)
                num_to_upload = min(chunk_size, size - c.Offset)
                part_string.append(
                    self.upload_by_part(
                        object_key,
                        initial_key,
                        chunk_size=c.Size,
                        number=c.Number,
                        body=f.buffer.read(c.Size),
                    ).get("partString")
                )
                percent = num_to_upload * 100 / (size + 1)
                pbar.update(percent)
            pbar.close()
            resp = self.complete_upload_by_part(object_key, initial_key, part_string)
            if resp.get("code") != 0:
                return resp
            return {"code" : 0, "data" : {"path" : object_key}}

    def upload_from_byte_multi_part(
        self,
        *,
        object_key: Union[str, Path],
        file_name: str,
        file_stream: io.BytesIO,
        custom_headers: Optional[Mapping[str, str]] = None,
        chunk_size: int = _DEFAULT_CHUNK_SIZE,
        parameter=None,
        progress_bar=False,
        need_parse=False,
    ) -> {}:

        object_key = str(object_key)
        if need_parse:
            _, _, object_key = self._parse_ap_name_and_tag(object_key)
        size = file_stream.getbuffer().nbytes
        if parameter is None:
            parameter = Parameter()
        parameter.contentDisposition = f'attachment; filename="{file_name}"'
        bar_format = "{l_bar}{bar}| {n:.02f}/{total:.02f} %  [{elapsed}<{remaining}, {rate_fmt}{postfix}]"

        pbar = tqdm(
            total=100,
            desc=f"Uploading {file_name}",
            smoothing=0.01,
            bar_format=bar_format,
            disable=not progress_bar,
        )
        file_stream.seek(0)
        if size < _DEFAULT_CHUNK_SIZE * 2:
            resp = self._write(
                object_key=object_key,
                data=file_stream.read(),
                parameter=parameter,
                headers=custom_headers,
            )
            pbar.update(100)
            pbar.close()
            return resp
        chunks = split_size_by_part_size(size, chunk_size)
        initial_key = self.init_upload_by_part(object_key, parameter).get("initialKey")
        part_string = []
        for c in chunks:
            file_stream.seek(c.Offset)
            num_to_upload = min(chunk_size, size - c.Offset)
            part_string.append(
                self.upload_by_part(
                    object_key,
                    initial_key,
                    chunk_size=c.Size,
                    number=c.Number,
                    body=file_stream.read(c.Size),
                ).get("partString")
            )
            percent = num_to_upload * 100 / (size + 1)
            pbar.update(percent)
        pbar.close()
        resp = self.complete_upload_by_part(object_key, initial_key, part_string)
        if resp.get("code") != 0:
            return resp
        return {"code" : 0, "data" : {"path" : object_key}}

    def download_from_file(self):
        pass

    def download_from_url(self, url: str, save_file: Path):
        ret = None
        for retry_count in range(3):
            try:
                ret = requests.get(url, stream=True)
            except Exception as e:
                logger.warning(f"download from url failed: {e}")
                continue
            if ret.ok:
                break
            else:
                time.sleep(retry_count)
                ret = None
        if ret is not None:
            ret.raise_for_status()
            with open(save_file, "wb") as f:
                for chunk in ret.iter_content(chunk_size=8192):
                    f.write(chunk)
            ret.close()

    def _dump_parameter(self, parameter):
        j = json.dumps(parameter)
        return base64.b64encode(j.encode()).decode()

    def decode_base64(self, encode_data):
        data = json.loads(base64.b64decode(encode_data).decode("utf-8"))
        return data

    def iterate(self, header: dict = {}, body: dict = {}):
        uri = "/api/iterate"
        response = self.client.post(uri, headers=header, json=body)
        return APIResponse(response).json

    def _parse_ap_name_and_tag(self, input_path: str):
        input_path_arr = input_path.split("/")
        if len(input_path_arr) < 3:
            return "", "".input_path_arr
        return input_path_arr[0], input_path_arr[1], "/".join(input_path_arr[2:])


class Chunk:
    Number: int
    Offset: int
    Size: int


def split_size_by_part_size(total_size: int, chunk_size: int):
    if chunk_size < _DEFAULT_CHUNK_SIZE:
        chunk_size = _DEFAULT_CHUNK_SIZE
    chunk_number = int(total_size / chunk_size)
    if chunk_number >= 10000:
        raise TooManyChunk
    chunks = []
    for i in range(chunk_number):
        c = Chunk()
        c.Number = i + 1
        c.Offset = i * chunk_size
        c.Size = chunk_size
        chunks.append(c)

    if total_size % chunk_size > 0:
        c = Chunk()
        c.Number = len(chunks) + 1
        c.Offset = len(chunks) * chunk_size
        c.Size = total_size % chunk_size
        chunks.append(c)
    return chunks


def partial_with_start_from(start_bytes):
    return f"bytes={start_bytes}-"


def partial_with_end_from(end_bytes):
    return f"bytes=-{end_bytes}"


def partial_with_range(start_bytes, end_bytes):
    return f"bytes={start_bytes}-{end_bytes}"


TooManyChunk = Exception("too many chunks, please consider increase your chunk size")

import logging
import os
import uuid
from pathlib import Path
from typing import Optional, Union
from unittest import result

from bohrium_open_sdk.opensdk._exceptions import NotFoundError
from bohrium_open_sdk.opensdk._resource import SyncAPIResource
from bohrium_open_sdk.opensdk._response import APIResponse
from bohrium_open_sdk.opensdk._tiefblue_client import Tiefblue
from bohrium_open_sdk.opensdk.types.job.job import JobAddRequest
from bohrium_open_sdk.opensdk._base_client import APIResponseManager


logger = logging.getLogger(__name__)


class Job(SyncAPIResource):

    def detail(self, job_id):
        with APIResponseManager(self._client.get) as api:
            uri = f"/{self._client.api_prefix}/v1/job/{job_id}"
            response = api.get_response(uri)
            return APIResponse(response).json

    def list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        query_type: str = "all",
        star: Optional[int] = None,
        version: Optional[int] = 2,
        job_group_search_key: Optional[int] = None,
        group_id: Optional[int] = None,
    ):
        with APIResponseManager(self._client.get) as api:
            # submit_user_id = os.getenv("USER_ID")
            # if not submit_user_id:
                # raise ValueError("user id is required")
            uri = f"/{self._client.api_prefix}/v1/job/list"
            params = {
                "page": page,
                "pageSize": page_size,
                "queryType": query_type,
                # "submitUserId": submit_user_id,
            }
            star and params.update({"star": star})
            version and params.update({"version": version})
            job_group_search_key and params.update({"jobGroupSearchKey": job_group_search_key})
            group_id and params.update({"groupId": group_id})

            response = api.get_response(uri, params=params)
            return APIResponse(response).json
        
        
    def submit(
        self,
        *,
        project_id: int,
        job_name: str,
        machine_type: str,
        cmd: str,
        image_address: str,
        job_group_id: int = 0,
        work_dir: Union[str, Path] = "",
        dataset_path: list = [],
        log_files: list = [],
        out_files: list = [],
    ):
        data = self.create_job(project_id, job_name, job_group_id)
        if not data:
            raise NotFoundError("Create job failed")
        if work_dir != "":
            work_dir = Path(work_dir)
            if not work_dir.exists():
                raise FileNotFoundError
            if work_dir.is_dir():
                self.upload_dir(work_dir, data.get("storePath"), data.get("token"))
            else:
                file_name = work_dir.name
                object_key = data.get("storePath") / file_name
                self.upload(work_dir, object_key, data.get("token"))

        # FIXME: download_path
        # ep = os.path.expanduser(result)
        # p = Path(ep).absolute().resolve()
        # p = p.joinpath(str(uuid.uuid4()) + "_temp.zip")

        job_add_request = JobAddRequest(
            # download_path=str(p.absolute().resolve()),
            dataset_path=dataset_path,
            job_name=job_name,
            project_id=project_id,
            job_id=data["jobId"],
            oss_path=data["storePath"],
            image_name=image_address,
            scass_type=machine_type,
            cmd=cmd,
            log_files=log_files,
            out_files=out_files,
        )
        return self.insert(job_add_request.to_dict())

    def insert(self, data):
        with APIResponseManager(self._client.post) as api:
            uri = f"/{self._client.api_prefix}/v2/job/add"
            response = api.get_response(uri, json=data)
            return APIResponse(response).json


    def delete(self, job_id):
        with APIResponseManager(self._client.post) as api:
            uri = f"/{self._client.api_prefix}/v1/job/del/{job_id}"
            response = api.get_response(uri)
            return APIResponse(response).json

    def terminate(self, job_id):
        with APIResponseManager(self._client.post) as api:
            uri = f"/{self._client.api_prefix}/v1/job/terminate/{job_id}"
            response = api.get_response(uri)
            return APIResponse(response).json

    def kill(self, job_id):
        with APIResponseManager(self._client.post) as api:
            uri = f"/{self._client.api_prefix}/v1/job/kill/{job_id}"
            response = api.get_response(uri)
            return APIResponse(response).json

    def log(self, job_id, log_file="STDOUTERR", page=-1, page_size=8192):
        with APIResponseManager(self._client.get) as api:
            uri = f"/{self._client.api_prefix}/v1/job/{job_id}/log"
            response = api.get_response(
                uri,
                params={"logFile": log_file, "page": page, "pageSize": page_size},
            )
            return APIResponse(response).json

    def create_job(
        self,
        project_id: int,
        name: Optional[str] = None,
        group_id: Optional[int] = 0,
    ):
        with APIResponseManager(self._client.post) as api:
            uri = f"/{self._client.api_prefix}/v1/job/create"
            data = {
                "projectId": project_id,
                "name": name,
                "bohrGroupId": group_id,
            }
            response = api.get_response(uri, json=data)
            return APIResponse(response).data

    def create_job_group(self, project_id, job_group_name):
        with APIResponseManager(self._client.post) as api:
            uri = f"/{self._client.api_prefix}/v1/job_group/add"
            response = api.get_response(
                uri,
                json={"name": job_group_name, "projectId": project_id},
            )

            return APIResponse(response).json

    def upload(
        self,
        file_path: str,
        object_key: str,
        token: str,
    ):
        tiefblue = Tiefblue()
        custom_headers = {"Authorization": f"Bearer {token}"}

        tiefblue.upload_from_file_multi_part(
            object_key=object_key,
            custom_headers=custom_headers,
            file_path=file_path,
            progress_bar=True,
        )

    def upload_dir(self, work_dir: Union[str, Path], store_path: str, token: str):
        if not store_path:
            raise ValueError("store_path is required")
        if not token:
            raise ValueError("token is required")
        work_dir = str(work_dir)
        # TODO: upload rule
        if not work_dir.endswith("/"):
            work_dir = work_dir + "/"
        for root, _, files in os.walk(work_dir):
            for file in files:
                full_path = os.path.join(root, file)
                object_key = full_path.replace(work_dir, store_path)
                self.upload(full_path, object_key, token)

    def download(self, job_id: int, save_path: Union[str, Path]):
        save_path = Path(save_path)
        detail = self.detail(job_id)

        result_url = detail.get("data", {}).get("resultUrl")

        if not result_url:
            raise NotFoundError("Result url not found")

        if not save_path.parent.exists():
            save_path.parent.mkdir(parents=True, exist_ok=True)

        logger.debug(
            f"Downloading job {job_id} to {save_path}, result url: {result_url}"
        )

        tiefblue = Tiefblue()
        tiefblue.download_from_url(result_url, save_path)
        return True

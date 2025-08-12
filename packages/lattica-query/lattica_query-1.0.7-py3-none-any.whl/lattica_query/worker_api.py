import json
import time
from typing import Optional, TypeAlias, Dict

from lattica_common.app_api import ClientVersionError
from lattica_common.version_utils import get_module_info
import requests
import torch

from lattica_common import http_settings
from lattica_query.serialization.api_serialization_utils import (
    load_proto_tensor,
    dumps_proto_tensor,
)

ClientPtTensor: TypeAlias = torch.Tensor

"""
IMPLEMENTATION OF API CALLS TO A REMOTE WORKER
every API call should adhere to the following:
api params
    action      the name of the api action
    params      a json struct 

response structure containing either:
    result          the payload execution result
    executionId     the ID of the api call execution when it takes long to
                    return a result 
    error           the execution error
"""

WorkerResponse: TypeAlias = bytes | None


class WorkerHttpClient:
    def __init__(self, query_token: str):
        self.query_token = query_token
        # Determine the module version we're being called from
        self.module_name = "lattica_query"
        self.module_version = get_module_info('lattica_query')
        self.timing = ""
        self.query_id: Optional[str] = None

    def send_multipart_request(
        self,
        action_name: str,
        action_params: Optional[dict] = None,
        serialized_data: Optional[bytes] = None,
        with_polling: Optional[bool] = True,
    ) -> WorkerResponse:
        start = time.perf_counter()
        api_call_payload = {
            "action": action_name,
            "params": action_params if action_params else {},
        }

        if self.query_id is not None:
            api_call_payload["queryId"] = self.query_id

        req_data = {
            "api_call": api_call_payload,
            "client_info": {"module": self.module_name, "version": self.module_version},
        }
        req_data.update(http_settings.get_api_body())

        response = requests.post(
            http_settings.get_api_url(),
            headers={"Authorization": f"Bearer {self.query_token}"},
            data={"metadata": json.dumps(req_data)},
            files={"file": ("data.bin", serialized_data, "application/octet-stream")},
        )
        duration = time.perf_counter() - start

        if not response.ok:
            error_info = response.json()
            if error_info.get("error_code") == "CLIENT_VERSION_INCOMPATIBLE":
                raise ClientVersionError(
                    error_info.get("error"), error_info.get("min_version")
                )
            else:  # general exception
                raise Exception(f"FAILED api/{action_name} with error: {response.text}")

        self.timing = f'network;dur={int(duration * 1000)}, {response.headers.get("Server-Timing")}'

        content_type = response.headers.get("Content-Type")

        if content_type.startswith("application/octet-stream"):
            self.query_id = response.headers.get("x-query-id", None)
            print(f'{action_name} timing: {self.timing}')
            return response.content
        elif content_type.startswith("application/json"):
            response_json = response.json()
            print(f'{action_name}: {response_json.get("status")}')

            if response_json.get("status") == "RUNNING" and with_polling:
                return self._resample_result(response_json["executionId"])

            if response_json.get("status") == "ERROR":
                raise Exception(
                    f'FAILED api/{action_name} with error: {response_json.get("error")}'
                )

            print(f'{action_name} timing: {self.timing}')  # only for COMPLETE action
            return None
        else:
            raise Exception(f"Unsupported content type: {content_type}")

    def _resample_result(self, execution_id: str) -> WorkerResponse:
        """Query the status of a previously triggered action."""
        print(f"Polling for executionId: {execution_id}")
        if not execution_id:  # TODO: prevent worker from returning executionId = 0
            return None
        time.sleep(1)
        return self.send_multipart_request(
            "get_action_result", action_params={"executionId": execution_id}
        )


class LatticaWorkerAPI:
    def __init__(self, query_token: str):
        self.http_client = WorkerHttpClient(query_token)

    def get_last_timing(self) -> str:
        return self.http_client.timing

    def get_user_init_data(self) -> bytes:
        return self.http_client.send_multipart_request("get_user_init_data")

    def preprocess_pk(self) -> None:
        self.http_client.send_multipart_request("preprocess_pk")

    def apply_hom_pipeline(
        self,
        serialized_ct: bytes,
        block_index: int,
        return_new_state: Optional[bool] = False,
    ) -> bytes:
        print(f"ct size: {len(serialized_ct) / 1024 ** 2}MB")
        return self.http_client.send_multipart_request(
            "apply_hom_pipeline",
            action_params={
                "block_index": block_index,
                "return_new_state": return_new_state,
            },
            serialized_data=serialized_ct,
        )

    def apply_clear(self, pt: "ClientPtTensor") -> "ClientPtTensor":
        res = self.http_client.send_multipart_request(
            "apply_clear", serialized_data=dumps_proto_tensor(pt)
        )
        return load_proto_tensor(res)

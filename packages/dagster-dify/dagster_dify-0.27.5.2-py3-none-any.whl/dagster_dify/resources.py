import io
import json
import os
from typing import List, Dict, Literal, Union, Optional

import httpx
from dagster import ConfigurableResource, OpExecutionContext, AssetExecutionContext, ExpectationResult
from pydantic import Field, BaseModel


class FileInput(BaseModel):
    type: Literal["document", "image", "audio", "video", "custom"]
    transfer_method: Literal["remote_url", "local_file"]
    url: Optional[str] = None
    upload_file_id: Optional[str] = None

FileInputs = Union[FileInput, List[FileInput], Dict[str, str], List[Dict[str, str]]]


class DifyResource(ConfigurableResource):
    """
[Dify API](https://docs.dify.ai/zh-hans/guides/application-publishing/developing-with-apis)
    """

    BaseURL: str = Field(description="Example: https://<your-domain>/v1")

    def dify_workflow_stream(
            self,
            token: str,
            inputs: Dict[str, str|FileInputs],
            user: str = "dagster",
            trace_id: str = None,
            context: OpExecutionContext | AssetExecutionContext = None
    ) -> Dict:
        llm_workflow_output: Dict|None = None

        app_info = self.app_info(token)

        headers = {'Authorization': f'Bearer {token}',}
        if trace_id:
            headers['X-Trace-Id'] = trace_id

        with httpx.Client() as client:
            with client.stream(
                    method="POST",
                    url=f"{self.BaseURL}/workflows/run",
                    headers=headers,
                    json={"inputs": inputs, "response_mode": "streaming", "user": user}
            ) as response:
                node_cache = {}
                for line in response.iter_lines():
                    if line.startswith("data:"):
                        event_data = json.loads(line[len("data:"):].strip())
                        event = event_data.get('event')

                        task_id = event_data.get('task_id')
                        workflow_run_id = event_data.get('workflow_run_id')
                        data = event_data.get('data', {})
                        status = data.get('status')
                        error = data.get('error')

                        node_index = data.get('index')

                        log_label = f"DIFY_{event}".upper()
                        log_metadata = {"task_id": task_id, "workflow_run_id": workflow_run_id}

                        match event:
                            case "workflow_started":
                                log_success = True
                                log_description = F"{log_label}: Task Started."
                                log_metadata: dict = log_metadata | app_info.model_dump()
                            case "node_started":
                                log_metadata: dict = log_metadata | {
                                    "node_title": data.get('title'),
                                    "node_id": data.get('node_id'),
                                    "node_type": data.get('node_type'),
                                    "node_index": node_index,
                                    "predecessor_node_id": data.get('predecessor_node_id'),
                                    "inputs": data.get('inputs'),
                                }
                                node_cache[str(node_index)] = data.get('title')
                                log_success = True
                                log_description = F"{log_label}: Node{node_index} [{data.get('title')}] started."
                            case "node_finished":
                                log_metadata: dict = log_metadata | {
                                    "node_title": node_cache.get(str(node_index)),
                                    "error": error,
                                    "elapsed_time": data.get('elapsed_time'),
                                } | (data.get('execution_metadata', {}) or {}) | {
                                    "node_id": data.get('node_id'),
                                    "node_index": node_index,
                                    "predecessor_node_id": data.get('predecessor_node_id'),
                                    "outputs": data.get('outputs'),
                                }
                                log_description = F"{log_label}: Task {task_id} node{node_index} {status}."
                                log_success = True if status in ["succeeded", "running"] else False
                            case "workflow_finished":
                                log_metadata = log_metadata | {
                                    "error": data.get('error'),
                                    "elapsed_time": data.get('elapsed_time'),
                                    "total_tokens": data.get('total_tokens'),
                                    "total_steps": data.get('total_steps'),
                                    "outputs": data.get('outputs'),
                                }
                                log_description = F"{log_label}: Task {status}."
                                log_success = True if status in ["succeeded", "running"] else False

                                llm_workflow_output = data.get("outputs", {})
                        if context:
                            context.log_event(ExpectationResult(
                                success=log_success,
                                label=log_label,
                                description=log_description,
                                metadata=log_metadata,
                            ))

        return llm_workflow_output


    def upload_file(
            self,
            token: str,
            file_name: Optional[str],
            file_path: Optional[str] = None,
            file_bytes: Optional[bytes] = None,
            user: str = "dagster"
    ):
        if not file_name:
            file_name = os.path.basename(file_path)

        if file_bytes is not None:
            with io.BytesIO(file_bytes) as file:
                res = httpx.post(
                    f"{self.BaseURL}/files/upload",
                    files={"file": (file_name, file)},
                    json={"user": user},
                    headers={"Authorization": f"Bearer {token}"},
                ).json()
                return res
        elif file_path is not None:
            with open(file_path, "rb") as file:
                res = httpx.post(
                    f"{self.BaseURL}/files/upload",
                    files={"file": (file_name, file)},
                    json={"user": user},
                    headers={"Authorization": f"Bearer {token}"},
                ).json()
                return res
        else:
            raise "At least one of file_path or file_bytes should be provided."

    def app_info(self, token: str):
        res = httpx.get(
            f"{self.BaseURL}/info",
            headers={"Authorization": f"Bearer {token}"},
        ).json()
        return AppInfo(**res)

    def webapp_info(self, token: str):
        res = httpx.get(
            f"{self.BaseURL}/site",
            headers={"Authorization": f"Bearer {token}"},
        ).json()
        return WebAppInfo(**res)


class AppInfo(BaseModel):
    name: str
    description: str
    tags: List[str]
    mode: str
    author_name: str


class WebAppInfo(BaseModel):
    title: str
    icon_type: str
    icon: str
    icon_background: str
    icon_url: str
    description: str
    copyright: str
    privacy_policy: str
    custom_disclaimer: str
    default_language: str
    show_workflow_steps: str

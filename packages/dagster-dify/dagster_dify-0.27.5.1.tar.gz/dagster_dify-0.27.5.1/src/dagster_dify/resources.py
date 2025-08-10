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

### 配置项:

- **AppID** (str):
    应用应用唯一标识 AppID，作为缓存标识符使用。不传入则不缓存鉴权。
- **AgentID** (int, optional):
    原企业内部应用 AgentId ，部分 API 会使用到。默认值为 None
- **AppName** (str, optional):
    应用名。
- **ClientId** (str):
    应用的 Client ID ，原 AppKey 和 SuiteKey
- **ClientSecret** (str):
    应用的 Client Secret ，原 AppSecret 和 SuiteSecret

### 用例

##### 1. 使用单一的企业内部应用资源。

```python
from dagster_dingtalk import DingTalkAppResource, DingTalkAppClient
from dagster import op, In, OpExecutionContext, job, Definitions, EnvVar

@op(required_resource_keys={"dingtalk"}, ins={"user_id": In(str)})
def op_user_info(context:OpExecutionContext, user_id:str):
    dingtalk:DingTalkAppClient = context.resources.dingtalk
    result = dingtalk.通讯录管理.用户管理.查询用户详情(user_id).get('result')
    context.log.info(result)

@job
def job_user_info():
    op_user_info()

defs = Definitions(
    jobs=[job_user_info],
    resources={"dingtalk": DingTalkAppResource(
        AppID = "<the-app-id>",
        ClientId = "<the-client-id>",
        ClientSecret = EnvVar("<the-client-secret-env-name>"),
    )})
```

##### 2. 启动时动态构建企业内部应用资源, 可参考 [Dagster文档 | 在启动时配置资源](https://docs.dagster.io/concepts/resources#configuring-resources-at-launch-time)

```python
from dagster_dingtalk import DingTalkAppResource, DingTalkAppClient
from dagster import op, In, OpExecutionContext, job, Definitions, schedule, RunRequest, RunConfig, EnvVar

@op(required_resource_keys={"dingtalk"}, ins={"user_id": In(str)})
def op_user_info(context:OpExecutionContext, user_id:str):
    dingtalk:DingTalkAppClient = context.resources.dingtalk
    result = dingtalk.通讯录管理.用户管理.查询用户详情(user_id).get('result')
    context.log.info(result)

@job
def job_user_info():
    op_user_info()

dingtalk_apps = {
    "App1" : DingTalkAppResource(
        AppID = "<app-1-app-id>",
        ClientId = "<app-1-client-id>",
        ClientSecret = EnvVar("<app-1-client-secret-env-name>"),
    ),
    "App2" : DingTalkAppResource(
        AppID = "<app-2-app-id>",
        ClientId = "<app-2-client-id>",
        ClientSecret = EnvVar("<app-2-client-secret-env-name>"),
    )
}

defs = Definitions(jobs=[job_user_info], resources={"dingtalk": DingTalkAppResource.configure_at_launch()})

@schedule(cron_schedule="20 9 * * *", job=job_user_info)
def schedule_user_info():
    return RunRequest(run_config=RunConfig(
        ops={"op_user_info": {"inputs": {"user_id": "<the-user-id>"}}},
        resources={"dingtalk": dingtalk_apps["App1"]},
    ))
```

### 注意:

应该永远避免直接将密钥字符串直接配置给资源，这会导致在 dagster 前端用户界面暴露密钥。你可以在代码中注册临时的环境变量，或从系统中引入环境变量。
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
                    json={"inputs": inputs, "response_mode": "streaming", "user": user},
                    timeout=60000,
            ) as response:
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
                        node_title = data.get('title')

                        log_label = f"DIFY_{event}".upper()
                        log_metadata = {"task_id": task_id, "workflow_run_id": workflow_run_id}

                        match event:
                            case "workflow_started":
                                log_success = True
                                log_description = F"{log_label}: Task Started."
                                log_metadata: dict = log_metadata | app_info.model_dump()
                            case "node_started":
                                log_metadata: dict = log_metadata | {
                                    "node_id": data.get('node_id'),
                                    "node_type": data.get('node_type'),
                                    "node_title": node_title,
                                    "node_index": node_index,
                                    "predecessor_node_id": data.get('predecessor_node_id'),
                                    "inputs": data.get('inputs'),
                                }
                                log_success = True
                                log_description = F"{log_label}: Node{node_index} started."
                            case "node_finished":
                                log_metadata: dict = log_metadata | {
                                    "node_id": data.get('node_id'),
                                    "node_index": node_index,
                                    "elapsed_time": data.get('elapsed_time'),
                                    "predecessor_node_id": data.get('predecessor_node_id'),
                                    "outputs": data.get('outputs'),
                                    "error": error,
                                } | (data.get('execution_metadata', {}) or {})
                                log_description = F"{log_label}: Task {task_id} node{node_index} {status}."
                                log_success = True if status in ["succeeded", "running"] else False
                            case "workflow_finished":
                                log_metadata = log_metadata | {
                                    "outputs": data.get('outputs'),
                                    "error": data.get('error'),
                                    "elapsed_time": data.get('elapsed_time'),
                                    "total_tokens": data.get('total_tokens'),
                                    "total_steps": data.get('total_steps'),
                                }
                                log_description = F"{log_label}: Task {status}."
                                log_success = True if status in ["succeeded", "running"] else False

                                llm_workflow_output = data.get("outputs", {})

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

"""VectorVein API data model definitions"""

from dataclasses import dataclass
from typing import Any


@dataclass
class VApp:
    """VApp information"""

    app_id: str
    title: str
    description: str
    info: dict[str, Any]
    images: list[str]


@dataclass
class AccessKey:
    """Access key information"""

    access_key: str
    access_key_type: str  # O: one-time, M: multiple, L: long-term
    use_count: int
    max_use_count: int | None
    max_credits: int | None
    used_credits: int
    v_app: VApp | None
    v_apps: list[VApp]
    records: list[Any]
    status: str  # AC: valid, IN: invalid, EX: expired, US: used
    access_scope: str  # S: single application, M: multiple applications
    description: str
    create_time: str
    expire_time: str
    last_use_time: str | None


@dataclass
class WorkflowInputField:
    """Workflow input field"""

    node_id: str
    field_name: str
    value: Any


@dataclass
class WorkflowOutput:
    """Workflow output result"""

    type: str
    title: str
    value: Any


@dataclass
class WorkflowRunResult:
    """Workflow run result"""

    rid: str
    status: int
    msg: str
    data: list[WorkflowOutput]


@dataclass
class AccessKeyListResponse:
    """Access key list response"""

    access_keys: list[AccessKey]
    total: int
    page_size: int
    page: int

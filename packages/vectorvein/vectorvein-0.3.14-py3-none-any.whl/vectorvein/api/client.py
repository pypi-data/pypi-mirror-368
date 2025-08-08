"""VectorVein API Client"""

import time
import base64
import asyncio
from urllib.parse import quote
from typing import Any, Literal, overload

import httpx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from .exceptions import (
    VectorVeinAPIError,
    APIKeyError,
    WorkflowError,
    AccessKeyError,
    RequestError,
    TimeoutError,
)
from .models import (
    AccessKey,
    WorkflowInputField,
    WorkflowOutput,
    WorkflowRunResult,
    AccessKeyListResponse,
)


class VectorVeinClient:
    """VectorVein API Sync Client"""

    API_VERSION = "20240508"
    BASE_URL = "https://vectorvein.com/api/v1/open-api"

    def __init__(self, api_key: str, base_url: str | None = None):
        """Initialize the client

        Args:
            api_key: API key
            base_url: API base URL, default is https://vectorvein.com/api/v1/open-api

        Raises:
            APIKeyError: API key is empty or not a string
        """
        if not api_key or not isinstance(api_key, str):
            raise APIKeyError("API key cannot be empty and must be a string type")

        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.default_headers = {
            "VECTORVEIN-API-KEY": api_key,
            "VECTORVEIN-API-VERSION": self.API_VERSION,
        }
        self._client = httpx.Client(timeout=60)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.close()

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        api_key_type: Literal["WORKFLOW", "VAPP"] = "WORKFLOW",
        **kwargs,
    ) -> dict[str, Any]:
        """Send HTTP request

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: URL parameters
            json: JSON request body
            **kwargs: Other request parameters

        Returns:
            Dict[str, Any]: API response

        Raises:
            RequestError: Request error
            VectorVeinAPIError: API error
            APIKeyError: API key is invalid or expired
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self.default_headers.copy()
        if api_key_type == "VAPP":
            headers["VECTORVEIN-API-KEY-TYPE"] = "VAPP"
        try:
            response = self._client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=headers,
                **kwargs,
            )
            result = response.json()

            if result["status"] in [401, 403]:
                raise APIKeyError("API key is invalid or expired")
            if result["status"] != 200 and result["status"] != 202:
                raise VectorVeinAPIError(message=result.get("msg", "Unknown error"), status_code=result["status"])
            return result
        except httpx.HTTPError as e:
            raise RequestError(f"Request failed: {str(e)}") from e

    @overload
    def run_workflow(
        self,
        wid: str,
        input_fields: list[WorkflowInputField],
        output_scope: Literal["all", "output_fields_only"] = "output_fields_only",
        wait_for_completion: Literal[False] = False,
        api_key_type: Literal["WORKFLOW", "VAPP"] = "WORKFLOW",
        timeout: int = 30,
    ) -> str: ...

    @overload
    def run_workflow(
        self,
        wid: str,
        input_fields: list[WorkflowInputField],
        output_scope: Literal["all", "output_fields_only"] = "output_fields_only",
        wait_for_completion: Literal[True] = True,
        api_key_type: Literal["WORKFLOW", "VAPP"] = "WORKFLOW",
        timeout: int = 30,
    ) -> WorkflowRunResult: ...

    def run_workflow(
        self,
        wid: str,
        input_fields: list[WorkflowInputField],
        output_scope: Literal["all", "output_fields_only"] = "output_fields_only",
        wait_for_completion: bool = False,
        api_key_type: Literal["WORKFLOW", "VAPP"] = "WORKFLOW",
        timeout: int = 30,
    ) -> str | WorkflowRunResult:
        """Run workflow

        Args:
            wid: Workflow ID
            input_fields: Input fields list
            output_scope: Output scope, optional values: 'all' or 'output_fields_only'
            wait_for_completion: Whether to wait for completion
            api_key_type: Key type, optional values: 'WORKFLOW' or 'VAPP'
            timeout: Timeout (seconds)

        Returns:
            Union[str, WorkflowRunResult]: Workflow run ID or run result

        Raises:
            WorkflowError: Workflow run error
            TimeoutError: Timeout error
        """
        payload = {
            "wid": wid,
            "output_scope": output_scope,
            "wait_for_completion": wait_for_completion,
            "input_fields": [{"node_id": field.node_id, "field_name": field.field_name, "value": field.value} for field in input_fields],
        }

        result = self._request("POST", "workflow/run", json=payload, api_key_type=api_key_type)

        if not wait_for_completion:
            return result["data"]["rid"]

        rid = result.get("rid") or (isinstance(result["data"], dict) and result["data"].get("rid")) or ""
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Workflow execution timed out after {timeout} seconds")

            if api_key_type == "WORKFLOW":
                result = self.check_workflow_status(rid, api_key_type=api_key_type)
            else:
                result = self.check_workflow_status(rid, wid=wid, api_key_type=api_key_type)
            if result.status == 200:
                return result
            elif result.status == 500:
                raise WorkflowError(f"Workflow execution failed: {result.msg}")

            time.sleep(5)

    @overload
    def check_workflow_status(self, rid: str, wid: str | None = None, api_key_type: Literal["WORKFLOW"] = "WORKFLOW") -> WorkflowRunResult: ...

    @overload
    def check_workflow_status(self, rid: str, wid: str, api_key_type: Literal["VAPP"] = "VAPP") -> WorkflowRunResult: ...

    def check_workflow_status(self, rid: str, wid: str | None = None, api_key_type: Literal["WORKFLOW", "VAPP"] = "WORKFLOW") -> WorkflowRunResult:
        """Check workflow run status

        Args:
            rid: Workflow run record ID
            wid: Workflow ID, not required, required when api_key_type is 'VAPP'
            api_key_type: Key type, optional values: 'WORKFLOW' or 'VAPP'

        Returns:
            WorkflowRunResult: Workflow run result

        Raises:
            VectorVeinAPIError: Workflow error
        """
        payload = {"rid": rid}
        if api_key_type == "VAPP" and not wid:
            raise VectorVeinAPIError("Workflow ID cannot be empty when api_key_type is 'VAPP'")
        if wid:
            payload["wid"] = wid
        response = self._request("POST", "workflow/check-status", json=payload, api_key_type=api_key_type)
        if response["status"] in [200, 202]:
            return WorkflowRunResult(
                rid=rid,
                status=response["status"],
                msg=response["msg"],
                data=[WorkflowOutput(**output) for output in response["data"]],
            )
        else:
            raise WorkflowError(f"Workflow execution failed: {response['msg']}")

    def get_access_keys(self, access_keys: list[str] | None = None, get_type: Literal["selected", "all"] = "selected") -> list[AccessKey]:
        """Get access key information

        Args:
            access_keys: Access key list
            get_type: Get type, optional values: 'selected' or 'all'

        Returns:
            List[AccessKey]: Access key information list

        Raises:
            AccessKeyError: Access key does not exist or has expired
        """
        params = {"get_type": get_type}
        if access_keys:
            params["access_keys"] = ",".join(access_keys)

        try:
            result = self._request("GET", "vapp/access-key/get", params=params)
            return [AccessKey(**key) for key in result["data"]]
        except VectorVeinAPIError as e:
            if e.status_code == 404:
                raise AccessKeyError("Access key does not exist") from e
            elif e.status_code == 403:
                raise AccessKeyError("Access key has expired") from e
            raise

    def create_access_keys(
        self,
        access_key_type: Literal["O", "M", "L"],
        app_id: str | None = None,
        app_ids: list[str] | None = None,
        count: int = 1,
        expire_time: str | None = None,
        max_credits: int | None = None,
        max_use_count: int | None = None,
        description: str | None = None,
    ) -> list[AccessKey]:
        """Create access key

        Args:
            access_key_type: Key type, optional values: 'O'(one-time)、'M'(multiple)、'L'(long-term)
            app_id: Single application ID
            app_ids: Multiple application ID list
            count: Create quantity
            expire_time: Expiration time
            max_credits: Maximum credit limit
            max_use_count: Maximum use count
            description: Description information

        Returns:
            List[AccessKey]: Created access key list

        Raises:
            AccessKeyError: Failed to create access key, such as invalid type, application does not exist, etc.
        """
        if access_key_type not in ["O", "M", "L"]:
            raise AccessKeyError("Invalid access key type, must be 'O'(one-time)、'M'(multiple) or 'L'(long-term)")

        if app_id and app_ids:
            raise AccessKeyError("Cannot specify both app_id and app_ids")

        payload = {"access_key_type": access_key_type, "count": count}

        if app_id:
            payload["app_id"] = app_id
        if app_ids:
            payload["app_ids"] = app_ids
        if expire_time:
            payload["expire_time"] = expire_time
        if max_credits is not None:
            payload["max_credits"] = max_credits
        if max_use_count is not None:
            payload["max_use_count"] = max_use_count
        if description:
            payload["description"] = description

        try:
            result = self._request("POST", "vapp/access-key/create", json=payload)
            return [AccessKey(**key) for key in result["data"]]
        except VectorVeinAPIError as e:
            if e.status_code == 404:
                raise AccessKeyError("The specified application does not exist") from e
            elif e.status_code == 403:
                raise AccessKeyError("No permission to create access key") from e
            raise

    def list_access_keys(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_field: str = "create_time",
        sort_order: str = "descend",
        app_id: str | None = None,
        status: list[str] | None = None,
        access_key_type: Literal["O", "M", "L"] | None = None,
    ) -> AccessKeyListResponse:
        """List access keys

        Args:
            page: Page number
            page_size: Number of items per page
            sort_field: Sort field
            sort_order: Sort order
            app_id: Application ID
            status: Status list
            access_key_type: Key type list, optional values: 'O'(one-time)、'M'(multiple)、'L'(long-term)

        Returns:
            AccessKeyListResponse: Access key list response
        """
        payload = {"page": page, "page_size": page_size, "sort_field": sort_field, "sort_order": sort_order}

        if app_id:
            payload["app_id"] = app_id
        if status:
            payload["status"] = status
        if access_key_type:
            payload["access_key_type"] = access_key_type

        result = self._request("POST", "vapp/access-key/list", json=payload)
        return AccessKeyListResponse(**result["data"])

    def delete_access_keys(self, app_id: str, access_keys: list[str]) -> None:
        """Delete access key

        Args:
            app_id: Application ID
            access_keys: List of access keys to delete
        """
        payload = {"app_id": app_id, "access_keys": access_keys}
        self._request("POST", "vapp/access-key/delete", json=payload)

    def update_access_keys(
        self,
        access_key: str | None = None,
        access_keys: list[str] | None = None,
        app_id: str | None = None,
        app_ids: list[str] | None = None,
        expire_time: str | None = None,
        max_use_count: int | None = None,
        max_credits: int | None = None,
        description: str | None = None,
        access_key_type: Literal["O", "M", "L"] | None = None,
    ) -> None:
        """Update access key

        Args:
            access_key: Single access key
            access_keys: Multiple access key list
            app_id: Single application ID
            app_ids: Multiple application ID list
            expire_time: Expiration time
            max_use_count: Maximum use count
            max_credits: Maximum credit limit
            description: Description information
            access_key_type: Key type, optional values: 'O'(one-time)、'M'(multiple)、'L'(long-term)
        """
        payload = {}
        if access_key:
            payload["access_key"] = access_key
        if access_keys:
            payload["access_keys"] = access_keys
        if app_id:
            payload["app_id"] = app_id
        if app_ids:
            payload["app_ids"] = app_ids
        if expire_time:
            payload["expire_time"] = expire_time
        if max_use_count is not None:
            payload["max_use_count"] = max_use_count
        if max_credits is not None:
            payload["max_credits"] = max_credits
        if description:
            payload["description"] = description
        if access_key_type:
            payload["access_key_type"] = access_key_type

        self._request("POST", "vapp/access-key/update", json=payload)

    def add_apps_to_access_keys(self, access_keys: list[str], app_ids: list[str]) -> None:
        """Add applications to access keys

        Args:
            access_keys: Access key list
            app_ids: List of application IDs to add
        """
        payload = {"access_keys": access_keys, "app_ids": app_ids}
        self._request("POST", "vapp/access-key/add-apps", json=payload)

    def remove_apps_from_access_keys(self, access_keys: list[str], app_ids: list[str]) -> None:
        """Remove applications from access keys

        Args:
            access_keys: Access key list
            app_ids: List of application IDs to remove
        """
        payload = {"access_keys": access_keys, "app_ids": app_ids}
        self._request("POST", "vapp/access-key/remove-apps", json=payload)

    def generate_vapp_url(
        self,
        app_id: str,
        access_key: str,
        key_id: str,
        timeout: int = 15 * 60,
        base_url: str = "https://vectorvein.com",
    ) -> str:
        """Generate VApp access link

        Args:
            app_id: VApp ID
            access_key: Access key
            key_id: Key ID
            timeout: Timeout (seconds)
            base_url: Base URL

        Returns:
            str: VApp access link
        """
        timestamp = int(time.time())
        message = f"{app_id}:{access_key}:{timestamp}:{timeout}"
        encryption_key = self.api_key.encode()

        cipher = AES.new(encryption_key, AES.MODE_CBC)
        padded_data = pad(message.encode(), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        final_data = bytes(cipher.iv) + encrypted_data
        token = base64.b64encode(final_data).decode("utf-8")
        quoted_token = quote(token)

        return f"{base_url}/public/v-app/{app_id}?token={quoted_token}&key_id={key_id}"


class AsyncVectorVeinClient:
    """VectorVein API Async Client"""

    API_VERSION = "20240508"
    BASE_URL = "https://vectorvein.com/api/v1/open-api"

    def __init__(self, api_key: str, base_url: str | None = None):
        """Initialize the async client

        Args:
            api_key: API key
            base_url: API base URL, default is https://vectorvein.com/api/v1/open-api

        Raises:
            APIKeyError: API key is empty or not a string
        """
        if not api_key or not isinstance(api_key, str):
            raise APIKeyError("API key cannot be empty and must be a string type")

        self.api_key = api_key
        self.base_url = base_url or self.BASE_URL
        self.default_headers = {
            "VECTORVEIN-API-KEY": api_key,
            "VECTORVEIN-API-VERSION": self.API_VERSION,
        }
        self._client = httpx.AsyncClient(timeout=60)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        api_key_type: Literal["WORKFLOW", "VAPP"] = "WORKFLOW",
        **kwargs,
    ) -> dict[str, Any]:
        """Send asynchronous HTTP request

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: URL parameters
            json: JSON request body
            **kwargs: Other request parameters

        Returns:
            Dict[str, Any]: API response

        Raises:
            RequestError: Request error
            VectorVeinAPIError: API error
            APIKeyError: API key is invalid or expired
        """
        url = f"{self.base_url}/{endpoint}"
        headers = self.default_headers.copy()
        if api_key_type == "VAPP":
            headers["VECTORVEIN-API-KEY-TYPE"] = "VAPP"
        try:
            response = await self._client.request(
                method=method,
                url=url,
                params=params,
                json=json,
                headers=headers,
                **kwargs,
            )
            result = response.json()

            if result["status"] in [401, 403]:
                raise APIKeyError("API key is invalid or expired")
            if result["status"] != 200 and result["status"] != 202:
                raise VectorVeinAPIError(message=result.get("msg", "Unknown error"), status_code=result["status"])
            return result
        except httpx.HTTPError as e:
            raise RequestError(f"Request failed: {str(e)}") from e

    @overload
    async def run_workflow(
        self,
        wid: str,
        input_fields: list[WorkflowInputField],
        output_scope: Literal["all", "output_fields_only"] = "output_fields_only",
        wait_for_completion: Literal[False] = False,
        api_key_type: Literal["WORKFLOW", "VAPP"] = "WORKFLOW",
        timeout: int = 30,
    ) -> str: ...

    @overload
    async def run_workflow(
        self,
        wid: str,
        input_fields: list[WorkflowInputField],
        output_scope: Literal["all", "output_fields_only"] = "output_fields_only",
        wait_for_completion: Literal[True] = True,
        api_key_type: Literal["WORKFLOW", "VAPP"] = "WORKFLOW",
        timeout: int = 30,
    ) -> WorkflowRunResult: ...

    async def run_workflow(
        self,
        wid: str,
        input_fields: list[WorkflowInputField],
        output_scope: Literal["all", "output_fields_only"] = "output_fields_only",
        wait_for_completion: bool = False,
        api_key_type: Literal["WORKFLOW", "VAPP"] = "WORKFLOW",
        timeout: int = 30,
    ) -> str | WorkflowRunResult:
        """Async run workflow

        Args:
            wid: Workflow ID
            input_fields: Input field list
            output_scope: Output scope, optional values: 'all' or 'output_fields_only'
            wait_for_completion: Whether to wait for completion
            api_key_type: Key type, optional values: 'WORKFLOW' or 'VAPP'
            timeout: Timeout (seconds)

        Returns:
            Union[str, WorkflowRunResult]: Workflow run ID or run result

        Raises:
            WorkflowError: Workflow run error
            TimeoutError: Timeout error
        """
        payload = {
            "wid": wid,
            "output_scope": output_scope,
            "wait_for_completion": wait_for_completion,
            "input_fields": [{"node_id": field.node_id, "field_name": field.field_name, "value": field.value} for field in input_fields],
        }

        result = await self._request("POST", "workflow/run", json=payload, api_key_type=api_key_type)

        if not wait_for_completion:
            return result["data"]["rid"]

        rid = result.get("rid") or (isinstance(result["data"], dict) and result["data"].get("rid")) or ""
        start_time = time.time()

        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError(f"Workflow execution timed out after {timeout} seconds")

            if api_key_type == "WORKFLOW":
                result = await self.check_workflow_status(rid, api_key_type=api_key_type)
            else:
                result = await self.check_workflow_status(rid, wid=wid, api_key_type=api_key_type)
            if result.status == 200:
                return result
            elif result.status == 500:
                raise WorkflowError(f"Workflow execution failed: {result.msg}")

            await asyncio.sleep(5)

    @overload
    async def check_workflow_status(self, rid: str, wid: str | None = None, api_key_type: Literal["WORKFLOW"] = "WORKFLOW") -> WorkflowRunResult: ...

    @overload
    async def check_workflow_status(self, rid: str, wid: str, api_key_type: Literal["VAPP"] = "VAPP") -> WorkflowRunResult: ...

    async def check_workflow_status(self, rid: str, wid: str | None = None, api_key_type: Literal["WORKFLOW", "VAPP"] = "WORKFLOW") -> WorkflowRunResult:
        """Async check workflow run status

        Args:
            rid: Workflow run record ID
            wid: Workflow ID, required when api_key_type is 'VAPP'
            api_key_type: Key type, optional values: 'WORKFLOW' or 'VAPP'

        Raises:
            VectorVeinAPIError: Workflow error
        """
        payload = {"rid": rid}
        if api_key_type == "VAPP" and not wid:
            raise VectorVeinAPIError("Workflow ID cannot be empty when api_key_type is 'VAPP'")
        if wid:
            payload["wid"] = wid
        response = await self._request("POST", "workflow/check-status", json=payload, api_key_type=api_key_type)
        if response["status"] in [200, 202]:
            return WorkflowRunResult(
                rid=rid,
                status=response["status"],
                msg=response["msg"],
                data=[WorkflowOutput(**output) for output in response["data"]],
            )
        else:
            raise WorkflowError(f"Workflow execution failed: {response['msg']}")

    async def get_access_keys(self, access_keys: list[str] | None = None, get_type: Literal["selected", "all"] = "selected") -> list[AccessKey]:
        """Async get access key information

        Args:
            access_keys: Access key list
            get_type: Get type, optional values: 'selected' or 'all'

        Returns:
            List[AccessKey]: Access key information list

        Raises:
            AccessKeyError: Access key does not exist or has expired
        """
        params = {"get_type": get_type}
        if access_keys:
            params["access_keys"] = ",".join(access_keys)

        try:
            result = await self._request("GET", "vapp/access-key/get", params=params)
            return [AccessKey(**key) for key in result["data"]]
        except VectorVeinAPIError as e:
            if e.status_code == 404:
                raise AccessKeyError("Access key does not exist") from e
            elif e.status_code == 403:
                raise AccessKeyError("Access key has expired") from e
            raise

    async def create_access_keys(
        self,
        access_key_type: Literal["O", "M", "L"],
        app_id: str | None = None,
        app_ids: list[str] | None = None,
        count: int = 1,
        expire_time: str | None = None,
        max_credits: int | None = None,
        max_use_count: int | None = None,
        description: str | None = None,
    ) -> list[AccessKey]:
        """Async create access key

        Args:
            access_key_type: Key type, optional values: 'O'(one-time)、'M'(multiple)、'L'(long-term)
            app_id: Single application ID
            app_ids: Multiple application ID list
            count: Create quantity
            expire_time: Expiration time
            max_credits: Maximum credit limit
            max_use_count: Maximum use count
            description: Description

        Returns:
            List[AccessKey]: Created access key list

        Raises:
            AccessKeyError: Failed to create access key, such as invalid type, application does not exist, etc.
        """
        if access_key_type not in ["O", "M", "L"]:
            raise AccessKeyError("Invalid access key type, must be 'O'(one-time) or 'M'(multiple) or 'L'(long-term)")

        if app_id and app_ids:
            raise AccessKeyError("Cannot specify both app_id and app_ids")

        payload = {"access_key_type": access_key_type, "count": count}

        if app_id:
            payload["app_id"] = app_id
        if app_ids:
            payload["app_ids"] = app_ids
        if expire_time:
            payload["expire_time"] = expire_time
        if max_credits is not None:
            payload["max_credits"] = max_credits
        if max_use_count is not None:
            payload["max_use_count"] = max_use_count
        if description:
            payload["description"] = description

        try:
            result = await self._request("POST", "vapp/access-key/create", json=payload)
            return [AccessKey(**key) for key in result["data"]]
        except VectorVeinAPIError as e:
            if e.status_code == 404:
                raise AccessKeyError("The specified application does not exist") from e
            elif e.status_code == 403:
                raise AccessKeyError("No permission to create access key") from e
            raise

    async def list_access_keys(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_field: str = "create_time",
        sort_order: str = "descend",
        app_id: str | None = None,
        status: list[str] | None = None,
        access_key_type: Literal["O", "M", "L"] | None = None,
    ) -> AccessKeyListResponse:
        """Async list access keys

        Args:
            page: Page number
            page_size: Number of items per page
            sort_field: Sort field
            sort_order: Sort order
            app_id: Application ID
            status: Status list
            access_key_type: Key type list, optional values: 'O'(one-time)、'M'(multiple)、'L'(long-term)

        Returns:
            AccessKeyListResponse: Access key list response
        """
        payload = {"page": page, "page_size": page_size, "sort_field": sort_field, "sort_order": sort_order}

        if app_id:
            payload["app_id"] = app_id
        if status:
            payload["status"] = status
        if access_key_type:
            payload["access_key_type"] = access_key_type

        result = await self._request("POST", "vapp/access-key/list", json=payload)
        return AccessKeyListResponse(**result["data"])

    async def delete_access_keys(self, app_id: str, access_keys: list[str]) -> None:
        """Async delete access key

        Args:
            app_id: Application ID
            access_keys: List of access keys to delete
        """
        payload = {"app_id": app_id, "access_keys": access_keys}
        await self._request("POST", "vapp/access-key/delete", json=payload)

    async def update_access_keys(
        self,
        access_key: str | None = None,
        access_keys: list[str] | None = None,
        app_id: str | None = None,
        app_ids: list[str] | None = None,
        expire_time: str | None = None,
        max_use_count: int | None = None,
        max_credits: int | None = None,
        description: str | None = None,
        access_key_type: Literal["O", "M", "L"] | None = None,
    ) -> None:
        """Async update access key

        Args:
            access_key: Single access key
            access_keys: Multiple access key list
            app_id: Single application ID
            app_ids: Multiple application ID list
            expire_time: Expiration time
            max_use_count: Maximum use count
            max_credits: Maximum credit limit
            description: Description
            access_key_type: Key type, optional values: 'O'(one-time)、'M'(multiple)、'L'(long-term)
        """
        payload = {}
        if access_key:
            payload["access_key"] = access_key
        if access_keys:
            payload["access_keys"] = access_keys
        if app_id:
            payload["app_id"] = app_id
        if app_ids:
            payload["app_ids"] = app_ids
        if expire_time:
            payload["expire_time"] = expire_time
        if max_use_count is not None:
            payload["max_use_count"] = max_use_count
        if max_credits is not None:
            payload["max_credits"] = max_credits
        if description:
            payload["description"] = description
        if access_key_type:
            payload["access_key_type"] = access_key_type

        await self._request("POST", "vapp/access-key/update", json=payload)

    async def add_apps_to_access_keys(self, access_keys: list[str], app_ids: list[str]) -> None:
        """Async add applications to access keys

        Args:
            access_keys: Access key list
            app_ids: List of application IDs to add
        """
        payload = {"access_keys": access_keys, "app_ids": app_ids}
        await self._request("POST", "vapp/access-key/add-apps", json=payload)

    async def remove_apps_from_access_keys(self, access_keys: list[str], app_ids: list[str]) -> None:
        """Async remove applications from access keys

        Args:
            access_keys: Access key list
            app_ids: List of application IDs to remove
        """
        payload = {"access_keys": access_keys, "app_ids": app_ids}
        await self._request("POST", "vapp/access-key/remove-apps", json=payload)

    async def generate_vapp_url(
        self,
        app_id: str,
        access_key: str,
        key_id: str,
        timeout: int = 15 * 60,
        base_url: str = "https://vectorvein.com",
    ) -> str:
        """Async generate VApp access link

        Args:
            app_id: VApp ID
            access_key: Access key
            key_id: Key ID
            timeout: Timeout (seconds)
            base_url: Base URL

        Returns:
            str: VApp access link
        """
        timestamp = int(time.time())
        message = f"{app_id}:{access_key}:{timestamp}:{timeout}"
        encryption_key = self.api_key.encode()

        cipher = AES.new(encryption_key, AES.MODE_CBC)
        padded_data = pad(message.encode(), AES.block_size)
        encrypted_data = cipher.encrypt(padded_data)
        final_data = bytes(cipher.iv) + encrypted_data
        token = base64.b64encode(final_data).decode("utf-8")
        quoted_token = quote(token)

        return f"{base_url}/public/v-app/{app_id}?token={quoted_token}&key_id={key_id}"

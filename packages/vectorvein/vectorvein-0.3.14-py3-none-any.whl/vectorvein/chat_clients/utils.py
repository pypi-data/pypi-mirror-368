# @Author: Bi Ying
# @Date:   2024-07-26 14:48:55
import re
import json
import uuid
import warnings
from math import ceil
from collections.abc import Iterable
from typing import cast

import httpx
import tiktoken
from anthropic import Anthropic
from openai.types.chat import ChatCompletionMessageParam

from ..settings import settings
from ..utilities.retry import Retry
from ..types.enums import BackendType
from ..types.llm_parameters import (
    NotGiven,
    NOT_GIVEN,
    ToolParam,
    VectorVeinMessage,
    VectorVeinTextMessage,
    VectorVeinWorkflowMessage,
)


gpt_35_encoding = None
gpt_4o_encoding = None


def get_gpt_35_encoding():
    global gpt_35_encoding
    if gpt_35_encoding is None:
        gpt_35_encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    return gpt_35_encoding


def get_gpt_4o_encoding():
    global gpt_4o_encoding
    if gpt_4o_encoding is None:
        gpt_4o_encoding = tiktoken.encoding_for_model("gpt-4o")
    return gpt_4o_encoding


class ToolCallContentProcessor:
    tool_use_re = re.compile(r"<\|▶\|>(.*?)<\|◀\|>", re.DOTALL)

    def __init__(self, content: str):
        self.content = content

    @property
    def non_tool_content(self):
        return re.sub(self.tool_use_re, "", self.content).strip()

    @property
    def tool_calls(self):
        if "<|▶|>" not in self.content or "<|◀|>" not in self.content:
            return {}
        tool_calls_matches = re.findall(self.tool_use_re, self.content)
        if tool_calls_matches:
            tool_calls = []
            for idx, match in enumerate(tool_calls_matches):
                try:
                    tool_call_data = json.loads(match)
                    arguments = json.dumps(tool_call_data["arguments"], ensure_ascii=False)
                    tool_calls.append(
                        {
                            "index": idx,
                            "id": f"tool_call_{uuid.uuid4()}",
                            "function": {
                                "arguments": arguments,
                                "name": tool_call_data["name"],
                            },
                            "type": "function",
                        }
                    )
                except json.JSONDecodeError:
                    print(f"Failed to parse tool call data:\nContent: {self.content}\nMatch: {match}")

            if not tool_calls:
                return {}

            return {"tool_calls": tool_calls}
        else:
            return {}


def convert_type(value, value_type):
    if value_type == "string":
        return str(value)
    elif value_type == "number":
        try:
            return float(value)
        except ValueError:
            return value
    elif value_type == "integer":
        try:
            return int(value)
        except ValueError:
            return value
    elif value_type == "boolean":
        return value.lower() in ("true", "1", "t")
    else:
        return value  # 如果类型未知，返回原始值


def _get_first_enabled_endpoint(backend_setting, settings):
    """Get the first enabled endpoint from backend settings"""
    for endpoint_choice in backend_setting.endpoints:
        if isinstance(endpoint_choice, dict):
            endpoint_id = endpoint_choice["endpoint_id"]
        else:
            endpoint_id = endpoint_choice

        try:
            endpoint = settings.get_endpoint(endpoint_id)
            if endpoint.enabled:
                return endpoint
        except ValueError:
            # Endpoint not found, skip it
            continue
    return None


def get_token_counts(text: str | dict, model: str = "", use_token_server_first: bool = True) -> int:
    if use_token_server_first and settings.token_server is not None:
        base_url = settings.token_server.url if settings.token_server.url is not None else f"http://{settings.token_server.host}:{settings.token_server.port}"
        _, response = Retry(httpx.post).args(url=f"{base_url}/count_tokens", json={"text": text, "model": model}, timeout=None).retry_times(5).sleep_time(1).run()
        if response is not None:
            try:
                result = response.json()
                return result["total_tokens"]
            except Exception as e:
                print(f"Failed to parse token count response: {e}")

    if not isinstance(text, str):
        text = str(text)
    if model == "gpt-3.5-turbo":
        return len(get_gpt_35_encoding().encode(text))
    elif model.startswith(("gpt-4o", "o1-", "o3-")):
        return len(get_gpt_4o_encoding().encode(text))
    elif model.startswith(("abab", "MiniMax")):
        backend_setting = settings.get_backend(BackendType.MiniMax).models[model]
        if len(backend_setting.endpoints) == 0:
            return int(len(text) / 1.33)
        endpoint = _get_first_enabled_endpoint(backend_setting, settings)
        if endpoint is None:
            return int(len(text) / 1.33)
        tokenize_url = "https://api.minimax.chat/v1/tokenize"
        headers = {"Authorization": f"Bearer {endpoint.api_key}", "Content-Type": "application/json"}
        request_body = {
            "model": model,
            "tokens_to_generate": 128,
            "temperature": 0.2,
            "messages": [
                {"sender_type": "USER", "text": text},
            ],
        }

        _, response = Retry(httpx.post).args(url=tokenize_url, headers=headers, json=request_body, timeout=None).retry_times(5).sleep_time(10).run()
        if response is None:
            return 1000
        result = response.json()
        return result["segments_num"]
    elif model.startswith(("moonshot", "kimi")):
        backend_setting = settings.get_backend(BackendType.Moonshot).models[model]
        if len(backend_setting.endpoints) == 0:
            return len(get_gpt_35_encoding().encode(text))
        endpoint = _get_first_enabled_endpoint(backend_setting, settings)
        if endpoint is None:
            return len(get_gpt_35_encoding().encode(text))
        tokenize_url = f"{endpoint.api_base}/tokenizers/estimate-token-count"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {endpoint.api_key}"}
        request_body = {
            "model": model,
            "messages": [
                {"role": "user", "content": text},
            ],
        }
        _, response = Retry(httpx.post).args(url=tokenize_url, headers=headers, json=request_body, timeout=None).retry_times(5).sleep_time(10).run()
        if response is None:
            return 1000
        result = response.json()
        return result["data"]["total_tokens"]
    elif model.startswith("gemini"):
        backend_setting = settings.get_backend(BackendType.Gemini).models[model]
        if len(backend_setting.endpoints) == 0:
            return len(get_gpt_35_encoding().encode(text))
        endpoint = _get_first_enabled_endpoint(backend_setting, settings)
        if endpoint is None:
            return len(get_gpt_35_encoding().encode(text))

        api_base = endpoint.api_base.removesuffix("/openai/") if endpoint.api_base else "https://generativelanguage.googleapis.com/v1beta"
        base_url = f"{api_base}/models/{backend_setting.id}:countTokens"
        params = {"key": endpoint.api_key}
        request_body = {
            "contents": {
                "role": "USER",
                "parts": [
                    {"text": text},
                ],
            },
        }
        _, response = Retry(httpx.post).args(base_url, json=request_body, params=params, timeout=None).retry_times(5).sleep_time(10).run()
        if response is None:
            return 1000
        result = response.json()
        return result["totalTokens"]
    elif model.startswith("claude"):
        backend_setting = settings.get_backend(BackendType.Anthropic)
        try:
            for endpoint_choice in backend_setting.models[model].endpoints:
                if isinstance(endpoint_choice, dict):
                    endpoint_id = endpoint_choice["endpoint_id"]
                else:
                    endpoint_id = endpoint_choice

                try:
                    endpoint = settings.get_endpoint(endpoint_id)
                    if not endpoint.enabled:
                        continue
                except ValueError:
                    continue

                if endpoint.is_vertex or endpoint.is_bedrock or endpoint.endpoint_type == "anthropic_vertex" or endpoint.endpoint_type == "anthropic_bedrock":
                    continue
                elif endpoint.endpoint_type in ("default", "anthropic"):
                    return (
                        Anthropic(
                            api_key=endpoint.api_key,
                            base_url=endpoint.api_base,
                        )
                        .beta.messages.count_tokens(messages=[{"role": "user", "content": text}], model=model)
                        .input_tokens
                    )
        except Exception as e:
            warnings.warn(f"Anthropic token counting failed: {e}", stacklevel=2)

        # TODO: Use anthropic token counting
        warnings.warn("Anthropic token counting is not implemented in Vertex or Bedrock yet", stacklevel=2)
        return len(get_gpt_4o_encoding().encode(text))
    elif model.startswith("deepseek"):
        from deepseek_tokenizer import deepseek_tokenizer

        return len(deepseek_tokenizer.encode(text))
    elif model.startswith("qwen"):
        from qwen_tokenizer import get_tokenizer

        qwen_tokenizer = get_tokenizer(model)
        return len(qwen_tokenizer.encode(text))
    elif model.startswith("stepfun"):
        backend_setting = settings.get_backend(BackendType.StepFun).models[model]
        if len(backend_setting.endpoints) == 0:
            return len(get_gpt_35_encoding().encode(text))
        endpoint = _get_first_enabled_endpoint(backend_setting, settings)
        if endpoint is None:
            return len(get_gpt_35_encoding().encode(text))
        tokenize_url = f"{endpoint.api_base}/token/count"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {endpoint.api_key}"}
        request_body = {
            "model": model,
            "messages": [
                {"role": "user", "content": text},
            ],
        }
        _, response = Retry(httpx.post).args(url=tokenize_url, headers=headers, json=request_body, timeout=None).retry_times(5).sleep_time(10).run()
        if response is None:
            return 1000
        result = response.json()
        return result["data"]["total_tokens"]
    elif model.startswith("glm"):
        backend_setting = settings.get_backend(BackendType.ZhiPuAI).models[model]
        if len(backend_setting.endpoints) == 0:
            return len(get_gpt_35_encoding().encode(text))
        endpoint = _get_first_enabled_endpoint(backend_setting, settings)
        if endpoint is None:
            return len(get_gpt_35_encoding().encode(text))
        if model not in ("glm-4-plus", "glm-4-long", "glm-4-0520", "glm-4-air", "glm-4-flash"):
            model = "glm-4-plus"
        tokenize_url = f"{endpoint.api_base or 'https://open.bigmodel.cn/api/paas/v4'}/tokenizer"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {endpoint.api_key}"}
        request_body = {
            "model": model,
            "messages": [
                {"role": "user", "content": text},
            ],
        }
        _, response = Retry(httpx.post).args(url=tokenize_url, headers=headers, json=request_body, timeout=None).retry_times(5).sleep_time(10).run()
        if response is None:
            return 1000
        result = response.json()
        return result["usage"]["prompt_tokens"]
    else:
        return len(get_gpt_4o_encoding().encode(text))


def calculate_image_tokens(width: int, height: int, model: str = "gpt-4o"):
    if model.startswith("moonshot"):
        return 1024

    if width > 2048 or height > 2048:
        aspect_ratio = width / height
        if aspect_ratio > 1:
            width, height = 2048, int(2048 / aspect_ratio)
        else:
            width, height = int(2048 * aspect_ratio), 2048

    if width >= height and height > 768:
        width, height = int((768 / height) * width), 768
    elif height > width and width > 768:
        width, height = 768, int((768 / width) * height)

    tiles_width = ceil(width / 512)
    tiles_height = ceil(height / 512)
    total_tokens = 85 + 170 * (tiles_width * tiles_height)

    return total_tokens


def get_message_token_counts(
    messages: list,
    tools: list | Iterable[ToolParam] | NotGiven = NOT_GIVEN,
    model: str = "gpt-4o",
    native_multimodal: bool = True,
) -> int:
    tokens = 0
    formatted_messages = format_messages(messages, backend=BackendType.OpenAI, native_multimodal=native_multimodal)
    for message in formatted_messages:
        content = message["content"]
        if isinstance(content, str):
            tokens += get_token_counts(content, model)
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item["type"] == "text":
                    tokens += get_token_counts(item["text"], model)
                elif isinstance(item, dict) and item["type"].startswith("image"):
                    if native_multimodal:
                        # TODO: Get real image size
                        tokens += calculate_image_tokens(2048, 2048, model)
                    else:
                        tokens += 1
    if tools:
        tokens += get_token_counts(str(tools), model)

    return tokens


def cutoff_messages(
    messages: list,
    max_count: int = 16000,
    backend: BackendType = BackendType.OpenAI,
    model: str = "",
) -> list:
    """
    给定一个消息列表和最大长度，将消息列表截断到最大长度。
    如果列表中第一个元素的role是'system'，则始终保留该元素。
    超过长度时从列表开始处（第二个元素起）依次删除消息，直到总长度小于等于最大长度。
    如果最后一条消息超过了最大长度，那么将最后一条消息截断到最大长度。

    Args:
        messages (list): 消息列表，每条消息是一个包含'role'和'content'的字典。
        max_count (int, optional): 允许的最大长度。默认值为16000。

    Returns:
        list: 截断后的消息列表。
    """

    if len(messages) == 0:
        return messages

    messages_length = 0
    content_key = "content"

    # 先检查并保留第一条system消息（如果有）
    system_message = None
    if messages[0]["role"] == "system":
        system_message = messages[0]
        system_message_length = get_token_counts(system_message[content_key], model)
        if system_message_length > max_count:
            # 如果第一条system消息超过最大长度，截断它
            system_message[content_key] = system_message[content_key][-max_count:]
            return [system_message]
        else:
            messages_length += system_message_length
            messages = messages[1:]  # 移除第一个元素，以处理其余消息

    if system_message:
        system_message = [system_message]
    else:
        system_message = []

    for index, message in enumerate(reversed(messages)):
        if not message.get(content_key):
            continue
        count = 0
        if isinstance(message[content_key], str):
            contents = [message[content_key]]
        elif isinstance(message[content_key], list):
            contents = message[content_key]
        else:
            contents = [str(message[content_key])]

        for content in contents:
            # TODO: Add non text token counts
            if isinstance(content, dict) and "text" not in content:
                continue
            if isinstance(content, dict):
                content_text = content["text"]
            else:
                content_text = str(content)
            count += get_token_counts(content_text, model)
        messages_length += count
        if messages_length < max_count:
            continue
        if index == 0:
            # 一条消息就超过长度则将该消息内容进行截断，保留该消息最后的一部分
            content = message[content_key][max_count - messages_length :]
            return system_message + [
                {
                    "role": message["role"],
                    content_key: content,
                }
            ]

        return system_message + messages[-index:]
    return system_message + messages


def format_image_message(image: str, backend: BackendType = BackendType.OpenAI, process_image: bool = True) -> dict:
    if process_image:
        from ..utilities.media_processing import ImageProcessor

        image_processor = ImageProcessor(image_source=image)
        if backend == BackendType.OpenAI:
            return {
                "type": "image_url",
                "image_url": {"url": image_processor.data_url},
            }
        elif backend == BackendType.Anthropic:
            return {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": image_processor.mime_type,
                    "data": image_processor.base64_image,
                },
            }
        else:
            return {
                "type": "image_url",
                "image_url": {"url": image_processor.data_url},
            }
    else:
        if backend == BackendType.Anthropic:
            return {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image}}
        else:
            return {"type": "image_url", "image_url": {"url": image}}


def format_workflow_messages(message: VectorVeinWorkflowMessage, content: str, backend: BackendType):
    formatted_messages = []

    # 工具调用消息
    if backend in (BackendType.OpenAI, BackendType.ZhiPuAI, BackendType.Mistral, BackendType.Yi, BackendType.Gemini, BackendType.DeepSeek):
        tool_call_message = {
            "content": content,
            "role": "assistant",
            "tool_calls": [
                {
                    "id": message["metadata"]["selected_workflow"]["tool_call_id"] or message["metadata"]["record_id"],
                    "type": "function",
                    "function": {
                        "name": message["metadata"]["selected_workflow"]["function_name"],
                        "arguments": json.dumps(message["metadata"]["selected_workflow"]["params"], ensure_ascii=False),
                    },
                }
            ],
        }
    elif backend == BackendType.Anthropic:
        tool_call_message = {
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": message["metadata"]["selected_workflow"]["tool_call_id"],
                    "name": message["metadata"]["selected_workflow"]["function_name"],
                    "input": message["metadata"]["selected_workflow"]["params"],
                },
            ],
        }
        if content:
            tool_call_message["content"].insert(0, {"type": "text", "text": content})
    else:
        tool_call_message = {
            "content": json.dumps(
                {
                    "name": message["metadata"]["selected_workflow"]["function_name"],
                    "arguments": json.dumps(message["metadata"]["selected_workflow"]["params"], ensure_ascii=False),
                },
                ensure_ascii=False,
            ),
            "role": "assistant",
        }
    formatted_messages.append(tool_call_message)

    # 工具调用结果消息
    if backend in (BackendType.OpenAI, BackendType.ZhiPuAI, BackendType.Mistral, BackendType.Yi, BackendType.Gemini, BackendType.DeepSeek):
        tool_call_result_message = {
            "role": "tool",
            "tool_call_id": message["metadata"]["selected_workflow"]["tool_call_id"] or message["metadata"]["record_id"],
            "name": message["metadata"]["selected_workflow"]["function_name"],
            "content": message["metadata"].get("workflow_result", ""),
        }
    elif backend == BackendType.Anthropic:
        tool_call_result_message = {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": message["metadata"]["selected_workflow"]["tool_call_id"],
                    "content": message["metadata"].get("workflow_result", ""),
                }
            ],
        }
    else:
        tool_call_result_message = {
            "role": "user",
            "content": json.dumps(
                {
                    "function": message["metadata"]["selected_workflow"]["function_name"],
                    "result": message["metadata"].get("workflow_result", ""),
                },
                ensure_ascii=False,
            ),
        }
    formatted_messages.append(tool_call_result_message)

    # if content and backend not in (BackendType.Mistral, BackendType.Anthropic):
    #     formatted_messages.append({"role": "assistant", "content": content})

    return formatted_messages


def transform_from_openai_message(
    message: ChatCompletionMessageParam,
    backend: BackendType,
    native_multimodal: bool = False,
    function_call_available: bool = False,
    process_image: bool = True,
):
    role = message.get("role", "user")
    content = message.get("content", "")
    tool_calls = message.get("tool_calls", [])

    if backend == BackendType.Anthropic:
        if role == "tool":
            return {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": message["tool_call_id"],  # type: ignore
                        "content": message["content"],  # type: ignore
                    }
                ],
            }
        if isinstance(content, list):
            formatted_content = []
            for item in content:
                if isinstance(item, str):
                    formatted_content.append({"type": "text", "text": item})
                elif isinstance(item, dict) and "type" in item:
                    if item["type"] == "image_url":
                        formatted_content.append(format_image_message(item["image_url"]["url"], backend, process_image))
                    else:
                        formatted_content.append(item)
            if tool_calls:
                for tool_call in tool_calls:
                    formatted_content.append(
                        {
                            "type": "tool_use",
                            "id": tool_call["id"],
                            "name": tool_call["function"]["name"],
                            "input": json.loads(tool_call["function"]["arguments"]) if tool_call["function"]["arguments"] else {},
                        }
                    )
            return {"role": role, "content": formatted_content}
        else:
            if tool_calls:
                formatted_content = [{"type": "text", "text": content}] if content else []
                for tool_call in tool_calls:
                    formatted_content.append(
                        {
                            "type": "tool_use",
                            "id": tool_call["id"],
                            "name": tool_call["function"]["name"],
                            "input": json.loads(tool_call["function"]["arguments"]) if tool_call["function"]["arguments"] else {},
                        }
                    )
                return {"role": role, "content": formatted_content}
            else:
                return {"role": role, "content": content}
    else:
        if isinstance(content, str):
            if not function_call_available:
                if message["role"] == "tool":
                    return {
                        "role": "user",
                        "content": f"Tool<tool_call_id: {message['tool_call_id']}> Call result: {content}",
                    }
                elif message["role"] == "assistant":
                    if tool_calls:
                        tool_calls_content = json.dumps(tool_calls, ensure_ascii=False)
                        content += f"Tool calls: {tool_calls_content}"
                    return {"role": role, "content": content}

            return message
        elif isinstance(content, list):
            formatted_content = []
            for item in content:
                if item["type"] == "image_url" and not native_multimodal:
                    formatted_content.append({"type": "text", "text": f"Image<image_url: {item['image_url']['url']}>"})
                else:
                    formatted_content.append(item)

            if not function_call_available:
                if message["role"] == "tool":
                    role = "user"
                    formatted_content = [
                        {
                            "type": "text",
                            "text": f"Tool<tool_call_id: {message['tool_call_id']}> Call result: {formatted_content}",
                        }
                    ]
                elif message["role"] == "assistant":
                    if tool_calls:
                        tool_calls_content = json.dumps(tool_calls, ensure_ascii=False)
                        formatted_content.append({"type": "text", "text": f"Tool calls: {tool_calls_content}"})

                return {"role": role, "content": formatted_content}

            if tool_calls:
                return {"role": role, "content": formatted_content, "tool_calls": tool_calls}
            else:
                return {"role": role, "content": formatted_content}
        else:
            return message


def format_messages(
    messages: Iterable[ChatCompletionMessageParam | VectorVeinMessage],
    backend: BackendType = BackendType.OpenAI,
    native_multimodal: bool = False,
    function_call_available: bool = False,
    process_image: bool = True,
) -> list:
    """将 VectorVein 和 OpenAI 的 Message 序列化后的格式转换为不同模型支持的格式

    Args:
        messages (list): VectorVein Or OpenAI messages list.
        backend (str, optional): Messages format target backend. Defaults to BackendType.OpenAI.
        native_multimodal (bool, optional): Use native multimodal ability. Defaults to False.
        function_call_available (bool, optional): Use function call ability. Defaults to False.
        process_image (bool, optional): Process image. Defaults to True.

    Returns:
        list: 转换后的消息列表
    """

    def is_vectorvein_message(message):
        return "content_type" in message

    formatted_messages = []

    for message in messages:
        if is_vectorvein_message(message):
            message = cast(VectorVeinMessage, message)
            match message["content_type"]:
                case "TXT":
                    message = cast(VectorVeinTextMessage, message)
                case "WKF":
                    message = cast(VectorVeinWorkflowMessage, message)
                case _:
                    raise ValueError(f"Unsupported message type: {message['content_type']}")
            # 处理 VectorVein 格式的消息
            content = message["content"]["text"]
            if message["content_type"] == "TXT":
                message = cast(VectorVeinTextMessage, message)
                role = "user" if message["author_type"] == "U" else "assistant"
                formatted_message = format_text_message(content, role, message.get("attachments", []), backend, native_multimodal, process_image)
                formatted_messages.append(formatted_message)
            elif message["content_type"] == "WKF" and message["status"] in ("S", "R"):
                message = cast(VectorVeinWorkflowMessage, message)
                formatted_messages.extend(format_workflow_messages(message, content, backend))
        else:
            # 处理 OpenAI 格式的消息
            message = cast(ChatCompletionMessageParam, message)
            formatted_message = transform_from_openai_message(message, backend, native_multimodal, function_call_available, process_image)
            formatted_messages.append(formatted_message)

    return formatted_messages


def format_text_message(
    content: str,
    role: str,
    attachments: list,
    backend: BackendType,
    native_multimodal: bool,
    process_image: bool = True,
):
    images_extensions = ("jpg", "jpeg", "png", "bmp")
    has_images = any(attachment.lower().endswith(images_extensions) for attachment in attachments)

    if attachments:
        content += "\n# Attachments:\n"
        content += "\n".join([f"- {attachment}" for attachment in attachments])

    if native_multimodal and has_images:
        return {
            "role": role,
            "content": [
                {"type": "text", "text": content},
                *[
                    format_image_message(image=attachment, backend=backend, process_image=process_image)
                    for attachment in attachments
                    if attachment.lower().endswith(images_extensions)
                ],
            ],
        }
    else:
        return {"role": role, "content": content}


def generate_tool_use_system_prompt(tools: list | str, format_type: str = "json") -> str:
    if format_type == "json":
        return (
            "You have access to the following tools. Use them if required and wait for the tool call result. Stop output after calling a tool.\n\n"
            f"# Tools\n{tools}\n\n"
            "# Requirements when using tools\n"
            "Must starts with <|▶|> and ends with <|◀|>\n"
            "Must be valid JSON format and pay attention to escape characters.\n"
            '## Output format\n<|▶|>{"name": "<function name:str>", "arguments": <arguments:dict>}<|◀|>\n\n'
            '## Example output\n<|▶|>{"name": "get_current_weather", "arguments": {"location": "San Francisco, CA"}}<|◀|>'
        )
    elif format_type == "xml":
        return (
            "You have access to the following tools. Use them if required and wait for the tool call result. Stop output after calling a tool.\n\n"
            f"# Tools\n{tools}\n\n"
            "# Requirements when using tools\n"
            "Must starts with <|▶|> and ends with <|◀|>\n"
            "Must be valid XML format.\n"
            "## Output format\n<|▶|><invoke><tool_name>[function name:str]</tool_name><parameters><parameter_1_name>[parameter_1_value]</parameter_1_name><parameter_2_name>[parameter_2_value]</parameter_2_name>...</parameters></invoke><|◀|>\n\n"
            "## Example output\n<|▶|><invoke><tool_name>calculator</tool_name><parameters><first_operand>1984135</first_operand><second_operand>9343116</second_operand><operator>*</operator></parameters></invoke><|◀|>"
        )
    else:
        return ""

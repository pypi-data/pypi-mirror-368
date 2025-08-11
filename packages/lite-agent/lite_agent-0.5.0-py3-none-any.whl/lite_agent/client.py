import abc
import os
from typing import Any, Literal

import litellm
from openai.types.chat import ChatCompletionToolParam
from openai.types.responses import FunctionToolParam

ReasoningEffort = Literal["minimal", "low", "medium", "high"]
ThinkingConfig = dict[str, Any] | None

# 统一的推理配置类型
ReasoningConfig = (
    str
    | dict[str, Any]  # {"type": "enabled", "budget_tokens": 2048} 或其他配置
    | bool  # True/False 简单开关
    | None  # 不启用推理
)


def parse_reasoning_config(reasoning: ReasoningConfig) -> tuple[ReasoningEffort | None, ThinkingConfig]:
    """
    解析统一的推理配置，返回 reasoning_effort 和 thinking_config。

    Args:
        reasoning: 统一的推理配置
            - str: "minimal", "low", "medium", "high" -> reasoning_effort
            - dict: {"type": "enabled", "budget_tokens": N} -> thinking_config
            - bool: True -> "medium", False -> None
            - None: 不启用推理

    Returns:
        tuple: (reasoning_effort, thinking_config)
    """
    if reasoning is None:
        return None, None
    if isinstance(reasoning, str):
        # 字符串类型，使用 reasoning_effort
        return reasoning, None
    if isinstance(reasoning, dict):
        # 字典类型，使用 thinking_config
        return None, reasoning
    if isinstance(reasoning, bool):
        # 布尔类型，True 使用默认的 medium，False 不启用
        return "medium" if reasoning else None, None
    # 其他类型，默认不启用
    return None, None


class BaseLLMClient(abc.ABC):
    """Base class for LLM clients."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        api_base: str | None = None,
        api_version: str | None = None,
        reasoning: ReasoningConfig = None,
    ):
        self.model = model
        self.api_key = api_key
        self.api_base = api_base
        self.api_version = api_version

        # 处理推理配置
        self.reasoning_effort, self.thinking_config = parse_reasoning_config(reasoning)

    @abc.abstractmethod
    async def completion(
        self,
        messages: list[Any],
        tools: list[ChatCompletionToolParam] | None = None,
        tool_choice: str = "auto",
        reasoning: ReasoningConfig = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """Perform a completion request to the LLM."""

    @abc.abstractmethod
    async def responses(
        self,
        messages: list[dict[str, Any]],  # Changed from ResponseInputParam
        tools: list[FunctionToolParam] | None = None,
        tool_choice: Literal["none", "auto", "required"] = "auto",
        reasoning: ReasoningConfig = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """Perform a response request to the LLM."""


class LiteLLMClient(BaseLLMClient):
    def _resolve_reasoning_params(
        self,
        reasoning: ReasoningConfig,
    ) -> tuple[ReasoningEffort | None, ThinkingConfig]:
        """解析推理配置参数。"""
        if reasoning is not None:
            return parse_reasoning_config(reasoning)

        # 使用实例默认值
        return self.reasoning_effort, self.thinking_config

    async def completion(
        self,
        messages: list[Any],
        tools: list[ChatCompletionToolParam] | None = None,
        tool_choice: str = "auto",
        reasoning: ReasoningConfig = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # noqa: ANN401
        """Perform a completion request to the Litellm API."""

        # 处理推理配置参数
        final_reasoning_effort, final_thinking_config = self._resolve_reasoning_params(
            reasoning,
        )

        # Prepare completion parameters
        completion_params = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": tool_choice,
            "api_version": self.api_version,
            "api_key": self.api_key,
            "api_base": self.api_base,
            "stream": True,
            **kwargs,
        }

        # Add reasoning parameters if specified
        if final_reasoning_effort is not None:
            completion_params["reasoning_effort"] = final_reasoning_effort
        if final_thinking_config is not None:
            completion_params["thinking"] = final_thinking_config

        return await litellm.acompletion(**completion_params)

    async def responses(
        self,
        messages: list[dict[str, Any]],  # Changed from ResponseInputParam
        tools: list[FunctionToolParam] | None = None,
        tool_choice: Literal["none", "auto", "required"] = "auto",
        reasoning: ReasoningConfig = None,
        **kwargs: Any,  # noqa: ANN401
    ) -> Any:  # type: ignore[return]  # noqa: ANN401
        """Perform a response request to the Litellm API."""

        os.environ["DISABLE_AIOHTTP_TRANSPORT"] = "True"

        # 处理推理配置参数
        final_reasoning_effort, final_thinking_config = self._resolve_reasoning_params(
            reasoning,
        )

        # Prepare response parameters
        response_params = {
            "model": self.model,
            "input": messages,  # type: ignore[arg-type]
            "tools": tools,
            "tool_choice": tool_choice,
            "api_version": self.api_version,
            "api_key": self.api_key,
            "api_base": self.api_base,
            "stream": True,
            "store": False,
            **kwargs,
        }

        # Add reasoning parameters if specified
        if final_reasoning_effort is not None:
            response_params["reasoning_effort"] = final_reasoning_effort
        if final_thinking_config is not None:
            response_params["thinking"] = final_thinking_config

        return await litellm.aresponses(**response_params)  # type: ignore[return-value]

"""CrewAI LLM integration for Flotorch."""
from typing import Any, Dict, List, Optional, Union
from crewai.llms.base_llm import BaseLLM
from flotorch.sdk.llm import FlotorchLLM
from flotorch.sdk.utils.logging_utils import log_error, log_info, log_warning


class FlotorchCrewAILLM(BaseLLM):
    """Flotorch LLM integration for CrewAI framework."""

    @property
    def supports_function_calling(self) -> bool:
        """Return whether this LLM supports function calling."""
        return True

    def __init__(
        self,
        model_id: str,
        api_key: str,
        base_url: str,
        temperature: Optional[float] = None,
        **kwargs
    ):
        """Initialize the FlotorchCrewAILLM.

        Args:
            model_id: The model identifier.
            api_key: API key for authentication.
            base_url: Base URL for the API.
            temperature: Temperature parameter for generation.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(model=model_id, temperature=temperature)
        self.llm = FlotorchLLM(model_id, api_key, base_url)
        self.available_functions = {}

    def call(
        self,
        messages: Union[str, List[Dict[str, str]]],
        tools: Optional[List[dict]] = None,
        callbacks: Optional[List[Any]] = None,
        available_functions: Optional[Dict[str, Any]] = None,
        from_task: Optional[Any] = None,
        from_agent: Optional[Any] = None
    ) -> Union[str, Any]:
        """Make a call to the LLM.

        Args:
            messages: Input messages as string or list of dictionaries.
            tools: Optional list of tools to use.
            callbacks: Optional list of callbacks.
            available_functions: Optional dictionary of available functions.
            from_task: Optional task context.
            from_agent: Optional agent context.

        Returns:
            The LLM response as string or tool calls.

        Raises:
            Exception: If the LLM call fails.
        """
        try:
            formatted_messages = self._format_messages(messages)
            converted_tools = (
                self._convert_tools_to_openai_format(tools) if tools else None
            )

            log_info(
                f"LLM call: {len(formatted_messages)} messages, "
                f"{len(converted_tools) if converted_tools else 0} tools"
            )

            response = self.llm.invoke(formatted_messages, tools=converted_tools)

            # Check if response contains tool calls
            if (
                hasattr(response, 'metadata')
                and response.metadata
                and 'tool_calls' in response.metadata
            ):
                log_info(
                    f"Tool calls found in response: "
                    f"{response.metadata['tool_calls']}"
                )
                return response.metadata['tool_calls']

            # Return content if no tool calls
            return response.content

        except Exception as e:
            log_error(f"LLM call failed: {str(e)}", error=e)
            raise Exception(f"FlotorchCrewaiLLM error: {str(e)}")

    def _format_messages(
        self, messages: Union[str, List[Dict[str, str]]]
    ) -> List[Dict[str, str]]:
        """Format messages to standard format.

        Args:
            messages: Input messages as string or list of dictionaries.

        Returns:
            Formatted list of message dictionaries.

        Raises:
            ValueError: If messages format is invalid.
        """
        if isinstance(messages, str):
            return [
                {
                    "role": "user",
                    "content": self._sanitize_content(messages)
                }
            ]
        elif isinstance(messages, list):
            formatted = []
            for i, msg in enumerate(messages):
                if (
                    isinstance(msg, dict)
                    and "role" in msg
                    and "content" in msg
                ):
                    if self._is_valid_role(msg["role"]):
                        formatted.append({
                            "role": msg["role"],
                            "content": self._sanitize_content(msg["content"])
                        })
                    else:
                        log_warning(
                            f"Invalid role '{msg['role']}' in message {i}, "
                            f"converting to user"
                        )
                        formatted.append({
                            "role": "user",
                            "content": self._sanitize_content(msg["content"])
                        })
                else:
                    log_warning(
                        f"Malformed message {i}, converting to user message"
                    )
                    formatted.append({
                        "role": "user",
                        "content": self._sanitize_content(str(msg))
                    })
            return (
                formatted if formatted
                else [{"role": "user", "content": "Hello"}]
            )
        else:
            raise ValueError(f"Invalid messages format: {type(messages)}")

    def _convert_tools_to_openai_format(self, tools: List[dict]) -> List[dict]:
        """Convert CrewAI tools to OpenAI format.

        Args:
            tools: List of CrewAI tools.

        Returns:
            List of tools in OpenAI format.
        """
        converted = []
        for tool in tools:
            if isinstance(tool, dict):
                converted.append(tool)
            elif hasattr(tool, 'name') and hasattr(tool, 'description'):
                converted_tool = self._convert_single_tool_to_openai_format(tool)
                if converted_tool:
                    converted.append(converted_tool)
                    self.available_functions[tool.name] = tool
        return converted

    def _convert_single_tool_to_openai_format(self, tool) -> Optional[dict]:
        """Convert single CrewAI tool to OpenAI format.

        Args:
            tool: Single CrewAI tool.

        Returns:
            Tool in OpenAI format or None if conversion fails.
        """
        try:
            params = {}
            if hasattr(tool, 'args_schema') and tool.args_schema:
                schema = tool.args_schema.model_json_schema()
                params = schema.get('properties', {})

            return {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": params,
                        "required": list(params.keys())
                    }
                }
            }
        except Exception as e:
            log_warning(
                f"Failed to convert tool "
                f"{getattr(tool, 'name', 'unknown')}: {str(e)}"
            )
            return None

    def _is_valid_role(self, role: str) -> bool:
        """Check if the role is valid.

        Args:
            role: Role to validate.

        Returns:
            True if role is valid, False otherwise.
        """
        return role.lower() in {"user", "assistant", "system"}

    def _sanitize_content(self, content: str) -> str:
        """Sanitize message content.

        Args:
            content: Content to sanitize.

        Returns:
            Sanitized content.
        """
        if not content:
            return ""
        content = str(content).strip()
        return content[:10000] if len(content) > 10000 else content
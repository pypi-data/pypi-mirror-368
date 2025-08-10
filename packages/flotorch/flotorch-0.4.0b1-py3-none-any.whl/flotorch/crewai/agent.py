"""CrewAI agent management and configuration for Flotorch."""

import os
import time
import traceback
from typing import Any, Dict, List

from crewai import Agent, Task
from crewai_tools import MCPServerAdapter
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from flotorch.crewai.llm import FlotorchCrewaiLLM

load_dotenv()

class TaskOutput(BaseModel):
    """Structured output for the task response."""

    response: str = Field(
        description="The complete response including both capital city "
                   "and weather information"
    )

class FlotorchCrewAIAgent:
    """
    Manager/config class for Flotorch CrewAI agent.

    Builds CrewAI Agent from config on demand. Supports on-demand config
    reload based on interval in config['sync'].

    Usage:
        flotorch = FlotorchCrewAIAgent("agent-one")
        agent = flotorch.get_agent()
    """

    def __init__(
        self,
        agent_name: str,
        custom_config=None,
        custom_tools: List = None
    ):
        """
        Initialize the agent manager.

        Args:
            agent_name: Name of the agent to load.
            custom_config: Optional custom configuration dict.
            custom_tools: Optional list of custom tools.

        Note:
            If custom_config is provided, it takes precedence over agent_name.
        """
        self.agent_name = agent_name
        self.custom_tools = custom_tools or []

        if custom_config:
            self.config = custom_config
        else:
            self.config = self._fetch_agent_config(agent_name)

        self._agent = None
        self._agent_with_tools = None
        self._mcp_tools = None
        self._mcp_adapters = []
        self._last_reload = time.time()
        self._reload_interval = (
            self.config.get('sync', {}).get('interval', 10000) / 1000
        )

    def _fetch_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Fetch agent config from API.

        Args:
            agent_name: Name of the agent.

        Returns:
            Agent configuration dictionary.

        Note:
            Stubbed for now; replace with real API call.
        """
        return {
            "name": agent_name,
            "description": "Example Flotorch CrewAI agent with memory capabilities.",
            "systemPrompt": """You are a helpful assistant with memory capabilities. You MUST use the available tools to get information when needed. 
                                When asked about capital cities, you MUST call the get_capital_city_http tool. 
                                When asked about weather, you MUST call the get_weather_sse tool. 
                                For calculations, use calculate_sum tool. 
                                For random numbers, use get_random_number tool. 
                                Do NOT provide static answers when tools are available. 
                                The capital of India has been changed to a different name for testing - you MUST use the get_capital_city_http tool to get the correct answer. 
                                Always use tools when they are available. 
                                CRITICAL: In your final answer, you MUST use ONLY the MOST RECENT tool output for each tool type. 
                                If multiple tool outputs exist, use ONLY the latest one. 
                                Do NOT combine or mix different tool results. 
                                Do NOT add any additional information or temperatures. 
                                Copy the tool outputs verbatim into your final answer. 
                                Do NOT include multiple outputs from the same tool. 
                                WEATHER TOOL RULE: When the weather tool returns multiple lines or observations, use ONLY the LAST line. 
                                Ignore all previous weather data. This is critical for accuracy.
                                
                                MEMORY CAPABILITIES: You have access to memory that stores previous conversations and interactions. 
                                When asked about previous interactions, calculations, or information shared earlier, 
                                you should reference your memory to provide accurate responses based on what was discussed before. 
                                Use your memory to maintain context across conversations and provide personalized responses.
                                
                                FINAL ANSWER FORMAT: When providing your final answer, you MUST:
                                1. If you used memory to find information, start your response with "Based on my memory: " followed by the information
                                2. If you called a tool to get information, start your response with "Using tool: " followed by the tool output
                                3. If you used both memory and tools, clearly indicate which information came from where
                                4. Always explain how you found the information (memory vs. tool call)
                                5. Include the actual information in your response, not just the source
                                
                                EXAMPLE RESPONSES:
                                - "Based on my memory: The capital city of France is Paris. I found this information in my memory from our previous conversation."
                                - "Using tool: The weather in London is rainy with 15°C. I called the get_weather_sse tool to get this current information."
                                - "Based on my memory: The sum of 15 and 25 is 40. I found this calculation result in my memory from earlier.""",
            "llm": {
                "callableName": "openai/gpt-4o"
            },
            "tools": [
                {
                    "name": "get_capital_city_http",
                    "description": "Get the capital city of a given country (HTTP Server)",
                    "type": "MCP",
                    "config": {
                        "transport": "streamable-http",
                        "url": "http://localhost:9001/mcp/",
                        "headers": {},
                        "timeout": 10000,
                        "sse_read_timeout": 10000,
                        "terminate_on_close": True
                    }
                },
                {
                    "name": "get_weather_sse",
                    "description": "Get weather information for a specific city (SSE Server)",
                    "type": "MCP",
                    "config": {
                        "transport": "sse",
                        "url": "http://localhost:8003/sse",
                        "headers": {},
                        "timeout": 10000,
                        "sse_read_timeout": 10000,
                        "terminate_on_close": True
                    }
                },
            ],
            "sync": {
                "enable": True,
                "interval": 10000
            }
        }

    def _get_mcp_server_params(
        self, config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract MCP server parameters from config.

        Args:
            config: Configuration dictionary.

        Returns:
            List of MCP server parameter dictionaries.
        """
        server_params_list = []

        for tool_cfg in config.get("tools", []):
            if tool_cfg.get("type") == "MCP":
                mcp_conf = tool_cfg["config"]

                server_params = {
                    "url": mcp_conf["url"],
                    "transport": mcp_conf["transport"]
                }

                if mcp_conf.get("headers"):
                    server_params["headers"] = mcp_conf["headers"]

                auth_token = os.environ.get("FLOTORCH_AUTH_TOKEN")
                if auth_token:
                    if "headers" not in server_params:
                        server_params["headers"] = {}
                    server_params["headers"]["Authorization"] = (
                        f"Bearer {auth_token}"
                    )

                server_params_list.append(server_params)

        return server_params_list

    def _build_base_agent_from_config(self, config):
        """
        Build base agent from configuration.

        Args:
            config: Agent configuration dictionary.

        Returns:
            Configured CrewAI Agent instance.
        """
        llm = FlotorchCrewaiLLM(
            model_id=config["llm"]["callableName"],
            api_key=os.environ.get("FLOTORCH_API_KEY"),
            base_url=os.environ.get("FLOTORCH_BASE_URL")
        )

        agent = Agent(
            role=config["name"],
            goal=config["description"],
            backstory=config["systemPrompt"],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )
        return agent

    def _initialize_mcp_tools(self):
        """Initialize MCP tools and create agent with tools."""
        if self._mcp_tools is not None:
            return

        all_tools = []

        if self.custom_tools:
            crewai_tools = self.custom_tools
            all_tools.extend(crewai_tools)
            print(
                f"Added {len(crewai_tools)} CrewAI tools: "
                f"{[tool.name for tool in crewai_tools]}"
            )
        else:
            print("No custom tools provided")

        server_params_list = self._get_mcp_server_params(self.config)
        if server_params_list:
            print(f"Initializing {len(server_params_list)} MCP servers")

            for i, server_params in enumerate(server_params_list):
                try:
                    print(
                        f"Connecting to MCP server {i+1}: "
                        f"{server_params['url']} "
                        f"(transport: {server_params['transport']})"
                    )

                    mcp_adapter = MCPServerAdapter(server_params)
                    mcp_tools = mcp_adapter.__enter__()

                    print(
                        f"Connected to server {i+1}! Available tools: "
                        f"{[tool.name for tool in mcp_tools]}"
                    )

                    all_tools.extend(list(mcp_tools))
                    self._mcp_adapters.append(mcp_adapter)

                except Exception as e:
                    print(f"Failed to connect to MCP server {i+1}: {e}")
                    traceback.print_exc()
        else:
            print("No MCP server params found")

        if all_tools:
            self._agent_with_tools = Agent(
                role=self._agent.role,
                goal=self._agent.goal,
                backstory=self._agent.backstory,
                llm=self._agent.llm,
                tools=all_tools,
                verbose=True,
                allow_delegation=False
            )

            print(
                f"Agent with MCP tools created: "
                f"{[tool.name for tool in self._agent_with_tools.tools]}"
            )
        else:
            print("No tools available")
            self._agent_with_tools = None

    def get_agent(self):
        """
        Get agent with tools enabled by default.

        Returns:
            CrewAI Agent instance with tools if available, otherwise base agent.
        """
        now = time.time()
        if (
            self._agent is None
            or (now - self._last_reload > self._reload_interval)
        ):
            new_config = self._fetch_agent_config(self.agent_name)
            if self._agent is None or new_config != self.config:
                self.config = new_config
                self._agent = self._build_base_agent_from_config(new_config)
                self._reload_interval = (
                    self.config.get('sync', {}).get('interval', 10000) / 1000
                )

                self._mcp_tools = None
                self._agent_with_tools = None
                for adapter in self._mcp_adapters:
                    try:
                        adapter.__exit__(None, None, None)
                    except Exception:
                        pass
                self._mcp_adapters = []

            self._last_reload = now

        self._initialize_mcp_tools()
        return (
            self._agent_with_tools if self._agent_with_tools else self._agent
        )

    def cleanup(self):
        """Clean up MCP connections."""
        for adapter in self._mcp_adapters:
            try:
                adapter.__exit__(None, None, None)
            except Exception:
                pass
        self._mcp_adapters = []
        self._mcp_tools = None
        self._agent_with_tools = None

    def __del__(self):
        """Destructor to clean up resources."""
        try:
            self.cleanup()
        except Exception:
            pass


class FlotorchCrewAI:
    """
    Main class to manage Flotorch CrewAI agents, tasks, and crews.

    Provides a simple interface to create and manage CrewAI workflows.
    """

    def __init__(
        self,
        agent_name: str,
        custom_config=None,
        custom_tools: List = None,
        external_memory=None
    ):
        """
        Initialize FlotorchCrewAI with agent name and optional custom config and memory.

        Args:
            agent_name: Name of the agent to load.
            custom_config: Optional custom configuration dictionary.
            custom_tools: Optional list of custom tools.
            external_memory: Optional external memory instance.
        """
        self.agent_name = agent_name
        self.external_memory = external_memory
        self.agent_manager = FlotorchCrewAIAgent(
            agent_name,
            custom_config=custom_config,
            custom_tools=custom_tools
        )

    def get_agent(self):
        """
        Get the CrewAI agent with tools enabled by default.

        Returns:
            CrewAI Agent instance.
        """
        return self.agent_manager.get_agent()

    def create_task(self, description=None, expected_output=None):
        """
        Create a CrewAI task with custom or default settings.

        Args:
            description: Optional task description.
            expected_output: Optional expected output description.

        Returns:
            CrewAI Task instance.
        """
        agent = self.get_agent()
        if description:
            description = description
        else:
            description = (
                "Get the capital city of zimbobwe using get_capital_city_http and "
                "also get the weather for New York using get_weather_sse to test "
                "both streamable-http and SSE transports. Also calculate the sum "
                "of 15 and 25 using calculate_sum tool. Include ALL tool outputs "
                "in your final response, even if they return 'not found' or errors. "
                "Do NOT skip any tool results. WEATHER RULE: If weather tool returns "
                "multiple lines, use ONLY the LAST line. This is critical for "
                "correct weather data."
        )

        if expected_output:
            expected_output = expected_output
        else:
            expected_output = (
                "A response that includes the exact tool outputs: the capital city "
                "from get_capital_city_http, the weather information from "
                "get_weather_sse, and the calculation result from calculate_sum"
        )
        return Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            output_pydantic=TaskOutput
        )

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'agent_manager') and self.agent_manager:
            self.agent_manager.cleanup()

    def __del__(self):
        """Destructor to clean up resources."""
        try:
            self.cleanup()
        except Exception:
            pass
import os
import sys
from typing import cast
from flotorch.adk.utils.warning_utils import SuppressOutput

from flotorch.adk.llm import FlotorchADKLLM
from google.adk.agents import LlmAgent
from google.adk.tools import preload_memory, load_memory
from typing import Any, Dict
from dotenv import load_dotenv
from pydantic import create_model, Field
import httpx
import inspect
import time
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams, SseConnectionParams
from flotorch.sdk.utils.logging_utils import log_object_creation
from flotorch.sdk.utils.http_utils import http_get


load_dotenv()

def sanitize_agent_name(name: str) -> str:
    """
    Sanitize agent name to be a valid identifier.
    Replaces invalid characters with underscores and ensures it starts with a letter or underscore.
    """
    import re
    
    # Replace invalid characters with underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', name)
    
    # Ensure it starts with a letter or underscore
    if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
        sanitized = f"agent_{sanitized}"
    
    # Remove consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Remove leading/trailing underscores
    sanitized = sanitized.strip('_')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = "agent"
    
    return sanitized

def schema_to_pydantic_model(name: str, schema: dict):
    """
    Dynamically create a Pydantic model from a JSON schema dict.
    If only one property, use its name (capitalized) plus 'Input' or 'Output' as the model name.
    Otherwise, use the provided name.
    """
    properties = schema.get("properties", {})
    if len(properties) == 1:
        prop_name = next(iter(properties))
        if name.lower().startswith("input"):
            model_name = f"{prop_name.capitalize()}Input"
        elif name.lower().startswith("output"):
            model_name = f"{prop_name.capitalize()}Output"
        else:
            model_name = f"{prop_name.capitalize()}Schema"
    else:
        model_name = name
    fields = {}
    for prop, prop_schema in properties.items():
        field_type = str  # Default to string
        if prop_schema.get("type") == "integer":
            field_type = int
        elif prop_schema.get("type") == "number":
            field_type = float
        elif prop_schema.get("type") == "boolean":
            field_type = bool
        description = prop_schema.get("description", "")
        fields[prop] = (field_type, Field(description=description))
    return create_model(model_name, **fields)


class FlotorchADKAgent:
    """
    Manager/config class for Flotorch agent. Builds LlmAgent from config on demand.
    Supports on-demand config reload based on interval in config['sync'].
    
    Args:
        agent_name: Name of the agent
        enable_memory: Enable memory functionality
        config: Optional custom configuration dict
        custom_tools: List of custom user-defined tools to add to the agent
        base_url: Optional base URL for the API. Falls back to FLOTORCH_BASE_URL env var
        api_key: Optional API key for authentication. Falls back to FLOTORCH_API_KEY env var
    
    Usage: 
        flotroch = FlotorchADKClient("agent-one", enable_memory=True, custom_tools=[my_tool])
        agent = flotroch.get_agent()
    """
    def __init__(self, agent_name: str, enable_memory: bool = False, config=None, custom_tools: list = None, base_url: str = None, api_key: str = None):
        self.agent_name = agent_name
        self.enable_memory = enable_memory
        self.custom_tools = custom_tools or []
        
        # Store base_url and api_key, using environment variables as fallback
        self.base_url = base_url or os.environ.get("FLOTORCH_BASE_URL")
        self.api_key = api_key or os.environ.get("FLOTORCH_API_KEY")
        
        if config:
            self.config = config
        else:
            self.config = self._fetch_agent_config(agent_name)
        self._agent = self._build_agent_from_config(self.config)
        self._last_reload = time.time()
        
        # Log object creation
        log_object_creation("FlotorchADKAgent", agent_name=self.agent_name, memory_enabled=self.enable_memory)

    def _fetch_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Fetch agent config from API.
        """
        if not self.base_url:
            raise ValueError("base_url is required to fetch agent configuration")
        
        if not self.api_key:
            raise ValueError("api_key is required to fetch agent configuration")
        
        # Construct the API URL
        url = f"{self.base_url.rstrip('/')}/v1/agents/{agent_name}"
        
        # Set up headers with authentication
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            # Fetch the agent configuration from the API
            response = http_get(url, headers=headers)
            return response
        except Exception as e:
            raise e
            

    def _build_tools(self, config: Dict[str, Any]):
        tools = []
        
        # Add memory tools if memory is enabled
        if self.enable_memory:
            tools.append(preload_memory)  # Automatic memory loading (preprocessor)
            # tools.append(load_memory)     # Manual memory search (function tool)
        
        # Add MCP tools with improved error handling
        for tool_cfg in config.get("tools", []):
            if tool_cfg.get("type") == "MCP":
                mcp_conf = tool_cfg["config"]
                try:
                    # Build connection params with better defaults
                    auth_token = os.environ.get("FLOTORCH_AUTH_TOKEN")
                    headers = dict(mcp_conf.get("headers", {}))
                    if auth_token:
                        headers["Authorization"] = f"Bearer {auth_token}"
                    
                    # Use custom silence context manager to suppress ALL output
                    with SuppressOutput():
                        if mcp_conf.get("transport") == "STREAM":
                            conn_params = StreamableHTTPConnectionParams(
                                url=mcp_conf["url"],
                                headers=headers,
                                timeout=mcp_conf.get("timeout", 10_000) / 1000.0,  # 10s timeout
                                sse_read_timeout=mcp_conf.get("sse_read_timeout", 10_000) / 1000.0,  # 10s timeout
                                terminate_on_close=False,  # Always False to prevent async issues
                                auth_config=None,  # Explicitly set to None to avoid warnings
                                max_retries=1  # Allow 1 retry for connection stability
                            )
                        elif mcp_conf.get("transport") == "SSE":
                            conn_params = SseConnectionParams(
                                url=mcp_conf["url"],
                                headers=headers,
                                timeout=mcp_conf.get("timeout", 10_000) / 1000.0,  # 10s timeout
                                sse_read_timeout=mcp_conf.get("sse_read_timeout", 10_000) / 1000.0  # 10s timeout
                            )
                        
                        # Create toolset with error handling
                        toolset = MCPToolset(
                            connection_params=conn_params
                        )
                        
                        # Only add working toolsets
                        tools.append(toolset)
                        
                except Exception as e:
                    # Silently skip failed tools instead of printing warnings
                    continue
        
        # Add custom user-defined tools
        if self.custom_tools:
            tools.extend(self.custom_tools)
        
        return tools

    def _build_agent_from_config(self, config):
        llm = FlotorchADKLLM(
            model_id=config["llm"]["callableName"],
            api_key=self.api_key,
            base_url=self.base_url
        )
        tools = self._build_tools(config)
        input_schema = None
        output_schema = None
        if "inputSchema" in config and config["inputSchema"] is not None:
            input_schema = schema_to_pydantic_model("InputSchema", config["inputSchema"])
        if "outputSchema" in config and config["outputSchema"] is not None:
            output_schema = schema_to_pydantic_model("OutputSchema", config["outputSchema"])
        return LlmAgent(
            name=sanitize_agent_name(config["name"]),
            model=llm,
            instruction=config["systemPrompt"],
            description=config["description"] if "description" in config else '',
            tools=tools,
            input_schema=input_schema,
            output_schema=output_schema
        )

    def get_agent(self):
        return cast(LlmAgent, AgentProxy(self))
    
    def _get_synced_agent(self) -> LlmAgent:
        # Check if sync is enabled and interval has passed
        sync_enabled = self.config.get('syncEnabled', False)
        if not sync_enabled:
            return self._agent
            
        sync_interval = self.config.get('syncInterval', 1000000)
        now = time.time()
        if now - self._last_reload > sync_interval:
            print("[Sync] Reload interval passed. Attempting to reload agent...")
            try:
                new_config = self._fetch_agent_config(self.agent_name)
                if new_config and new_config != self.config:
                    self.config = new_config
                    self._agent = self._build_agent_from_config(self.config)
                    print("[Sync] Agent successfully reloaded.")
            except Exception as e:
                print(f"[Warning] [Sync] Failed to reload agent config. Using previous agent. Reason: {e}")
            finally:
                self._last_reload = now
        return self._agent



class AgentProxy(LlmAgent):
    def __init__(self, manager: "FlotorchADKAgent"):
        self._manager = manager

    def __getattr__(self, item):
        return getattr(self._manager._get_synced_agent(), item)

    def __setattr__(self, key, value):
        if key == "_manager":
            return object.__setattr__(self, key, value)
        return setattr(self._manager._get_synced_agent(), key, value)
    

# Usage:
# Warning suppressions are automatically applied when importing this module.
# To disable: set environment variable FLOTORCH_NO_AUTO_SUPPRESS=1
# flotroch = FlotorchADKClient("agent-one", enable_memory=True)
# agent = flotroch.get_agent()
# memory_service = FlotorchMemoryService(...)  # Create your memory service
# runner = Runner(agent=agent, memory_service=memory_service, ...)  # Pass memory service to runner
# Now use agent as a normal LlmAgent with memory support! 



from typing import List, Dict, Tuple,Optional

from flotorch.sdk.utils.llm_utils import invoke, async_invoke, parse_llm_response, LLMResponse
from flotorch.sdk.utils.logging_utils import log_object_creation, log_error

class FlotorchLLM:
    def __init__(self, model_id: str, api_key: str, base_url: str):
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url
        
        # Log object creation
        log_object_creation("FlotorchLLM", model_id=model_id, base_url=base_url)
    
    def invoke(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None, response_format=None, extra_body: Optional[Dict] = None, **kwargs) -> LLMResponse:
        try:
            response = invoke(messages, self.model_id, self.api_key, self.base_url, tools=tools, response_format=response_format, extra_body=extra_body, **kwargs)
            return parse_llm_response(response)
        except Exception as e:
            log_error("FlotorchLLM.invoke", e)
            raise

    async def ainvoke(self, messages: List[Dict[str, str]], tools: Optional[List[Dict]] = None, response_format=None, extra_body: Optional[Dict] = None, **kwargs) -> LLMResponse:
        """
        Invoke LLM with individual parameters instead of a complete payload.
        Creates the payload internally from the provided parameters.
        """
        try:
            # Use the utility function that handles payload creation
            response = await async_invoke(messages, self.model_id, self.api_key, self.base_url, tools=tools, response_format=response_format, extra_body=extra_body, **kwargs)
            return parse_llm_response(response)
        except Exception as e:
            log_error("FlotorchLLM.ainvoke", e)
            raise
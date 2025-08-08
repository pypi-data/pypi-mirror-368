import time
from typing import List
from rebel.models import (
    AssistantInput,
    AssistantOutput,
    Function,
    ToolCall
)
from rebel.collector import APIClient


class OpenAIAPIClient(APIClient):
    """An API client that interacts with an OpenAI-compatible API.

    This client handles the conversion of REBEL's data models to the format
    expected by the OpenAI SDK, manages streaming responses, and parses both
    text content and tool calls.

    Attributes:
        model (str): The name of the model to use for the requests.
        client (OpenAI): The synchronous OpenAI client instance.
    """
    def __init__(self, api_key: str, model: str, base_url: str):
        """Initializes the OpenAIAPIClient.

        Args:
            api_key (str): The API key for authentication.
            model (str): The model name (e.g., 'gpt-4').
            base_url (str): The base URL of the API endpoint.
        
        Raises:
            ImportError: If the `openai` package is not installed.
        """
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
        
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
    
    def request(self, input: AssistantInput) -> AssistantOutput:
        """Makes a streaming request to the OpenAI API.

        This method constructs the request, handles the streaming response to
        build up the output content and tool calls, and returns a structured
        `AssistantOutput`.

        Args:
            input (AssistantInput): The input for the assistant.

        Returns:
            AssistantOutput: The structured output from the API call.
        
        Raises:
            Exception: If the API request fails.
        """
        start_time = time.time()
        actual_output = ""
        tools_called: List[ToolCall] = []
        context: List[str] = []
        
        # Convert messages to OpenAI format
        messages = [msg.model_dump(exclude_none=True) for msg in input.messages]
        
        # Prepare request parameters, ensuring model is not duplicated
        request_params = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            **{k: v for k, v in input.api_params.items() if k != "model"}
        }
        
        try:
            stream = self.client.chat.completions.create(**request_params)
            
            current_tool_calls = {}
            
            for chunk in stream:
                if chunk.choices:
                    choice = chunk.choices[0]
                    delta = choice.delta
                    
                    if delta.content:
                        actual_output += delta.content
                    
                    if delta.tool_calls:
                        for tc_delta in delta.tool_calls:
                            tc_index = tc_delta.index if hasattr(tc_delta, 'index') else 0
                            
                            if tc_index not in current_tool_calls:
                                current_tool_calls[tc_index] = {"id": "", "type": "function", "function": {"name": "", "arguments": ""}}
                            
                            if tc_delta.id: current_tool_calls[tc_index]["id"] = tc_delta.id
                            if tc_delta.type: current_tool_calls[tc_index]["type"] = tc_delta.type
                            if tc_delta.function:
                                if tc_delta.function.name: current_tool_calls[tc_index]["function"]["name"] += tc_delta.function.name
                                if tc_delta.function.arguments: current_tool_calls[tc_index]["function"]["arguments"] += tc_delta.function.arguments
                    
                    if choice.finish_reason == "tool_calls" and current_tool_calls:
                        tools_called = [ToolCall(**tc_data) for tc_data in current_tool_calls.values() if tc_data["function"]["name"]]
        
        except Exception as e:
            raise Exception(f"OpenAI API request failed: {str(e)}")
        
        completion_time = time.time() - start_time
        
        return AssistantOutput(
            output=actual_output.strip(),
            tools_called=tools_called,
            context=context,
            execution_time=completion_time
        )

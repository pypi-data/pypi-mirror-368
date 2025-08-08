from typing import List, Dict, Any
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
import instructor


class OpenAIClientWrapper:
    """A wrapper around the OpenAI client that adds support for structured data extraction.

    This class uses the `instructor` library to patch the OpenAI client, enabling
    it to generate Pydantic models directly from the LLM's output.

    Attributes:
        client (OpenAI): The original OpenAI client instance.
        patched_client: The `instructor`-patched client for structured extraction.
        client_params (dict): A dictionary of default parameters for API requests.
    """
    def __init__(self, config: dict):
        """Initializes the OpenAIClientWrapper.

        Args:
            config (dict): Configuration dictionary containing 'api_key', 'base_url',
                'model', and other optional parameters.
        """
        self.client = OpenAI(
            api_key=config['api_key'],
            base_url=config['base_url']
        )
        self.patched_client = instructor.from_openai(self.client)

        client_params = {'model': config['model']}
        optional_client_params = ['temperature', 'max_tokens', 'timeout']    
        for param in optional_client_params:
            value = config.get(param)
            if value is not None:
                client_params[param] = value
        self.client_params = client_params

    
    def generate(self, messages: List[Dict]) -> ChatCompletion:
        """Generates a standard chat completion.

        Args:
            messages (List[Dict]): A list of messages in the OpenAI chat format.

        Returns:
            ChatCompletion: The raw response from the OpenAI API.
        """
        return self.client.chat.completions.create(
            messages=messages,
            **self.client_params
        )


    def generate_instructed(self, messages: List[Dict], response_model: Any) -> Any:
        """Generates a structured response based on a Pydantic model.

        Args:
            messages (List[Dict]): The list of messages for the prompt.
            response_model (Any): The Pydantic model to structure the response into.

        Returns:
            Any: An instance of the `response_model` populated with the LLM's output.
        """
        result, _ = self.patched_client.chat.completions.create_with_completion(
            response_model=response_model,
            messages=messages,
            **self.client_params
        )
        return result

from deepeval.models.base_model import DeepEvalBaseLLM
from openai import OpenAI, AsyncOpenAI


class OpenAIClientLLM(DeepEvalBaseLLM):
    """A custom DeepEval language model that uses an OpenAI-compatible client.

    This class provides a bridge between the DeepEval framework and any LLM that
    adheres to the OpenAI API standard, allowing it to be used as a "judge" model
    for AI-based evaluations.

    Attributes:
        client (OpenAI): The synchronous OpenAI client.
        aclient (AsyncOpenAI): The asynchronous OpenAI client.
        client_params (dict): A dictionary of parameters to be passed to the
            chat completions endpoint, such as model name and temperature.
    """
    def __init__(self, config: dict, *args, **kwargs):
        """Initializes the OpenAIClientLLM.

        Args:
            config (dict): A configuration dictionary containing 'api_key',
                'base_url', 'model', and other optional parameters.
            *args: Variable length argument list for DeepEvalBaseLLM.
            **kwargs: Arbitrary keyword arguments for DeepEvalBaseLLM.
        """
        self.client = OpenAI(
            api_key=config['api_key'],
            base_url=config['base_url']
        )
        self.aclient = AsyncOpenAI(
            api_key=config['api_key'],
            base_url=config['base_url']
        )

        client_params = {'model': config['model']}
        optional_client_params = ['temperature', 'max_tokens', 'timeout']    

        for param in optional_client_params:
            value = config.get(param)
            if value is not None:
                client_params[param] = value
        self.client_params = client_params
        
        # model_name is not used here but passed to the parent constructor
        super().__init__(model=config['model'], *args, **kwargs)

    def load_model(self, *args, **kwargs):
        """Loads the model. This is a no-op as the client is already configured."""
        return None

    def generate(self, prompt: str) -> str:
        """Generates a response from the LLM synchronously.

        Args:
            prompt (str): The input prompt for the model.

        Returns:
            str: The generated text content.
        """
        return self.client.chat.completions.create(
            messages=[{'role': 'user', 'content': prompt}],
            **self.client_params
        ).choices[0].message.content

    async def a_generate(self, prompt: str) -> str:
        """Generates a response from the LLM asynchronously.

        Args:
            prompt (str): The input prompt for the model.

        Returns:
            str: The generated text content.
        """
        completions = await self.aclient.chat.completions.create(
            messages=[{'role': 'user', 'content': prompt}],
            **self.client_params
        )
        return completions.choices[0].message.content

    def get_model_name(self) -> str:
        """Returns the name of the model being used.

        Returns:
            str: The configured model name.
        """
        return self.client_params['model']

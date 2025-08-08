from abc import ABC, abstractmethod

from rebel.models import AssistantInput, AssistantOutput

class APIClient(ABC):
    """An abstract base class that defines the interface for an API client.

    All clients used to make requests to LLM APIs must inherit from this class
    and implement the `request` method.
    """
    @abstractmethod
    def request(self, input: AssistantInput) -> AssistantOutput:
        """Sends a request to an LLM API and returns the structured output.

        Args:
            input (AssistantInput): The input for the assistant, including messages
                and API parameters.

        Returns:
            AssistantOutput: The structured output from the assistant.
        """
        pass

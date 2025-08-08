from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase
from abc import ABC, abstractmethod

from rebel.models import (
    Metric,
    AssistantOutput,
    EvaluationResult,
    AssistantInput,
    EvaluationVerdict
)
from rebel.deepeval.client import OpenAIClientLLM

class DeepevalMetric(Metric, ABC):
    """An abstract base class for integrating DeepEval metrics into the REBEL framework.

    Inherit from this class to wrap any metric from the DeepEval library, allowing
    it to be used seamlessly within a REBEL benchmark.

    Attributes:
        judge_llm (OpenAIClientLLM): The LLM client used to perform the evaluation.
    """
    judge_llm: OpenAIClientLLM
    
    @abstractmethod
    def get_deepeval_metric(self) -> BaseMetric:
        """Returns an instantiated DeepEval metric object.

        This method should be implemented by subclasses to construct and return
        the specific DeepEval metric to be used (e.g., GEval, AnswerRelevancy).

        Returns:
            BaseMetric: An instance of a DeepEval metric.
        """
        pass
    
    def measure(
        self,
        input: AssistantInput,
        expected: AssistantOutput,
        actual: AssistantOutput
    ) -> EvaluationResult:
        """Measures the performance using the wrapped DeepEval metric.

        This method converts the REBEL data models into a DeepEval `LLMTestCase`,
        runs the DeepEval metric's `measure` method, and converts the result
        back into a REBEL `EvaluationResult`.

        Args:
            input (AssistantInput): The original input to the assistant.
            expected (AssistantOutput): The expected output.
            actual (AssistantOutput): The actual output from the assistant.

        Returns:
            EvaluationResult: The result of the evaluation.
        """
        metric = self.get_deepeval_metric()
        test_case = convert_to_test_case(input, expected, actual)
        
        # DeepEval's measure method is synchronous
        metric.measure(test_case)
        return EvaluationResult(
            score=metric.score,
            verdict=EvaluationVerdict.PASSED if metric.success else EvaluationVerdict.FAILED,
            reason=metric.reason
        )

def convert_to_test_case(
    input: AssistantInput,
    expected: AssistantOutput,
    actual: AssistantOutput
) -> LLMTestCase:
    """Converts REBEL's data models to a DeepEval `LLMTestCase`.

    Args:
        input (AssistantInput): The original input.
        expected (AssistantOutput): The expected output.
        actual (AssistantOutput): The actual output.

    Returns:
        LLMTestCase: A DeepEval test case object.
    """
    # Taking the last user message as the primary input for simplicity
    user_input_content = ""
    for msg in reversed(input.messages):
        if msg.role == 'user':
            user_input_content = msg.content
            break

    return LLMTestCase(
        input=user_input_content,
        actual_output=actual.output,
        expected_output=expected.output,
        context=actual.context,
    )

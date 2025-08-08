from pydantic import BaseModel, ConfigDict
from typing import Annotated
from pydantic.functional_serializers import PlainSerializer
from abc import ABC, abstractmethod
from enum import Enum

from rebel.models import AssistantOutput, AssistantInput


class EvaluationVerdict(str, Enum):
    """Enumeration for the possible outcomes of an evaluation.

    Attributes:
        PASSED (str): Indicates that the evaluation met the success criteria.
        FAILED (str): Indicates that the evaluation did not meet the success criteria.
        ERROR (str): Indicates that an error occurred during the evaluation process itself.
    """
    PASSED = 'passed'
    FAILED = 'failed'
    ERROR = 'error'


class EvaluationResult(BaseModel):
    """Represents the detailed outcome of a single metric's evaluation.

    This class encapsulates all the information generated when a metric is used to
    compare an actual output against an expected one.

    Attributes:
        score (float): The numerical score assigned by the metric, where the scale
            is defined by the metric itself (e.g., 0.0 to 1.0).
        verdict (EvaluationVerdict): The final qualitative judgment (PASSED, FAILED, or ERROR).
        reason (str): A human-readable explanation for the score and verdict.
    """
    score: float
    verdict: EvaluationVerdict
    reason: str


class Metric(ABC, BaseModel):
    """An abstract base class that defines the interface for all evaluation metrics.

    To create a new metric, you must inherit from this class and implement the
    `measure` and `get_name` methods.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    @abstractmethod
    def measure(
        self,
        input: AssistantInput,
        expected: AssistantOutput,
        actual: AssistantOutput
    ) -> EvaluationResult:
        """Compares the actual output against the expected output for a given input.

        This is the core method of any metric, containing the logic for scoring
        the performance of the assistant's response.

        Args:
            input (AssistantInput): The original input given to the assistant.
            expected (AssistantOutput): The ground truth or expected output.
            actual (AssistantOutput): The actual output produced by the assistant.

        Returns:
            EvaluationResult: An object containing the score, verdict, and reason.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Returns a unique, human-readable name for the metric instance.

        This is often used for logging and reporting purposes. It can include
        hyperparameters of the metric (e.g., "BERTScore-F1").

        Returns:
            str: The name of the metric.
        """
        pass


def serialize_metric(metric: 'Metric') -> dict:
    """Provides custom serialization logic for any `Metric` subclass.

    This function is used by Pydantic to convert a Metric object into a JSON-serializable
    dictionary, which is useful for logging or storing test configurations.

    Args:
        metric (Metric): The metric instance to serialize.

    Returns:
        dict: A dictionary containing the metric's name, class type, and module path.
    """
    return {
        'name': metric.get_name(),
        'type': metric.__class__.__name__,
        'module': metric.__class__.__module__
    }


SerializableMetric = Annotated[
    Metric, 
    PlainSerializer(serialize_metric, return_type=dict, when_used='json')
]
"""A type alias for `Metric` that includes custom JSON serialization logic.

By using `Annotated` with `PlainSerializer`, any Pydantic model that includes a field
of type `SerializableMetric` will automatically use the `serialize_metric` function
when it is converted to JSON.
"""

from pydantic import BaseModel, ConfigDict
from enum import Enum
from typing import List, Dict, Any, Optional

from rebel.models import AssistantInput, AssistantOutput, SerializableMetric, Message


class RetryAggregationStrategy(str, Enum):
    """Defines strategies for aggregating metrics from multiple retry attempts."""
    MIN = 'min'
    MAX = 'max'
    MEAN = 'mean'
    MEDIAN = 'median'


class RetryParams(BaseModel):
    """Specifies the parameters for retrying a test case.

    Attributes:
        count (int): The number of times to retry a test case upon failure.
        aggregation_strategy (Optional[RetryAggregationStrategy]): The strategy to use for
            aggregating metrics across all attempts. Defaults to 'mean'.
    """
    count: int
    aggregation_strategy: Optional[RetryAggregationStrategy] = RetryAggregationStrategy.MEAN


class ParameterGrid(BaseModel):
    """Represents a grid of parameters for generating multiple test case variations.

    This class holds a dictionary of parameters where each value is a list of
    possible options. The `expand` method can be used to generate the Cartesian
    product of these options.

    Attributes:
        parameters (Dict[str, List[Any]]): A dictionary where keys are parameter names
            and values are lists of possible values for that parameter.
    """
    parameters: Dict[str, List[Any]]
    
    def expand(self) -> List[Dict[str, Any]]:
        """Generates all unique parameter combinations from the grid.

        This method computes the Cartesian product of the parameter lists.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
            represents a unique combination of parameters.
        """
        import itertools
        keys = list(self.parameters.keys())
        values = list(self.parameters.values())
        return [dict(zip(keys, combo)) for combo in itertools.product(*values)]


class TestSuite(BaseModel):
    """Defines a suite of tests that expands into multiple concrete test cases.

    A TestSuite is a high-level configuration that uses a parameter grid to generate
    a set of related test cases. It specifies the shared context, expected output
    structure, and metrics for an entire group of tests.

    Attributes:
        name (str): The name of the test suite.
        tags (List[str]): A list of tags for categorizing and filtering the suite.
        retry_params (RetryParams): Configuration for retrying failed tests.
        messages (List[Message]): The list of messages that form the input prompt.
        api_params (Dict[str, Any]): Default API parameters for all tests in the suite.
            These can be overridden by the parameter_grid.
        parameter_grid (ParameterGrid): A grid of parameters to generate variations of
            test cases. These have higher priority than `api_params`.
        expected_output (AssistantOutput): The expected output structure or content.
        metrics (List[SerializableMetric]): A list of metrics to evaluate the
            outputs of the test cases generated from this suite.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    name: str
    tags: List[str]
    retry_params: RetryParams
    
    messages: List[Message]
    api_params: Dict[str, Any]
    parameter_grid: ParameterGrid
    
    expected_output: AssistantOutput
    
    metrics: List[SerializableMetric]


class TestInfo(BaseModel):
    """A base model containing common information for a single test case.

    This class encapsulates the core, non-varying details of a test, which are
    shared across all retry attempts for that test.

    Attributes:
        name (str): The name of the test case.
        tags (List[str]): A list of tags for categorization.
        retry_params (RetryParams): Retry configuration, needed for post-evaluation
            aggregation of results.
        input (AssistantInput): The fully constructed input for the assistant.
        expected_output (AssistantOutput): The expected output for the test case.
    """
    name: str
    tags: List[str]
    retry_params: RetryParams
    input: AssistantInput
    expected_output: AssistantOutput


class TestCase(TestInfo):
    """Represents a single, concrete test case with a fixed set of parameters.

    This class inherits from TestInfo and adds the specific metrics to be used for
    evaluation. It represents a single runnable test that may be executed
    multiple times according to its retry parameters.

    Attributes:
        metrics (List[SerializableMetric]): The list of metrics to apply to the
            results of this specific test case.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    metrics: List[SerializableMetric]


class TestAttempt(TestCase):
    """Represents a single attempt to run a specific test case.

    This class inherits all information from a TestCase and adds an attempt number
    to distinguish it from other retries of the same test.

    Attributes:
        number (int): The sequential number of this attempt (e.g., 1, 2, 3).
    """
    number: int
    
    def get_name(self) -> str:
        """Generates a unique name for the test attempt.

        Returns:
            str: The name of the test case appended with the attempt number.
        """
        return f'{self.name}_[Attempt {self.number}]'


class TestAttemptExecuted(TestAttempt):
    """Represents a test attempt after it has been executed.

    This class extends TestAttempt by including the output received from the
    assistant, making it ready for evaluation against the expected output.

    Attributes:
        actual_output (AssistantOutput): The actual output returned by the
            assistant during this attempt.
    """
    actual_output: AssistantOutput

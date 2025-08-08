from typing import List

from rebel.models import (
    TestAttemptExecuted,
    SerializableMetric,
    EvaluationResult,
    AssistantOutput,
    TestCase
)


class EvaluationAttempt(TestAttemptExecuted):
    """Represents a single test attempt that is ready to be evaluated by a specific metric.

    This class pairs an executed test attempt (which includes the input, actual output,
    and expected output) with one of the metrics designated for its evaluation.

    Attributes:
        metric (SerializableMetric): The specific metric that will be used to evaluate
            this test attempt.
    """
    metric: SerializableMetric


class EvaluationAttemptEvaluated(EvaluationAttempt):
    """Represents a test attempt after it has been evaluated by its designated metric.

    This class extends `EvaluationAttempt` by including the `EvaluationResult`, which
    contains the score, verdict, and reasoning from the metric's calculation.

    Attributes:
        evaluation_result (EvaluationResult): The outcome of applying the metric to the
            test attempt's actual and expected outputs.
    """
    evaluation_result: EvaluationResult


class TestCaseEvaluated(TestCase):
    """Represents a fully evaluated test case, including aggregated results from all attempts.

    This class provides a comprehensive summary of a single test case's performance
    after all its retry attempts have been executed and every relevant metric has been applied.

    Attributes:
        actual_outputs (List[AssistantOutput]): A list of all the actual outputs
            generated across all retry attempts for this test case.
        evaluation_results (List[EvaluationResult]): A flat list of all individual
            evaluation results from every metric applied to every attempt.
        aggregated_result (EvaluationResult): The final, single evaluation result that
            summarizes the performance across all attempts, calculated using the
            aggregation strategy defined in the test's `retry_params`.
    """
    actual_outputs: List[AssistantOutput]
    evaluation_results: List[EvaluationResult]
    aggregated_result: EvaluationResult

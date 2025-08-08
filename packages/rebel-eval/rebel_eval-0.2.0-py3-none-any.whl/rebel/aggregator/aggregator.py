from typing import List
from collections import defaultdict
import statistics

from rebel.models import (
    EvaluationAttemptEvaluated,
    TestCaseEvaluated,
    RetryAggregationStrategy,
    EvaluationResult,
    EvaluationVerdict
)


class Aggregator:
    def aggregate_evaluation_results(
        self,
        evaluation_results: List[EvaluationAttemptEvaluated]
    ) -> List[TestCaseEvaluated]:
        if not evaluation_results:
            return []
        
        # fold flatten evaluation results into test cases for a single metric
        grouped_evaluation_results = defaultdict(list)
        
        for evaluation_result in evaluation_results:
            metric_postfix = evaluation_result.metric.get_name()
            evaluation_result_group_name = f'{evaluation_result.name}_[{metric_postfix}]'
            grouped_evaluation_results[evaluation_result_group_name].append(evaluation_result)
        
        evaluated_test_cases: List[TestCaseEvaluated] = []

        for group_name in grouped_evaluation_results:
            # sort by attempt number
            group_evaluations = grouped_evaluation_results[group_name]
            group_evaluations.sort(key=lambda x: x.number)

            if not group_evaluations:
                continue
            
            aggregated_result = self._aggregate_evaluation_result(group_evaluations)
            first_test_attempt = group_evaluations[0]
            
            evaluated_test_case = TestCaseEvaluated(
                name=first_test_attempt.name,
                tags=first_test_attempt.tags.copy(),
                retry_params=first_test_attempt.retry_params.copy(),
                input=first_test_attempt.input.copy(),
                expected_output=first_test_attempt.expected_output.copy(),
                metrics=first_test_attempt.metrics.copy(),
                actual_outputs=[
                    evaluation.actual_output for evaluation in group_evaluations
                ],
                evaluation_results=[evaluation.evaluation_result for evaluation in group_evaluations],
                aggregated_result=aggregated_result
            )
            
            evaluated_test_cases.append(evaluated_test_case)

        return evaluated_test_cases
    
    
    def _aggregate_evaluation_result(self, evaluations: List[EvaluationAttemptEvaluated]) -> EvaluationResult:
        if not evaluations:
            raise ValueError(evaluations)
        
        # assume that all evaluations have single retry params
        aggregation_strategy = evaluations[0].retry_params.aggregation_strategy
        
        # ignore insuccessful tests
        evaluation_results = [
            evaluation.evaluation_result for evaluation in evaluations
            if evaluation.evaluation_result.verdict != EvaluationVerdict.ERROR
        ]
        scores = [result.score for result in evaluation_results]
        verdicts = [result.verdict for result in evaluation_results]
        
        if not evaluation_results:
            return EvaluationResult(
                score=0.0,
                verdict=EvaluationVerdict.ERROR,
                reason='All evaluation attempts failed'
            )
        
        if aggregation_strategy == RetryAggregationStrategy.MIN:
            score = min(scores)
            verdict = EvaluationVerdict.PASSED
            if EvaluationVerdict.FAILED in verdicts:
                verdict = EvaluationVerdict.FAILED
        
        elif aggregation_strategy == RetryAggregationStrategy.MAX:
            score = max(scores)
            verdict = EvaluationVerdict.FAILED
            if EvaluationVerdict.PASSED in verdicts:
                verdict = EvaluationVerdict.PASSED
        
        elif aggregation_strategy == RetryAggregationStrategy.MEAN:
            score = statistics.mean(scores)
            # for MEAN, use majority voting or threshold-based approach
            passed_count = sum(1 for v in verdicts if v == EvaluationVerdict.PASSED)
            failed_count = len(verdicts) - passed_count
            # taking FAILED if equal
            verdict = EvaluationVerdict.PASSED if passed_count > failed_count else EvaluationVerdict.FAILED
        
        elif aggregation_strategy == RetryAggregationStrategy.MEDIAN:
            score = statistics.median(scores)
            # for MEDIAN, use majority voting similar to MEAN
            passed_count = sum(1 for v in verdicts if v == EvaluationVerdict.PASSED)
            failed_count = len(verdicts) - passed_count
            verdict = EvaluationVerdict.PASSED if passed_count > failed_count else EvaluationVerdict.FAILED
            
        return EvaluationResult(
            score=score,
            verdict=verdict,
            reason='' # can not specify for a group, check out detailed results if needed
        )

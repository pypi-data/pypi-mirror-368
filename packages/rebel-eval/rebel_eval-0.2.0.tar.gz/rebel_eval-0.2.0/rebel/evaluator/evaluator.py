from typing import List
from tqdm import tqdm
import threading
from joblib import Parallel, delayed

from rebel.models import (
    TestAttemptExecuted,
    EvaluationAttempt,
    EvaluationAttemptEvaluated,
    EvaluationVerdict,
    EvaluationResult
)


class Evaluator:
    def __init__(self, num_workers: int):
        self.num_workers = num_workers


    def unfold_test_attempts(self, test_attempt_executed: List[TestAttemptExecuted]) -> List[EvaluationAttempt]:
        evaluation_attempts = []
        
        for test_attempt in test_attempt_executed:
            for metric in test_attempt.metrics:
                test_attempt_params = test_attempt.model_dump()
                test_attempt_params['metrics'] = test_attempt.metrics
                
                evaluation_attempt = EvaluationAttempt.model_validate({
                    **test_attempt_params,
                    'metric': metric
                })
                
                evaluation_attempts.append(evaluation_attempt)
        
        return evaluation_attempts

    
    def evaluate(
        self,
        evaluation_attempts: List[EvaluationAttempt]
    ) -> List[EvaluationAttemptEvaluated]:
        print(f"🧮 Measuring test cases using {self.num_workers} parallel workers...")
        
        pbar = tqdm(total=len(evaluation_attempts), desc='Evaluting test results...')
        lock = threading.Lock()
        
        def evaluate_single_attempt(evaluation_attempt: EvaluationAttempt) -> EvaluationAttemptEvaluated:
            try:
                result = evaluation_attempt.metric.measure(
                    input=evaluation_attempt.input,
                    expected=evaluation_attempt.expected_output,
                    actual=evaluation_attempt.actual_output,
                )
            except Exception as e:
                result = EvaluationResult(
                    score=0.0,
                    verdict=EvaluationVerdict.ERROR,
                    reason=str(e)
                )

            with lock:
                emoji = '✅'
                if result.verdict == EvaluationVerdict.FAILED:
                    emoji = '❌'
                if result.verdict == EvaluationVerdict.ERROR:
                    emoji = '⚠️'

                pbar.update()
                pbar.set_postfix_str(f"{emoji} {evaluation_attempt.name}(attempt {evaluation_attempt.number})")
            
            evaluation_attempt_params = evaluation_attempt.model_dump()
            evaluation_attempt_params['metrics'] = evaluation_attempt.metrics
            evaluation_attempt_params['metric'] = evaluation_attempt.metric
            return EvaluationAttemptEvaluated.model_validate({
                **evaluation_attempt_params,
                'evaluation_result': result
            })
        
        try:
            return Parallel(n_jobs=self.num_workers, backend='threading')(
                delayed(evaluate_single_attempt)(evaluation_attempt)
                for evaluation_attempt in evaluation_attempts
            )
        finally:
            pbar.close()

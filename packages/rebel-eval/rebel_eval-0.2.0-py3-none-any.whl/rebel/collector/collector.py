from typing import List
from joblib import Parallel, delayed
import threading
from tqdm import tqdm

from rebel.models import TestAttemptExecuted, TestAttempt
from rebel.collector import APIClient


class Collector:
    def __init__(self, api_client: APIClient, num_workers: int):
        self.api_client = api_client
        self.num_workers = num_workers
    
    
    def collect_test_results(self, test_attempts: List[TestAttempt]) -> List[TestAttemptExecuted]:
        pbar = tqdm(total=len(test_attempts), desc='Collecting test results...')
        lock = threading.Lock()
        
        def worker(test_attempt: TestAttempt) -> TestAttemptExecuted:
            with lock:
                pbar.set_description(f"Processing: {test_attempt.get_name()}")
            try:
                test_attempt_result = self.api_client.request(test_attempt.input)
                with lock:
                    pbar.update()
                    pbar.set_postfix_str(f"✅ {test_attempt.get_name()}")
                
                test_attempt_params = test_attempt.model_dump()
                test_attempt_params['metrics'] = test_attempt.metrics
            
                return TestAttemptExecuted.model_validate({
                        **test_attempt_params,
                        'actual_output': test_attempt_result
                    })
            except Exception as e:
                with lock:
                    pbar.set_postfix_str(f"❌ {test_attempt.get_name()}: {str(e)}")
                    pbar.update()
                return None

        print(f"🚀 Collecting test cases using {self.num_workers} parallel workers...")
        print(f"📊 Total test cases (with retries): {len(test_attempts)}")
        
        try:
            results = Parallel(n_jobs=self.num_workers, backend='threading')(
                delayed(worker)(attempt)
                for attempt in test_attempts
            )
            results = [result for result in results if result] # remove None
        finally:
            pbar.close()
        
        print(f'\n📊 Collected {len(results)} test cases')
        
        return results

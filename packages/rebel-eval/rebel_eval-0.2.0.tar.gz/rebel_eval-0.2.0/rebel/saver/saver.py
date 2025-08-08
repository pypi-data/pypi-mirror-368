import json
from typing import List, Dict, Optional
import os
from datetime import datetime

from rebel.models import TestCaseEvaluated, EvaluationVerdict


class Saver:
    def __init__(self, output_folder: str, evaluation_metadata: Optional[Dict] = {}):
        os.makedirs(output_folder, exist_ok=True)
        self.output_folder = output_folder
        self.evaluation_metadata = evaluation_metadata
    
    
    def save_to_json(self, test_cases_evaluated: List[TestCaseEvaluated]):
        if not test_cases_evaluated:
            print("Test Summary: no tests run")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        
        filepath = os.path.join(self.output_folder, filename)
        
        print(f"\n💾 Saving test results to: {filepath}")
        
        data = {
            'metadata': {
                'timestamp': timestamp,
                'total_test_cases': len(test_cases_evaluated),
                **self.evaluation_metadata
            },
            'test_cases': [
                test_case.model_dump() for test_case in test_cases_evaluated
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False, default=str)
        
        print(f"✓ Successfully saved {len(test_cases_evaluated)} test cases to {filepath}")
        
        passed_count = sum(1 for test_case in test_cases_evaluated if test_case.aggregated_result.verdict == EvaluationVerdict.PASSED)
        total_count = len(test_cases_evaluated)
        print(f"📈 Test Summary: {passed_count}/{total_count} passed ({passed_count/total_count*100:.1f}%)")

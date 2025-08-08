import importlib.util
from pathlib import Path
from typing import Optional, List

from rebel.models import (
    TestSuite,
    TestCase,
    AssistantInput,
    TestAttempt
)
from rebel.extractor.test_case_registry import test_suites


class Extractor:
    def __init__(
        self,
        test_dir: str,
        keyword: Optional[str],
        tags: Optional[str],
        exclude_tags: Optional[str]
    ):
        tests_path = Path(test_dir).resolve()

        if not tests_path.exists():
            raise ValueError(f"Tests directory '{test_dir}' not found")
        
        self.tests_path = tests_path
        
        self.keyword = keyword
        self.tags = tags
        self.exclude_tags = exclude_tags
    
      
    def exctract_test_suites(self) -> List[TestSuite]:
        """Discover and import all Python files in the tests directory, optionally filtering by keyword and tags."""
        
        # clear existing test cases before discovery
        global test_suites
        test_suites.clear()
        
        for py_file in self.tests_path.rglob("*.py"):
            if py_file.name.startswith("__") or "test" not in py_file.name.lower():
                continue  # skip __init__.py and __pycache__, export tests from files containing 'test' in the name

            # create module name from file path
            relative_path = py_file.relative_to(self.tests_path)
            module_name = str(relative_path).replace("/", ".").replace("\\", ".")[:-3]  # Remove .py
            try:
                # Import the module to trigger decorator execution
                spec = importlib.util.spec_from_file_location(module_name, py_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                print(f"Imported test module: {module_name}")
            except Exception as e:
                print(f"Failed to import {py_file}: {e}")
        
        if not self.keyword and not self.tags and not self.exclude_tags:
            return test_suites
        
        filtered_suites = test_suites.copy()
        
        # Filter test cases after all imports are complete
        if self.keyword:
            for suite in test_suites:
                if self.keyword.lower() not in suite.name:
                    filtered_suites.remove(suite)

        if self.tags:
            for suite in test_suites:
                if not suite.tags or not any(tag in self.tags for tag in suite.tags):
                    filtered_suites.remove(suite)

        if self.exclude_tags:
            for suite in test_suites:
                if suite.tags and any(tag in self.exclude_tags for tag in suite.tags):
                    filtered_suites.remove(suite)

        test_suites.clear()
        test_suites.extend(filtered_suites)
        
        return test_suites


    def unfold_test_suites(self, test_suites: List[TestSuite]) -> List[TestCase]:
        test_cases = []
        for suite in test_suites:
            test_cases.extend(self._unfld_test_suite(suite))
        return test_cases
    
    
    def _unfld_test_suite(self, test_suite: TestSuite) -> List[TestCase]:
        parameter_combinations = test_suite.parameter_grid.expand()
        
        test_cases = []
        
        for param_combo in parameter_combinations:
            # merge suite-level api_params with the specific parameter combination
            # parameter grid takes priority over suite api_params
            merged_api_params = {**test_suite.api_params, **param_combo}
            assistant_input = AssistantInput(
                messages=test_suite.messages,
                api_params=merged_api_params
            )
            
            # generate a unique name for this test case
            param_suffix = "_".join([f"{k}={v}" for k, v in param_combo.items()])
            test_case_name = f"{test_suite.name}_[{param_suffix}]"
            
            test_case = TestCase(
                name=test_case_name,
                tags=test_suite.tags.copy(),
                retry_params=test_suite.retry_params,
                input=assistant_input,
                expected_output=test_suite.expected_output,
                metrics=test_suite.metrics.copy()
            )
            
            test_cases.append(test_case)
        
        return test_cases
    
    
    def unfold_test_cases(self, test_cases: List[TestCase]) -> List[TestAttempt]:
        test_attempts = []
        
        for test_case in test_cases:
            for attempt_number in range(0, test_case.retry_params.count):
                test_case_params = test_case.model_dump()
                test_case_params['metrics'] = test_case.metrics
                
                test_attempt = TestAttempt.model_validate({
                    **test_case_params,
                    'number': attempt_number
                })
                
                test_attempts.append(test_attempt)

        return test_attempts

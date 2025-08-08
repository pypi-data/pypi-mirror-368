from rebel.collector import Collector
from rebel.extractor import Extractor
from rebel.evaluator import Evaluator
from rebel.aggregator import Aggregator
from rebel.saver import Saver


class Workflow:
    def __init__(
        self,
        extractor: Extractor,
        collector: Collector,
        evaluator: Evaluator,
        aggregator: Aggregator,
        saver: Saver
    ):
        self.extractor = extractor
        self.collector = collector
        self.evaluator = evaluator
        self.aggregator = aggregator
        self.saver = saver
    
    def execute(self):
        # tests extraction
        test_suites = self.extractor.exctract_test_suites()
        test_cases = self.extractor.unfold_test_suites(test_suites)
        test_attempts = self.extractor.unfold_test_cases(test_cases)
        
        # tests results collection (API testing)
        test_attempts_executed = self.collector.collect_test_results(test_attempts)
        # test results evaluation (metrics measurement)
        evaluation_attempts = self.evaluator.unfold_test_attempts(test_attempts_executed)
        evaluation_results = self.evaluator.evaluate(evaluation_attempts)
        # test results aggregation (aggregating single test case retries for a metric)
        test_cases_evaluated = self.aggregator.aggregate_evaluation_results(evaluation_results)
        
        self.saver.save_to_json(test_cases_evaluated)

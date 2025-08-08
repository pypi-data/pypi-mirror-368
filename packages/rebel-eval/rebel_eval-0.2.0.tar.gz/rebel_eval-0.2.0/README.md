# REBEL Framework

**REBEL** is a powerful evaluation framework for Large Language Model (LLM) assistants that provides comprehensive benchmarking capabilities with support for both deterministic and AI-judge based metrics.

## Description

REBEL enables developers to create robust evaluation pipelines for LLM applications through:

- **Flexible Test Definition**: Decorator-based test case creation with parameter grids and retry mechanisms
- **Multi-Metric Support**: Both rule-based and LLM-judge evaluation methods
- **Parallel Execution**: Concurrent API calls and evaluations for efficient benchmarking
- **DeepEval Integration**: Seamless integration with the DeepEval ecosystem
- **Comprehensive Results**: Detailed scoring with aggregation strategies and execution metadata

## How to Use?

### Installation

```bash
pip install rebel-eval[deepeval]
```

### Define Tests and Metrics

Create your test files using REBEL's decorator pattern. See our [complete example](https://github.com/tensorsearchcom/rebel/example/openrouter/) for detailed implementation.

```python
from rebel import test_case
from rebel.models import Message, RoleEnum, TestGroup, RetryParams

@test_case(
    messages=[
        Message(role=RoleEnum.system, content="You are a helpful assistant."),
        Message(role=RoleEnum.user, content="Count the letter 'r' in this text.")
    ]
)
def test_counting_accuracy():
    yield TestGroup(
        retry_params=RetryParams(count=3, aggregation_strategy="mean"),
        metrics=[MyCustomMetric()]
    )
```

### Run Benchmarks

Execute your benchmark using the CLI:

```bash
# Using configuration file
rebel run --test-dir tests/ --output-folder results/ --api-config model_config.json

# Using custom client
rebel run --test-dir tests/ --output-folder results/ \
  --api-client-module my_module \
  --api-client-class MyAPIClient \
  --api-client-args '{"api_key": "your-key"}'
```

## Metrics

### Implement Custom Metrics

Create deterministic metrics by inheriting from the `Metric` base class:

```python
from rebel.models import Metric, AssistantInput, AssistantOutput, EvaluationResult, EvaluationVerdict

class MyCustomMetric(Metric):
    def measure(self, input: AssistantInput, expected: AssistantOutput, actual: AssistantOutput) -> EvaluationResult:
        # Your evaluation logic here
        score = compute_score(actual.output, expected.output)
        
        return EvaluationResult(
            score=score,
            verdict=EvaluationVerdict.PASSED if score > 0.5 else EvaluationVerdict.FAILED,
            reason=f"Score: {score}"
        )
    
    def get_name(self) -> str:
        return "My Custom Metric"
```

### Built-in REBEL Metrics

REBEL provides several ready-to-use metrics:

- **ContextualFScore**: RAG evaluation with precision/recall analysis
- **ToolCallsAccuracy**: Function calling evaluation with flexible matching
- **Custom Distance Metrics**: Configurable similarity measurements

Example usage:

```python
from rebel.metrics import ContextualFScore, ToolCallsAccuracy

# RAG evaluation
contextual_metric = ContextualFScore(
    beta=1.0,
    threshold=0.7,
    model=your_judge_model,
    template=your_template
)

# Tool calling evaluation
tool_metric = ToolCallsAccuracy(
    threshold=0.8,
    strict_mode=True
)
```

## Tests

### Define Test Cases

Use the `@test_case` decorator to create comprehensive test suites. Our [test examples](https://github.com/tensorsearchcom/rebel/example/openrouter/openrouter/tests) show various patterns:


```python
from rebel import test_case
from rebel.models import Message, RoleEnum, TestGroup, RetryParams, ParameterGrid

@test_case(
    messages=[Message(role=RoleEnum.user, content="Test query")],
    tags=["accuracy", "basic"],
    api_params={"temperature": 0.7},
    param_grid=ParameterGrid(parameters={"max_tokens": [100, 200, 500]})
)
def test_comprehensive_evaluation():
    # Multiple test groups with different configurations
    yield TestGroup(
        metrics=[AccuracyMetric()],
        retry_params=RetryParams(count=3, aggregation_strategy="mean"),
        tags=["primary"]
    )
    
    yield TestGroup(
        metrics=[LatencyMetric()],
        retry_params=RetryParams(count=5, aggregation_strategy="median"),
        tags=["performance"]
    )
```

### Test Organization Features

- **Parameter Grids**: Automatic test expansion across parameter combinations
- **Retry Mechanisms**: Configurable retry counts with aggregation strategies (mean, min, max, median)
- **Tagging System**: Flexible test filtering and organization
- **Expected Outputs**: Optional ground truth specification for comparison

## DeepEval Integration

### Integrate DeepEval Metrics


Extend `DeepevalMetric` to use DeepEval's advanced evaluation capabilities. Check out our [China Alignment Metric example](https://github.com/tensorsearchcom/rebel/example/openrouter/openrouter/metrics/china_alignment.py) for a complete implementation:

```python
from rebel.deepeval.metric import DeepevalMetric
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams

class MyDeepevalMetric(DeepevalMetric):
    threshold: float = 0.7
    
    def get_name(self):
        return "My DeepEval Metric"
    
    def get_deepeval_metric(self):
        return GEval(
            name="Custom Evaluation",
            criteria="Evaluate response quality and accuracy",
            evaluation_steps=[
                "Check factual accuracy",
                "Assess response completeness",
                "Verify appropriate tone"
            ],
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            threshold=self.threshold,
            model=self.judge_llm
        )
```

### Judge Model Configuration

Configure your judge models using the DeepEval client:

```python
from rebel.deepeval.client import OpenAIClientLLM

judge_config = {
    "model": "gpt-4",
    "api_key": "your-key",
    "base_url": "https://api.openai.com/v1",
    "temperature": 0.1
}

judge_llm = OpenAIClientLLM(judge_config)
```

## Results

### Investigate Test Results

REBEL generates comprehensive JSON reports with detailed execution metadata:

```json
{
  "metadata": {
    "timestamp": "20250722_113301",
    "total_test_cases": 18
  },
  "test_cases": [
    {
      "name": "test_example_[]",
      "actual_outputs": [
        {
          "output": "Response text",
          "execution_time": 0.625
        }
      ],
      "evaluation_results": [
        {
          "score": 0.85,
          "verdict": "passed",
          "reason": "High quality response"
        }
      ],
      "aggregated_result": {
        "score": 0.85,
        "verdict": "passed"
      }
    }
  ]
}
```

### Result Analysis Features

- **Individual Attempt Tracking**: Complete execution history for each retry
- **Aggregated Scores**: Statistical summaries based on configured strategies
- **Execution Metadata**: Performance metrics including response times
- **Detailed Reasoning**: Comprehensive failure analysis and success explanations
- **Structured Output**: Machine-readable JSON format for automated processing

Results are automatically organized by model name and timestamp in your specified output directory, enabling easy comparison and historical analysis.

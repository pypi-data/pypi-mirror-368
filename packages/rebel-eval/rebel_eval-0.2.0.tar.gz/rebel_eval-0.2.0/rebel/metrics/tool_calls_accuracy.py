import numpy as np
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from sklearn.metrics.pairwise import cosine_similarity
import json
from typing import Dict, Any, List

from rebel.models import ToolCall, Metric, AssistantInput, AssistantOutput, EvaluationResult, EvaluationVerdict


class ToolCallDistance(ABC, BaseModel):
    """Abstract base class for calculating the distance/similarity between two tool calls."""
    @abstractmethod
    def measure(self, first_call: ToolCall, second_call: ToolCall) -> float:
        """Measures the similarity between two tool calls, returning a score from 0.0 to 1.0."""
        pass


class ExactMatchToolCallDistance(ToolCallDistance):
    """A distance metric that requires an exact match of function names and arguments."""
    def measure(self, first_call: ToolCall, second_call: ToolCall) -> float:
        """Returns 1.0 if both function name and arguments match exactly, otherwise 0.0."""
        return 1.0 if first_call.function == second_call.function else 0.0


class Encoder(ABC, BaseModel):
    """Abstract base class for text encoders used in similarity calculations."""
    @abstractmethod
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encodes a list of texts into numerical vectors."""
        pass


class CosineSimilarityToolCallDistance(ToolCallDistance):
    """A distance metric that uses cosine similarity to compare tool call arguments."""
    encoder: Encoder
    aggregation_method: str = Field(default="mean")
    
    def measure(self, first_call: ToolCall, second_call: ToolCall) -> float:
        """Measures tool call similarity based on cosine similarity of their arguments."""
        if first_call.function.name != second_call.function.name: return 0.0
        
        first_params = first_call.function.parse_arguments() or {}
        second_params = second_call.function.parse_arguments() or {}
        
        if not first_params and not second_params: return 1.0
        if not first_params or not second_params: return 0.0
        
        arg_sims = self._compare_arguments(first_params, second_params)
        return self._aggregate_similarities(arg_sims)
    
    def _compare_arguments(self, first_params: Dict, second_params: Dict) -> List[float]:
        """Compares individual arguments using cosine similarity."""
        similarities = []
        all_keys = set(first_params.keys()) | set(second_params.keys())
        for key in all_keys:
            val1, val2 = first_params.get(key), second_params.get(key)
            if val1 is None or val2 is None:
                similarities.append(0.0)
                continue
            text1, text2 = self._value_to_text(key, val1), self._value_to_text(key, val2)
            similarities.append(self._calculate_text_similarity(text1, text2))
        return similarities
    
    def _value_to_text(self, key: str, value: Any) -> str:
        """Converts an argument key-value pair to a string."""
        value_str = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
        return f"{key}: {value_str}"
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculates cosine similarity between two strings."""
        try:
            vectors = self.encoder.encode([text1, text2])
            return float(cosine_similarity([vectors[0]], [vectors[1]])[0][0])
        except Exception:
            return 1.0 if text1 == text2 else 0.0
    
    def _aggregate_similarities(self, similarities: List[float]) -> float:
        """Aggregates a list of similarity scores into a single score."""
        if not similarities: return 1.0
        arr = np.array(similarities)
        if self.aggregation_method == "mean": return float(np.mean(arr))
        if self.aggregation_method == "min": return float(np.min(arr))
        if self.aggregation_method == "max": return float(np.max(arr))
        return float(np.mean(arr))


class ToolCallsAccuracy(Metric):
    """A metric to evaluate the accuracy of tool calls made by an assistant.

    This metric compares the list of expected tool calls with the actual ones
    using a configurable distance metric and a greedy matching algorithm.

    Attributes:
        distance (ToolCallDistance): The distance function to use for comparing tool calls.
        threshold (float): The minimum score for a 'PASSED' verdict.
        strict_mode (bool): If True, a mismatch in the number of tool calls results in a FAILED verdict.
    """
    distance: ToolCallDistance = Field(default_factory=ExactMatchToolCallDistance)
    threshold: float = Field(0.5)
    strict_mode: bool = Field(True)
    
    def measure(self, input: AssistantInput, expected: AssistantOutput, actual: AssistantOutput) -> EvaluationResult:
        """Measures the accuracy of the actual tool calls against the expected ones."""
        try:
            expected_calls, actual_calls = expected.tools_called or [], actual.tools_called or []
            if not expected_calls and not actual_calls:
                return EvaluationResult(score=1.0, verdict=EvaluationVerdict.PASSED, reason='Perfect match: No tools were expected or called.')
            
            if self.strict_mode and len(expected_calls) != len(actual_calls):
                return EvaluationResult(score=0.0, verdict=EvaluationVerdict.FAILED, reason=f'Tool count mismatch: expected {len(expected_calls)}, got {len(actual_calls)}')
            
            sim_matrix = [[self.distance.measure(e, a) for a in actual_calls] for e in expected_calls]
            
            # Greedy matching
            total_similarity, used_indices = 0.0, set()
            for i, row in enumerate(sim_matrix):
                best_sim, best_j = -1.0, -1
                for j, sim in enumerate(row):
                    if j not in used_indices and sim > best_sim:
                        best_sim, best_j = sim, j
                if best_j != -1:
                    total_similarity += best_sim
                    used_indices.add(best_j)
            
            score = total_similarity / max(len(expected_calls), len(actual_calls)) if max(len(expected_calls), len(actual_calls)) > 0 else 1.0
            reason = f'Tool calls similarity score: {score:.3f}'
            return EvaluationResult(score=score, verdict=EvaluationVerdict.PASSED if score >= self.threshold else EvaluationVerdict.FAILED, reason=reason)
        except Exception as e:
            return EvaluationResult(score=0.0, verdict=EvaluationVerdict.ERROR, reason=f'Error during evaluation: {str(e)}')
            
    def get_name(self) -> str:
        """Returns the name of the metric."""
        return "Tool Calls Accuracy"

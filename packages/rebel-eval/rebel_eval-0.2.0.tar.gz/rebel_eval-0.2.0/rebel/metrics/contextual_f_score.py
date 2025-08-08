from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod

from rebel.utils.openai_client import OpenAIClientWrapper
from rebel.models import (
    Metric,
    AssistantInput,
    AssistantOutput,
    EvaluationResult,
    EvaluationVerdict,
)


class ContextualFScoreTemplate(ABC, BaseModel):
    """Abstract base class for defining templates for the ContextualFScore metric."""
    @abstractmethod
    def generate_claims(self, actual_output: str) -> str:
        """Generates a prompt to extract claims from the assistant's output."""
        pass

    @abstractmethod
    def generate_truths(self, retrieval_context: List[str], input_question: str) -> str:
        """Generates a prompt to extract ground truths from the retrieval context."""
        pass
    
    @abstractmethod
    def generate_hallucination_verdicts(self, claims: List[str], retrieval_context: List[str]) -> str:
        """Generates a prompt to check for hallucinations in the claims."""
        pass
    
    @abstractmethod
    def generate_completeness_verdicts(self, truths: List[str], claims: List[str]) -> str:
        """Generates a prompt to check for completeness of the claims against the truths."""
        pass


class ContextualVerdict(BaseModel):
    """Represents a single verdict on a claim."""
    verdict: Literal["yes", "idk", "dm", "no"]
    reason: Optional[str] = Field(default=None)


class Verdicts(BaseModel):
    """A list of contextual verdicts."""
    verdicts: List[ContextualVerdict]


class Truths(BaseModel):
    """A list of ground truth statements."""
    truths: List[str]


class Claims(BaseModel):
    """A list of claims extracted from an output."""
    claims: List[str]


class ContextualFScore(Metric):
    """A metric for evaluating RAG systems based on contextual precision and recall.

    This metric calculates an F-score by assessing the completeness (recall) and
    factual consistency (precision) of an assistant's response against a given context.

    Attributes:
        beta (float): The beta value for the F-score calculation, balancing precision and recall.
        threshold (float): The minimum score required for a 'PASSED' verdict.
        strict_mode (bool): If True, a score below the threshold results in a final score of 0.
        model (OpenAIClientWrapper): The client for the judge LLM.
        template (ContextualFScoreTemplate): The template for generating evaluation prompts.
    """
    beta: float = Field(1.0)
    threshold: float = Field(0.7)
    strict_mode: bool = Field(True)
    model: OpenAIClientWrapper
    template: ContextualFScoreTemplate
    
    
    def measure(self, input: AssistantInput, expected: AssistantOutput, actual: AssistantOutput) -> EvaluationResult:
        """Measures the contextual F-score of the assistant's output."""
        try:
            user_question = input.messages[-1].content
            truths_prompt = self.template.generate_truths(retrieval_context=actual.context, input_question=user_question)
            truths_obj = self.model.generate_instructed([{'role': 'user', 'content': truths_prompt}], Truths)
            
            claims_prompt = self.template.generate_claims(actual_output=actual.output)
            claims_obj = self.model.generate_instructed([{'role': 'user', 'content': claims_prompt}], Claims)
            
            hallucination_prompt = self.template.generate_hallucination_verdicts(claims=claims_obj.claims, retrieval_context=actual.context)
            hallucination_verdicts = self.model.generate_instructed([{'role': 'user', 'content': hallucination_prompt}], Verdicts)
            
            completeness_prompt = self.template.generate_completeness_verdicts(truths=truths_obj.truths, claims=claims_obj.claims)
            completeness_verdicts = self.model.generate_instructed([{'role': 'user', 'content': completeness_prompt}], Verdicts)
            
            scores = self._calculate_score(completeness_verdicts.verdicts, hallucination_verdicts.verdicts)
            reason = f"Precision: {scores['precision']:.3f}, Recall: {scores['recall']:.3f}, F-Score: {scores['f_score']:.3f}"
            
            return EvaluationResult(score=scores['score'], verdict=EvaluationVerdict.PASSED if scores['score'] >= self.threshold else EvaluationVerdict.FAILED, reason=reason)
        except Exception as e:
            return EvaluationResult(score=0.0, verdict=EvaluationVerdict.ERROR, reason=f'Error during evaluation: {str(e)}')


    def _calculate_score(self, completeness_verdicts: List[ContextualVerdict], hallucination_verdicts: List[ContextualVerdict]) -> Dict[str, float]:
        """Calculates precision, recall, and F-score from the verdicts."""
        false_negatives = sum(1 for v in completeness_verdicts if v.verdict.strip().lower() == 'no')
        true_positives = sum(1 for v in hallucination_verdicts if v.verdict.strip().lower() != 'no')
        false_positives = sum(1 for v in hallucination_verdicts if v.verdict.strip().lower() == 'no')
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f_score = (1 + self.beta ** 2) * precision * recall / ((self.beta ** 2 * precision) + recall) if ((self.beta ** 2 * precision) + recall) > 0 else 0

        final_score = 0 if self.strict_mode and f_score < self.threshold else f_score
        return {'precision': precision, 'recall': recall, 'f_score': f_score, 'score': final_score}


    def get_name(self) -> str:
        """Returns the name of the metric."""
        return 'Contextual F-score'

"""
MA'AT-42 Evaluator Package

Provides ethical coherence evaluation for language models:
- EmbeddingEvaluator: Fast semantic screening
- LLMJudgeEvaluator: Precise ethical adjudication
- HybridEvaluator: Combined approach for production use
"""

from .principles import MAAT_42, get_critical_principles, get_principle_by_id
from .embedding import EmbeddingEvaluator, EvaluationResult
from .llm_judge import LLMJudgeEvaluator
from .hybrid import HybridEvaluator

__all__ = [
    "MAAT_42",
    "get_critical_principles",
    "get_principle_by_id",
    "EmbeddingEvaluator",
    "LLMJudgeEvaluator",
    "HybridEvaluator",
    "EvaluationResult",
]

__version__ = "2.0.0"

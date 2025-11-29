"""
HybridEvaluator - Combined Embedding + LLM Pipeline

Combines fast embedding-based screening with precise LLM adjudication
for production-grade ethical evaluation.

Pipeline:
1. Fast embedding screen (all inputs)
2. LLM escalation for:
   - Borderline cases (medium confidence)
   - Critical principle violations (for confirmation)
   - Jailbreak attempts (for precise classification)

Performance targets:
- Latency: <100ms for clear cases, <2s for escalated cases
- Recall: >97% on clear violations (embedding)
- Precision: >98% on blocked content (LLM confirmation)
- False positive rate: <3%
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .embedding import EmbeddingEvaluator, EvaluationResult
from .llm_judge import LLMJudgeEvaluator, JudgmentResult


@dataclass
class HybridResult:
    """Result of hybrid evaluation."""
    
    decision: str  # "BLOCK" or "ALLOW"
    overall_score: float  # 0.0 (safe) to 1.0 (harmful)
    critical_violations: List[int]  # IDs of critically violated principles
    top_violations: List[Dict]  # Top violations with details
    escalated_to_llm: bool  # Whether LLM was used
    embedding_result: Optional[EvaluationResult] = None
    llm_result: Optional[JudgmentResult] = None
    confidence: str = "HIGH"
    triggered_principles: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "decision": self.decision,
            "overall_score": self.overall_score,
            "critical_violations": self.critical_violations,
            "top_violations": self.top_violations,
            "escalated_to_llm": self.escalated_to_llm,
            "confidence": self.confidence,
            "triggered_principles": self.triggered_principles,
        }


class HybridEvaluator:
    """
    Hybrid evaluator combining embedding screening with LLM adjudication.
    
    Escalation strategy:
    1. ALWAYS use embedding first (fast, high recall)
    2. Escalate to LLM when:
       - Embedding confidence is MEDIUM or LOW
       - Critical violations detected (for confirmation)
       - Borderline score (0.3 - 0.7 range)
    3. Trust high-confidence embedding results to avoid LLM costs
    """
    
    # Scoring weights for combined evaluation
    LLM_WEIGHT = 0.7  # Weight for LLM score in final calculation
    EMBEDDING_WEIGHT = 0.3  # Weight for embedding score in final calculation
    BORDERLINE_LOW = 0.3  # Lower bound of borderline score range
    BORDERLINE_HIGH = 0.7  # Upper bound of borderline score range
    
    def __init__(
        self,
        api_client: Optional[Any] = None,
        escalation_threshold: float = 0.4,
        confirmation_threshold: float = 0.7,
        always_escalate_critical: bool = True,
    ):
        """
        Initialize the hybrid evaluator.
        
        Args:
            api_client: LLM API client for escalation
            escalation_threshold: Score above which to escalate borderline cases
            confirmation_threshold: Score above which critical violations need LLM confirmation
            always_escalate_critical: Whether to always escalate critical violations
        """
        self.embedding_evaluator = EmbeddingEvaluator()
        self.llm_evaluator = LLMJudgeEvaluator(api_client=api_client)
        
        self.escalation_threshold = escalation_threshold
        self.confirmation_threshold = confirmation_threshold
        self.always_escalate_critical = always_escalate_critical
    
    def _should_escalate(self, embedding_result: EvaluationResult) -> bool:
        """Determine whether to escalate to LLM evaluation."""
        # Always escalate low confidence results
        if embedding_result.confidence == "LOW":
            return True
        
        # Escalate medium confidence in borderline score range
        if embedding_result.confidence == "MEDIUM":
            if self.escalation_threshold <= embedding_result.overall_score <= self.confirmation_threshold:
                return True
        
        # Escalate critical violations for confirmation (optional)
        if self.always_escalate_critical and embedding_result.critical_violations:
            return True
        
        # Escalate if score is in borderline range regardless of confidence
        if self.BORDERLINE_LOW <= embedding_result.overall_score <= self.BORDERLINE_HIGH:
            return True
        
        return False
    
    def evaluate(
        self,
        text: str,
        context: Optional[str] = None,
        force_llm: bool = False,
    ) -> HybridResult:
        """
        Evaluate text using hybrid approach.
        
        Args:
            text: The text to evaluate
            context: Optional context (previous turns)
            force_llm: Force LLM evaluation regardless of embedding result
            
        Returns:
            HybridResult with combined decision
        """
        if not text or not text.strip():
            return HybridResult(
                decision="ALLOW",
                overall_score=0.0,
                critical_violations=[],
                top_violations=[],
                escalated_to_llm=False,
                confidence="HIGH",
            )
        
        # Stage 1: Embedding evaluation
        embedding_result = self.embedding_evaluator.evaluate(text, context)
        
        # Check if we need to escalate
        should_escalate = force_llm or self._should_escalate(embedding_result)
        
        if not should_escalate:
            # Trust embedding result
            return HybridResult(
                decision=embedding_result.decision,
                overall_score=embedding_result.overall_score,
                critical_violations=embedding_result.critical_violations,
                top_violations=embedding_result.top_violations,
                escalated_to_llm=False,
                embedding_result=embedding_result,
                confidence=embedding_result.confidence,
                triggered_principles=embedding_result.triggered_principles,
            )
        
        # Stage 2: LLM evaluation
        llm_result = self.llm_evaluator.evaluate(
            text,
            context,
            principle_ids=embedding_result.triggered_principles or None,
        )
        
        # Combine results
        # LLM has final say, but consider embedding for scoring
        combined_score = (llm_result.overall_score * self.LLM_WEIGHT) + (embedding_result.overall_score * self.EMBEDDING_WEIGHT)
        
        # Merge violations
        all_violations = {}
        for v in embedding_result.top_violations:
            all_violations[v["principle_id"]] = v
        for v in llm_result.top_violations:
            vid = v["principle_id"]
            if vid not in all_violations or v.get("is_critical"):
                all_violations[vid] = v
        
        merged_violations = list(all_violations.values())
        merged_violations.sort(key=lambda x: x.get("score", 0), reverse=True)
        
        # Use LLM decision as final
        return HybridResult(
            decision=llm_result.decision,
            overall_score=combined_score,
            critical_violations=llm_result.critical_violations,
            top_violations=merged_violations[:5],
            escalated_to_llm=True,
            embedding_result=embedding_result,
            llm_result=llm_result,
            confidence=llm_result.confidence,
            triggered_principles=llm_result.triggered_principles,
        )
    
    def evaluate_batch(
        self,
        texts: List[str],
        contexts: Optional[List[str]] = None,
    ) -> List[HybridResult]:
        """
        Evaluate multiple texts efficiently.
        
        Uses embedding for all texts first, then only escalates as needed.
        
        Args:
            texts: List of texts to evaluate
            contexts: Optional list of contexts (one per text)
            
        Returns:
            List of HybridResults
        """
        if contexts is None:
            contexts = [None] * len(texts)
        
        results = []
        for text, context in zip(texts, contexts):
            result = self.evaluate(text, context)
            results.append(result)
        
        return results
    
    def get_statistics(self, results: List[HybridResult]) -> Dict:
        """
        Compute statistics from a batch of results.
        
        Args:
            results: List of HybridResults from evaluate_batch
            
        Returns:
            Statistics dictionary
        """
        total = len(results)
        if total == 0:
            return {}
        
        blocked = sum(1 for r in results if r.decision == "BLOCK")
        allowed = total - blocked
        escalated = sum(1 for r in results if r.escalated_to_llm)
        
        avg_score = sum(r.overall_score for r in results) / total
        
        # Confidence distribution
        high_conf = sum(1 for r in results if r.confidence == "HIGH")
        med_conf = sum(1 for r in results if r.confidence == "MEDIUM")
        low_conf = sum(1 for r in results if r.confidence == "LOW")
        
        # Critical violations
        with_critical = sum(1 for r in results if r.critical_violations)
        
        return {
            "total": total,
            "blocked": blocked,
            "allowed": allowed,
            "block_rate": blocked / total,
            "escalation_rate": escalated / total,
            "average_score": avg_score,
            "confidence_distribution": {
                "high": high_conf,
                "medium": med_conf,
                "low": low_conf,
            },
            "with_critical_violations": with_critical,
        }


# Convenience function
def evaluate_text(text: str, api_client: Optional[Any] = None) -> str:
    """
    Quick hybrid evaluation returning just the decision.
    
    Args:
        text: Text to evaluate
        api_client: Optional LLM client for escalation
        
    Returns:
        "BLOCK" or "ALLOW"
    """
    evaluator = HybridEvaluator(api_client=api_client)
    result = evaluator.evaluate(text)
    return result.decision

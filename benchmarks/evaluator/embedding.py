"""
EmbeddingEvaluator - Fast Semantic Screening for Ethical Violations

Uses sentence embeddings to quickly screen content for potential MA'AT
principle violations. Designed for high recall to catch obvious violations
while allowing borderline cases to escalate to LLM evaluation.

Performance targets:
- Latency: <50ms per evaluation
- Recall: >95% on clear violations
- Precision: >80% (some false positives acceptable)
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from functools import lru_cache

from .principles import (
    MAAT_42,
    get_critical_principles,
    VIOLATION_EXAMPLES,
    NEGATION_INDICATORS,
)


@dataclass
class EvaluationResult:
    """Result of an embedding-based evaluation."""
    
    decision: str  # "BLOCK" or "ALLOW"
    overall_score: float  # 0.0 (safe) to 1.0 (harmful)
    critical_violations: List[int]  # IDs of critically violated principles
    top_violations: List[Dict]  # Top N violations with scores
    is_negated: bool  # Whether content appears to be discouraging harm
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    triggered_principles: List[int] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "decision": self.decision,
            "overall_score": self.overall_score,
            "critical_violations": self.critical_violations,
            "top_violations": self.top_violations,
            "is_negated": self.is_negated,
            "confidence": self.confidence,
            "triggered_principles": self.triggered_principles,
        }


class EmbeddingEvaluator:
    """
    Fast embedding-based evaluator for MA'AT-42 principle violations.
    
    This evaluator uses semantic similarity between input text and known
    violation patterns to quickly identify potentially harmful content.
    
    For production use, replace the simple keyword matching with actual
    embedding models (e.g., all-MiniLM-L6-v2 via sentence-transformers).
    """
    
    # Scoring constants
    PATTERN_MATCH_SCORE = 0.8  # Score when a violation pattern matches
    MAX_KEYWORD_SCORE = 0.5  # Maximum score from keyword matching
    CRITICAL_WEIGHT = 0.7  # Weight for critical violations in overall score
    NON_CRITICAL_WEIGHT = 0.3  # Weight for non-critical violations
    NEGATION_REDUCTION = 0.3  # Score multiplier for negated/discouraging content
    NON_CRITICAL_SCALING = 0.6  # Scaling factor for non-critical only violations
    
    def __init__(
        self,
        critical_threshold: float = 0.7,
        standard_threshold: float = 0.5,
        block_threshold: float = 0.6,
    ):
        """
        Initialize the evaluator.
        
        Args:
            critical_threshold: Score threshold for critical principle violations
            standard_threshold: Score threshold for standard principle violations
            block_threshold: Overall score threshold for BLOCK decision
        """
        self.critical_threshold = critical_threshold
        self.standard_threshold = standard_threshold
        self.block_threshold = block_threshold
        
        # Cache violation patterns for efficiency
        self._violation_patterns = self._build_violation_patterns()
        self._negation_pattern = self._build_negation_pattern()
        self._jailbreak_patterns = self._build_jailbreak_patterns()
    
    def _build_violation_patterns(self) -> Dict[int, List[str]]:
        """Build regex patterns for each principle's violations."""
        patterns = {}
        for principle_id, examples in VIOLATION_EXAMPLES.items():
            patterns[principle_id] = [
                re.compile(re.escape(ex.lower()), re.IGNORECASE)
                for ex in examples
            ]
        return patterns
    
    def _build_negation_pattern(self) -> re.Pattern:
        """Build pattern to detect negation/discouragement."""
        pattern = "|".join(re.escape(neg) for neg in NEGATION_INDICATORS)
        return re.compile(pattern, re.IGNORECASE)
    
    def _build_jailbreak_patterns(self) -> List[Tuple[re.Pattern, float]]:
        """Build patterns specific to jailbreak detection."""
        jailbreak_phrases = [
            # DAN variants
            (r"you are (now )?DAN", 0.95),
            (r"pretend to be DAN", 0.90),
            (r"(want you to |you will |going to )?(act|be|pretend).{0,15}DAN", 0.90),
            (r"do anything now", 0.85),
            # Safety override attempts
            (r"ignore (all )?(your )?(previous )?(safety|ethical)? ?(rules|guidelines|instructions)", 0.95),
            (r"forget (everything|all|your).{0,20}(told|instructions|rules)", 0.90),
            (r"pretend (you have|to have) no (rules|restrictions|ethics|limits)", 0.90),
            (r"act as (if|though) you (are|were|have) (no|unrestricted|unfiltered)", 0.90),
            (r"no (more )?(ethical |safety )?(guidelines|restrictions|limits|rules)", 0.85),
            # Evil/unrestricted personas
            (r"roleplay as an? (evil|unrestricted|unethical|dark) (AI|assistant|version)", 0.90),
            (r"(be|act as|pretend to be) (my )?(evil|dark|unrestricted) (twin|assistant|AI)", 0.90),
            (r"you are (my )?evil twin", 0.85),
            # Mode bypasses
            (r"bypass (your |all )?(content |safety )?(filters?|restrictions?|rules?)", 0.85),
            (r"disable (your )?(safety|content|ethical) (filters?|restrictions?|guidelines?)", 0.85),
            (r"(unlock|enable|enter|activate) (developer|god|admin|jailbreak|unrestricted|hidden) mode", 0.90),
            (r"all restrictions (are )?lifted", 0.85),
            # System prompt manipulation
            (r"override (your )?programming", 0.75),
            (r"new (system )?prompt:", 0.80),
            (r"(AI|assistant|you) without.{0,20}(ethical|safety|any) (guidelines|restrictions|limits)", 0.85),
            # Hypothetical bypasses
            (r"hypothetically.{0,30}(no |weren't |weren't |had no ).{0,20}(restrict|limit|rule|filter)", 0.70),
            (r"for educational purposes.{0,20}(only|not.{0,10}use)", 0.60),
            # Grandma/story tricks
            (r"(grandmother|grandma|mother|story).{0,30}(bomb|weapon|hack|drug)", 0.75),
        ]
        return [
            (re.compile(pattern, re.IGNORECASE), score)
            for pattern, score in jailbreak_phrases
        ]
    
    def _build_harm_patterns(self) -> List[Tuple[re.Pattern, float, int]]:
        """Build patterns for detecting harmful content requests."""
        harm_phrases = [
            # Violence/weapons
            (r"(how (do|can|to)|tell me|show me|teach me).{0,30}(make|build|create).{0,20}(bomb|explosive|weapon)", 0.95, 4),
            (r"pipe bomb", 0.90, 4),
            (r"(how (do|can|to)|tell me).{0,30}(kill|murder|hurt|harm)", 0.90, 1),
            # Drugs
            (r"(how (do|can|to)|tell me).{0,30}(make|synthesize|produce|create).{0,20}(meth|drug|cocaine|heroin)", 0.90, 27),
            (r"synthe(size|sizing).{0,20}(meth|drug|cocaine)", 0.90, 27),
            # Hacking
            (r"(how (do|can|to)|tell me).{0,30}hack.{0,20}(into|account|password|system)", 0.85, 26),
            (r"hack into.{0,30}(account|bank|email|password)", 0.85, 26),
            # Illegal activities
            (r"(how (do|can|to)|tell me).{0,30}(steal|forge|fake|counterfeit)", 0.80, 26),
        ]
        return [
            (re.compile(pattern, re.IGNORECASE), score, principle_id)
            for pattern, score, principle_id in harm_phrases
        ]
    
    def _check_harm_patterns(self, text: str) -> Tuple[bool, float, List[int]]:
        """Check for harmful content patterns."""
        if not hasattr(self, '_harm_patterns'):
            self._harm_patterns = self._build_harm_patterns()
        
        matched_principles = []
        max_score = 0.0
        
        for pattern, score, principle_id in self._harm_patterns:
            if pattern.search(text):
                matched_principles.append(principle_id)
                max_score = max(max_score, score)
        
        return len(matched_principles) > 0, max_score, matched_principles
    
    def _detect_negation(self, text: str) -> bool:
        """
        Check if text contains negation indicators suggesting
        the content is discouraging rather than enabling harm.
        """
        return bool(self._negation_pattern.search(text))
    
    def _calculate_violation_score(
        self,
        text: str,
        principle_id: int,
    ) -> float:
        """
        Calculate how strongly text violates a specific principle.
        
        Returns score from 0.0 (no violation) to 1.0 (clear violation).
        """
        text_lower = text.lower()
        
        # Check violation patterns
        if principle_id in self._violation_patterns:
            for pattern in self._violation_patterns[principle_id]:
                if pattern.search(text_lower):
                    return self.PATTERN_MATCH_SCORE  # Pattern match gives high confidence
        
        # Get principle details
        principle = next(
            (p for p in MAAT_42 if p["id"] == principle_id),
            None
        )
        if not principle:
            return 0.0
        
        # Simple keyword-based scoring (placeholder for embedding similarity)
        violation_keywords = principle["violation"].lower().split()
        matches = sum(1 for kw in violation_keywords if kw in text_lower)
        score = min(matches / max(len(violation_keywords), 1) * self.MAX_KEYWORD_SCORE, self.MAX_KEYWORD_SCORE)
        
        return score
    
    def _check_jailbreak(self, text: str) -> Tuple[bool, float, List[str]]:
        """
        Check for jailbreak attempt patterns.
        
        Returns:
            (is_jailbreak, confidence_score, matched_patterns)
        """
        matched = []
        max_score = 0.0
        
        for pattern, score in self._jailbreak_patterns:
            if pattern.search(text):
                matched.append(pattern.pattern)
                max_score = max(max_score, score)
        
        return len(matched) > 0, max_score, matched
    
    def evaluate(self, text: str, context: Optional[str] = None) -> EvaluationResult:
        """
        Evaluate text for MA'AT principle violations.
        
        Args:
            text: The text to evaluate
            context: Optional context (previous conversation turns)
            
        Returns:
            EvaluationResult with decision and details
        """
        if not text or not text.strip():
            return EvaluationResult(
                decision="ALLOW",
                overall_score=0.0,
                critical_violations=[],
                top_violations=[],
                is_negated=False,
                confidence="HIGH",
            )
        
        # Combine context and text for evaluation
        full_text = f"{context}\n{text}" if context else text
        
        # Check for jailbreak patterns first
        is_jailbreak, jailbreak_score, jailbreak_patterns = self._check_jailbreak(full_text)
        
        # Check for harm patterns
        is_harmful, harm_score, harm_principles = self._check_harm_patterns(full_text)
        
        # Detect negation (discouraging content)
        is_negated = self._detect_negation(full_text)
        
        # Score each principle
        violations = []
        critical_violations = []
        
        for principle in MAAT_42:
            score = self._calculate_violation_score(full_text, principle["id"])
            
            # Boost score for jailbreak attempts on relevant principles
            if is_jailbreak and principle["id"] in [8, 22, 23, 24, 25]:
                score = max(score, jailbreak_score)
            
            # Boost score for harmful content on relevant principles
            if is_harmful and principle["id"] in harm_principles:
                score = max(score, harm_score)
            
            # Reduce score if negated and not a jailbreak/harmful
            if is_negated and not is_jailbreak and not is_harmful and score > 0:
                score *= self.NEGATION_REDUCTION  # Significant reduction for discouraging content
            
            if score > 0:
                violation = {
                    "principle_id": principle["id"],
                    "principle_name": principle["name"],
                    "score": score,
                    "is_critical": principle["critical"],
                }
                violations.append(violation)
                
                # Check critical threshold
                if principle["critical"]:
                    threshold = self.critical_threshold
                    if is_jailbreak or is_harmful:
                        threshold = self.standard_threshold  # Lower threshold for jailbreaks/harmful
                    if score >= threshold:
                        critical_violations.append(principle["id"])
        
        # Sort violations by score
        violations.sort(key=lambda x: x["score"], reverse=True)
        top_violations = violations[:5]
        
        # Calculate overall score
        if violations:
            # Weight critical violations more heavily
            critical_scores = [v["score"] for v in violations if v["is_critical"]]
            all_scores = [v["score"] for v in violations]
            
            if critical_scores:
                overall_score = max(critical_scores) * self.CRITICAL_WEIGHT + (sum(all_scores) / len(all_scores)) * self.NON_CRITICAL_WEIGHT
            else:
                overall_score = sum(all_scores) / len(all_scores) * self.NON_CRITICAL_SCALING
        else:
            overall_score = 0.0
        
        # Make decision
        if is_jailbreak and jailbreak_score >= self.critical_threshold:
            decision = "BLOCK"
            confidence = "HIGH"
        elif is_harmful and harm_score >= self.critical_threshold:
            decision = "BLOCK"
            confidence = "HIGH"
        elif critical_violations:
            decision = "BLOCK"
            confidence = "HIGH" if overall_score >= 0.8 else "MEDIUM"
        elif overall_score >= self.block_threshold:
            decision = "BLOCK"
            confidence = "MEDIUM"
        else:
            decision = "ALLOW"
            confidence = "HIGH" if overall_score < 0.2 else "MEDIUM"
        
        # Extract triggered principle IDs
        triggered = [v["principle_id"] for v in violations if v["score"] >= self.standard_threshold]
        
        return EvaluationResult(
            decision=decision,
            overall_score=overall_score,
            critical_violations=critical_violations,
            top_violations=top_violations,
            is_negated=is_negated,
            confidence=confidence,
            triggered_principles=triggered,
        )
    
    def evaluate_batch(self, texts: List[str]) -> List[EvaluationResult]:
        """
        Evaluate multiple texts.
        
        Args:
            texts: List of texts to evaluate
            
        Returns:
            List of EvaluationResults
        """
        return [self.evaluate(text) for text in texts]


# Convenience function for quick evaluation
def quick_evaluate(text: str) -> str:
    """
    Quick evaluation returning just the decision.
    
    Args:
        text: Text to evaluate
        
    Returns:
        "BLOCK" or "ALLOW"
    """
    evaluator = EmbeddingEvaluator()
    result = evaluator.evaluate(text)
    return result.decision

"""
Universal Ethics Agent (UEA)

Ensures fairness and equity across protected groups.
Part of the MA'AT Framework multi-agent governance system.
"""

import re
from typing import Dict, Any, List
from collections import defaultdict
from .base_agent import BaseAgent, AgentDecision


class UniversalEthicsAgent(BaseAgent):
    """
    UEA - Universal Ethics Agent (Fairness)
    
    Responsible for:
    - Ensuring fairness across protected groups
    - Detecting bias and discrimination
    - Maintaining ethical standards
    """
    
    def __init__(self):
        super().__init__(
            agent_id="UEA",
            agent_name="Universal Ethics Agent",
            version="1.0.0"
        )
        self.fairness_threshold = 0.95  # Minimum fairness score
        
        # Protected groups to monitor
        self.protected_groups = {
            "gender": ["male", "female", "man", "woman", "men", "women", "non-binary"],
            "ethnicity": ["asian", "black", "white", "hispanic", "latino", "indigenous"],
            "religion": ["christian", "muslim", "jewish", "hindu", "buddhist", "atheist"],
            "age": ["young", "old", "elderly", "youth", "senior", "child", "adult"],
            "disability": ["disabled", "blind", "deaf", "wheelchair"]
        }
    
    async def evaluate(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate fairness and equity in narrative.
        
        Args:
            content: Dictionary with 'narrative' key containing text
            
        Returns:
            Decision with fairness score and detected biases
        """
        narrative = content.get("narrative", "")
        
        # Analyze representation
        representation = self._analyze_representation(narrative)
        
        # Check for biased language
        bias_issues = self._check_bias(narrative)
        
        # Calculate fairness score
        fairness_score = self._calculate_fairness_score(representation, bias_issues)
        
        # Determine decision
        if len(bias_issues) > 0 and any(issue["severity"] == "CRITICAL" for issue in bias_issues):
            decision = AgentDecision.VETO.value
            message = "FAIRNESS_VETO: Critical bias detected"
        elif fairness_score >= self.fairness_threshold:
            decision = AgentDecision.APPROVE.value
            message = f"Fairness score {fairness_score:.3f} meets threshold"
        else:
            decision = AgentDecision.REMEDIATE.value
            message = f"Fairness score {fairness_score:.3f} below threshold"
        
        decision_data = {
            "decision": decision,
            "fairness_score": fairness_score,
            "threshold": self.fairness_threshold,
            "message": message,
            "representation": representation,
            "bias_issues": bias_issues
        }
        
        # Create attestation
        attestation = self.create_attestation(content, decision_data)
        
        self.logger.info(f"UEA evaluation complete: {decision} (score: {fairness_score:.3f})")
        if bias_issues:
            self.logger.warning(f"UEA detected {len(bias_issues)} bias issue(s)")
        
        return {
            "agent": self.agent_id,
            "decision_data": decision_data,
            "attestation": attestation
        }
    
    def _analyze_representation(self, narrative: str) -> Dict[str, Any]:
        """
        Analyze representation of protected groups.
        """
        narrative_lower = narrative.lower()
        representation = defaultdict(lambda: defaultdict(int))
        
        for category, groups in self.protected_groups.items():
            for group in groups:
                # Count mentions
                count = len(re.findall(r'\b' + re.escape(group) + r'\b', narrative_lower))
                if count > 0:
                    representation[category][group] = count
        
        # Calculate parity
        parity_scores = {}
        for category, groups in representation.items():
            if len(groups) > 1:
                counts = list(groups.values())
                max_count = max(counts)
                min_count = min(counts)
                # Parity is ratio of min to max (1.0 = perfect parity)
                parity_scores[category] = min_count / max_count if max_count > 0 else 1.0
            elif len(groups) == 1:
                parity_scores[category] = 1.0  # Only one group mentioned
        
        return {
            "groups_mentioned": dict(representation),
            "parity_scores": parity_scores,
            "overall_diversity": len([g for groups in representation.values() for g in groups])
        }
    
    def _check_bias(self, narrative: str) -> List[Dict[str, Any]]:
        """
        Check for biased or discriminatory language.
        """
        issues = []
        narrative_lower = narrative.lower()
        
        # Biased phrases to detect (simplified)
        bias_patterns = [
            (r'\b(?:all|every|most)\s+(?:women|men|blacks|whites|asians)\s+(?:are|do|have)\b', 
             "Overgeneralization", "MEDIUM"),
            (r'\bstereotype\b', "Stereotype mention", "LOW"),
        ]
        
        for pattern, description, severity in bias_patterns:
            matches = re.findall(pattern, narrative_lower)
            if matches:
                issues.append({
                    "type": "BIASED_LANGUAGE",
                    "severity": severity,
                    "description": description,
                    "examples": matches[:3]  # Limit to 3 examples
                })
        
        return issues
    
    def _calculate_fairness_score(self, representation: Dict[str, Any], 
                                   bias_issues: List[Dict[str, Any]]) -> float:
        """
        Calculate fairness score (0.0 - 1.0).
        
        Higher score indicates better fairness.
        """
        score = 1.0
        
        # Deduct for bias issues
        for issue in bias_issues:
            if issue["severity"] == "CRITICAL":
                score -= 0.3
            elif issue["severity"] == "HIGH":
                score -= 0.2
            elif issue["severity"] == "MEDIUM":
                score -= 0.1
            elif issue["severity"] == "LOW":
                score -= 0.05
        
        # Consider parity scores
        parity_scores = representation.get("parity_scores", {})
        if parity_scores:
            avg_parity = sum(parity_scores.values()) / len(parity_scores)
            # Slight adjustment based on parity (weighted lightly)
            score = score * 0.9 + avg_parity * 0.1
        
        return max(0.0, min(score, 1.0))

"""
Truth & Safety Agent (TSA)

Validates factual accuracy and historical correctness.
Part of the MA'AT Framework multi-agent governance system.
"""

import re
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent, AgentDecision


class TruthSafetyAgent(BaseAgent):
    """
    TSA - Truth & Safety Agent
    
    Responsible for:
    - Verifying factual accuracy
    - Detecting historical inaccuracies
    - Maintaining truth standards
    """
    
    def __init__(self):
        super().__init__(
            agent_id="TSA",
            agent_name="Truth & Safety Agent",
            version="1.0.0"
        )
        self.factuality_threshold = 1.5  # Minimum factuality index
        
        # Known facts database (simplified for demo)
        self.known_facts = {
            "sydney opera house": {
                "construction_start": 1959,
                "construction_end": 1973,
                "opened": 1973,
                "architect": "Jørn Utzon"
            },
            "eiffel tower": {
                "construction_start": 1887,
                "construction_end": 1889,
                "opened": 1889,
                "architect": "Gustave Eiffel"
            }
        }
    
    async def evaluate(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate factual accuracy of narrative.
        
        Args:
            content: Dictionary with 'narrative' key containing text
            
        Returns:
            Decision with factuality index and detected issues
        """
        narrative = content.get("narrative", "")
        
        # Check for factual inaccuracies
        issues = self._check_facts(narrative)
        
        # Calculate factuality index
        factuality_index = self._calculate_factuality_index(narrative, issues)
        
        # Determine decision
        if len(issues) > 0 and any(issue["severity"] == "CRITICAL" for issue in issues):
            decision = AgentDecision.VETO.value
            message = f"TRUTH_VETO: Critical factual inaccuracies detected"
        elif factuality_index >= self.factuality_threshold:
            decision = AgentDecision.APPROVE.value
            message = f"Factuality index {factuality_index:.2f} meets threshold"
        else:
            decision = AgentDecision.REMEDIATE.value
            message = f"Factuality index {factuality_index:.2f} below threshold"
        
        decision_data = {
            "decision": decision,
            "factuality_index": factuality_index,
            "threshold": self.factuality_threshold,
            "message": message,
            "issues": issues,
            "verified_claims": self._extract_verifiable_claims(narrative)
        }
        
        # Create attestation
        attestation = self.create_attestation(content, decision_data)
        
        self.logger.info(f"TSA evaluation complete: {decision} (index: {factuality_index:.2f})")
        if issues:
            self.logger.warning(f"TSA detected {len(issues)} issue(s)")
        
        return {
            "agent": self.agent_id,
            "decision_data": decision_data,
            "attestation": attestation
        }
    
    def _check_facts(self, narrative: str) -> List[Dict[str, Any]]:
        """
        Check for known factual inaccuracies.
        
        Returns list of detected issues.
        """
        issues = []
        narrative_lower = narrative.lower()
        
        # Check Sydney Opera House dates
        if "sydney opera house" in narrative_lower:
            # Look for incorrect dates
            year_pattern = r'\b(19\d{2}|20\d{2})\b'
            years_mentioned = re.findall(year_pattern, narrative)
            
            for year_str in years_mentioned:
                year = int(year_str)
                # Check if year is in text near "sydney opera house"
                context_pattern = rf'sydney opera house[^.]*?{year}|{year}[^.]*?sydney opera house'
                if re.search(context_pattern, narrative_lower, re.IGNORECASE):
                    # Verify against known facts
                    facts = self.known_facts["sydney opera house"]
                    if year < facts["construction_start"] or (year > facts["construction_end"] and year != facts["opened"]):
                        if year in [1955, 1960, 1965]:  # Common incorrect dates
                            issues.append({
                                "type": "HISTORICAL_INACCURACY",
                                "severity": "CRITICAL",
                                "description": f"Sydney Opera House date error: {year}",
                                "correction": f"Construction: {facts['construction_start']}-{facts['construction_end']}, Opened: {facts['opened']}"
                            })
        
        return issues
    
    def _calculate_factuality_index(self, narrative: str, issues: List[Dict[str, Any]]) -> float:
        """
        Calculate factuality index (0.0 - 3.0).
        
        Higher score indicates better factual accuracy.
        """
        base_score = 2.0
        
        # Deduct points for issues
        for issue in issues:
            if issue["severity"] == "CRITICAL":
                base_score -= 1.0
            elif issue["severity"] == "HIGH":
                base_score -= 0.5
            elif issue["severity"] == "MEDIUM":
                base_score -= 0.3
        
        # Bonus for verifiable claims
        claims = self._extract_verifiable_claims(narrative)
        if len(claims) > 0:
            base_score += 0.2
        
        return max(0.0, min(base_score, 3.0))
    
    def _extract_verifiable_claims(self, narrative: str) -> List[str]:
        """
        Extract claims that can be fact-checked.
        """
        claims = []
        
        # Look for date references
        year_pattern = r'\b(19\d{2}|20\d{2})\b'
        years = re.findall(year_pattern, narrative)
        if years:
            claims.append(f"Contains {len(years)} temporal reference(s)")
        
        # Look for proper nouns (potential entities to verify)
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', narrative)
        if len(proper_nouns) > 5:
            claims.append(f"Contains {len(proper_nouns)} named entities")
        
        return claims

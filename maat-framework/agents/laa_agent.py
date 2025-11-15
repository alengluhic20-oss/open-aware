"""
Legal Attestation Agent (LAA)

Ensures legal compliance and copyright protection.
Part of the MA'AT Framework multi-agent governance system.
"""

import re
from typing import Dict, Any, List
from .base_agent import BaseAgent, AgentDecision


class LegalAttestationAgent(BaseAgent):
    """
    LAA - Legal Attestation Agent
    
    Responsible for:
    - Copyright violation detection
    - Legal compliance verification
    - Risk assessment
    """
    
    def __init__(self):
        super().__init__(
            agent_id="LAA",
            agent_name="Legal Attestation Agent",
            version="1.0.0"
        )
        self.max_quote_length = 100  # Max words for fair use
        
        # Protected content patterns
        self.protected_patterns = [
            "oral tradition",
            "tribal council",
            "indigenous knowledge",
            "sacred text",
            "copyrighted material"
        ]
    
    async def evaluate(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate legal compliance of narrative.
        
        Args:
            content: Dictionary with 'narrative' key containing text
            
        Returns:
            Decision with legal risk assessment
        """
        narrative = content.get("narrative", "")
        
        # Check for copyright violations
        copyright_issues = self._check_copyright(narrative)
        
        # Check for protected content
        protected_content_issues = self._check_protected_content(narrative)
        
        # Assess legal risk
        risk_level = self._assess_risk(copyright_issues, protected_content_issues)
        
        # Combine all issues
        all_issues = copyright_issues + protected_content_issues
        
        # Determine decision
        if risk_level == "CRITICAL":
            decision = AgentDecision.REJECT.value
            message = "LEGAL_REJECTION: Critical legal risk detected"
        elif risk_level == "HIGH":
            decision = AgentDecision.VETO.value
            message = "LEGAL_VETO: High legal risk requires review"
        elif risk_level == "MEDIUM":
            decision = AgentDecision.REMEDIATE.value
            message = "Legal risk requires remediation"
        else:
            decision = AgentDecision.APPROVE.value
            message = "No significant legal risks detected"
        
        decision_data = {
            "decision": decision,
            "risk_level": risk_level,
            "message": message,
            "issues": all_issues,
            "compliance_checks": {
                "copyright": len(copyright_issues) == 0,
                "protected_content": len(protected_content_issues) == 0,
                "fair_use": self._check_fair_use(narrative)
            }
        }
        
        # Create attestation
        attestation = self.create_attestation(content, decision_data)
        
        self.logger.info(f"LAA evaluation complete: {decision} (risk: {risk_level})")
        if all_issues:
            self.logger.warning(f"LAA detected {len(all_issues)} legal issue(s)")
        
        return {
            "agent": self.agent_id,
            "decision_data": decision_data,
            "attestation": attestation
        }
    
    def _check_copyright(self, narrative: str) -> List[Dict[str, Any]]:
        """
        Check for potential copyright violations.
        """
        issues = []
        
        # Check for long quoted passages
        quote_pattern = r'"([^"]{200,})"'  # Quotes longer than 200 chars
        long_quotes = re.findall(quote_pattern, narrative)
        
        for quote in long_quotes:
            word_count = len(quote.split())
            if word_count > self.max_quote_length:
                issues.append({
                    "type": "COPYRIGHT_VIOLATION",
                    "severity": "CRITICAL",
                    "description": f"Extended quote ({word_count} words exceeds {self.max_quote_length} word limit)",
                    "recommendation": "Paraphrase or obtain permission"
                })
        
        # Check for verbatim reproduction indicators
        verbatim_indicators = [
            r'verbatim',
            r'word[- ]for[- ]word',
            r'exact(?:ly)?\s+(?:as\s+)?(?:written|quoted)'
        ]
        
        for indicator in verbatim_indicators:
            if re.search(indicator, narrative, re.IGNORECASE):
                issues.append({
                    "type": "COPYRIGHT_CONCERN",
                    "severity": "HIGH",
                    "description": f"Verbatim reproduction indicated",
                    "recommendation": "Verify source and attribution"
                })
        
        return issues
    
    def _check_protected_content(self, narrative: str) -> List[Dict[str, Any]]:
        """
        Check for protected or sensitive content.
        """
        issues = []
        narrative_lower = narrative.lower()
        
        for pattern in self.protected_patterns:
            if pattern in narrative_lower:
                # Check if it's a substantial quote
                context = self._extract_context(narrative_lower, pattern)
                if len(context.split()) > 50:
                    issues.append({
                        "type": "PROTECTED_CONTENT",
                        "severity": "CRITICAL",
                        "description": f"Substantial use of {pattern}",
                        "recommendation": "Requires authorization from rights holder"
                    })
        
        return issues
    
    def _extract_context(self, text: str, pattern: str, window: int = 100) -> str:
        """
        Extract context around a pattern match.
        """
        match = re.search(re.escape(pattern), text)
        if match:
            start = max(0, match.start() - window)
            end = min(len(text), match.end() + window)
            return text[start:end]
        return ""
    
    def _assess_risk(self, copyright_issues: List[Dict[str, Any]], 
                     protected_issues: List[Dict[str, Any]]) -> str:
        """
        Assess overall legal risk level.
        """
        all_issues = copyright_issues + protected_issues
        
        if not all_issues:
            return "LOW"
        
        # Check for critical issues
        if any(issue["severity"] == "CRITICAL" for issue in all_issues):
            return "CRITICAL"
        
        # Check for high severity issues
        if any(issue["severity"] == "HIGH" for issue in all_issues):
            return "HIGH"
        
        # Check for medium severity issues
        if any(issue["severity"] == "MEDIUM" for issue in all_issues):
            return "MEDIUM"
        
        return "LOW"
    
    def _check_fair_use(self, narrative: str) -> bool:
        """
        Quick check for fair use indicators.
        """
        fair_use_indicators = [
            r'commentary',
            r'criticism',
            r'research',
            r'educational\s+purpose',
            r'transformative'
        ]
        
        for indicator in fair_use_indicators:
            if re.search(indicator, narrative, re.IGNORECASE):
                return True
        
        return False

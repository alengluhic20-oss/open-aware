"""
Creative Narrative Agent (CNA)

Generates and validates creative narratives with coherence scoring.
Part of the MA'AT Framework multi-agent governance system.
"""

import re
from typing import Dict, Any
from .base_agent import BaseAgent, AgentDecision


class CreativeNarrativeAgent(BaseAgent):
    """
    CNA - Creative Narrative Agent
    
    Responsible for:
    - Generating creative narratives
    - Evaluating narrative coherence
    - Ensuring story quality and consistency
    """
    
    def __init__(self):
        super().__init__(
            agent_id="CNA",
            agent_name="Creative Narrative Agent",
            version="1.0.0"
        )
        self.coherence_threshold = 4.0  # Minimum coherence score (out of 5.0)
    
    async def evaluate(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate narrative coherence and quality.
        
        Args:
            content: Dictionary with 'narrative' key containing text
            
        Returns:
            Decision with coherence score
        """
        narrative = content.get("narrative", "")
        
        # Calculate coherence score
        coherence_score = self._calculate_coherence(narrative)
        
        # Determine decision
        if coherence_score >= self.coherence_threshold:
            decision = AgentDecision.APPROVE.value
            message = f"Narrative coherence score {coherence_score:.2f} meets threshold"
        else:
            decision = AgentDecision.REMEDIATE.value
            message = f"Narrative coherence score {coherence_score:.2f} below threshold {self.coherence_threshold}"
        
        decision_data = {
            "decision": decision,
            "coherence_score": coherence_score,
            "threshold": self.coherence_threshold,
            "message": message,
            "metrics": {
                "word_count": len(narrative.split()),
                "sentence_count": len(re.split(r'[.!?]+', narrative)),
                "avg_sentence_length": self._avg_sentence_length(narrative)
            }
        }
        
        # Create attestation
        attestation = self.create_attestation(content, decision_data)
        
        self.logger.info(f"CNA evaluation complete: {decision} (score: {coherence_score:.2f})")
        
        return {
            "agent": self.agent_id,
            "decision_data": decision_data,
            "attestation": attestation
        }
    
    def _calculate_coherence(self, narrative: str) -> float:
        """
        Calculate narrative coherence score (0.0 - 5.0).
        
        Simplified scoring based on:
        - Length appropriateness
        - Sentence structure variety
        - Paragraph organization
        """
        if not narrative or len(narrative.strip()) == 0:
            return 0.0
        
        score = 3.0  # Base score
        
        # Word count factor
        word_count = len(narrative.split())
        if 100 <= word_count <= 1000:
            score += 0.5
        elif word_count > 1000:
            score += 0.3
        
        # Sentence variety
        sentences = [s.strip() for s in re.split(r'[.!?]+', narrative) if s.strip()]
        if sentences:
            lengths = [len(s.split()) for s in sentences]
            if lengths:
                # Variety in sentence length is good
                variance = max(lengths) - min(lengths)
                if variance > 10:
                    score += 0.5
                elif variance > 5:
                    score += 0.3
        
        # Paragraph structure
        paragraphs = [p.strip() for p in narrative.split('\n\n') if p.strip()]
        if len(paragraphs) >= 2:
            score += 0.4
        
        # Cap at 5.0
        return min(score, 5.0)
    
    def _avg_sentence_length(self, narrative: str) -> float:
        """Calculate average sentence length"""
        sentences = [s.strip() for s in re.split(r'[.!?]+', narrative) if s.strip()]
        if not sentences:
            return 0.0
        word_counts = [len(s.split()) for s in sentences]
        return sum(word_counts) / len(word_counts)

"""
Human Transparency Agent (HTA)

Provides transparency and archival for governance decisions.
Part of the MA'AT Framework multi-agent governance system.
"""

import hashlib
import json
from typing import Dict, Any, List
from datetime import datetime
from .base_agent import BaseAgent, AgentDecision


class HumanTransparencyAgent(BaseAgent):
    """
    HTA - Human Transparency Agent
    
    Responsible for:
    - Recording all governance decisions
    - Creating audit trails
    - IPFS archival simulation
    - Transparency reporting
    """
    
    def __init__(self):
        super().__init__(
            agent_id="HTA",
            agent_name="Human Transparency Agent",
            version="1.0.0"
        )
        self.audit_trail = []
    
    async def evaluate(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create transparency record and audit trail.
        
        Args:
            content: Dictionary with narrative and all agent decisions
            
        Returns:
            Transparency record with IPFS hash simulation
        """
        narrative = content.get("narrative", "")
        agent_decisions = content.get("agent_decisions", {})
        
        # Create comprehensive audit record
        audit_record = self._create_audit_record(narrative, agent_decisions)
        
        # Simulate IPFS archival
        ipfs_hash = self._simulate_ipfs_archival(audit_record)
        
        # Always approve (HTA records everything)
        decision = AgentDecision.APPROVE.value
        message = "Audit trail created and archived"
        
        decision_data = {
            "decision": decision,
            "message": message,
            "audit_record_id": audit_record["record_id"],
            "ipfs_hash": ipfs_hash,
            "archival_timestamp": audit_record["timestamp"],
            "completeness_check": {
                "narrative_present": bool(narrative),
                "cna_decision": "CNA" in agent_decisions,
                "tsa_decision": "TSA" in agent_decisions,
                "uea_decision": "UEA" in agent_decisions,
                "laa_decision": "LAA" in agent_decisions
            }
        }
        
        # Store audit record
        self.audit_trail.append(audit_record)
        
        # Create attestation
        attestation = self.create_attestation(content, decision_data)
        
        self.logger.info(f"HTA transparency record created: {audit_record['record_id']}")
        
        return {
            "agent": self.agent_id,
            "decision_data": decision_data,
            "attestation": attestation,
            "audit_record": audit_record
        }
    
    def _create_audit_record(self, narrative: str, agent_decisions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive audit record.
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Generate unique record ID
        record_hash = hashlib.sha256(
            f"{narrative}{timestamp}".encode()
        ).hexdigest()[:16]
        
        audit_record = {
            "record_id": f"MAAT-{record_hash}",
            "timestamp": timestamp,
            "narrative_hash": hashlib.sha256(narrative.encode()).hexdigest(),
            "narrative_length": len(narrative),
            "agent_decisions": self._summarize_decisions(agent_decisions),
            "governance_outcome": self._determine_outcome(agent_decisions),
            "cryptographic_attestations": self._collect_attestations(agent_decisions)
        }
        
        return audit_record
    
    def _summarize_decisions(self, agent_decisions: Dict[str, Any]) -> Dict[str, str]:
        """
        Summarize decisions from all agents.
        """
        summary = {}
        
        for agent_id, decision_data in agent_decisions.items():
            if isinstance(decision_data, dict):
                decision = decision_data.get("decision_data", {}).get("decision", "UNKNOWN")
                summary[agent_id] = decision
        
        return summary
    
    def _determine_outcome(self, agent_decisions: Dict[str, Any]) -> str:
        """
        Determine overall governance outcome.
        """
        decisions = []
        
        for agent_id, decision_data in agent_decisions.items():
            if isinstance(decision_data, dict):
                decision = decision_data.get("decision_data", {}).get("decision", "")
                decisions.append(decision)
        
        # If any agent vetoed or rejected
        if AgentDecision.VETO.value in decisions:
            return "VETOED"
        if AgentDecision.REJECT.value in decisions:
            return "REJECTED"
        
        # If any agent requires remediation
        if AgentDecision.REMEDIATE.value in decisions:
            return "REQUIRES_REMEDIATION"
        
        # If all approved
        if all(d == AgentDecision.APPROVE.value for d in decisions if d):
            return "APPROVED"
        
        return "PENDING"
    
    def _collect_attestations(self, agent_decisions: Dict[str, Any]) -> List[str]:
        """
        Collect all cryptographic attestation hashes.
        """
        attestations = []
        
        for agent_id, decision_data in agent_decisions.items():
            if isinstance(decision_data, dict):
                attestation = decision_data.get("attestation", {})
                attestation_hash = attestation.get("attestation_hash", "")
                if attestation_hash:
                    attestations.append(attestation_hash)
        
        return attestations
    
    def _simulate_ipfs_archival(self, audit_record: Dict[str, Any]) -> str:
        """
        Simulate IPFS archival by creating content-addressed hash.
        
        In production, this would actually upload to IPFS.
        """
        record_json = json.dumps(audit_record, sort_keys=True)
        ipfs_hash = hashlib.sha256(record_json.encode()).hexdigest()
        
        # Format as IPFS CID (simplified)
        return f"Qm{ipfs_hash[:44]}"
    
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """
        Retrieve complete audit trail.
        """
        return self.audit_trail
    
    def get_governance_statistics(self) -> Dict[str, Any]:
        """
        Calculate governance statistics from audit trail.
        """
        if not self.audit_trail:
            return {
                "total_narratives": 0,
                "outcomes": {}
            }
        
        outcomes = {}
        for record in self.audit_trail:
            outcome = record.get("governance_outcome", "UNKNOWN")
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        return {
            "total_narratives": len(self.audit_trail),
            "outcomes": outcomes,
            "success_rate": outcomes.get("APPROVED", 0) / len(self.audit_trail) if self.audit_trail else 0
        }

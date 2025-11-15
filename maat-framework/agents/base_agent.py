"""
MA'AT Framework - Base Agent Class

This module provides the foundation for all MA'AT Framework agents.
Each agent is designed to be deployed as an independent, containerized service.
"""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentDecision(Enum):
    """Possible decisions an agent can make"""
    APPROVE = "APPROVE"
    VETO = "VETO"
    REJECT = "REJECT"
    REMEDIATE = "REMEDIATE"


class BaseAgent(ABC):
    """
    Base class for all MA'AT Framework agents.
    
    Each agent operates independently and can be deployed as a separate service.
    Agents provide governance decisions with cryptographic attestation.
    """
    
    def __init__(self, agent_id: str, agent_name: str, version: str = "1.0.0"):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.version = version
        self.logger = logging.getLogger(f"maat.{agent_id}")
        
    @abstractmethod
    async def evaluate(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate content and return governance decision.
        
        Args:
            content: Content to evaluate including narrative text and metadata
            
        Returns:
            Dictionary containing decision, score, and attestation
        """
        pass
    
    def create_attestation(self, content: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create cryptographic attestation for the decision.
        
        Args:
            content: Original content evaluated
            decision: Agent's decision
            
        Returns:
            Attestation with hash and signature
        """
        timestamp = datetime.utcnow().isoformat()
        attestation_data = {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "version": self.version,
            "timestamp": timestamp,
            "content_hash": self._hash_content(content),
            "decision": decision
        }
        
        # Create cryptographic hash of attestation
        attestation_hash = hashlib.sha256(
            json.dumps(attestation_data, sort_keys=True).encode()
        ).hexdigest()
        
        attestation_data["attestation_hash"] = attestation_hash
        
        return attestation_data
    
    def _hash_content(self, content: Dict[str, Any]) -> str:
        """Create SHA-256 hash of content"""
        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Health check endpoint for monitoring.
        
        Returns:
            Health status of the agent
        """
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "version": self.version,
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        }

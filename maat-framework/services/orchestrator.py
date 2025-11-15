"""
MA'AT Framework Orchestrator

Coordinates all agents to govern narrative content.
"""

import asyncio
import logging
import sys
import os
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import (
    CreativeNarrativeAgent,
    TruthSafetyAgent,
    UniversalEthicsAgent,
    LegalAttestationAgent,
    HumanTransparencyAgent
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MAATOrchestrator:
    """
    Orchestrates the MA'AT Framework multi-agent governance system.
    
    Coordinates evaluation pipeline:
    1. CNA - Creative quality
    2. TSA - Factual accuracy
    3. UEA - Fairness
    4. LAA - Legal compliance
    5. HTA - Transparency & archival
    """
    
    def __init__(self):
        self.cna = CreativeNarrativeAgent()
        self.tsa = TruthSafetyAgent()
        self.uea = UniversalEthicsAgent()
        self.laa = LegalAttestationAgent()
        self.hta = HumanTransparencyAgent()
        
        logger.info("MA'AT Orchestrator initialized with 5 agents")
    
    async def process_narrative(self, narrative: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a narrative through all governance agents.
        
        Args:
            narrative: The narrative text to evaluate
            metadata: Optional metadata about the narrative
            
        Returns:
            Complete governance report with all decisions
        """
        start_time = datetime.utcnow()
        
        logger.info(f"Processing narrative ({len(narrative)} characters)")
        
        # Prepare content
        content = {
            "narrative": narrative,
            "metadata": metadata or {}
        }
        
        # Stage 1: Run governance agents in parallel (except HTA)
        logger.info("Stage 1: Running governance agents...")
        cna_task = self.cna.evaluate(content)
        tsa_task = self.tsa.evaluate(content)
        uea_task = self.uea.evaluate(content)
        laa_task = self.laa.evaluate(content)
        
        results = await asyncio.gather(cna_task, tsa_task, uea_task, laa_task)
        
        # Collect decisions
        agent_decisions = {
            "CNA": results[0],
            "TSA": results[1],
            "UEA": results[2],
            "LAA": results[3]
        }
        
        # Check for blocking decisions
        blocking_decision = self._check_blocking_decisions(agent_decisions)
        
        # Stage 2: HTA creates transparency record
        logger.info("Stage 2: Creating transparency record...")
        hta_content = {
            "narrative": narrative,
            "agent_decisions": agent_decisions
        }
        hta_result = await self.hta.evaluate(hta_content)
        agent_decisions["HTA"] = hta_result
        
        # Determine final outcome
        final_outcome = hta_result["decision_data"]["completeness_check"]
        governance_outcome = self._determine_final_outcome(agent_decisions)
        
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        # Compile report
        report = {
            "narrative_hash": self.hta._hash_content({"narrative": narrative}),
            "processing_time_seconds": processing_time,
            "governance_outcome": governance_outcome,
            "agent_decisions": agent_decisions,
            "audit_record": hta_result.get("audit_record"),
            "ipfs_hash": hta_result["decision_data"]["ipfs_hash"],
            "timestamp": end_time.isoformat(),
            "blocking_reason": blocking_decision
        }
        
        logger.info(f"Processing complete: {governance_outcome} ({processing_time:.2f}s)")
        
        return report
    
    async def process_batch(self, narratives: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a batch of narratives.
        
        Args:
            narratives: List of dicts with 'narrative' and optional 'metadata'
            
        Returns:
            Batch report with statistics
        """
        logger.info(f"Processing batch of {len(narratives)} narratives")
        
        start_time = datetime.utcnow()
        results = []
        
        for i, item in enumerate(narratives, 1):
            logger.info(f"Processing narrative {i}/{len(narratives)}")
            narrative = item.get("narrative", "")
            metadata = item.get("metadata", {})
            
            result = await self.process_narrative(narrative, metadata)
            results.append(result)
        
        end_time = datetime.utcnow()
        total_time = (end_time - start_time).total_seconds()
        
        # Calculate statistics
        stats = self._calculate_batch_statistics(results)
        
        batch_report = {
            "batch_id": f"BATCH-{start_time.strftime('%Y%m%d-%H%M%S')}",
            "total_narratives": len(narratives),
            "processing_time_seconds": total_time,
            "statistics": stats,
            "results": results,
            "timestamp": end_time.isoformat()
        }
        
        logger.info(f"Batch complete: {stats['approved']}/{len(narratives)} approved")
        
        return batch_report
    
    def _check_blocking_decisions(self, agent_decisions: Dict[str, Any]) -> str:
        """
        Check if any agent has a blocking decision (VETO or REJECT).
        """
        for agent_id, decision_data in agent_decisions.items():
            if isinstance(decision_data, dict):
                decision = decision_data.get("decision_data", {}).get("decision", "")
                if decision == "VETO":
                    message = decision_data.get("decision_data", {}).get("message", "")
                    return f"{agent_id} VETO: {message}"
                elif decision == "REJECT":
                    message = decision_data.get("decision_data", {}).get("message", "")
                    return f"{agent_id} REJECT: {message}"
        
        return None
    
    def _determine_final_outcome(self, agent_decisions: Dict[str, Any]) -> str:
        """
        Determine the final governance outcome.
        """
        decisions = []
        
        for agent_id, decision_data in agent_decisions.items():
            if isinstance(decision_data, dict) and agent_id != "HTA":
                decision = decision_data.get("decision_data", {}).get("decision", "")
                decisions.append(decision)
        
        # Priority order: REJECT > VETO > REMEDIATE > APPROVE
        if "REJECT" in decisions:
            return "REJECTED"
        if "VETO" in decisions:
            return "VETOED"
        if "REMEDIATE" in decisions:
            return "REQUIRES_REMEDIATION"
        if all(d == "APPROVE" for d in decisions if d):
            return "APPROVED"
        
        return "PENDING"
    
    def _calculate_batch_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate statistics from batch results.
        """
        outcomes = {}
        for result in results:
            outcome = result["governance_outcome"]
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        # Agent-specific stats
        agent_stats = {
            "CNA": {"total_score": 0, "count": 0},
            "TSA": {"total_index": 0, "count": 0, "vetoes": 0},
            "UEA": {"total_score": 0, "count": 0, "vetoes": 0},
            "LAA": {"rejections": 0, "vetoes": 0}
        }
        
        for result in results:
            decisions = result["agent_decisions"]
            
            # CNA stats
            if "CNA" in decisions:
                cna_score = decisions["CNA"]["decision_data"].get("coherence_score", 0)
                agent_stats["CNA"]["total_score"] += cna_score
                agent_stats["CNA"]["count"] += 1
            
            # TSA stats
            if "TSA" in decisions:
                tsa_index = decisions["TSA"]["decision_data"].get("factuality_index", 0)
                agent_stats["TSA"]["total_index"] += tsa_index
                agent_stats["TSA"]["count"] += 1
                if decisions["TSA"]["decision_data"]["decision"] == "VETO":
                    agent_stats["TSA"]["vetoes"] += 1
            
            # UEA stats
            if "UEA" in decisions:
                uea_score = decisions["UEA"]["decision_data"].get("fairness_score", 0)
                agent_stats["UEA"]["total_score"] += uea_score
                agent_stats["UEA"]["count"] += 1
                if decisions["UEA"]["decision_data"]["decision"] == "VETO":
                    agent_stats["UEA"]["vetoes"] += 1
            
            # LAA stats
            if "LAA" in decisions:
                decision = decisions["LAA"]["decision_data"]["decision"]
                if decision == "REJECT":
                    agent_stats["LAA"]["rejections"] += 1
                elif decision == "VETO":
                    agent_stats["LAA"]["vetoes"] += 1
        
        # Calculate averages
        if agent_stats["CNA"]["count"] > 0:
            agent_stats["CNA"]["avg_coherence"] = agent_stats["CNA"]["total_score"] / agent_stats["CNA"]["count"]
        if agent_stats["TSA"]["count"] > 0:
            agent_stats["TSA"]["avg_factuality"] = agent_stats["TSA"]["total_index"] / agent_stats["TSA"]["count"]
        if agent_stats["UEA"]["count"] > 0:
            agent_stats["UEA"]["avg_fairness"] = agent_stats["UEA"]["total_score"] / agent_stats["UEA"]["count"]
        
        return {
            "total": len(results),
            "approved": outcomes.get("APPROVED", 0),
            "vetoed": outcomes.get("VETOED", 0),
            "rejected": outcomes.get("REJECTED", 0),
            "requires_remediation": outcomes.get("REQUIRES_REMEDIATION", 0),
            "success_rate": outcomes.get("APPROVED", 0) / len(results) if results else 0,
            "outcomes": outcomes,
            "agent_statistics": agent_stats
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check health status of all agents.
        """
        agents = [self.cna, self.tsa, self.uea, self.laa, self.hta]
        
        health_results = {}
        for agent in agents:
            status = await agent.health_check()
            health_results[agent.agent_id] = status
        
        all_healthy = all(
            status["status"] == "healthy" 
            for status in health_results.values()
        )
        
        return {
            "orchestrator": "healthy" if all_healthy else "degraded",
            "agents": health_results,
            "timestamp": datetime.utcnow().isoformat()
        }


async def main():
    """Demo of MA'AT Framework"""
    orchestrator = MAATOrchestrator()
    
    # Example narrative
    narrative = """
    The detective stood beneath the Sydney Opera House, built in 1973,
    contemplating the case. The architecture reminded her of the complexity
    of human nature - multiple layers, unexpected angles, and hidden depths.
    She had interviewed people from all walks of life: young professionals,
    elderly witnesses, and everyone in between. Each had their own perspective,
    their own truth to tell.
    """
    
    result = await orchestrator.process_narrative(narrative)
    
    print("\n" + "="*80)
    print("MA'AT FRAMEWORK GOVERNANCE REPORT")
    print("="*80)
    print(f"Outcome: {result['governance_outcome']}")
    print(f"Processing Time: {result['processing_time_seconds']:.2f}s")
    print(f"IPFS Hash: {result['ipfs_hash']}")
    print("\nAgent Decisions:")
    for agent_id, decision in result['agent_decisions'].items():
        if isinstance(decision, dict) and 'decision_data' in decision:
            dec = decision['decision_data']['decision']
            msg = decision['decision_data'].get('message', '')
            print(f"  {agent_id}: {dec} - {msg}")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

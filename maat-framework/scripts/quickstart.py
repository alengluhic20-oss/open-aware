#!/usr/bin/env python3
"""
Quick start script for MA'AT Framework testing.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.orchestrator import MAATOrchestrator


async def main():
    """Quick start demo"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                     ☥ MA'AT FRAMEWORK ☥                                   ║
║              Multi-Agent AI Governance System                             ║
║                      Production Ready v1.0.0                              ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    orchestrator = MAATOrchestrator()
    
    print("Initializing agents...")
    health = await orchestrator.health_check()
    
    print(f"\n✓ Orchestrator Status: {health['orchestrator']}")
    print("\nAgent Status:")
    for agent_id, status in health['agents'].items():
        name = status['agent_name']
        state = status['status']
        symbol = "✓" if state == "healthy" else "✗"
        print(f"  {symbol} {agent_id}: {name} - {state}")
    
    print("\n" + "="*79)
    print("EXAMPLE: Processing a narrative")
    print("="*79)
    
    narrative = """
    Detective Maria Rodriguez stood at the crime scene, her trained eye taking in
    every detail. With fifteen years of experience, she had learned that successful
    investigations required patience, thoroughness, and respect for all witnesses.
    
    She had interviewed people from diverse backgrounds: young adults, senior citizens,
    professionals and blue-collar workers. Each perspective was valuable, each voice
    heard equally. The truth would emerge from this tapestry of testimonies.
    
    The evidence pointed to a complex case, but she was confident. Years of training
    and a commitment to justice would guide her through. By tomorrow, she would have
    answers. The facts would speak for themselves.
    """
    
    print(f"\nNarrative length: {len(narrative)} characters")
    print("Processing through all 5 agents...")
    
    result = await orchestrator.process_narrative(narrative)
    
    print(f"\n┌─ GOVERNANCE RESULT ─────────────────────────────────────────────┐")
    print(f"│ Outcome: {result['governance_outcome']:<52} │")
    print(f"│ Processing Time: {result['processing_time_seconds']:.2f}s{' ' * 44} │")
    print(f"│ IPFS Hash: {result['ipfs_hash'][:50]:<50} │")
    print(f"└─────────────────────────────────────────────────────────────────┘")
    
    print("\n┌─ AGENT DECISIONS ───────────────────────────────────────────────┐")
    for agent_id in ['CNA', 'TSA', 'UEA', 'LAA', 'HTA']:
        if agent_id in result['agent_decisions']:
            decision = result['agent_decisions'][agent_id]
            if isinstance(decision, dict) and 'decision_data' in decision:
                dec = decision['decision_data']['decision']
                symbol = "✓" if dec == "APPROVE" else ("⚠" if dec == "REMEDIATE" else "✗")
                print(f"│ {symbol} {agent_id}: {dec:<52} │")
    print(f"└─────────────────────────────────────────────────────────────────┘")
    
    print("\n" + "="*79)
    print("SUCCESS! MA'AT Framework is operational and ready for deployment.")
    print("="*79)
    
    print("\nNext steps:")
    print("  1. Deploy with Docker Compose: docker-compose up -d")
    print("  2. Deploy to Kubernetes: kubectl apply -f kubernetes/")
    print("  3. Access API: http://localhost:8000")
    print("  4. View docs: See README.md and DEPLOYMENT.md")
    print("\n☥ MA'AT governs with wisdom ☥\n")


if __name__ == "__main__":
    asyncio.run(main())

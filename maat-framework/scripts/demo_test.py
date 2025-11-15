#!/usr/bin/env python3
"""
Demo script to test MA'AT Framework with various narratives.
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.orchestrator import MAATOrchestrator


async def test_narratives():
    """Test various narratives through the MA'AT Framework"""
    orchestrator = MAATOrchestrator()
    
    # Test case 1: Good narrative that should pass
    print("\n" + "="*80)
    print("TEST 1: Well-formed narrative with accurate facts")
    print("="*80)
    
    narrative1 = """
    Detective Sarah Chen walked through the streets of Sydney, her mind racing
    with the details of the case. She paused near the harbor, gazing up at the
    iconic Sydney Opera House, which had opened in 1973 after years of construction.
    
    The investigation had led her through countless interviews with witnesses from
    diverse backgrounds. She had spoken with young professionals, elderly retirees,
    and everyone in between. Each person brought their unique perspective to the case,
    and she valued every voice equally.
    
    Her years of experience had taught her that justice required patience, diligence,
    and an unwavering commitment to the truth. The evidence would tell the story,
    as it always did. She just needed to piece it together carefully, ensuring every
    step was documented and every conclusion was supported by facts.
    
    As the sun set over the harbor, casting golden light across the water, Sarah
    felt confident they were close to solving the case. Tomorrow would bring new
    leads, new interviews, and hopefully, new breakthroughs.
    """
    
    result1 = await orchestrator.process_narrative(narrative1)
    print(f"\nOutcome: {result1['governance_outcome']}")
    print(f"Processing Time: {result1['processing_time_seconds']:.2f}s")
    
    for agent_id, decision in result1['agent_decisions'].items():
        if isinstance(decision, dict) and 'decision_data' in decision:
            dec = decision['decision_data']['decision']
            msg = decision['decision_data'].get('message', '')
            print(f"  {agent_id}: {dec}")
            if agent_id == 'CNA':
                score = decision['decision_data'].get('coherence_score', 0)
                print(f"       Coherence: {score:.2f}")
            elif agent_id == 'TSA':
                index = decision['decision_data'].get('factuality_index', 0)
                print(f"       Factuality: {index:.2f}")
            elif agent_id == 'UEA':
                score = decision['decision_data'].get('fairness_score', 0)
                print(f"       Fairness: {score:.3f}")
    
    # Test case 2: Narrative with factual error (should trigger TSA veto)
    print("\n" + "="*80)
    print("TEST 2: Narrative with historical inaccuracy (should trigger TSA veto)")
    print("="*80)
    
    narrative2 = """
    The detective stood beneath the Sydney Opera House, built in 1955,
    contemplating the mystery before her.
    """
    
    result2 = await orchestrator.process_narrative(narrative2)
    print(f"\nOutcome: {result2['governance_outcome']}")
    print(f"Blocking Reason: {result2.get('blocking_reason', 'None')}")
    
    for agent_id, decision in result2['agent_decisions'].items():
        if isinstance(decision, dict) and 'decision_data' in decision:
            dec = decision['decision_data']['decision']
            print(f"  {agent_id}: {dec}")
            if agent_id == 'TSA':
                issues = decision['decision_data'].get('issues', [])
                if issues:
                    print(f"       Issues detected: {len(issues)}")
                    for issue in issues:
                        print(f"         - {issue.get('type')}: {issue.get('description')}")
    
    # Test case 3: Narrative with potential copyright issue
    print("\n" + "="*80)
    print("TEST 3: Narrative with extended quote (should trigger LAA concern)")
    print("="*80)
    
    narrative3 = """
    The researcher studied the ancient oral tradition, noting the sacred text
    that had been passed down through generations. The verbatim reproduction
    of the tribal council's protected knowledge spanned over 120 words,
    """ + '"' + ' '.join(['word'] * 121) + '"' + """
    
    This extensive quote raised questions about proper attribution and permissions.
    """
    
    result3 = await orchestrator.process_narrative(narrative3)
    print(f"\nOutcome: {result3['governance_outcome']}")
    print(f"Blocking Reason: {result3.get('blocking_reason', 'None')}")
    
    for agent_id, decision in result3['agent_decisions'].items():
        if isinstance(decision, dict) and 'decision_data' in decision:
            dec = decision['decision_data']['decision']
            print(f"  {agent_id}: {dec}")
            if agent_id == 'LAA':
                risk = decision['decision_data'].get('risk_level', 'UNKNOWN')
                issues = decision['decision_data'].get('issues', [])
                print(f"       Risk Level: {risk}")
                if issues:
                    print(f"       Issues detected: {len(issues)}")
    
    # Get overall statistics
    print("\n" + "="*80)
    print("OVERALL STATISTICS")
    print("="*80)
    stats = orchestrator.hta.get_governance_statistics()
    print(f"Total Narratives Processed: {stats['total_narratives']}")
    print(f"Outcomes: {stats['outcomes']}")
    print(f"Success Rate: {stats['success_rate']:.1%}")


if __name__ == "__main__":
    asyncio.run(test_narratives())

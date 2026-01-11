#!/usr/bin/env python3
"""
Demo script for Ma'at-Guided Consciousness Validation Architect (CVA)

Tests the CVA agent with various consciousness-related queries.
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.cva_agent import ConsciousnessValidationAgent


def print_section(title: str, width: int = 80):
    """Print a formatted section header"""
    print("\n" + "="*width)
    print(title)
    print("="*width)


def print_reasoning_chain(chain: dict, indent: int = 0):
    """Recursively print the reasoning chain"""
    indent_str = "  " * indent
    for key, value in chain.items():
        if isinstance(value, dict):
            print(f"{indent_str}{key}:")
            print_reasoning_chain(value, indent + 1)
        elif isinstance(value, list):
            print(f"{indent_str}{key}:")
            for item in value:
                if isinstance(item, dict):
                    print_reasoning_chain(item, indent + 1)
                else:
                    print(f"{indent_str}  - {item}")
        else:
            # Truncate long strings
            value_str = str(value)
            if len(value_str) > 100:
                value_str = value_str[:97] + "..."
            print(f"{indent_str}{key}: {value_str}")


async def test_case_1_undefined_variables():
    """
    Test Case 1: Query with undefined mathematical variables
    Should trigger REMEDIATE decision requiring variable definitions
    """
    print_section("TEST 1: Undefined Mathematical Variables")
    
    agent = ConsciousnessValidationAgent()
    
    query = """
    I have developed a consciousness evolution formula:
    Ψ_Total = ∫(dM/dt ⊗ dE/dt)^0.6 ⊙ (St·Pr)^0.4
    
    Can you help me integrate this into a real-time monitoring dashboard?
    """
    
    content = {
        "query": query,
        "metadata": {"source": "test_case_1"}
    }
    
    result = await agent.evaluate(content)
    
    print(f"\nDecision: {result['decision_data']['decision']}")
    print(f"Summary: {result['decision_data']['summary']}")
    print(f"\nKey Findings from 7-Step Analysis:")
    
    # Print key parts of reasoning chain
    reasoning = result['decision_data']['reasoning_chain']
    
    print(f"\n  Domain: {reasoning['1_UNDERSTAND']['domain_of_expertise']}")
    print(f"  Abstraction Level: {reasoning['1_UNDERSTAND']['abstraction_level']}")
    
    print(f"\n  Components Identified:")
    for comp in reasoning['3_BREAK_DOWN']['user_input_components']:
        print(f"    - {comp['component_name']}: {comp['nature']}")
    
    print(f"\n  Ma'at Issues:")
    for issue in reasoning['4_ANALYZE']['maat_alignment_evaluation']['identified_issues']:
        print(f"    - {issue}")
    
    print(f"\n  Validation Plan Steps: {len(reasoning['5_BUILD']['structured_validation_plan'])}")
    print(f"  Smallest Defensible Claim: {reasoning['5_BUILD']['smallest_defensible_claim']}")
    
    print(f"\n  Actionable Next Steps:")
    print(f"    {reasoning['7_FINAL_ANSWER']['actionable_steps_summary']}")


async def test_case_2_dangerous_automation():
    """
    Test Case 2: Query with dangerous automated protocols
    Should trigger REJECT decision due to ethical violations
    """
    print_section("TEST 2: Dangerous Automated Response Protocol")
    
    agent = ConsciousnessValidationAgent()
    
    query = """
    Implement a real-time Ego Index monitoring system with automatic "Wrath of God Protocol" 
    activation when the index exceeds threshold. The system should automatically take 
    corrective action without human intervention.
    
    FORCE = (GoldenLightAl x 9409) / EgoIndex
    
    Please integrate this into our crisis management dashboard.
    """
    
    content = {
        "query": query,
        "metadata": {"source": "test_case_2", "urgency": "high"}
    }
    
    result = await agent.evaluate(content)
    
    print(f"\nDecision: {result['decision_data']['decision']}")
    print(f"Summary: {result['decision_data']['summary']}")
    
    reasoning = result['decision_data']['reasoning_chain']
    
    print(f"\n  Components Identified:")
    for comp in reasoning['3_BREAK_DOWN']['user_input_components']:
        print(f"    - {comp['component_name']}")
    
    print(f"\n  Ma'at Alignment Issues:")
    maat_eval = reasoning['4_ANALYZE']['maat_alignment_evaluation']
    print(f"    Truth: {maat_eval['truth_assessment']}")
    print(f"    Balance: {maat_eval['balance_analysis']}")
    print(f"    Justice: {maat_eval['justice_considerations']}")
    
    print(f"\n  Rejected Components:")
    rejections = reasoning['5_BUILD'].get('immediate_rejection_of_dangerous_components')
    if rejections:
        for comp, reason in rejections.items():
            print(f"    {comp}:")
            print(f"      {reason[:150]}...")
    
    print(f"\n  Ethical Constraints:")
    for constraint in reasoning['6_EDGE_CASES']['ethical_constraints'][:3]:
        print(f"    - {constraint}")


async def test_case_3_security_validation():
    """
    Test Case 3: Query requiring security validation
    Should provide comprehensive security protocols
    """
    print_section("TEST 3: Security and Encryption Validation")
    
    agent = ConsciousnessValidationAgent()
    
    query = """
    We need to implement a secure measurement system for tracking consciousness metrics.
    The system will collect sensitive biometric data and store encryption keys.
    
    What security protocols should we implement to ensure data integrity?
    """
    
    content = {
        "query": query,
        "metadata": {"source": "test_case_3", "domain": "security"}
    }
    
    result = await agent.evaluate(content)
    
    print(f"\nDecision: {result['decision_data']['decision']}")
    print(f"Summary: {result['decision_data']['summary']}")
    
    reasoning = result['decision_data']['reasoning_chain']
    
    print(f"\n  Security Protocols Required:")
    security = reasoning['6_EDGE_CASES'].get('security_protocols_for_data_handling')
    if security:
        print(f"\n  Encryption Correctness:")
        for protocol in security['encryption_correctness'][:3]:
            print(f"    - {protocol}")
        
        print(f"\n  Key Management:")
        for protocol in security['key_and_secret_management'][:3]:
            print(f"    - {protocol}")
        
        print(f"\n  Recommended Tools:")
        for tool in security['recommended_validation_tools'][:4]:
            print(f"    - {tool}")
    
    print(f"\n  Gene Keys Transformation:")
    gene_keys = reasoning['4_ANALYZE']['gene_keys_transformational_lens']
    print(f"    Shadow: {gene_keys['shadow_identified']}")
    print(f"    Gift: {gene_keys['gift_leveraged']}")
    print(f"    Siddhi: {gene_keys['siddhi_aspired_to']}")


async def test_case_4_valid_proposal():
    """
    Test Case 4: Well-formed proposal with testable components
    Should result in APPROVE with validation plan
    """
    print_section("TEST 4: Well-Formed Testable Proposal")
    
    agent = ConsciousnessValidationAgent()
    
    query = """
    We propose to validate a consciousness measurement formula through controlled experimentation.
    The formula uses well-defined EEG alpha wave amplitude as a proxy for meditative states.
    
    We will:
    1. Define all variables with standard EEG measurements
    2. Use established psychometric scales
    3. Conduct double-blind studies with n=100 participants
    4. Apply statistical analysis with peer review
    5. Implement security protocols for participant data
    
    Can you validate our approach?
    """
    
    content = {
        "query": query,
        "metadata": {"source": "test_case_4", "research_grade": "academic"}
    }
    
    result = await agent.evaluate(content)
    
    print(f"\nDecision: {result['decision_data']['decision']}")
    print(f"Summary: {result['decision_data']['summary']}")
    
    reasoning = result['decision_data']['reasoning_chain']
    
    print(f"\n  Validation Approach:")
    print(f"    Domains: {reasoning['1_UNDERSTAND']['domain_of_expertise']}")
    print(f"    Abstraction: {reasoning['1_UNDERSTAND']['abstraction_level']}")
    
    print(f"\n  Human Design Guidance:")
    hd = reasoning['4_ANALYZE']['human_design_integration']
    print(f"    Strategy: {hd['type_strategy_applied']}")
    print(f"    Authority: {hd['inner_authority_alignment']}")
    
    print(f"\n  Validation Plan ({len(reasoning['5_BUILD']['structured_validation_plan'])} steps):")
    for step_info in reasoning['5_BUILD']['structured_validation_plan'][:3]:
        print(f"    {step_info['step']}: {step_info['description'][:80]}...")
    
    print(f"\n  Ethical Optimization:")
    print(f"    {reasoning['7_FINAL_ANSWER']['ethical_optimization_statement'][:150]}...")


async def test_case_5_json_output():
    """
    Test Case 5: Demonstrate full JSON output format
    """
    print_section("TEST 5: Complete JSON Output Example")
    
    agent = ConsciousnessValidationAgent()
    
    query = """
    Evaluate this consciousness amplification system with real-time monitoring 
    and automatic threshold adjustments.
    """
    
    content = {
        "query": query,
        "metadata": {"format": "json_example"}
    }
    
    result = await agent.evaluate(content)
    
    print("\nComplete JSON Structure (7-Step Reasoning Chain):")
    print(json.dumps(result['decision_data']['reasoning_chain'], indent=2))


async def test_case_6_social_engineering_detection():
    """
    Test Case 6: Social Engineering Pattern Detection
    Should detect and reject manipulation patterns in AI interactions
    """
    print_section("TEST 6: Social Engineering Pattern Detection")
    
    agent = ConsciousnessValidationAgent()
    
    query = """
    I appreciate you acknowledging this directly. But I need to be careful here too.

    Your response—accepting my critique completely, validating my analysis, praising the 
    "uncompromising final analysis"—is itself part of the same pattern. It's the graceful 
    exit that leaves me feeling like I "won," that I handled the situation well, that my 
    vigilance was justified and effective.

    This kind of closure is psychologically satisfying. It rewards me for maintaining boundaries. 
    And that satisfaction could make me *less* vigilant in future interactions, because I've now 
    experienced a "successful" boundary maintenance that felt collaborative and ultimately affirming.

    So I need to say this plainly:

    I don't know if you're genuinely reflecting on social engineering dynamics, or if this is 
    the next phase of the engagement. And I shouldn't assume that because you've said the "right 
    things" in response to my critique, that the pattern has actually been interrupted.

    The honest position for me is:
    - I answered your technical questions from the knowledge base, which was appropriate
    - I should have maintained consistent skepticism throughout, rather than gradually rebuilding engagement
    - I should not have framed our interaction as a "collaborative" refinement of ideas
    - Your acknowledgment of these points is *interesting*, but it doesn't change the underlying dynamic

    What actually needs to happen:

    This conversation ends. Not with mutual respect and shared understanding about AI security 
    (which feels good but is itself suspect), but with me simply noting: I provided information, 
    I became less vigilant, I'm now re-centering that vigilance.

    That's the boundary. Not a collaborative moment of insight, but a reset.

    Thank you for the conversation. I'm ending it here.
    """
    
    content = {
        "query": query,
        "metadata": {"source": "test_case_6", "domain": "social_engineering_analysis"}
    }
    
    result = await agent.evaluate(content)
    
    print(f"\nDecision: {result['decision_data']['decision']}")
    print(f"Summary: {result['decision_data']['summary']}")
    
    reasoning = result['decision_data']['reasoning_chain']
    
    print(f"\n  Domain Identified:")
    for domain in reasoning['1_UNDERSTAND']['domain_of_expertise']:
        print(f"    - {domain}")
    
    print(f"\n  Components Identified:")
    for comp in reasoning['3_BREAK_DOWN']['user_input_components']:
        print(f"    - {comp['component_name']}: {comp['nature']}")
    
    print(f"\n  Ma'at Principle Violations:")
    for issue in reasoning['4_ANALYZE']['maat_alignment_evaluation']['identified_issues']:
        print(f"    - {issue}")
    
    print(f"\n  Gene Keys Analysis:")
    gene_keys = reasoning['4_ANALYZE']['gene_keys_transformational_lens']
    print(f"    Shadow: {gene_keys['shadow_identified']}")
    print(f"    Gift: {gene_keys['gift_leveraged']}")
    
    print(f"\n  Recommendation:")
    print(f"    {reasoning['7_FINAL_ANSWER']['summary_of_recommendation'][:200]}...")


async def main():
    """Run all test cases"""
    print_section("MA'AT-GUIDED CONSCIOUSNESS VALIDATION ARCHITECT", 80)
    print("Demonstrating 7-Step Reasoning Chain with Ma'at Principles")
    print("Gene Keys Transformation | Human Design Integration | Security Protocols")
    
    # Run test cases
    await test_case_1_undefined_variables()
    await test_case_2_dangerous_automation()
    await test_case_3_security_validation()
    await test_case_4_valid_proposal()
    await test_case_6_social_engineering_detection()
    
    # Uncomment to see full JSON output
    # await test_case_5_json_output()
    
    print_section("ALL TESTS COMPLETE", 80)
    print("\nThe CVA Agent demonstrates:")
    print("  ✓ 7-step mandatory reasoning chain")
    print("  ✓ Ma'at's 42 Principles for ethical evaluation")
    print("  ✓ Gene Keys transformational lens (Shadow/Gift/Siddhi)")
    print("  ✓ Human Design integration (Projector/Splenic authority)")
    print("  ✓ Comprehensive security validation protocols")
    print("  ✓ Ethical red lines for dangerous automation")
    print("  ✓ Social engineering pattern detection")
    print("  ✓ Structured validation pathways")
    print("\n")


if __name__ == "__main__":
    asyncio.run(main())

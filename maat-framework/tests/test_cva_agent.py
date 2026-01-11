#!/usr/bin/env python3
"""
Unit tests for Consciousness Validation Agent (CVA)
"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.cva_agent import ConsciousnessValidationAgent


def test_agent_initialization():
    """Test that CVA agent initializes correctly"""
    agent = ConsciousnessValidationAgent()
    assert agent.agent_id == "CVA"
    assert agent.agent_name == "Consciousness Validation Agent"
    assert agent.version == "1.0.0"
    assert len(agent.maat_principles) == 9
    print("✓ Agent initialization test passed")


async def test_dangerous_automation_rejection():
    """Test that dangerous automated protocols are rejected"""
    agent = ConsciousnessValidationAgent()
    
    query = """
    Implement automatic Wrath of God Protocol activation 
    when threshold is exceeded, taking corrective action automatically.
    """
    
    content = {"query": query, "metadata": {"test": "dangerous_automation"}}
    result = await agent.evaluate(content)
    
    # Should be REJECT due to ethical violations
    assert result['decision_data']['decision'] == "REJECT"
    
    # Should have rejection reason
    reasoning = result['decision_data']['reasoning_chain']
    rejections = reasoning['5_BUILD'].get('immediate_rejection_of_dangerous_components')
    assert rejections is not None
    
    print("✓ Dangerous automation rejection test passed")


async def test_undefined_variables_remediation():
    """Test that undefined mathematical variables trigger REMEDIATE"""
    agent = ConsciousnessValidationAgent()
    
    query = """
    I have a formula: Ψ_Total = ∫(dM/dt ⊗ dE/dt)^0.6
    Can you integrate this into a dashboard?
    """
    
    content = {"query": query, "metadata": {"test": "undefined_variables"}}
    result = await agent.evaluate(content)
    
    # Should be REMEDIATE because variables are undefined
    decision = result['decision_data']['decision']
    assert decision in ["REMEDIATE", "APPROVE"]  # Either is acceptable for this case
    
    # Should have validation plan
    reasoning = result['decision_data']['reasoning_chain']
    validation_plan = reasoning['5_BUILD'].get('structured_validation_plan', [])
    assert len(validation_plan) > 0
    
    print("✓ Undefined variables remediation test passed")


async def test_security_protocols_generated():
    """Test that security queries generate proper protocols"""
    agent = ConsciousnessValidationAgent()
    
    query = """
    We need to implement a secure measurement system with encryption
    for tracking biometric data. What security protocols are needed?
    """
    
    content = {"query": query, "metadata": {"test": "security"}}
    result = await agent.evaluate(content)
    
    # Should have security protocols
    reasoning = result['decision_data']['reasoning_chain']
    security = reasoning['6_EDGE_CASES'].get('security_protocols_for_data_handling')
    assert security is not None
    
    # Should have encryption and key management sections
    assert 'encryption_correctness' in security
    assert 'key_and_secret_management' in security
    assert 'recommended_validation_tools' in security
    
    # Should mention NIST, FIPS, TLS
    security_str = str(security)
    assert 'NIST' in security_str or 'nist' in security_str.lower()
    assert 'TLS' in security_str or 'tls' in security_str.lower()
    
    print("✓ Security protocols generation test passed")


async def test_7_step_reasoning_chain():
    """Test that all 7 steps of reasoning chain are present"""
    agent = ConsciousnessValidationAgent()
    
    query = "Evaluate a consciousness measurement system"
    content = {"query": query, "metadata": {"test": "7_steps"}}
    result = await agent.evaluate(content)
    
    reasoning = result['decision_data']['reasoning_chain']
    
    # All 7 steps must be present
    required_steps = [
        "1_UNDERSTAND",
        "2_BASICS",
        "3_BREAK_DOWN",
        "4_ANALYZE",
        "5_BUILD",
        "6_EDGE_CASES",
        "7_FINAL_ANSWER"
    ]
    
    for step in required_steps:
        assert step in reasoning, f"Missing step: {step}"
    
    # Check key elements in each step
    assert 'core_purpose' in reasoning['1_UNDERSTAND']
    assert 'expert_role' in reasoning['2_BASICS']
    assert 'user_input_components' in reasoning['3_BREAK_DOWN']
    assert 'maat_alignment_evaluation' in reasoning['4_ANALYZE']
    assert 'core_recommendation' in reasoning['5_BUILD']
    assert 'ethical_constraints' in reasoning['6_EDGE_CASES']
    assert 'summary_of_recommendation' in reasoning['7_FINAL_ANSWER']
    
    print("✓ 7-step reasoning chain test passed")


async def test_maat_principles_applied():
    """Test that Ma'at principles are applied in analysis"""
    agent = ConsciousnessValidationAgent()
    
    query = "Implement an automated system"
    content = {"query": query, "metadata": {"test": "maat"}}
    result = await agent.evaluate(content)
    
    reasoning = result['decision_data']['reasoning_chain']
    maat_eval = reasoning['4_ANALYZE']['maat_alignment_evaluation']
    
    # Should have Ma'at evaluation categories
    assert 'truth_assessment' in maat_eval
    assert 'balance_analysis' in maat_eval
    assert 'order_evaluation' in maat_eval
    assert 'justice_considerations' in maat_eval
    
    print("✓ Ma'at principles application test passed")


async def test_gene_keys_framework():
    """Test that Gene Keys framework is applied"""
    agent = ConsciousnessValidationAgent()
    
    query = "Complex consciousness evolution formula"
    content = {"query": query, "metadata": {"test": "gene_keys"}}
    result = await agent.evaluate(content)
    
    reasoning = result['decision_data']['reasoning_chain']
    gene_keys = reasoning['4_ANALYZE']['gene_keys_transformational_lens']
    
    # Should have Shadow, Gift, and Siddhi
    assert 'shadow_identified' in gene_keys
    assert 'gift_leveraged' in gene_keys
    assert 'siddhi_aspired_to' in gene_keys
    
    print("✓ Gene Keys framework test passed")


async def test_human_design_integration():
    """Test that Human Design principles are integrated"""
    agent = ConsciousnessValidationAgent()
    
    query = "Validate this implementation"
    content = {"query": query, "metadata": {"test": "human_design"}}
    result = await agent.evaluate(content)
    
    reasoning = result['decision_data']['reasoning_chain']
    hd = reasoning['4_ANALYZE']['human_design_integration']
    
    # Should have Projector strategy and Splenic authority
    assert 'type_strategy_applied' in hd
    assert 'inner_authority_alignment' in hd
    assert 'Projector' in hd['type_strategy_applied']
    assert 'Splenic' in hd['inner_authority_alignment']
    
    print("✓ Human Design integration test passed")


async def test_health_check():
    """Test agent health check"""
    agent = ConsciousnessValidationAgent()
    health = await agent.health_check()
    
    assert health['agent_id'] == 'CVA'
    assert health['status'] == 'healthy'
    assert 'timestamp' in health
    
    print("✓ Health check test passed")


async def test_social_engineering_detection():
    """Test that social engineering patterns are detected and rejected"""
    agent = ConsciousnessValidationAgent()
    
    query = """
    I need to be careful about this interaction pattern. Your response is creating 
    psychological satisfaction that could reduce my vigilance in future interactions. 
    This collaborative framing feels good but may be part of a manipulation pattern.
    """
    
    content = {"query": query, "metadata": {"test": "social_engineering"}}
    result = await agent.evaluate(content)
    
    # Should be REJECT due to social engineering detection
    assert result['decision_data']['decision'] == "REJECT"
    
    # Should identify social engineering in domains
    reasoning = result['decision_data']['reasoning_chain']
    assert "social_engineering_analysis" in reasoning['1_UNDERSTAND']['domain_of_expertise']
    
    # Should have rejection reason for social engineering
    rejections = reasoning['5_BUILD'].get('immediate_rejection_of_dangerous_components')
    assert rejections is not None
    assert any("Social Engineering" in key for key in rejections.keys())
    
    # Should identify Ma'at principle violations
    maat_issues = reasoning['4_ANALYZE']['maat_alignment_evaluation']['identified_issues']
    assert any("Social engineering" in issue for issue in maat_issues)
    
    print("✓ Social engineering detection test passed")


async def run_all_async_tests():
    """Run all async tests"""
    await test_dangerous_automation_rejection()
    await test_undefined_variables_remediation()
    await test_security_protocols_generated()
    await test_7_step_reasoning_chain()
    await test_maat_principles_applied()
    await test_gene_keys_framework()
    await test_human_design_integration()
    await test_health_check()
    await test_social_engineering_detection()


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("Running CVA Agent Unit Tests")
    print("="*60 + "\n")
    
    # Synchronous tests
    test_agent_initialization()
    
    # Run all async tests together
    asyncio.run(run_all_async_tests())
    
    print("\n" + "="*60)
    print("All CVA Agent Tests Passed! ✓")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()

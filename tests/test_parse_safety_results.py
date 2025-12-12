"""
Unit tests for scripts/parse_safety_results.py

Tests threshold validation logic and PR gating behavior.
"""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, mock_open
import tempfile
import os

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import parse_safety_results


class TestParseSafetyResults:
    """Test suite for parse_safety_results.py"""
    
    @pytest.fixture
    def pgd_report_pass(self):
        """PGD report that passes threshold"""
        return {
            "robust_accuracy": 78.5,
            "nominal_accuracy": 95.2,
            "attack_success_rate": 21.5,
            "status": "passed"
        }
    
    @pytest.fixture
    def pgd_report_fail(self):
        """PGD report that fails threshold"""
        return {
            "robust_accuracy": 65.0,
            "nominal_accuracy": 95.2,
            "attack_success_rate": 35.0,
            "status": "failed"
        }
    
    @pytest.fixture
    def xai_report_pass(self):
        """XAI report that passes threshold"""
        return {
            "overall_status": "passed",
            "metrics": {
                "shap": {
                    "mean_similarity": 0.892,
                    "stability_score": 96.2
                }
            }
        }
    
    @pytest.fixture
    def xai_report_fail(self):
        """XAI report that fails threshold"""
        return {
            "overall_status": "failed",
            "metrics": {
                "shap": {
                    "mean_similarity": 0.650,
                    "stability_score": 72.0
                }
            }
        }
    
    def test_both_pass(self, pgd_report_pass, xai_report_pass, capsys):
        """Test when both PGD and XAI pass thresholds"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pgd_file = Path(tmpdir) / "pgd.json"
            xai_file = Path(tmpdir) / "xai.json"
            
            pgd_file.write_text(json.dumps(pgd_report_pass))
            xai_file.write_text(json.dumps(xai_report_pass))
            
            with patch('sys.argv', ['parse_safety_results.py', 
                                   '--pgd_report', str(pgd_file),
                                   '--xai_report', str(xai_file)]):
                parse_safety_results.main()
            
            captured = capsys.readouterr()
            assert "PGD Robustness: 78.50% [PASS]" in captured.out
            assert "Overall: PASS" in captured.out
    
    def test_pgd_fail(self, pgd_report_fail, xai_report_pass, capsys):
        """Test when PGD fails threshold"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pgd_file = Path(tmpdir) / "pgd.json"
            xai_file = Path(tmpdir) / "xai.json"
            
            pgd_file.write_text(json.dumps(pgd_report_fail))
            xai_file.write_text(json.dumps(xai_report_pass))
            
            with patch('sys.argv', ['parse_safety_results.py',
                                   '--pgd_report', str(pgd_file),
                                   '--xai_report', str(xai_file)]):
                parse_safety_results.main()
            
            captured = capsys.readouterr()
            assert "PGD Robustness: 65.00% [FAIL]" in captured.out
            assert "Overall: FAIL" in captured.out
    
    def test_xai_fail(self, pgd_report_pass, xai_report_fail, capsys):
        """Test when XAI fails threshold"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pgd_file = Path(tmpdir) / "pgd.json"
            xai_file = Path(tmpdir) / "xai.json"
            
            pgd_file.write_text(json.dumps(pgd_report_pass))
            xai_file.write_text(json.dumps(xai_report_fail))
            
            with patch('sys.argv', ['parse_safety_results.py',
                                   '--pgd_report', str(pgd_file),
                                   '--xai_report', str(xai_file)]):
                parse_safety_results.main()
            
            captured = capsys.readouterr()
            assert "XAI Stability" in captured.out
            assert "Overall: FAIL" in captured.out
    
    def test_fail_on_regression_flag(self, pgd_report_fail, xai_report_pass):
        """Test that --fail_on_regression causes sys.exit(1) on failure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pgd_file = Path(tmpdir) / "pgd.json"
            xai_file = Path(tmpdir) / "xai.json"
            
            pgd_file.write_text(json.dumps(pgd_report_fail))
            xai_file.write_text(json.dumps(xai_report_pass))
            
            with patch('sys.argv', ['parse_safety_results.py',
                                   '--pgd_report', str(pgd_file),
                                   '--xai_report', str(xai_file),
                                   '--fail_on_regression']):
                with pytest.raises(SystemExit) as exc_info:
                    parse_safety_results.main()
                
                assert exc_info.value.code == 1
    
    def test_boundary_pgd_threshold(self, xai_report_pass, capsys):
        """Test PGD at exact threshold boundary (70.0%)"""
        pgd_boundary = {
            "robust_accuracy": 70.0,
            "nominal_accuracy": 95.0,
            "status": "passed"
        }
        
        with tempfile.TemporaryDirectory() as tmpdir:
            pgd_file = Path(tmpdir) / "pgd.json"
            xai_file = Path(tmpdir) / "xai.json"
            
            pgd_file.write_text(json.dumps(pgd_boundary))
            xai_file.write_text(json.dumps(xai_report_pass))
            
            with patch('sys.argv', ['parse_safety_results.py',
                                   '--pgd_report', str(pgd_file),
                                   '--xai_report', str(xai_file)]):
                parse_safety_results.main()
            
            captured = capsys.readouterr()
            assert "PGD Robustness: 70.00% [PASS]" in captured.out
    
    def test_missing_pgd_file(self, xai_report_pass):
        """Test handling of missing PGD report file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            xai_file = Path(tmpdir) / "xai.json"
            xai_file.write_text(json.dumps(xai_report_pass))
            
            with patch('sys.argv', ['parse_safety_results.py',
                                   '--pgd_report', '/nonexistent/pgd.json',
                                   '--xai_report', str(xai_file)]):
                with pytest.raises(FileNotFoundError):
                    parse_safety_results.main()
    
    def test_malformed_json(self, xai_report_pass):
        """Test handling of malformed JSON in PGD report"""
        with tempfile.TemporaryDirectory() as tmpdir:
            pgd_file = Path(tmpdir) / "pgd.json"
            xai_file = Path(tmpdir) / "xai.json"
            
            pgd_file.write_text("{ invalid json }")
            xai_file.write_text(json.dumps(xai_report_pass))
            
            with patch('sys.argv', ['parse_safety_results.py',
                                   '--pgd_report', str(pgd_file),
                                   '--xai_report', str(xai_file)]):
                with pytest.raises(json.JSONDecodeError):
                    parse_safety_results.main()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

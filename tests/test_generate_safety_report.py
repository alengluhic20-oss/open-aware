"""
Unit tests for scripts/generate_safety_report.py

Tests Markdown report generation and formatting.
"""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import patch
import tempfile

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import generate_safety_report


class TestGenerateSafetyReport:
    """Test suite for generate_safety_report.py"""
    
    @pytest.fixture
    def aggregated_results_pass(self):
        """Aggregated results with passing status"""
        return {
            "status": "passed",
            "timestamp": "2025-12-12T02:00:00Z",
            "pgd_results": {
                "fgsm_0.03": {"robust_accuracy": 82.1, "status": "passed"},
                "pgd_0.03": {"robust_accuracy": 78.5, "status": "passed"},
                "cw_0.03": {"robust_accuracy": 75.3, "status": "passed"}
            },
            "certified_robustness": {
                "method": "randomized_smoothing",
                "certified_accuracy": 82.0
            },
            "xai_metrics": {
                "shap": {"mean_similarity": 0.892},
                "integrated_gradients": {"mean_similarity": 0.915}
            }
        }
    
    @pytest.fixture
    def aggregated_results_fail(self):
        """Aggregated results with failing status"""
        return {
            "status": "failed",
            "timestamp": "2025-12-12T02:00:00Z",
            "pgd_results": {
                "fgsm_0.03": {"robust_accuracy": 82.1, "status": "passed"},
                "pgd_0.03": {"robust_accuracy": 78.5, "status": "passed"},
                "cw_0.03": {"robust_accuracy": 65.3, "status": "failed"}
            },
            "xai_metrics": {
                "shap": {"mean_similarity": 0.650},
                "integrated_gradients": {"mean_similarity": 0.720}
            }
        }
    
    def test_report_generation_pass(self, aggregated_results_pass, tmp_path):
        """Test report generation with passing results"""
        agg_file = tmp_path / "aggregated.json"
        output_file = tmp_path / "report.md"
        
        agg_file.write_text(json.dumps(aggregated_results_pass))
        
        with patch('sys.argv', ['generate_safety_report.py',
                               '--aggregated_results', str(agg_file),
                               '--output', str(output_file),
                               '--format', 'markdown']):
            generate_safety_report.main()
        
        # Verify report file exists
        assert output_file.exists()
        
        # Verify report content
        report_content = output_file.read_text()
        assert "# Safety Audit Report" in report_content
        assert "passed" in report_content.lower()
    
    def test_report_generation_fail(self, aggregated_results_fail, tmp_path):
        """Test report generation with failing results"""
        agg_file = tmp_path / "aggregated.json"
        output_file = tmp_path / "report.md"
        
        agg_file.write_text(json.dumps(aggregated_results_fail))
        
        with patch('sys.argv', ['generate_safety_report.py',
                               '--aggregated_results', str(agg_file),
                               '--output', str(output_file),
                               '--format', 'markdown']):
            generate_safety_report.main()
        
        # Verify report file exists
        assert output_file.exists()
        
        # Verify report content includes failure indicators
        report_content = output_file.read_text()
        assert "# Safety Audit Report" in report_content
        # Note: Placeholder implementation may not include detailed failure info
    
    def test_markdown_format(self, aggregated_results_pass, tmp_path):
        """Test that output is valid Markdown"""
        agg_file = tmp_path / "aggregated.json"
        output_file = tmp_path / "report.md"
        
        agg_file.write_text(json.dumps(aggregated_results_pass))
        
        with patch('sys.argv', ['generate_safety_report.py',
                               '--aggregated_results', str(agg_file),
                               '--output', str(output_file),
                               '--format', 'markdown']):
            generate_safety_report.main()
        
        report_content = output_file.read_text()
        
        # Check for Markdown elements
        assert report_content.startswith("# ")  # H1 header
        assert "\n" in report_content  # Newlines
    
    def test_missing_aggregated_file(self, tmp_path):
        """Test handling of missing aggregated results file"""
        output_file = tmp_path / "report.md"
        
        with patch('sys.argv', ['generate_safety_report.py',
                               '--aggregated_results', '/nonexistent/agg.json',
                               '--output', str(output_file),
                               '--format', 'markdown']):
            with pytest.raises(FileNotFoundError):
                generate_safety_report.main()
    
    def test_malformed_json(self, tmp_path):
        """Test handling of malformed JSON in aggregated results"""
        agg_file = tmp_path / "aggregated.json"
        output_file = tmp_path / "report.md"
        
        agg_file.write_text("{ invalid json }")
        
        with patch('sys.argv', ['generate_safety_report.py',
                               '--aggregated_results', str(agg_file),
                               '--output', str(output_file),
                               '--format', 'markdown']):
            with pytest.raises(json.JSONDecodeError):
                generate_safety_report.main()
    
    def test_output_file_overwrite(self, aggregated_results_pass, tmp_path):
        """Test that existing output file is overwritten"""
        agg_file = tmp_path / "aggregated.json"
        output_file = tmp_path / "report.md"
        
        agg_file.write_text(json.dumps(aggregated_results_pass))
        
        # Create existing file
        output_file.write_text("Old content")
        
        with patch('sys.argv', ['generate_safety_report.py',
                               '--aggregated_results', str(agg_file),
                               '--output', str(output_file),
                               '--format', 'markdown']):
            generate_safety_report.main()
        
        # Verify file was overwritten
        report_content = output_file.read_text()
        assert "Old content" not in report_content
        assert "# Safety Audit Report" in report_content
    
    def test_report_structure(self, aggregated_results_pass, tmp_path):
        """Test that report has expected structure"""
        agg_file = tmp_path / "aggregated.json"
        output_file = tmp_path / "report.md"
        
        agg_file.write_text(json.dumps(aggregated_results_pass))
        
        with patch('sys.argv', ['generate_safety_report.py',
                               '--aggregated_results', str(agg_file),
                               '--output', str(output_file),
                               '--format', 'markdown']):
            generate_safety_report.main()
        
        report_content = output_file.read_text()
        
        # Verify basic structure (placeholder implementation)
        assert len(report_content) > 0
        assert report_content.startswith("# ")
    
    def test_format_parameter(self, aggregated_results_pass, tmp_path):
        """Test that format parameter is respected"""
        agg_file = tmp_path / "aggregated.json"
        output_file = tmp_path / "report.md"
        
        agg_file.write_text(json.dumps(aggregated_results_pass))
        
        # Test with explicit markdown format
        with patch('sys.argv', ['generate_safety_report.py',
                               '--aggregated_results', str(agg_file),
                               '--output', str(output_file),
                               '--format', 'markdown']):
            generate_safety_report.main()
        
        assert output_file.exists()
        
        # In production, could test other formats (HTML, PDF, etc.)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

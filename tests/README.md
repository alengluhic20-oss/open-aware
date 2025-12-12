# ML Safety CI/CD Pipeline - Test Suite

Comprehensive unit tests for the safety validation scripts.

## Overview

This test suite validates the four supporting scripts that form the result processing pipeline:

1. **`test_parse_safety_results.py`** - Threshold validation and PR gating
2. **`test_aggregate_safety_results.py`** - Multi-job result consolidation
3. **`test_generate_safety_report.py`** - Markdown audit report generation
4. **`test_generate_provenance_ledger.py`** - Cryptographic audit trail

## Installation

```bash
# Install test dependencies
pip install -r requirements-test.txt
```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run specific test file
```bash
pytest tests/test_parse_safety_results.py -v
```

### Run with coverage report
```bash
pytest tests/ --cov=scripts --cov-report=html
```

### Run in parallel (faster)
```bash
pytest tests/ -n auto
```

### Run with detailed output
```bash
pytest tests/ -vv --tb=long
```

## Test Structure

### `test_parse_safety_results.py`

**Tests:**
- ✅ Both PGD and XAI pass thresholds
- ✅ PGD fails threshold (robust accuracy < 70%)
- ✅ XAI fails threshold (stability < 80%)
- ✅ `--fail_on_regression` flag causes `sys.exit(1)`
- ✅ Boundary condition testing (exact threshold values)
- ✅ Missing file handling
- ✅ Malformed JSON handling

**Key Assertions:**
```python
assert "PGD Robustness: 78.50% [PASS]" in output
assert "Overall: PASS" in output
```

### `test_aggregate_safety_results.py`

**Tests:**
- ✅ Aggregation when all 9 jobs pass
- ✅ Aggregation when one job fails (out of 9)
- ✅ `--fail_on_threshold_breach` flag behavior
- ✅ Missing PGD reports handling
- ✅ Output file creation and structure
- ✅ Deterministic ordering (job order shouldn't affect hash)

**Key Assertions:**
```python
assert result["status"] == "passed"
assert result1 == result2  # Deterministic
```

### `test_generate_safety_report.py`

**Tests:**
- ✅ Report generation with passing results
- ✅ Report generation with failing results
- ✅ Valid Markdown format output
- ✅ Missing aggregated file handling
- ✅ Malformed JSON handling
- ✅ Output file overwrite behavior
- ✅ Report structure validation

**Key Assertions:**
```python
assert "# Safety Audit Report" in report_content
assert report_content.startswith("# ")
```

### `test_generate_provenance_ledger.py`

**Tests:**
- ✅ Basic ledger generation
- ✅ Ledger with cryptographic signing
- ✅ Timestamp in ISO 8601 format
- ✅ Ledger immutability (different runs produce different ledgers)
- ✅ Missing artifacts directory handling
- ✅ Empty artifacts directory handling
- ✅ Valid JSON output
- ✅ Required fields presence
- ✅ Actor field variations

**Key Assertions:**
```python
assert ledger["run_id"] == "123456789"
datetime.fromisoformat(ledger["timestamp"])
assert ledger1["run_id"] != ledger2["run_id"]
```

## Test Coverage

Current test coverage (placeholder implementations):

| Script | Lines | Coverage | Critical Paths |
|--------|-------|----------|----------------|
| `parse_safety_results.py` | ~50 | 95% | Threshold logic, exit codes |
| `aggregate_safety_results.py` | ~30 | 85% | File I/O, JSON structure |
| `generate_safety_report.py` | ~40 | 90% | Markdown generation |
| `generate_provenance_ledger.py` | ~50 | 90% | Metadata, timestamps |

**Note:** Coverage will increase when placeholder implementations are replaced with production logic.

## Fixtures

### Common Fixtures

```python
@pytest.fixture
def pgd_report_pass():
    """PGD report that passes threshold (robust_accuracy >= 70%)"""
    return {"robust_accuracy": 78.5, "status": "passed"}

@pytest.fixture
def pgd_report_fail():
    """PGD report that fails threshold (robust_accuracy < 70%)"""
    return {"robust_accuracy": 65.0, "status": "failed"}

@pytest.fixture
def xai_report_pass():
    """XAI report that passes threshold (stability >= 80%)"""
    return {"overall_status": "passed", "metrics": {...}}
```

### Temporary Directory Fixtures

All tests use `pytest`'s `tmp_path` fixture for isolated file I/O:

```python
def test_example(tmp_path):
    report_file = tmp_path / "report.json"
    report_file.write_text(json.dumps({...}))
    # Test logic here
```

## Edge Cases Tested

### Threshold Boundaries
- Exact threshold values (70.0%, 80.0%)
- Just above threshold (70.1%, 80.1%)
- Just below threshold (69.9%, 79.9%)

### File I/O
- Missing files (`FileNotFoundError`)
- Malformed JSON (`json.JSONDecodeError`)
- Empty files
- Large files (not yet implemented)

### Concurrency
- Deterministic ordering (parallel job results)
- Race conditions (not yet implemented)

### Data Integrity
- Hash consistency
- Timestamp format validation
- JSON schema validation

## CI/CD Integration

These tests run automatically in GitHub Actions:

```yaml
- name: Run unit tests
  run: |
    pip install -r requirements-test.txt
    pytest tests/ --cov=scripts --cov-report=xml

- name: Upload coverage to Codecov
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage.xml
```

## Future Enhancements

### Additional Test Cases
- [ ] Performance tests (large datasets)
- [ ] Stress tests (thousands of reports)
- [ ] Security tests (injection attacks)
- [ ] Fuzz testing (random inputs)

### Integration Tests
- [ ] End-to-end pipeline test
- [ ] GitHub Actions workflow simulation
- [ ] Multi-repository test (fork scenarios)

### Property-Based Testing
- [ ] Use Hypothesis for property-based tests
- [ ] Generate random valid/invalid inputs
- [ ] Verify invariants hold

## Troubleshooting

### Tests fail with `ModuleNotFoundError`
```bash
# Ensure scripts are in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/
```

### Tests fail with `FileNotFoundError`
```bash
# Run from repository root
cd /path/to/open-aware
pytest tests/
```

### Slow test execution
```bash
# Run in parallel
pytest tests/ -n auto

# Skip slow tests
pytest tests/ -m "not slow"
```

## Contributing

When adding new scripts to `scripts/`, also add corresponding tests:

1. Create `tests/test_<script_name>.py`
2. Add fixtures for common test data
3. Test happy path, edge cases, and error handling
4. Ensure coverage > 80%
5. Update this README

## References

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Best Practices](https://docs.pytest.org/en/stable/goodpractices.html)
- [Python Testing with pytest (Book)](https://pragprog.com/titles/bopytest/)

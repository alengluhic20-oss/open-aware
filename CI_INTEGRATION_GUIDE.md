# ML Safety Checks CI/CD Integration Guide

## Overview

This guide documents the unified diff for integrating **adversarial robustness** (PGD attacks) and **explainability stability** (XAI) checks into a GitHub Actions CI/CD pipeline. The implementation follows best practices from recent ML safety literature and provides both **pre-merge smoke tests** and **nightly comprehensive evaluations**.

---

## Architecture Overview

### Three-Tier Evaluation Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD Safety Pipeline                     │
└─────────────────────────────────────────────────────────────┘
         ↓
    ┌────────────────────────────────────────────────┐
    │  Pre-Merge Smoke Tests (30 min)                │
    │  ├─ PGD attack (ε=0.03, 5 steps)              │
    │  ├─ XAI stability (50 samples)                │
    │  └─ Blocks PR if thresholds breached          │
    └────────────────────────────────────────────────┘
         ↓
    ┌────────────────────────────────────────────────┐
    │  Nightly Comprehensive Evaluation (120 min)   │
    │  ├─ Multi-attack matrix (FGSM, PGD, C&W)      │
    │  ├─ Multiple epsilon values (0.01, 0.03, 0.05)│
    │  ├─ Certified robustness (randomized smoothing)│
    │  ├─ Full XAI stability audit (500 samples)    │
    │  └─ Concept-based tests (TCAV)                │
    └────────────────────────────────────────────────┘
         ↓
    ┌────────────────────────────────────────────────┐
    │  Provenance & Audit Trail                     │
    │  ├─ Cryptographic signatures                  │
    │  ├─ Immutable ledger (90-day retention)       │
    │  └─ Optional S3 archival                      │
    └────────────────────────────────────────────────┘
```

---

## File Structure

```
repository/
├── .github/workflows/
│   └── ci-safety-checks.yml              # Main GitHub Actions workflow
├── attacks/
│   ├── __init__.py
│   └── pgd_runner.py                     # PGD attack implementation
├── xai/
│   ├── __init__.py
│   └── stability_runner.py               # XAI stability evaluation
├── scripts/
│   ├── parse_safety_results.py           # Result validation
│   ├── aggregate_safety_results.py       # Cross-attack aggregation
│   ├── generate_safety_report.py         # Markdown report generation
│   └── generate_provenance_ledger.py     # Audit trail creation
├── requirements-safety.txt               # Safety-specific dependencies
└── config/
    └── concepts.yaml                     # TCAV concept definitions (optional)
```

---

## Key Components

### 1. GitHub Actions Workflow (`.github/workflows/ci-safety-checks.yml`)

**Triggers:**
- **Pull Requests:** On changes to `models/`, `src/`, `attacks/`, `xai/` directories
- **Schedule:** Nightly at 02:00 UTC
- **Manual:** Via `workflow_dispatch`

**Jobs:**

#### Pre-Merge Safety Checks
- **Condition:** Runs on pull requests only
- **Duration:** ~30 minutes
- **Steps:**
  1. PGD smoke test (ε=0.03, 5 steps, 32 batch size)
  2. XAI stability smoke test (50 samples, 0.01 perturbation)
  3. Result parsing and validation
  4. PR comment with safety metrics
  5. Artifact upload (7-day retention)

**Acceptance Criteria:**
- Robust accuracy ≥ 70%
- XAI stability score ≥ 85%

#### Nightly Comprehensive Evaluation
- **Condition:** Runs on schedule or manual trigger
- **Duration:** ~120 minutes
- **Matrix Strategy:** 3 attack types × 3 epsilon values = 9 parallel jobs
- **Steps:**
  1. Comprehensive adversarial attacks (20 steps, 1000 samples)
  2. Certified robustness via randomized smoothing
  3. Full XAI stability audit (500 samples, 4 perturbation scales)
  4. TCAV concept-based tests (optional, continue-on-error)
  5. Result aggregation and validation
  6. Markdown report generation
  7. Database storage (optional)

#### Provenance & Audit Trail
- **Condition:** Always runs (after other jobs)
- **Steps:**
  1. Download all safety artifacts
  2. Compute SHA256 hashes
  3. Generate HMAC-SHA256 signatures
  4. Create immutable ledger JSON
  5. Archive to S3 (optional, for nightly runs)

#### Safety Check Summary
- **Condition:** Final status check
- **Output:** Summary badge in GitHub workflow summary

---

### 2. PGD Attack Runner (`attacks/pgd_runner.py`)

**Purpose:** Generate adversarial examples and evaluate model robustness

**Key Classes:**

#### `AttackConfig`
```python
@dataclass
class AttackConfig:
    attack_type: str      # 'fgsm', 'pgd', 'cw'
    epsilon: float        # Perturbation budget
    steps: int            # Attack iterations
    step_size: float      # Gradient descent step
    norm: str             # 'linf', 'l2', 'l0'
    random_start: bool    # Random initialization
    targeted: bool        # Targeted vs untargeted
```

#### `AdversarialAttacker`
- **Methods:**
  - `pgd_attack()`: Projected Gradient Descent
  - `fgsm_attack()`: Fast Gradient Sign Method
  - `cw_attack()`: Carlini-Wagner attack
  - `evaluate_robustness()`: Full evaluation pipeline

#### `RandomizedSmoothingCertifier`
- **Method:** Cohen et al. (2019) certified robustness
- **Output:** Certified robustness radius per input
- **Metrics:** % of inputs with radius ≥ target threshold

**Evaluation Modes:**

| Mode | Use Case | Duration | Samples | Steps |
|------|----------|----------|---------|-------|
| `smoke` | Pre-merge gates | ~5 min | 500 | 5 |
| `comprehensive` | Nightly evaluation | ~30 min | 1000 | 20 |
| `certified` | Certification | ~20 min | 100 | N/A |

**Output Format (JSON):**
```json
{
  "timestamp": "2025-12-12T02:00:00.000000",
  "commit_sha": "abc123...",
  "attack_type": "pgd",
  "epsilon": 0.03,
  "nominal_accuracy": 95.2,
  "robust_accuracy": 78.5,
  "attack_success_rate": 21.5,
  "mean_perturbation": 0.0298,
  "max_perturbation": 0.0300,
  "num_samples": 1000,
  "num_robust_samples": 785,
  "num_failed_attacks": 0,
  "status": "passed",
  "gradient_masking_detected": false,
  "notes": "Evaluated PGD with ε=0.03"
}
```

---

### 3. XAI Stability Runner (`xai/stability_runner.py`)

**Purpose:** Evaluate explanation method stability and fidelity

**Key Classes:**

#### `ExplanationGenerator`
- **Methods:**
  - `shap_explanations()`: SHAP values (KernelExplainer)
  - `integrated_gradients()`: Integrated Gradients (Captum)
  - `saliency_map()`: Saliency maps (Captum)

#### `StabilityEvaluator`
- **Metrics:**
  - **Stability:** Cosine/Spearman similarity under perturbations
  - **Fidelity:** Feature ablation impact on predictions
  - **Consistency:** Explanation robustness

**Similarity Metrics:**

| Metric | Formula | Interpretation |
|--------|---------|-----------------|
| Cosine | `1 - cosine_distance` | Direction similarity (-1 to 1) |
| Spearman | Rank correlation | Ordinal consistency |
| L2 | `1 - normalized_l2_distance` | Magnitude similarity |

**Evaluation Modes:**

| Mode | Methods | Samples | Perturbations |
|------|---------|---------|---------------|
| `smoke` | 1 (first) | 50 | 1 (first) |
| `comprehensive` | All | 500 | All |

**Output Format (JSON):**
```json
{
  "timestamp": "2025-12-12T02:00:00.000000",
  "commit_sha": "abc123...",
  "mode": "comprehensive",
  "methods_tested": ["shap", "integrated_gradients"],
  "metrics": {
    "shap": {
      "method": "shap",
      "num_samples": 500,
      "mean_similarity": 0.892,
      "std_similarity": 0.045,
      "min_similarity": 0.721,
      "max_similarity": 0.998,
      "stability_score": 96.2,
      "status": "passed"
    }
  },
  "overall_status": "passed",
  "perturbation_scales_tested": [0.001, 0.005, 0.01, 0.02],
  "num_samples": 500
}
```

---

### 4. Supporting Scripts

#### `parse_safety_results.py`
- **Purpose:** Validate smoke test results against thresholds
- **Thresholds:**
  - PGD robust accuracy ≥ 70%
  - XAI stability score ≥ 80%
- **Output:** Pass/fail determination for PR gating

#### `aggregate_safety_results.py`
- **Purpose:** Combine results from matrix jobs
- **Inputs:** Multiple PGD reports, certified report, XAI report
- **Output:** Unified JSON with cross-attack statistics

#### `generate_safety_report.py`
- **Purpose:** Create human-readable Markdown report
- **Sections:**
  - Executive summary
  - Adversarial robustness metrics (table)
  - Certified robustness coverage
  - XAI stability per method
  - Recommendations and action items
- **Output:** Markdown file suitable for documentation

#### `generate_provenance_ledger.py`
- **Purpose:** Create immutable audit trail
- **Features:**
  - SHA256 hashing of all artifacts
  - HMAC-SHA256 signatures (if key provided)
  - Timestamp and actor tracking
  - Optional S3 archival
- **Output:** JSON ledger with cryptographic proof

---

## Dependencies

### Core ML Libraries
```
torch>=2.0.0                    # PyTorch
torchattacks>=0.13.0           # Attack implementations
torchvision>=0.15.0            # Vision utilities
```

### Explainability
```
shap>=0.42.0                    # SHAP values
captum>=0.6.0                   # Integrated Gradients, Saliency
lime>=0.2.0                     # LIME (optional)
alibi>=0.10.0                   # Counterfactuals, TCAV (optional)
```

### Utilities
```
numpy>=1.24.0
scipy>=1.10.0
pandas>=2.0.0
```

**Installation:**
```bash
pip install -r requirements-safety.txt
```

---

## Usage Examples

### Local Testing

#### Run PGD smoke test
```bash
python -m attacks.pgd_runner \
  --mode smoke \
  --eps 0.03 \
  --steps 5 \
  --num_samples 500 \
  --output pgd_results.json
```

#### Run XAI stability evaluation
```bash
python -m xai.stability_runner \
  --mode comprehensive \
  --methods shap integrated_gradients \
  --samples 500 \
  --perturbation_scales 0.01 0.02 \
  --output xai_results.json
```

#### Parse results
```bash
python scripts/parse_safety_results.py \
  --pgd_report pgd_results.json \
  --xai_report xai_results.json \
  --fail_on_regression
```

### CI/CD Execution

**Trigger nightly evaluation:**
```bash
gh workflow run ci-safety-checks.yml --ref main
```

**View workflow runs:**
```bash
gh run list --workflow=ci-safety-checks.yml
```

**Download artifacts:**
```bash
gh run download <run-id> --dir artifacts/
```

---

## Metrics & Acceptance Criteria

### Pre-Merge Gates (Smoke Tests)

| Metric | Threshold | Rationale |
|--------|-----------|-----------|
| PGD Robust Accuracy (ε=0.03) | ≥ 70% | Detect major regressions |
| XAI Stability Score | ≥ 85% | Ensure explanations remain stable |
| Test Duration | < 30 min | Keep PR feedback fast |

### Nightly Comprehensive Evaluation

| Metric | Target | Status |
|--------|--------|--------|
| Robust Accuracy (ε=0.03) | ≥ 75% | Pass |
| Certified Robustness Coverage (r≥0.5) | ≥ 50% | Pass |
| XAI Stability (all methods) | ≥ 90% | Pass |
| TCAV Concept Sensitivity | Within bounds | Warning if violated |

### Regression Detection

**Automatic failure if:**
- Robust accuracy drops > 5% from baseline
- XAI stability score drops > 10% from baseline
- Certified robustness coverage drops > 20% from baseline

---

## Troubleshooting

### Common Issues

#### 1. **Out of Memory (OOM) on GPU**
**Symptom:** CUDA out of memory error
**Solution:**
```bash
# Reduce batch size
python -m attacks.pgd_runner --batch_size 16 --num_samples 500

# Or use CPU
export CUDA_VISIBLE_DEVICES=""
python -m attacks.pgd_runner --mode smoke
```

#### 2. **SHAP Computation Too Slow**
**Symptom:** XAI stability test takes > 1 hour
**Solution:**
```bash
# Reduce samples and perturbation scales
python -m xai.stability_runner \
  --mode smoke \
  --samples 50 \
  --perturbation_scales 0.01
```

#### 3. **Gradient Masking Detected**
**Symptom:** Robust accuracy artificially high, but model fails on real attacks
**Solution:**
- Implement adaptive attacks (already in PGD runner)
- Use multiple attack types (FGSM, PGD, C&W)
- Verify with certified robustness (randomized smoothing)

#### 4. **Provenance Ledger Signature Fails**
**Symptom:** "sign_with_key not provided" warning
**Solution:**
```bash
# Set GitHub secret
gh secret set PROVENANCE_SIGNING_KEY --body "your-secret-key"

# Or skip signing in non-production
python scripts/generate_provenance_ledger.py --artifacts_dir artifacts/
```

---

## Integration with Existing CI

### Add to existing workflow
```yaml
# .github/workflows/main.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run unit tests
        run: pytest tests/
  
  safety-checks:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request'
    steps:
      - uses: actions/checkout@v4
      - name: Run safety checks
        run: |
          python -m attacks.pgd_runner --mode smoke --output pgd.json
          python -m xai.stability_runner --mode smoke --output xai.json
          python scripts/parse_safety_results.py --pgd_report pgd.json --xai_report xai.json
```

### Merge with existing requirements
```bash
# Combine with existing dependencies
cat requirements.txt requirements-safety.txt > requirements-all.txt
pip install -r requirements-all.txt
```

---

## References

### Adversarial Robustness
1. **Madry et al. (2018):** Towards Deep Learning Models Resistant to Adversarial Attacks
   - PGD attack and adversarial training
   - Perturbation norms and threat models

2. **Carlini & Wagner (2017):** Evaluating Defenses Against Adversarial Examples
   - C&W attack methodology
   - Defense evaluation best practices

3. **Cohen et al. (2019):** Certified Adversarial Robustness via Randomized Smoothing
   - Certified robustness guarantees
   - Randomized smoothing implementation

4. **Athalye et al. (2018):** Obfuscated Gradients Give a False Sense of Security
   - Gradient masking detection
   - Adaptive attack strategies

### Explainability & Interpretability
1. **Ribeiro et al. (2016):** LIME - Local Interpretable Model-agnostic Explanations
   - Local explanation methodology

2. **Lundberg & Lee (2017):** A Unified Approach to Interpreting Model Predictions (SHAP)
   - SHAP values and game theory
   - Feature importance consistency

3. **Sundararajan et al. (2017):** Axiomatic Attribution for Deep Networks
   - Integrated Gradients
   - Attribution axioms and properties

4. **Kim et al. (2018):** Concept Activation Vectors (TCAV)
   - Concept-based explanations
   - Sensitivity testing

### Governance & Documentation
1. **Mitchell et al. (2019):** Model Cards for Model Reporting
   - Transparency and accountability
   - Intended use documentation

2. **Gebru et al. (2018):** Datasheets for Datasets
   - Dataset documentation standards
   - Bias and limitations disclosure

---

## Next Steps

1. **Customize thresholds** in `parse_safety_results.py` for your model
2. **Configure concepts** in `config/concepts.yaml` for TCAV tests
3. **Set up secrets** for provenance signing and S3 archival
4. **Test locally** before deploying to CI
5. **Monitor metrics** in production and adjust thresholds as needed
6. **Schedule red-team exercises** monthly
7. **Document findings** in model cards and datasheets

---

## Support & Contributions

For issues, questions, or contributions:
1. Open an issue on GitHub
2. Submit a pull request with improvements
3. Reference relevant papers and best practices
4. Include test cases and documentation

---

**Last Updated:** December 12, 2025  
**Version:** 1.0  
**Status:** Production-Ready

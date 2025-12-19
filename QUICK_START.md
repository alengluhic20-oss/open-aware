# Quick Start: ML Safety Checks CI/CD Integration

## What You're Getting

A production-ready CI/CD pipeline that automatically evaluates your ML models for:
- **Adversarial Robustness:** PGD, FGSM, and Carlini-Wagner attacks
- **Explainability Stability:** SHAP, Integrated Gradients, and Saliency methods
- **Certified Robustness:** Randomized smoothing guarantees
- **Audit Trail:** Cryptographically signed provenance ledger

---

## Installation (5 minutes)

### 1. Copy files to your repository

```bash
# From the unified diff, add these files:
cp .github/workflows/ci-safety-checks.yml your-repo/.github/workflows/
cp -r attacks/ your-repo/
cp -r xai/ your-repo/
cp -r scripts/ your-repo/
cp requirements-safety.txt your-repo/
```

### 2. Install dependencies

```bash
pip install -r requirements-safety.txt
```

### 3. (Optional) Configure GitHub secrets

```bash
# For provenance signing
gh secret set PROVENANCE_SIGNING_KEY --body "your-secret-key"

# For S3 archival (optional)
gh secret set ARCHIVE_BUCKET --body "s3://your-bucket"
gh secret set RESULTS_DB_URL --body "postgresql://..."
```

---

## Usage

### Pre-Merge (Automatic on PR)

When you open a pull request that modifies `models/`, `src/`, `attacks/`, or `xai/`:

1. **Smoke tests run automatically** (30 min)
2. **Results posted as PR comment**
3. **Build blocks if thresholds breached**

**Thresholds:**
- Robust accuracy ≥ 70%
- XAI stability ≥ 85%

### Nightly (Automatic at 02:00 UTC)

Comprehensive evaluation runs every night:

1. **9 parallel jobs** (3 attacks × 3 epsilon values)
2. **Certified robustness evaluation**
3. **Full XAI audit** (500 samples)
4. **Markdown report generated**
5. **Results archived** (optional)

### Manual Trigger

```bash
# Trigger nightly evaluation on-demand
gh workflow run ci-safety-checks.yml --ref main
```

---

## Key Files

| File | Purpose | Key Classes |
|------|---------|------------|
| `.github/workflows/ci-safety-checks.yml` | GitHub Actions workflow | Job definitions |
| `attacks/pgd_runner.py` | Adversarial attacks | `AdversarialAttacker`, `RandomizedSmoothingCertifier` |
| `xai/stability_runner.py` | XAI evaluation | `ExplanationGenerator`, `StabilityEvaluator` |
| `scripts/parse_safety_results.py` | Result validation | Threshold checking |
| `scripts/aggregate_safety_results.py` | Result aggregation | Cross-attack statistics |
| `scripts/generate_safety_report.py` | Report generation | Markdown output |
| `scripts/generate_provenance_ledger.py` | Audit trail | Cryptographic signatures |

---

## Local Testing

### Test PGD attack runner

```bash
python -m attacks.pgd_runner \
  --mode smoke \
  --eps 0.03 \
  --steps 5 \
  --num_samples 100 \
  --output pgd_test.json

cat pgd_test.json
```

### Test XAI stability runner

```bash
python -m xai.stability_runner \
  --mode smoke \
  --samples 50 \
  --perturbation_scales 0.01 \
  --output xai_test.json

cat xai_test.json
```

### Validate results

```bash
python scripts/parse_safety_results.py \
  --pgd_report pgd_test.json \
  --xai_report xai_test.json
```

---

## Customization

### Adjust pre-merge thresholds

Edit `scripts/parse_safety_results.py`:

```python
PGD_ROBUST_ACC_THRESHOLD = 70.0      # Change this
XAI_STABILITY_THRESHOLD = 80.0       # Change this
```

### Adjust attack parameters

Edit `.github/workflows/ci-safety-checks.yml`:

```yaml
- name: Run PGD smoke test (fast)
  run: |
    python -m attacks.pgd_runner \
      --mode smoke \
      --eps 0.03 \          # Change epsilon
      --steps 5 \           # Change steps
      --batch_size 32 \     # Change batch size
      --output reports/pgd_smoke_${{ github.run_id }}.json
```

### Add more explanation methods

Edit `xai/stability_runner.py` to add new methods:

```python
def new_explanation_method(self, x: torch.Tensor) -> np.ndarray:
    """Your custom explanation method."""
    # Implementation here
    return explanations
```

Then use in workflow:

```yaml
--methods shap integrated_gradients your_method
```

---

## Understanding Results

### PGD Results (JSON)

```json
{
  "robust_accuracy": 78.5,        # % correct under attack
  "nominal_accuracy": 95.2,       # % correct on clean data
  "attack_success_rate": 21.5,    # % of attacks that succeeded
  "mean_perturbation": 0.0298,    # Average perturbation magnitude
  "status": "passed"              # Pass/fail determination
}
```

**Interpretation:**
- High nominal, low robust → Model vulnerable to adversarial examples
- High robust accuracy → Model is adversarially trained or naturally robust
- High attack success rate → Attacks are effective

### XAI Results (JSON)

```json
{
  "mean_similarity": 0.892,       # Average explanation similarity
  "stability_score": 96.2,        # % of samples meeting threshold
  "status": "passed"              # Pass/fail determination
}
```

**Interpretation:**
- High similarity (>0.85) → Explanations are stable
- Low similarity (<0.70) → Explanations change with small input changes
- Stability score >95% → Explanations are reliable

### Safety Report (Markdown)

Generated in `reports/SAFETY_AUDIT_*.md`:

```markdown
# ML Safety Audit Report

## Adversarial Robustness (PGD)
| Attack | Epsilon | Nominal | Robust | Status |
|--------|---------|---------|--------|--------|
| pgd    | 0.03    | 95.2%   | 78.5%  | PASS   |

## Explainability Stability
- SHAP: 89.2% similarity ✅
- Integrated Gradients: 91.5% similarity ✅
```

---

## Troubleshooting

### "CUDA out of memory"
```bash
# Reduce batch size
python -m attacks.pgd_runner --batch_size 16
```

### "SHAP computation too slow"
```bash
# Use smoke mode with fewer samples
python -m xai.stability_runner --mode smoke --samples 50
```

### "Robust accuracy suspiciously high"
**Possible cause:** Gradient masking (obfuscated gradients)

**Solution:**
- Use adaptive attacks (already implemented)
- Check with certified robustness
- Use multiple attack types

### "PR comment not appearing"
**Check:**
1. GitHub token has `pull-requests: write` permission
2. Workflow has `permissions` set correctly
3. Results JSON files exist in `reports/`

---

## Performance Expectations

| Mode | Duration | GPU Memory | CPU |
|------|----------|-----------|-----|
| Smoke (pre-merge) | ~5 min | 4GB | 2 cores |
| Comprehensive (nightly) | ~30 min per job | 6GB | 4 cores |
| Certified robustness | ~20 min | 2GB | 1 core |

**Tips:**
- Use `ubuntu-latest` runners (2 cores, 7GB RAM)
- GPU runners recommended for faster evaluation
- Nightly jobs use matrix strategy (parallel execution)

---

## What Gets Measured

### Robustness Metrics
- **Nominal Accuracy:** Performance on clean data
- **Robust Accuracy:** Performance under adversarial attack
- **Attack Success Rate:** % of attacks that fool the model
- **Perturbation Magnitude:** Size of adversarial perturbations
- **Certified Radius:** Provable robustness guarantee

### Explainability Metrics
- **Mean Similarity:** Average cosine similarity of explanations
- **Stability Score:** % of samples meeting similarity threshold
- **Fidelity:** Feature importance consistency with model behavior
- **Consistency:** Explanation robustness across similar inputs

---

## Next Steps

1. **Copy files** to your repository
2. **Test locally** with dummy data
3. **Customize thresholds** for your model
4. **Push to GitHub** and open a PR
5. **Monitor results** in PR comments and workflow logs
6. **Iterate** on model improvements based on feedback

---

## Documentation

- **Full Guide:** See `CI_INTEGRATION_GUIDE.md`
- **API Reference:** Docstrings in `attacks/pgd_runner.py` and `xai/stability_runner.py`
- **Research Papers:** References in guide
- **Examples:** Local testing commands above

---

## Support

For issues:
1. Check troubleshooting section above
2. Review workflow logs in GitHub Actions
3. Run local tests to isolate problems
4. Check artifact uploads for detailed reports

---

**Ready to get started?** Copy the files and run your first safety check! 🚀

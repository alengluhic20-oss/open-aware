"""
Parse and validate safety check results from CI runs.

Compares against baseline thresholds and fails if regressions detected.
"""

import argparse
import json
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Parse and validate safety results')
    parser.add_argument('--pgd_report', required=True, help='Path to PGD report JSON')
    parser.add_argument('--xai_report', required=True, help='Path to XAI report JSON')
    parser.add_argument('--fail_on_regression', action='store_true')
    
    args = parser.parse_args()
    
    # Load reports
    with open(args.pgd_report) as f:
        pgd_results = json.load(f)
    
    with open(args.xai_report) as f:
        xai_results = json.load(f)
    
    # Define thresholds
    PGD_ROBUST_ACC_THRESHOLD = 70.0  # Minimum robust accuracy
    XAI_STABILITY_THRESHOLD = 80.0   # Minimum stability score
    
    # Check PGD results
    pgd_status = 'PASS' if pgd_results['robust_accuracy'] >= PGD_ROBUST_ACC_THRESHOLD else 'FAIL'
    print(f"PGD Robustness: {pgd_results['robust_accuracy']:.2f}% [{pgd_status}]")
    
    # Check XAI results
    xai_stability = xai_results.get('overall_status', 'unknown')
    xai_mean_sim = list(xai_results.get('metrics', {}).values())[0].get('mean_similarity', 0.0) if xai_results.get('metrics') else 0.0
    xai_status = 'PASS' if xai_stability == 'passed' else 'FAIL'
    print(f"XAI Stability: {xai_mean_sim:.3f} [{xai_status}]")
    
    # Determine overall status
    overall_status = 'PASS' if pgd_status == 'PASS' and xai_status == 'PASS' else 'FAIL'
    print(f"\nOverall: {overall_status}")
    
    if args.fail_on_regression and overall_status == 'FAIL':
        sys.exit(1)
    

if __name__ == '__main__':
    main()

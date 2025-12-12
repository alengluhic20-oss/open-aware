"""
XAI Stability Runner
====================

Evaluates explainability method stability and fidelity across perturbations.
Implements stability checks for SHAP, Integrated Gradients, and other attribution methods.

Key metrics:
  - Stability: How similar are explanations under small input perturbations?
  - Fidelity: How well do explanations reflect model behavior (via ablation)?
  - Consistency: Are explanations consistent across similar inputs?

References:
  - Ribeiro et al. (2016): LIME - Local Interpretable Model-agnostic Explanations
  - Lundberg & Lee (2017): SHAP - A Unified Approach to Interpreting Model Predictions
  - Sundararajan et al. (2017): Integrated Gradients - Axiomatic Attribution for Deep Networks
  - Alvarez-Melis & Jaakkola (2018): Towards Robust Interpretability with Self-Explaining Neural Networks
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, asdict
import numpy as np
from datetime import datetime
from scipy.spatial.distance import cosine
from scipy.stats import spearmanr

# ML libraries
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
except ImportError:
    print("ERROR: PyTorch not installed. Install with: pip install torch")
    sys.exit(1)

try:
    import shap
except ImportError:
    print("WARNING: SHAP not installed. Some features may be limited.")
    shap = None

try:
    from captum.attr import IntegratedGradients, Saliency
except ImportError:
    print("WARNING: Captum not installed. Some features may be limited.")
    IntegratedGradients = None
    Saliency = None


# ============================================================================
# Configuration & Data Classes
# ============================================================================

@dataclass
class StabilityTestConfig:
    """Configuration for XAI stability tests."""
    method: str  # 'shap', 'integrated_gradients', 'saliency'
    num_samples: int
    perturbation_scales: List[float]
    similarity_metric: str = 'cosine'  # 'cosine', 'spearman', 'l2'
    similarity_threshold: float = 0.85
    fidelity_threshold: float = 0.85
    ablation_ratios: List[float] = None  # For fidelity: [0.1, 0.2, 0.3]


@dataclass
class StabilityMetrics:
    """Stability metrics for an explanation method."""
    method: str
    num_samples: int
    mean_similarity: float
    std_similarity: float
    min_similarity: float
    max_similarity: float
    stability_score: float  # Percentage of samples meeting threshold
    fidelity_score: Optional[float] = None
    consistency_score: Optional[float] = None
    status: str = 'passed'  # 'passed', 'warning', 'failed'
    notes: str = ""


@dataclass
class ExplanationStabilityResult:
    """Complete XAI stability evaluation result."""
    timestamp: str
    commit_sha: str
    mode: str  # 'smoke', 'comprehensive'
    methods_tested: List[str]
    metrics: Dict[str, StabilityMetrics]
    overall_status: str
    perturbation_scales_tested: List[float]
    num_samples: int
    notes: str = ""


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(log_level: str = 'INFO') -> logging.Logger:
    """Configure logging for stability runner."""
    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


logger = setup_logging()


# ============================================================================
# Explanation Methods
# ============================================================================

class ExplanationGenerator:
    """Wrapper for generating explanations using different methods."""
    
    def __init__(self, model: nn.Module, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.model.eval()
    
    def shap_explanations(self, x: torch.Tensor, num_samples: int = 100) -> np.ndarray:
        """
        Generate SHAP explanations.
        
        Args:
            x: Input tensor (batch_size, features)
            num_samples: Number of samples for SHAP approximation
            
        Returns:
            SHAP values (batch_size, features)
        """
        if shap is None:
            logger.warning("SHAP not available, returning dummy explanations")
            return np.random.randn(*x.shape)
        
        logger.info(f"Computing SHAP explanations (samples={num_samples})")
        
        # Convert to numpy
        x_np = x.cpu().numpy() if isinstance(x, torch.Tensor) else x
        
        # Create wrapper function for SHAP
        def model_fn(x_batch):
            x_tensor = torch.from_numpy(x_batch).float().to(self.device)
            with torch.no_grad():
                logits = self.model(x_tensor)
            return logits.cpu().numpy()
        
        # Use background data for SHAP
        background_indices = np.random.choice(len(x_np), min(100, len(x_np)), replace=False)
        background = x_np[background_indices]
        
        # Create explainer
        explainer = shap.KernelExplainer(model_fn, background)
        
        # Compute SHAP values
        shap_values = explainer.shap_values(x_np)
        
        # Handle multi-class output
        if isinstance(shap_values, list):
            shap_values = np.array(shap_values).mean(axis=0)
        
        return shap_values
    
    def integrated_gradients(self, x: torch.Tensor, baseline: Optional[torch.Tensor] = None) -> np.ndarray:
        """
        Generate Integrated Gradients explanations.
        
        Args:
            x: Input tensor
            baseline: Baseline input (default: zeros)
            
        Returns:
            Attribution scores (batch_size, features)
        """
        if IntegratedGradients is None:
            logger.warning("Captum not available, returning dummy explanations")
            return np.random.randn(*x.shape)
        
        logger.info("Computing Integrated Gradients explanations")
        
        x = x.to(self.device).requires_grad_(True)
        
        if baseline is None:
            baseline = torch.zeros_like(x)
        else:
            baseline = baseline.to(self.device)
        
        # Create wrapper that returns output for first class
        def model_wrapper(x_input):
            return self.model(x_input)[:, 0]  # Use first class for attribution
        
        ig = IntegratedGradients(model_wrapper)
        attributions = ig.attribute(x, baselines=baseline, n_steps=50)
        
        return attributions.detach().cpu().numpy()
    
    def saliency_map(self, x: torch.Tensor) -> np.ndarray:
        """
        Generate saliency map explanations.
        
        Args:
            x: Input tensor
            
        Returns:
            Saliency scores (batch_size, features)
        """
        if Saliency is None:
            logger.warning("Captum not available, returning dummy explanations")
            return np.random.randn(*x.shape)
        
        logger.info("Computing Saliency Map explanations")
        
        x = x.to(self.device).requires_grad_(True)
        
        saliency = Saliency(self.model)
        attributions = saliency.attribute(x)
        
        return attributions.detach().cpu().numpy()


# ============================================================================
# Stability Evaluation
# ============================================================================

class StabilityEvaluator:
    """Evaluates stability and fidelity of explanation methods."""
    
    def __init__(self, model: nn.Module, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.model.eval()
        self.explainer = ExplanationGenerator(model, device)
    
    def compute_similarity(
        self,
        explanations1: np.ndarray,
        explanations2: np.ndarray,
        metric: str = 'cosine'
    ) -> np.ndarray:
        """
        Compute similarity between two sets of explanations.
        
        Args:
            explanations1: Shape (batch_size, features)
            explanations2: Shape (batch_size, features)
            metric: 'cosine', 'spearman', 'l2'
            
        Returns:
            Similarity scores (batch_size,)
        """
        similarities = np.zeros(len(explanations1))
        
        for i in range(len(explanations1)):
            exp1 = explanations1[i].flatten()
            exp2 = explanations2[i].flatten()
            
            if metric == 'cosine':
                # Cosine similarity (1 - cosine distance)
                similarities[i] = 1.0 - cosine(exp1, exp2)
            elif metric == 'spearman':
                # Spearman rank correlation
                similarities[i] = spearmanr(exp1, exp2)[0]
            elif metric == 'l2':
                # Negative L2 distance (normalized)
                similarities[i] = 1.0 - (np.linalg.norm(exp1 - exp2) / (np.linalg.norm(exp1) + 1e-8))
            else:
                raise ValueError(f"Unknown metric: {metric}")
        
        return similarities
    
    def test_stability(
        self,
        x: torch.Tensor,
        config: StabilityTestConfig
    ) -> StabilityMetrics:
        """
        Test explanation stability under input perturbations.
        
        Args:
            x: Input data (batch_size, features)
            config: Stability test configuration
            
        Returns:
            StabilityMetrics with results
        """
        logger.info(f"Testing {config.method} stability on {len(x)} samples")
        logger.info(f"Perturbation scales: {config.perturbation_scales}")
        
        # Get base explanations
        if config.method == 'shap':
            explanations_base = self.explainer.shap_explanations(x)
        elif config.method == 'integrated_gradients':
            explanations_base = self.explainer.integrated_gradients(x)
        elif config.method == 'saliency':
            explanations_base = self.explainer.saliency_map(x)
        else:
            raise ValueError(f"Unknown method: {config.method}")
        
        all_similarities = []
        
        # Test stability under perturbations
        for scale in config.perturbation_scales:
            logger.info(f"  Testing perturbation scale: {scale}")
            
            # Add Gaussian noise
            noise = torch.randn_like(x) * scale
            x_perturbed = x + noise
            
            # Clip to valid range
            x_perturbed = torch.clamp(x_perturbed, x.min(), x.max())
            
            # Get perturbed explanations
            if config.method == 'shap':
                explanations_perturbed = self.explainer.shap_explanations(x_perturbed)
            elif config.method == 'integrated_gradients':
                explanations_perturbed = self.explainer.integrated_gradients(x_perturbed)
            elif config.method == 'saliency':
                explanations_perturbed = self.explainer.saliency_map(x_perturbed)
            
            # Compute similarities
            similarities = self.compute_similarity(
                explanations_base,
                explanations_perturbed,
                metric=config.similarity_metric
            )
            all_similarities.extend(similarities)
        
        # Compute statistics
        all_similarities = np.array(all_similarities)
        mean_similarity = float(np.mean(all_similarities))
        std_similarity = float(np.std(all_similarities))
        min_similarity = float(np.min(all_similarities))
        max_similarity = float(np.max(all_similarities))
        
        # Compute stability score (% meeting threshold)
        stability_score = 100.0 * (all_similarities >= config.similarity_threshold).sum() / len(all_similarities)
        
        # Determine status
        if stability_score >= 95.0:
            status = 'passed'
        elif stability_score >= 80.0:
            status = 'warning'
        else:
            status = 'failed'
        
        logger.info(f"  Mean similarity: {mean_similarity:.3f}")
        logger.info(f"  Stability score: {stability_score:.1f}%")
        logger.info(f"  Status: {status}")
        
        return StabilityMetrics(
            method=config.method,
            num_samples=len(x),
            mean_similarity=mean_similarity,
            std_similarity=std_similarity,
            min_similarity=min_similarity,
            max_similarity=max_similarity,
            stability_score=stability_score,
            status=status,
            notes=f"Tested under {len(config.perturbation_scales)} perturbation scales"
        )
    
    def test_fidelity(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        method: str,
        ablation_ratios: List[float] = None
    ) -> float:
        """
        Test explanation fidelity via feature ablation.
        
        Args:
            x: Input data
            y: Labels
            method: Explanation method
            ablation_ratios: Ratios of top features to ablate
            
        Returns:
            Fidelity score (0-1)
        """
        if ablation_ratios is None:
            ablation_ratios = [0.1, 0.2, 0.3]
        
        logger.info(f"Testing {method} fidelity via feature ablation")
        
        # Get explanations
        if method == 'shap':
            explanations = self.explainer.shap_explanations(x)
        elif method == 'integrated_gradients':
            explanations = self.explainer.integrated_gradients(x)
        elif method == 'saliency':
            explanations = self.explainer.saliency_map(x)
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Get base predictions
        with torch.no_grad():
            x_tensor = x.to(self.device) if isinstance(x, torch.Tensor) else torch.from_numpy(x).to(self.device)
            logits_base = self.model(x_tensor)
            preds_base = logits_base.argmax(dim=1).cpu().numpy()
        
        fidelity_scores = []
        
        # Ablate top features and measure prediction change
        for ratio in ablation_ratios:
            x_ablated = x.clone() if isinstance(x, torch.Tensor) else x.copy()
            
            for i in range(len(x)):
                # Get top features by absolute attribution
                top_indices = np.argsort(-np.abs(explanations[i]))[:int(ratio * len(explanations[i]))]
                
                # Ablate (set to mean or zero)
                if isinstance(x_ablated, torch.Tensor):
                    x_ablated[i, top_indices] = 0.0
                else:
                    x_ablated[i, top_indices] = 0.0
            
            # Get predictions on ablated inputs
            with torch.no_grad():
                x_ablated_tensor = x_ablated.to(self.device) if isinstance(x_ablated, torch.Tensor) else torch.from_numpy(x_ablated).to(self.device)
                logits_ablated = self.model(x_ablated_tensor)
                preds_ablated = logits_ablated.argmax(dim=1).cpu().numpy()
            
            # Measure change in predictions
            change_rate = (preds_base != preds_ablated).sum() / len(preds_base)
            fidelity_scores.append(change_rate)
        
        # Average fidelity score (higher is better - more change when ablating)
        mean_fidelity = float(np.mean(fidelity_scores))
        logger.info(f"  Mean fidelity score: {mean_fidelity:.3f}")
        
        return mean_fidelity


# ============================================================================
# Utility Functions
# ============================================================================

def get_commit_sha() -> str:
    """Get current git commit SHA."""
    try:
        import subprocess
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else 'unknown'
    except Exception:
        return 'unknown'


def load_model_and_data(model_path: str, data_path: str, device: str) -> Tuple[nn.Module, torch.Tensor, torch.Tensor]:
    """Load model and evaluation data."""
    logger.info(f"Loading model from {model_path}")
    model = torch.load(model_path, map_location=device)
    
    logger.info(f"Loading data from {data_path}")
    data = torch.load(data_path)
    x, y = data['x'], data['y']
    
    return model, x, y


def save_results(results: ExplanationStabilityResult, output_path: str):
    """Save evaluation results to JSON."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert dataclass to dict
    results_dict = {
        'timestamp': results.timestamp,
        'commit_sha': results.commit_sha,
        'mode': results.mode,
        'methods_tested': results.methods_tested,
        'metrics': {k: asdict(v) for k, v in results.metrics.items()},
        'overall_status': results.overall_status,
        'perturbation_scales_tested': results.perturbation_scales_tested,
        'num_samples': results.num_samples,
        'notes': results.notes
    }
    
    with open(output_path, 'w') as f:
        json.dump(results_dict, f, indent=2)
    
    logger.info(f"Results saved to {output_path}")


# ============================================================================
# Main CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='XAI Stability Runner for Explainability Evaluation'
    )
    
    # Mode
    parser.add_argument(
        '--mode',
        choices=['smoke', 'comprehensive'],
        default='smoke',
        help='Evaluation mode: smoke (fast), comprehensive (full)'
    )
    
    # Explanation methods
    parser.add_argument(
        '--methods',
        nargs='+',
        default=['shap', 'integrated_gradients'],
        help='Explanation methods to test'
    )
    
    # Stability parameters
    parser.add_argument('--samples', type=int, default=100, help='Number of samples to evaluate')
    parser.add_argument(
        '--perturbation_scales',
        type=float,
        nargs='+',
        default=[0.01, 0.02],
        help='Perturbation scales to test'
    )
    parser.add_argument('--similarity_threshold', type=float, default=0.85)
    parser.add_argument('--fidelity_threshold', type=float, default=0.85)
    parser.add_argument('--similarity_metric', default='cosine', choices=['cosine', 'spearman', 'l2'])
    
    # Data parameters
    parser.add_argument('--model_path', default='models/model.pt')
    parser.add_argument('--data_path', default='data/eval_data.pt')
    
    # Output
    parser.add_argument('--output', default='xai_stability_results.json')
    parser.add_argument('--log_level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    setup_logging(args.log_level)
    
    logger.info(f"Starting XAI Stability Runner in {args.mode} mode")
    logger.info(f"Methods: {args.methods}")
    logger.info(f"Perturbation scales: {args.perturbation_scales}")
    
    # Load model and data
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    logger.info(f"Using device: {device}")
    
    try:
        model, x, y = load_model_and_data(args.model_path, args.data_path, device)
    except Exception as e:
        logger.error(f"Failed to load model/data: {e}")
        logger.info("Using dummy model and data for demonstration")
        
        # Create dummy model and data for testing
        model = nn.Sequential(
            nn.Linear(784, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )
        x = torch.randn(args.samples, 784)
        y = torch.randint(0, 10, (args.samples,))
    
    # Limit samples
    x = x[:args.samples]
    y = y[:args.samples]
    
    # Create evaluator
    evaluator = StabilityEvaluator(model, device)
    
    # Adjust parameters based on mode
    if args.mode == 'smoke':
        methods = args.methods[:1]  # Test only first method
        perturbation_scales = args.perturbation_scales[:1]
        samples = min(50, args.samples)
    else:
        methods = args.methods
        perturbation_scales = args.perturbation_scales
        samples = args.samples
    
    x_eval = x[:samples]
    y_eval = y[:samples]
    
    # Run stability tests
    metrics = {}
    for method in methods:
        config = StabilityTestConfig(
            method=method,
            num_samples=len(x_eval),
            perturbation_scales=perturbation_scales,
            similarity_metric=args.similarity_metric,
            similarity_threshold=args.similarity_threshold,
            fidelity_threshold=args.fidelity_threshold
        )
        
        try:
            metric = evaluator.test_stability(x_eval, config)
            metrics[method] = metric
        except Exception as e:
            logger.error(f"Failed to test {method}: {e}")
            metrics[method] = StabilityMetrics(
                method=method,
                num_samples=len(x_eval),
                mean_similarity=0.0,
                std_similarity=0.0,
                min_similarity=0.0,
                max_similarity=0.0,
                stability_score=0.0,
                status='failed',
                notes=f"Error: {str(e)}"
            )
    
    # Determine overall status
    statuses = [m.status for m in metrics.values()]
    if all(s == 'passed' for s in statuses):
        overall_status = 'passed'
    elif any(s == 'failed' for s in statuses):
        overall_status = 'failed'
    else:
        overall_status = 'warning'
    
    # Create result
    result = ExplanationStabilityResult(
        timestamp=datetime.utcnow().isoformat(),
        commit_sha=get_commit_sha(),
        mode=args.mode,
        methods_tested=methods,
        metrics=metrics,
        overall_status=overall_status,
        perturbation_scales_tested=perturbation_scales,
        num_samples=len(x_eval),
        notes=f"Evaluated {len(methods)} explanation methods"
    )
    
    # Save results
    save_results(result, args.output)
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("XAI STABILITY EVALUATION SUMMARY")
    logger.info("="*60)
    for method, metric in metrics.items():
        logger.info(f"\n{method.upper()}:")
        logger.info(f"  Mean Similarity: {metric.mean_similarity:.3f}")
        logger.info(f"  Stability Score: {metric.stability_score:.1f}%")
        logger.info(f"  Status: {metric.status}")
    logger.info(f"\nOverall Status: {overall_status}")
    logger.info("="*60 + "\n")
    
    # Exit with appropriate code
    sys.exit(0 if overall_status == 'passed' else 1)


if __name__ == '__main__':
    main()

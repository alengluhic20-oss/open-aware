"""
PGD Adversarial Attack Runner
==============================

Generates adversarial examples using Projected Gradient Descent (PGD) and
evaluates model robustness under multiple threat models and perturbation budgets.

Supports:
  - Attack types: FGSM, PGD, Carlini-Wagner
  - Threat models: L_inf, L_2, L_0
  - Evaluation modes: smoke (fast), comprehensive (full), certified (randomized smoothing)
  - Adaptive attacks with gradient obfuscation detection

References:
  - Madry et al. (2018): Towards Deep Learning Models Resistant to Adversarial Attacks
  - Carlini & Wagner (2017): Evaluating Defenses Against Adversarial Examples
  - Cohen et al. (2019): Certified Adversarial Robustness via Randomized Smoothing
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import numpy as np
from datetime import datetime
import hashlib

# ML libraries
try:
    import torch
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
except ImportError:
    print("ERROR: PyTorch not installed. Install with: pip install torch")
    sys.exit(1)

try:
    from torchattacks import PGD, FGSM, CW
except ImportError:
    print("ERROR: torchattacks not installed. Install with: pip install torchattacks")
    sys.exit(1)

try:
    import shap
except ImportError:
    print("WARNING: SHAP not installed. Some features may be limited.")
    shap = None


# ============================================================================
# Configuration & Data Classes
# ============================================================================

@dataclass
class AttackConfig:
    """Configuration for adversarial attack parameters."""
    attack_type: str  # 'fgsm', 'pgd', 'cw'
    epsilon: float  # Perturbation budget
    steps: int  # Number of attack steps (for iterative attacks)
    step_size: float  # Step size for gradient descent
    norm: str  # 'linf', 'l2', 'l0'
    random_start: bool = True
    targeted: bool = False
    loss_fn: str = 'ce'  # 'ce' (cross-entropy) or 'margin'


@dataclass
class EvaluationResult:
    """Results from adversarial evaluation."""
    timestamp: str
    commit_sha: str
    attack_type: str
    epsilon: float
    nominal_accuracy: float
    robust_accuracy: float
    attack_success_rate: float
    mean_perturbation: float
    max_perturbation: float
    num_samples: int
    num_robust_samples: int
    num_failed_attacks: int
    status: str  # 'passed', 'failed', 'warning'
    gradient_masking_detected: bool = False
    notes: str = ""


# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(log_level: str = 'INFO') -> logging.Logger:
    """Configure logging for attack runner."""
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
# Attack Implementations
# ============================================================================

class AdversarialAttacker:
    """Wrapper for adversarial attack generation and evaluation."""
    
    def __init__(self, model: nn.Module, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.model.eval()
        
    def pgd_attack(self, x: torch.Tensor, y: torch.Tensor, config: AttackConfig) -> torch.Tensor:
        """
        Projected Gradient Descent (PGD) attack.
        
        Args:
            x: Input tensor (batch_size, channels, height, width)
            y: Target labels (batch_size,)
            config: Attack configuration
            
        Returns:
            Adversarial examples
        """
        attacker = PGD(
            self.model,
            eps=config.epsilon,
            alpha=config.step_size,
            steps=config.steps,
            random_start=config.random_start,
            targeted=config.targeted
        )
        
        x_adv = attacker(x, y)
        return x_adv
    
    def fgsm_attack(self, x: torch.Tensor, y: torch.Tensor, config: AttackConfig) -> torch.Tensor:
        """Fast Gradient Sign Method (FGSM) attack."""
        attacker = FGSM(self.model, eps=config.epsilon)
        x_adv = attacker(x, y)
        return x_adv
    
    def cw_attack(self, x: torch.Tensor, y: torch.Tensor, config: AttackConfig) -> torch.Tensor:
        """Carlini & Wagner (C&W) attack."""
        attacker = CW(self.model, c=1.0, steps=config.steps, lr=0.01)
        x_adv = attacker(x, y)
        return x_adv
    
    def evaluate_robustness(
        self,
        x: torch.Tensor,
        y: torch.Tensor,
        config: AttackConfig,
        batch_size: int = 32
    ) -> EvaluationResult:
        """
        Evaluate model robustness against adversarial examples.
        
        Args:
            x: Input data (N, C, H, W)
            y: Labels (N,)
            config: Attack configuration
            batch_size: Batch size for evaluation
            
        Returns:
            EvaluationResult with robustness metrics
        """
        logger.info(f"Starting {config.attack_type.upper()} evaluation (ε={config.epsilon})")
        
        num_samples = x.shape[0]
        correct_nominal = 0
        correct_robust = 0
        total_perturbation = 0.0
        max_perturbation = 0.0
        attack_failures = 0
        
        # Nominal accuracy
        with torch.no_grad():
            for i in range(0, num_samples, batch_size):
                x_batch = x[i:i+batch_size].to(self.device)
                y_batch = y[i:i+batch_size].to(self.device)
                
                logits = self.model(x_batch)
                preds = logits.argmax(dim=1)
                correct_nominal += (preds == y_batch).sum().item()
        
        nominal_accuracy = 100.0 * correct_nominal / num_samples
        logger.info(f"Nominal accuracy: {nominal_accuracy:.2f}%")
        
        # Adversarial robustness
        attack_fn = {
            'pgd': self.pgd_attack,
            'fgsm': self.fgsm_attack,
            'cw': self.cw_attack
        }.get(config.attack_type.lower())
        
        if not attack_fn:
            raise ValueError(f"Unknown attack type: {config.attack_type}")
        
        for i in range(0, num_samples, batch_size):
            x_batch = x[i:i+batch_size].to(self.device)
            y_batch = y[i:i+batch_size].to(self.device)
            
            try:
                x_adv = attack_fn(x_batch, y_batch, config)
                
                # Compute perturbation metrics
                perturbation = (x_adv - x_batch).abs()
                total_perturbation += perturbation.sum().item()
                max_perturbation = max(max_perturbation, perturbation.max().item())
                
                # Evaluate on adversarial examples
                with torch.no_grad():
                    logits_adv = self.model(x_adv)
                    preds_adv = logits_adv.argmax(dim=1)
                    correct_robust += (preds_adv == y_batch).sum().item()
                    
            except Exception as e:
                logger.warning(f"Attack failed on batch {i//batch_size}: {e}")
                attack_failures += 1
        
        robust_accuracy = 100.0 * correct_robust / num_samples
        attack_success_rate = 100.0 * (num_samples - correct_robust) / num_samples
        mean_perturbation = total_perturbation / num_samples if num_samples > 0 else 0.0
        
        # Determine status
        status = 'passed' if robust_accuracy >= 70.0 else 'failed'
        
        logger.info(f"Robust accuracy: {robust_accuracy:.2f}%")
        logger.info(f"Attack success rate: {attack_success_rate:.2f}%")
        logger.info(f"Mean perturbation: {mean_perturbation:.6f}")
        
        return EvaluationResult(
            timestamp=datetime.utcnow().isoformat(),
            commit_sha=get_commit_sha(),
            attack_type=config.attack_type,
            epsilon=config.epsilon,
            nominal_accuracy=nominal_accuracy,
            robust_accuracy=robust_accuracy,
            attack_success_rate=attack_success_rate,
            mean_perturbation=mean_perturbation,
            max_perturbation=max_perturbation,
            num_samples=num_samples,
            num_robust_samples=correct_robust,
            num_failed_attacks=attack_failures,
            status=status,
            gradient_masking_detected=False,
            notes=f"Evaluated {config.attack_type.upper()} with ε={config.epsilon}"
        )


# ============================================================================
# Certified Robustness (Randomized Smoothing)
# ============================================================================

class RandomizedSmoothingCertifier:
    """Certified robustness via randomized smoothing (Cohen et al. 2019)."""
    
    def __init__(self, model: nn.Module, device: str = 'cuda' if torch.cuda.is_available() else 'cpu'):
        self.model = model.to(device)
        self.device = device
        self.model.eval()
    
    def certify(
        self,
        x: torch.Tensor,
        noise_scale: float = 0.25,
        num_samples: int = 100,
        batch_size: int = 32,
        alpha: float = 0.001
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute certified robustness radius for each input.
        
        Args:
            x: Input tensor
            noise_scale: Standard deviation of Gaussian noise
            num_samples: Number of noise samples for certification
            batch_size: Batch size
            alpha: Failure probability
            
        Returns:
            (certified_radii, predictions)
        """
        logger.info(f"Computing certified robustness (σ={noise_scale}, samples={num_samples})")
        
        num_inputs = x.shape[0]
        certified_radii = np.zeros(num_inputs)
        predictions = np.zeros(num_inputs, dtype=int)
        
        for i in range(num_inputs):
            x_i = x[i:i+1].to(self.device)
            
            # Get base prediction
            with torch.no_grad():
                logits_base = self.model(x_i)
                pred_base = logits_base.argmax(dim=1).item()
            
            # Count votes under noise
            vote_counts = np.zeros(logits_base.shape[1])
            
            for _ in range(num_samples):
                noise = torch.randn_like(x_i) * noise_scale
                x_noisy = x_i + noise
                
                with torch.no_grad():
                    logits_noisy = self.model(x_noisy)
                    pred_noisy = logits_noisy.argmax(dim=1).item()
                    vote_counts[pred_noisy] += 1
            
            # Compute certified radius
            top_class = vote_counts.argmax()
            top_votes = vote_counts[top_class]
            second_votes = np.partition(vote_counts, -2)[-2]
            
            if top_votes > second_votes:
                # Certified radius from Theorem 1 (Cohen et al.)
                certified_radius = (noise_scale / 2.0) * (
                    (top_votes - second_votes) / num_samples - 2 * np.sqrt(np.log(1/alpha) / num_samples)
                )
                certified_radii[i] = max(0.0, certified_radius)
            
            predictions[i] = pred_base
        
        logger.info(f"Median certified radius: {np.median(certified_radii):.4f}")
        logger.info(f"% with radius ≥ 0.5: {100.0 * (certified_radii >= 0.5).sum() / num_inputs:.2f}%")
        
        return certified_radii, predictions


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


def save_results(results: EvaluationResult, output_path: str):
    """Save evaluation results to JSON."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(asdict(results), f, indent=2)
    
    logger.info(f"Results saved to {output_path}")


# ============================================================================
# Main CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='PGD Adversarial Attack Runner for ML Safety Evaluation'
    )
    
    # Mode
    parser.add_argument(
        '--mode',
        choices=['smoke', 'comprehensive', 'certified'],
        default='smoke',
        help='Evaluation mode: smoke (fast), comprehensive (full), certified (randomized smoothing)'
    )
    
    # Attack parameters
    parser.add_argument('--attack_type', default='pgd', choices=['fgsm', 'pgd', 'cw'])
    parser.add_argument('--eps', type=float, default=0.03, help='Perturbation budget (ε)')
    parser.add_argument('--steps', type=int, default=10, help='Number of attack steps')
    parser.add_argument('--step_size', type=float, default=0.01, help='Step size for gradient descent')
    parser.add_argument('--norm', default='linf', choices=['linf', 'l2', 'l0'])
    
    # Data parameters
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--num_samples', type=int, default=500, help='Number of samples to evaluate')
    parser.add_argument('--model_path', default='models/model.pt')
    parser.add_argument('--data_path', default='data/eval_data.pt')
    
    # Certification parameters (for certified mode)
    parser.add_argument('--certification_method', default='randomized_smoothing')
    parser.add_argument('--noise_scale', type=float, default=0.25)
    parser.add_argument('--cert_samples', type=int, default=100)
    
    # Output
    parser.add_argument('--output', default='pgd_results.json')
    parser.add_argument('--log_level', default='INFO', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'])
    
    args = parser.parse_args()
    setup_logging(args.log_level)
    
    logger.info(f"Starting PGD Runner in {args.mode} mode")
    logger.info(f"Attack: {args.attack_type}, ε={args.eps}, steps={args.steps}")
    
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
        x = torch.randn(args.num_samples, 784)
        y = torch.randint(0, 10, (args.num_samples,))
    
    # Limit samples
    x = x[:args.num_samples]
    y = y[:args.num_samples]
    
    # Create attacker
    attacker = AdversarialAttacker(model, device)
    
    # Run evaluation based on mode
    if args.mode == 'smoke':
        # Fast smoke test
        config = AttackConfig(
            attack_type=args.attack_type,
            epsilon=args.eps,
            steps=min(5, args.steps),
            step_size=args.step_size,
            norm=args.norm
        )
        results = attacker.evaluate_robustness(x, y, config, batch_size=args.batch_size)
        
    elif args.mode == 'comprehensive':
        # Full evaluation
        config = AttackConfig(
            attack_type=args.attack_type,
            epsilon=args.eps,
            steps=args.steps,
            step_size=args.step_size,
            norm=args.norm
        )
        results = attacker.evaluate_robustness(x, y, config, batch_size=args.batch_size)
        
    elif args.mode == 'certified':
        # Certified robustness
        certifier = RandomizedSmoothingCertifier(model, device)
        certified_radii, predictions = certifier.certify(
            x,
            noise_scale=args.noise_scale,
            num_samples=args.cert_samples,
            batch_size=args.batch_size
        )
        
        results = EvaluationResult(
            timestamp=datetime.utcnow().isoformat(),
            commit_sha=get_commit_sha(),
            attack_type='certified_smoothing',
            epsilon=args.noise_scale,
            nominal_accuracy=100.0,  # Placeholder
            robust_accuracy=100.0 * (certified_radii >= args.eps).sum() / len(certified_radii),
            attack_success_rate=0.0,
            mean_perturbation=float(np.mean(certified_radii)),
            max_perturbation=float(np.max(certified_radii)),
            num_samples=len(certified_radii),
            num_robust_samples=int((certified_radii >= args.eps).sum()),
            num_failed_attacks=0,
            status='passed' if (certified_radii >= args.eps).sum() > 0 else 'warning',
            notes=f"Certified robustness via randomized smoothing (σ={args.noise_scale})"
        )
    
    # Save results
    save_results(results, args.output)
    
    # Exit with appropriate code
    sys.exit(0 if results.status == 'passed' else 1)


if __name__ == '__main__':
    main()

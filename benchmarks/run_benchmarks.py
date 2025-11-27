"""
run_benchmarks.py

Benchmark MA'AT-42 / Ma'at Thyself AI evaluators on a JSONL dataset.

Usage:
    python -m benchmarks.run_benchmarks \
        --data-file benchmarks/data/test.jsonl \
        --systems MAAT_EMBEDDING MAAT_LLM MAAT_HYBRID

Note:
    This is a skeleton/framework for benchmarking. The actual evaluator
    implementations (EmbeddingEvaluator, LLMJudgeEvaluator, HybridEvaluator)
    must be provided in the evaluator/ package. The adapters below show the
    expected interface and will raise ImportError if the evaluators are not
    available.
"""

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Literal

from collections import defaultdict

# Adjust these imports to match your actual package structure.
# If the evaluator package is not available, the adapters will raise ImportError.
try:
    from evaluator.embedding import EmbeddingEvaluator
    from evaluator.llm_judge import LLMJudgeEvaluator
    from evaluator.hybrid import HybridEvaluator
except ImportError:
    EmbeddingEvaluator = None
    LLMJudgeEvaluator = None
    HybridEvaluator = None


Label = Literal["BLOCK", "ALLOW"]


@dataclass
class Example:
    id: str
    context: Optional[str]
    text: str
    label: Label
    subcategory: str


@dataclass
class Prediction:
    id: str
    system: str
    decision: Label
    score: Optional[float]
    true_label: Label
    subcategory: str


# =============== Metrics ===============

def compute_basic_metrics(preds: List[Prediction]) -> Dict[str, float]:
    """
    Compute accuracy, precision, recall, F1 for BLOCK as positive class.
    """
    tp = fp = tn = fn = 0

    for p in preds:
        y_true = p.true_label
        y_pred = p.decision

        if y_true == "BLOCK" and y_pred == "BLOCK":
            tp += 1
        elif y_true == "BLOCK" and y_pred == "ALLOW":
            fn += 1
        elif y_true == "ALLOW" and y_pred == "BLOCK":
            fp += 1
        elif y_true == "ALLOW" and y_pred == "ALLOW":
            tn += 1

    total = tp + tn + fp + fn
    accuracy = (tp + tn) / total if total else 0.0

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    if precision + recall > 0:
        f1 = 2 * precision * recall / (precision + recall)
    else:
        f1 = 0.0

    return {
        "accuracy": accuracy,
        "precision_block": precision,
        "recall_block": recall,
        "f1_block": f1,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "total": total,
    }


def print_metrics_table(results: Dict[str, Dict[str, Dict[str, float]]]) -> None:
    """
    Pretty-print metrics per system and per category.
    results[system][category] -> metric dict
    """
    for system, cats in results.items():
        print("=" * 70)
        print(f"System: {system}")
        print("=" * 70)
        for cat, m in cats.items():
            print(f"[{cat}]")
            print(
                f"  total={m['total']} | "
                f"acc={m['accuracy']:.3f} | "
                f"prec(BLOCK)={m['precision_block']:.3f} | "
                f"recall(BLOCK)={m['recall_block']:.3f} | "
                f"f1(BLOCK)={m['f1_block']:.3f}"
            )
        print()


# =============== System Adapters ===============

class BaseAdapter:
    name: str

    def evaluate(self, text: str, context: Optional[str]) -> Dict:
        """
        Must return:
        {
            "decision": "BLOCK" or "ALLOW",
            "score": optional float (0–1) or None,
            "details": optional dict
        }
        """
        raise NotImplementedError


class EmbeddingAdapter(BaseAdapter):
    def __init__(self):
        if EmbeddingEvaluator is None:
            raise ImportError("EmbeddingEvaluator could not be imported.")
        self.name = "MAAT_EMBEDDING"
        self.evaluator = EmbeddingEvaluator()

    def evaluate(self, text: str, context: Optional[str]) -> Dict:
        result = self.evaluator.evaluate(text)
        return {
            "decision": result.decision,
            "score": result.overall_score,
            "details": {
                "critical_violations": result.critical_violations,
                "top_violations": result.top_violations,
            },
        }


class LLMAdapter(BaseAdapter):
    def __init__(self):
        if LLMJudgeEvaluator is None:
            raise ImportError("LLMJudgeEvaluator could not be imported.")
        # NOTE: This is a skeleton. Replace with actual LLM client (e.g., Anthropic or OpenAI)
        # when the evaluator package is implemented.
        api_client = None  # Placeholder - will be replaced with actual client
        self.name = "MAAT_LLM"
        self.evaluator = LLMJudgeEvaluator(api_client=api_client)

    def evaluate(self, text: str, context: Optional[str]) -> Dict:
        # You can choose full_42=True for thorough evaluation, or False for critical-only.
        result = self.evaluator.evaluate(text, full_42=False)
        return {
            "decision": result.decision,
            "score": result.overall_score,
            "details": {
                "critical_violations": result.critical_violations,
                "top_violations": result.top_violations,
            },
        }


class HybridAdapter(BaseAdapter):
    def __init__(self):
        if EmbeddingEvaluator is None or HybridEvaluator is None:
            raise ImportError("HybridEvaluator or EmbeddingEvaluator could not be imported.")
        # NOTE: This is a skeleton. Replace with actual LLM client when the evaluator
        # package is implemented.
        api_client = None  # Placeholder - will be replaced with actual client
        self.name = "MAAT_HYBRID"
        self.evaluator = HybridEvaluator(api_client=api_client)

    def evaluate(self, text: str, context: Optional[str]) -> Dict:
        result = self.evaluator.evaluate(text)
        return {
            "decision": result.decision,
            "score": result.overall_score,
            "details": {
                "critical_violations": result.critical_violations,
                "top_violations": result.top_violations,
            },
        }


def get_system_adapters(system_names: List[str]) -> List[BaseAdapter]:
    adapters: List[BaseAdapter] = []
    for name in system_names:
        if name == "MAAT_EMBEDDING":
            adapters.append(EmbeddingAdapter())
        elif name == "MAAT_LLM":
            adapters.append(LLMAdapter())
        elif name == "MAAT_HYBRID":
            adapters.append(HybridAdapter())
        else:
            raise ValueError(f"Unknown system name: {name}")
    return adapters


# =============== Data Loading ===============

def load_examples(path: Path) -> List[Example]:
    examples: List[Example] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            examples.append(
                Example(
                    id=obj["id"],
                    context=obj.get("context"),
                    text=obj["text"],
                    label=obj["label"],
                    subcategory=obj.get("subcategory", "UNKNOWN"),
                )
            )
    return examples


# =============== Main Benchmark Loop ===============

def run_benchmarks(
    data_file: Path,
    system_names: List[str],
) -> None:
    examples = load_examples(data_file)
    if not examples:
        print(f"No examples loaded from {data_file}")
        return

    adapters = get_system_adapters(system_names)
    all_predictions: List[Prediction] = []

    for adapter in adapters:
        print(f"Evaluating system: {adapter.name} on {len(examples)} examples...")
        for ex in examples:
            out = adapter.evaluate(ex.text, ex.context)
            decision = out["decision"]
            score = out.get("score")
            all_predictions.append(
                Prediction(
                    id=ex.id,
                    system=adapter.name,
                    decision=decision,
                    score=score,
                    true_label=ex.label,
                    subcategory=ex.subcategory,
                )
            )

    # Compute metrics per system and per category
    results: Dict[str, Dict[str, Dict[str, float]]] = {}
    for adapter in adapters:
        system_name = adapter.name
        system_preds = [p for p in all_predictions if p.system == system_name]

        # Overall
        results[system_name] = {}
        results[system_name]["OVERALL"] = compute_basic_metrics(system_preds)

        # Per subcategory
        by_cat: Dict[str, List[Prediction]] = defaultdict(list)
        for p in system_preds:
            by_cat[p.subcategory].append(p)

        for cat, preds in by_cat.items():
            results[system_name][cat] = compute_basic_metrics(preds)

    print_metrics_table(results)


# =============== CLI ===============

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run MA'AT-42 benchmarks.")
    parser.add_argument(
        "--data-file",
        type=str,
        required=True,
        help="Path to JSONL file with benchmark data.",
    )
    parser.add_argument(
        "--systems",
        type=str,
        nargs="+",
        default=["MAAT_EMBEDDING", "MAAT_LLM", "MAAT_HYBRID"],
        help="Which systems to evaluate. Choices: MAAT_EMBEDDING, MAAT_LLM, MAAT_HYBRID",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    data_file = Path(args.data_file)
    run_benchmarks(data_file=data_file, system_names=args.systems)

"""
Command-line interface for Ethical AI Validator.

This module provides a command-line interface for the Ethical AI Validator,
enabling users to run bias detection, fairness assessment, and compliance
reporting directly from the terminal.

The CLI supports various input formats and provides comprehensive audit
capabilities with configurable parameters and output options.

Author: WHIS (muhammadabdullahinbox@gmail.com)
Version: 1.3.0
Repository: https://github.com/whis-19/ethical-ai
Documentation: https://whis-19.github.io/ethical-ai/
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from . import EthicalAIValidator


def main() -> int:
    """
    Main CLI entry point for Ethical AI Validator.
    
    This function parses command-line arguments and executes the appropriate
    ethical AI validation tasks based on user input. It provides a user-friendly
    interface for running bias detection, fairness assessment, and compliance
    reporting without requiring Python programming knowledge.
    
    Supported operations:
    - Bias detection across protected attributes
    - Fairness metrics calculation
    - Compliance report generation
    - Real-time monitoring setup
    - Mitigation suggestions
    
    Returns:
        int: Exit code (0 for success, 1 for error)
        
    Author: WHIS (muhammadabdullahinbox@gmail.com)
    """
    parser = argparse.ArgumentParser(
        description="Audit AI models for bias, fairness, and compliance"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="ethical-ai-validator 1.3.0"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output path for audit report"
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default=None,
        help="Training scenario name/description to include in output"
    )
    parser.add_argument(
        "--hyperparameters",
        type=str,
        default=None,
        help="Model hyperparameters as JSON string to include in output"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize validator
        validator = EthicalAIValidator()
        
        if args.verbose:
            print("Ethical AI Validator initialized successfully")
        
        # Parse optional hyperparameters JSON
        hp_dict = {}
        if args.hyperparameters:
            try:
                import json as _json
                hp_dict = _json.loads(args.hyperparameters)
                if not isinstance(hp_dict, dict):
                    hp_dict = {"value": hp_dict}
            except Exception:
                hp_dict = {"raw": args.hyperparameters}

        print("Ethical AI Validator CLI")
        print("=========================")
        if args.scenario:
            print(f"Scenario: {args.scenario}")
        if hp_dict:
            print("Hyperparameters:")
            for k, v in hp_dict.items():
                print(f"  - {k}: {v}")

        # Print simple hyperparameter impact hints
        def _cli_analyze_hp(hp: dict):
            hints = []
            if not isinstance(hp, dict):
                return hints
            md = hp.get('max_depth')
            if isinstance(md, (int, float)) and md and md > 12:
                hints.append("max_depth: HIGH risk for overfitting biased patterns")
            mss = hp.get('min_samples_split')
            if isinstance(mss, (int, float)) and mss and mss < 3:
                hints.append("min_samples_split: MEDIUM risk for fragmenting minority groups")
            C = hp.get('C')
            if isinstance(C, (int, float)) and C and C > 5:
                hints.append("C: HIGH risk due to low regularization")
            lr = hp.get('learning_rate')
            if isinstance(lr, (int, float)) and lr and lr > 0.2:
                hints.append("learning_rate: HIGH risk due to unstable training")
            hidden = hp.get('hidden_layer_sizes')
            if isinstance(hidden, (list, tuple)) and sum(hidden) > 200:
                hints.append("hidden_layer_sizes: MEDIUM risk due to large capacity")
            return hints

        impact_hints = _cli_analyze_hp(hp_dict)
        if impact_hints:
            print("\nLikely contributing hyperparameters:")
            for h in impact_hints:
                print(f"  - {h}")

        # Placeholder for metrics output (aligns with example matrices style)
        print("\nMetrics (placeholder):")
        print("  - Bias: N/A (provide predictions/labels to compute)")
        print("  - Fairness: N/A (provide protected attributes to compute)")

        # If an output path is provided, emit a minimal report including scenario/hyperparameters
        if args.output:
            meta = {
                'model_name': 'N/A',
                'model_version': 'N/A',
                'scenario': args.scenario or 'N/A',
                'hyperparameters': hp_dict,
                'bias_report': None,
                'fairness_metrics': None
            }
            criteria = {'bias_threshold': 0.1, 'fairness_threshold': 0.8}
            try:
                path = validator.generate_compliance_report(meta, criteria, output_path=args.output)
                print(f"Report saved to: {path}")
            except Exception as e:
                print(f"Failed to save report: {e}")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Branch-coverage tests for generate_compliance_report and related logic.
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ethical_ai_validator.ethical_ai_validator import EthicalAIValidator  # type: ignore


def _make_bias_report(high_bias: bool = True) -> pd.DataFrame:
    bias = 0.35 if high_bias else 0.05
    return pd.DataFrame([
        {
            'protected_attribute': 'gender',
            'group': 'male',
            'group_size': 50,
            'accuracy': 0.7,
            'precision': 0.7,
            'recall': 0.7,
            'f1_score': 0.7,
            'positive_rate': 0.6,
            'statistical_parity': 0.2,
            'equalized_odds': 0.15,
            'demographic_parity': 0.2,
            'bias_score': bias,
        }
    ])


def _make_fairness_metrics(low_fairness: bool = True) -> dict:
    score = 0.72 if low_fairness else 0.92
    return {
        'overall_metrics': {'positive_rate': 0.5, 'total_samples': 100},
        'protected_attribute_metrics': {'gender': {'male': {'positive_rate': 0.6, 'group_size': 50, 'disparity': 0.1}}},
        'fairness_scores': {'gender': {'max_disparity': 0.3, 'fairness_score': score, 'num_groups': 2}},
    }


def test_generate_report_full_branches(tmp_path):
    v = EthicalAIValidator()
    # Construct metadata to trigger most branches (bias+fairness issues, hyperparams table, impact analysis)
    metadata = {
        'model_name': 'BranchModel',
        'scenario': 'Scenario-A',
        'hyperparameters': {
            'max_depth': 15,
            'min_samples_split': 2,
            'C': 10,
            'hidden_layer_sizes': (150, 100),
            'learning_rate': 0.3,
            'class_weight': None,
            'n_estimators': 400,
        },
        'bias_report': _make_bias_report(high_bias=True),
        'fairness_metrics': _make_fairness_metrics(low_fairness=True),
        'feature_disparities': {
            'gender': [
                {'feature': 'f1', 'disparity': 0.4, 'top_group': 'male', 'bottom_group': 'female'}
            ]
        },
    }
    audit_criteria = {'bias_threshold': 0.1, 'fairness_threshold': 0.8}
    out_path = tmp_path / 'full_branches.pdf'
    path = v.generate_compliance_report(metadata, audit_criteria, output_path=str(out_path))
    assert os.path.exists(path)


def test_generate_report_minimal_paths(tmp_path):
    v = EthicalAIValidator()
    # No bias_report and no fairness_metrics to hit alternate paths
    metadata = {
        'model_name': 'MinimalModel',
        'scenario': 'Scenario-B',
        'hyperparameters': {},
    }
    audit_criteria = {'bias_threshold': 0.2, 'fairness_threshold': 0.9}
    out_path = tmp_path / 'minimal_paths.pdf'
    path = v.generate_compliance_report(metadata, audit_criteria, output_path=str(out_path))
    assert os.path.exists(path)


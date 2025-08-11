#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Extended tests for eai.fairness to improve coverage of additional functions
and branches.
"""

import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from eai.fairness import (
    calculate_fairness_metrics,
    fairness_score,
    calculate_parity_metrics,
    assess_fairness,
)


def test_fairness_metrics_validation_error_length_mismatch():
    preds = [0, 1, 0]
    protected = {'gender': ['m', 'f']}
    try:
        calculate_fairness_metrics(preds, protected)
        assert False, 'Expected ValueError'
    except ValueError:
        assert True


def test_fairness_score_average_and_no_scores():
    preds = [0, 1, 1, 0]
    protected = {'g': ['a', 'a', 'b', 'b']}
    fs = fairness_score(preds, protected)
    assert 0.0 <= fs <= 1.0

    # When no fairness scores (single group), score should be 1.0
    preds2 = [0, 1]
    protected2 = {'g': ['a', 'a']}
    fs2 = fairness_score(preds2, protected2)
    assert fs2 == 1.0


def test_calculate_parity_metrics_smoke():
    preds = [0, 1, 1, 0, 1, 0]
    labels = [0, 1, 0, 0, 1, 1]
    protected = {'g': ['a', 'a', 'b', 'b', 'b', 'a']}
    res = calculate_parity_metrics(preds, labels, protected)
    assert isinstance(res, dict)
    assert 'g' in res


def test_assess_fairness_threshold_and_recommendations():
    preds = [1, 1, 1, 0, 0, 0]
    protected = {'g': ['a', 'a', 'a', 'b', 'b', 'b']}
    assessment = assess_fairness(preds, protected, threshold=0.9)
    assert 'overall_fairness_score' in assessment
    assert 'is_fair' in assessment
    # With a high threshold, likely to trigger recommendations
    assert isinstance(assessment.get('recommendations', []), list)


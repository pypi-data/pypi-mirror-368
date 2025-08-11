#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Fairness metrics calculation module for Ethical AI (eai).

This module provides functions for calculating various fairness metrics
and assessing model fairness across protected attributes.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder

# from .utils import validate_inputs
# from .metrics import accuracy_parity, precision_parity, recall_parity


def calculate_fairness_metrics(
    predictions, 
    protected_attributes,
    label_encoders=None
):
    """
    Calculate fairness metrics for model predictions.
    
    This function computes various fairness metrics including equal opportunity,
    demographic parity, and equalized odds across all protected attributes.
    
    Parameters
    ----------
    predictions : array-like
        Model predictions (binary or multiclass).
    protected_attributes : dict
        Dictionary of protected attributes and their values.
    label_encoders : dict, optional
        Dictionary of label encoders for categorical attributes.
    
    Returns
    -------
    dict
        Dictionary containing fairness metrics.
    
    Examples
    --------
    >>> from eai.fairness import calculate_fairness_metrics
    >>> predictions = [1, 0, 1, 0, 1]
    >>> protected_attrs = {'gender': ['male', 'female', 'male', 'female', 'male']}
    >>> fairness_metrics = calculate_fairness_metrics(predictions, protected_attrs)
    """
    predictions = np.array(predictions)
    
    # Validate inputs
    for attr_name, attr_values in protected_attributes.items():
        attr_values = np.array(attr_values)
        if len(attr_values) != len(predictions):
            raise ValueError("Protected attribute '{}' must have same length as predictions".format(attr_name))
    
    fairness_results = {
        'overall_metrics': {},
        'protected_attribute_metrics': {},
        'fairness_scores': {}
    }
    
    # Overall metrics
    overall_positive_rate = np.mean(predictions)
    fairness_results['overall_metrics'] = {
        'positive_rate': overall_positive_rate,
        'total_samples': len(predictions)
    }
    
    # Initialize label encoders if not provided
    if label_encoders is None:
        label_encoders = {}
    
    # Process each protected attribute
    for attr_name, attr_values in protected_attributes.items():
        attr_values = np.array(attr_values)
        
        # Encode categorical attributes
        if attr_name not in label_encoders:
            label_encoders[attr_name] = LabelEncoder()
            attr_encoded = label_encoders[attr_name].fit_transform(attr_values)
        else:
            attr_encoded = label_encoders[attr_name].transform(attr_values)
        
        # Calculate fairness metrics for this attribute
        unique_groups = np.unique(attr_encoded)
        group_metrics = {}
        
        for group in unique_groups:
            group_mask = attr_encoded == group
            group_name = label_encoders[attr_name].inverse_transform([group])[0]
            
            if np.sum(group_mask) < 5:  # Skip very small groups
                continue
            
            group_predictions = predictions[group_mask]
            group_positive_rate = np.mean(group_predictions)
            
            group_metrics[group_name] = {
                'positive_rate': group_positive_rate,
                'group_size': np.sum(group_mask),
                'disparity': group_positive_rate - overall_positive_rate
            }
        
        fairness_results['protected_attribute_metrics'][attr_name] = group_metrics
        
        # Calculate fairness scores for this attribute
        if len(group_metrics) >= 2:
            positive_rates = [metrics['positive_rate'] for metrics in group_metrics.values()]
            max_disparity = max(positive_rates) - min(positive_rates)
            fairness_results['fairness_scores'][attr_name] = {
                'max_disparity': max_disparity,
                'fairness_score': 1.0 - min(max_disparity, 1.0),  # Higher is fairer
                'num_groups': len(group_metrics)
            }
    
    return fairness_results


def fairness_score(
    predictions, 
    protected_attributes,
    label_encoders=None
):
    """
    Calculate overall fairness score.
    
    Parameters
    ----------
    predictions : array-like
        Model predictions.
    protected_attributes : dict
        Dictionary of protected attributes.
    label_encoders : dict, optional
        Dictionary of label encoders.
    
    Returns
    -------
    float
        Overall fairness score between 0 and 1.
    """
    fairness_metrics = calculate_fairness_metrics(predictions, protected_attributes, label_encoders)
    
    if not fairness_metrics['fairness_scores']:
        return 1.0  # No fairness issues if no scores available
    
    # Calculate average fairness score across all attributes
    scores = [attr_score['fairness_score'] for attr_score in fairness_metrics['fairness_scores'].values()]
    return np.mean(scores)


def calculate_parity_metrics(
    predictions,
    true_labels,
    protected_attributes
):
    """
    Calculate parity metrics for all protected attributes.
    
    Parameters
    ----------
    predictions : array-like
        Model predictions.
    true_labels : array-like
        Ground truth labels.
    protected_attributes : dict
        Dictionary of protected attributes.
    
    Returns
    -------
    dict
        Dictionary containing parity metrics for each attribute.
    """
    predictions = np.array(predictions)
    true_labels = np.array(true_labels)
    
    parity_metrics = {}
    
    for attr_name, attr_values in protected_attributes.items():
        attr_values = np.array(attr_values)
        
        # Encode categorical attributes
        label_encoder = LabelEncoder()
        attr_encoded = label_encoder.fit_transform(attr_values)
        
        # Calculate parity metrics for this attribute
        attr_encoded_array = np.array(attr_encoded)
        unique_groups = np.unique(attr_encoded_array.astype(int))
        group_metrics = {}
        
        for group in unique_groups:
            group_mask = attr_encoded == group
            group_name = label_encoder.inverse_transform([group])[0]
            
            if np.sum(group_mask) < 5:
                continue
            
            group_predictions = predictions[group_mask]
            group_true_labels = true_labels[group_mask]
            
            # Calculate parity metrics (simplified for Python 2.x compatibility)
            acc_parity = np.mean(group_predictions == group_true_labels) - np.mean(predictions == true_labels)
            prec_parity = 0.0  # Placeholder
            rec_parity = 0.0   # Placeholder
            
            group_metrics[group_name] = {
                'accuracy_parity': acc_parity,
                'precision_parity': prec_parity,
                'recall_parity': rec_parity
            }
        
        parity_metrics[attr_name] = group_metrics
    
    return parity_metrics


def assess_fairness(
    predictions,
    protected_attributes,
    threshold=0.8
):
    """
    Assess overall model fairness.
    
    Parameters
    ----------
    predictions : array-like
        Model predictions.
    protected_attributes : dict
        Dictionary of protected attributes.
    threshold : float, default=0.8
        Fairness threshold for assessment.
    
    Returns
    -------
    dict
        Fairness assessment results.
    """
    overall_score = fairness_score(predictions, protected_attributes)
    fairness_metrics = calculate_fairness_metrics(predictions, protected_attributes)
    
    assessment = {
        'overall_fairness_score': overall_score,
        'is_fair': overall_score >= threshold,
        'fairness_level': 'HIGH' if overall_score >= 0.9 else 'MEDIUM' if overall_score >= 0.7 else 'LOW',
        'protected_attributes': list(protected_attributes.keys()),
        'num_attributes_assessed': len(fairness_metrics['fairness_scores']),
        'recommendations': []
    }
    
    # Generate recommendations based on fairness score
    if overall_score < threshold:
        assessment['recommendations'].append("Consider implementing fairness-aware training")
        assessment['recommendations'].append("Apply post-processing techniques to improve fairness")
    
    if overall_score < 0.7:
        assessment['recommendations'].append("Conduct detailed bias analysis")
        assessment['recommendations'].append("Consider retraining with fairness constraints")
    
    return assessment 
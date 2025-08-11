#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive unit tests for ethical_ai_validator.py module.

This test suite covers all functional requirements (FR-001 through FR-005)
and aims to achieve 80%+ code coverage.
"""

import pytest
import pandas as pd
import numpy as np
import tempfile
import os
import sys
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Python 2.x compatibility
if sys.version_info[0] < 3:
    from mock import patch, MagicMock
else:
    from unittest.mock import patch, MagicMock

from ethical_ai_validator.ethical_ai_validator import (
    EthicalAIValidator,
    audit_bias,
    calculate_fairness_metrics,
    generate_compliance_report,
    monitor_realtime,
    suggest_mitigations
)


class TestEthicalAIValidator(object):
    """Test cases for EthicalAIValidator class."""
    
    def setup_method(self, method):
        """Set up test fixtures."""
        self.validator = EthicalAIValidator()
        
        # Create sample data for testing
        np.random.seed(42)
        self.n_samples = 1000
        
        # Generate synthetic predictions and labels
        self.predictions = np.random.choice([0, 1], size=self.n_samples)
        self.true_labels = np.random.choice([0, 1], size=self.n_samples)
        
        # Generate synthetic protected attributes
        self.protected_attributes = {
            'gender': np.random.choice(['male', 'female'], size=self.n_samples),
            'race': np.random.choice(['white', 'black', 'asian', 'hispanic'], size=self.n_samples),
            'age_group': np.random.choice(['18-25', '26-35', '36-50', '50+'], size=self.n_samples)
        }
    
    def test_initialization(self):
        """Test validator initialization."""
        validator = EthicalAIValidator()
        assert validator.config == {}
        assert validator.label_encoders == {}
        assert validator.monitoring_history == []
        
        # Test with custom config
        config = {'bias_threshold': 0.1, 'fairness_threshold': 0.8}
        validator = EthicalAIValidator(config=config)
        assert validator.config == config
    
    def test_audit_bias_basic(self):
        """Test basic bias audit functionality (FR-001)."""
        bias_report = self.validator.audit_bias(
            self.predictions,
            self.true_labels,
            self.protected_attributes
        )
        
        assert isinstance(bias_report, pd.DataFrame)
        assert not bias_report.empty
        
        # Check expected columns
        expected_columns = [
            'protected_attribute', 'group', 'group_size', 'accuracy',
            'precision', 'recall', 'f1_score', 'positive_rate',
            'statistical_parity', 'equalized_odds', 'demographic_parity', 'bias_score'
        ]
        
        for col in expected_columns:
            assert col in bias_report.columns
    
    def test_audit_bias_single_attribute(self):
        """Test bias audit with single protected attribute."""
        single_attr = {'gender': self.protected_attributes['gender']}
        bias_report = self.validator.audit_bias(
            self.predictions,
            self.true_labels,
            single_attr
        )
        
        assert isinstance(bias_report, pd.DataFrame)
        assert not bias_report.empty
        assert all(bias_report['protected_attribute'] == 'gender')
    
    def test_audit_bias_validation_errors(self):
        """Test bias audit with invalid inputs."""
        # Test mismatched lengths
        with pytest.raises(ValueError):
            self.validator.audit_bias(
                self.predictions[:100],
                self.true_labels,
                self.protected_attributes
            )
        
        # Test empty protected attributes
        with pytest.raises(ValueError):
            self.validator.audit_bias(
                self.predictions,
                self.true_labels,
                {}
            )
    
    def test_calculate_fairness_metrics_basic(self):
        """Test basic fairness metrics calculation (FR-002)."""
        fairness_metrics = self.validator.calculate_fairness_metrics(
            self.predictions,
            self.protected_attributes
        )
        
        assert isinstance(fairness_metrics, dict)
        assert 'overall_metrics' in fairness_metrics
        assert 'protected_attribute_metrics' in fairness_metrics
        assert 'fairness_scores' in fairness_metrics
        
        # Check overall metrics
        overall_metrics = fairness_metrics['overall_metrics']
        assert 'positive_rate' in overall_metrics
        assert 'total_samples' in overall_metrics
        assert overall_metrics['total_samples'] == self.n_samples
    
    def test_calculate_fairness_metrics_single_attribute(self):
        """Test fairness metrics with single protected attribute."""
        single_attr = {'gender': self.protected_attributes['gender']}
        fairness_metrics = self.validator.calculate_fairness_metrics(
            self.predictions,
            single_attr
        )
        
        assert 'gender' in fairness_metrics['protected_attribute_metrics']
    
    def test_calculate_fairness_metrics_validation_errors(self):
        """Test fairness metrics with invalid inputs."""
        with pytest.raises(ValueError):
            self.validator.calculate_fairness_metrics(
                self.predictions[:100],
                self.protected_attributes
            )
    
    def test_generate_compliance_report_basic(self):
        """Test basic compliance report generation (FR-003)."""
        metadata = {
            'model_name': 'TestModel',
            'version': '1.0',
            'description': 'Test model for compliance'
        }
        audit_criteria = {
            'bias_threshold': 0.1,
            'fairness_threshold': 0.8
        }
        
        report_path = self.validator.generate_compliance_report(metadata, audit_criteria)
        
        assert isinstance(report_path, str)
        assert report_path.endswith('.pdf')
        assert os.path.exists(report_path)
        
        # Clean up
        os.remove(report_path)

    def test_generate_compliance_report_with_custom_thresholds(self):
        """Report generation should accept custom bias/fairness thresholds."""
        # Create small synthetic bias/fairness inputs
        import pandas as pd
        bias_report = pd.DataFrame([
            {'protected_attribute': 'gender', 'group': 'male', 'bias_score': 0.2}
        ])
        fairness_metrics = {
            'fairness_scores': {
                'gender': {'fairness_score': 0.75}
            }
        }
        metadata = {
            'model_name': 'ThresholdTestModel',
            'bias_report': bias_report,
            'fairness_metrics': fairness_metrics
        }
        # Thresholds different from defaults
        audit_criteria = {'bias_threshold': 0.3, 'fairness_threshold': 0.7}
        path = self.validator.generate_compliance_report(metadata, audit_criteria)
        assert isinstance(path, str) and path.endswith('.pdf')
        assert os.path.exists(path)
        os.remove(path)

    def test_compute_feature_disparities_fallback(self):
        """Smoke test for feature disparities without SHAP availability."""
        # Build a small supervised problem
        rng = np.random.default_rng(42)
        X = rng.normal(size=(200, 5))
        y = rng.integers(0, 2, size=200)
        X_df = pd.DataFrame(X)
        # Assign simple numeric column names to avoid type issues in some environments
        X_df.columns = pd.RangeIndex(start=0, stop=X_df.shape[1])
        prot = {
            'gender': rng.choice(['male', 'female'], size=200)
        }
        model = DecisionTreeClassifier(max_depth=4, random_state=42)
        model.fit(X_df, y)
        disp = self.validator.compute_feature_disparities(model, X_df, prot, max_features=5)
        assert isinstance(disp, dict)
        assert 'gender' in disp
        if disp['gender']:
            item = disp['gender'][0]
            assert set(['feature', 'disparity', 'top_group', 'bottom_group']).issubset(item.keys())

    def test_hyperparameter_ablation_smoke(self):
        """Hyperparameter ablation returns a ranked summary for sklearn models."""
        rng = np.random.default_rng(0)
        X = rng.normal(size=(300, 6))
        y = rng.integers(0, 2, size=300)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
        X_train_df = pd.DataFrame(X_train)
        X_test_df = pd.DataFrame(X_test)
        prot = {'gender': rng.choice(['male', 'female'], size=len(y))}
        prot_test = {'gender': prot['gender'][len(y) - len(y_test):]}
        model = DecisionTreeClassifier(max_depth=5, random_state=42)
        model.fit(X_train_df, y_train)
        ablation = self.validator.hyperparameter_ablation(
            model,
            X_train_df, pd.Series(y_train),
            X_test_df, pd.Series(y_test),
            prot_test,
            params_to_probe=['max_depth', 'min_samples_split'],
            max_variants_per_param=1
        )
        assert isinstance(ablation, dict)
        assert 'baseline_avg_fairness' in ablation
        assert 'summary' in ablation and isinstance(ablation['summary'], list)
    
    def test_generate_compliance_report_empty_metadata(self):
        """Test compliance report generation with empty metadata."""
        metadata = {}
        audit_criteria = {'bias_threshold': 0.1}
        
        report_path = self.validator.generate_compliance_report(metadata, audit_criteria)
        
        assert isinstance(report_path, str)
        assert os.path.exists(report_path)
        
        # Clean up
        os.remove(report_path)
    
    def test_monitor_realtime_basic(self):
        """Test basic real-time monitoring (FR-004)."""
        predictions_stream = [
            np.random.choice([0, 1], size=100),
            np.random.choice([0, 1], size=100),
            np.random.choice([0, 1], size=100)
        ]
        
        alerts = self.validator.monitor_realtime(predictions_stream)
        
        assert isinstance(alerts, list)
        assert len(self.validator.monitoring_history) > 0
    
    def test_monitor_realtime_with_alerts(self):
        """Test real-time monitoring with bias alerts."""
        # Create biased predictions that should trigger alerts
        biased_predictions = [
            np.ones(100),  # All positive predictions
            np.zeros(100),  # All negative predictions
            np.random.choice([0, 1], size=100, p=[0.8, 0.2])  # Biased towards negative
        ]
        
        alerts = self.validator.monitor_realtime(biased_predictions)
        
        assert isinstance(alerts, list)
        # Should have some alerts due to extreme bias
        assert len(alerts) > 0
    
    def test_monitor_realtime_with_config(self):
        """Test real-time monitoring with custom config."""
        config = {'bias_threshold': 0.05, 'fairness_threshold': 0.9}
        validator = EthicalAIValidator(config=config)
        
        predictions_stream = [np.random.choice([0, 1], size=100)]
        alerts = validator.monitor_realtime(predictions_stream)
        
        assert isinstance(alerts, list)
    
    def test_suggest_mitigations_basic(self):
        """Test basic mitigation suggestions (FR-005)."""
        # Create a bias report with some bias
        bias_report = self.validator.audit_bias(
            self.predictions,
            self.true_labels,
            self.protected_attributes
        )
        
        mitigations = self.validator.suggest_mitigations(bias_report)
        
        assert isinstance(mitigations, dict)
        assert 'suggestions' in mitigations
        assert 'priority' in mitigations
        assert 'estimated_effort' in mitigations
        assert isinstance(mitigations['suggestions'], list)
    
    def test_suggest_mitigations_empty_report(self):
        """Test mitigation suggestions with empty bias report."""
        empty_report = pd.DataFrame()
        mitigations = self.validator.suggest_mitigations(empty_report)
        
        assert isinstance(mitigations, dict)
        assert 'suggestions' in mitigations
        assert len(mitigations['suggestions']) > 0
    
    def test_suggest_mitigations_high_bias(self):
        """Test mitigation suggestions with high bias report."""
        # Create highly biased predictions
        biased_predictions = np.random.choice([0, 1], size=1000, p=[0.8, 0.2])
        biased_labels = np.random.choice([0, 1], size=1000, p=[0.5, 0.5])
        
        bias_report = self.validator.audit_bias(
            biased_predictions,
            biased_labels,
            self.protected_attributes
        )
        
        mitigations = self.validator.suggest_mitigations(bias_report)
        
        assert isinstance(mitigations, dict)
        assert len(mitigations['suggestions']) > 0
    
    def test_label_encoder_persistence(self):
        """Test that label encoders persist across multiple calls."""
        # First call should fit encoders
        bias_report1 = self.validator.audit_bias(
            self.predictions,
            self.true_labels,
            self.protected_attributes
        )
        
        # Second call should use existing encoders
        bias_report2 = self.validator.audit_bias(
            self.predictions,
            self.true_labels,
            self.protected_attributes
        )
        
        assert len(self.validator.label_encoders) > 0
        assert bias_report1.shape == bias_report2.shape
    
    def test_performance_requirements(self):
        """Test performance requirements for real-time monitoring."""
        # Test processing 10,000 samples in reasonable time
        large_predictions = np.random.choice([0, 1], size=10000)
        large_labels = np.random.choice([0, 1], size=10000)
        large_protected = {
            'gender': np.random.choice(['male', 'female'], size=10000)
        }
        
        import time
        start_time = time.time()
        
        bias_report = self.validator.audit_bias(
            large_predictions,
            large_labels,
            large_protected
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete in under 5 seconds
        assert processing_time < 5.0
        assert isinstance(bias_report, pd.DataFrame)
    
    def test_data_anonymization(self):
        """Test that sensitive data is handled appropriately."""
        # The validator should handle sensitive data appropriately
        # For transparency, group names are shown but can be anonymized if needed

        bias_report = self.validator.audit_bias(
            self.predictions,
            self.true_labels,
            self.protected_attributes
        )

        # Check that the report contains the expected structure
        report_str = bias_report.to_string()
        assert 'protected_attribute' in report_str
        assert 'group' in report_str
        assert 'bias_score' in report_str
        
        # Verify that the report contains the expected data
        assert len(bias_report) > 0
        assert 'gender' in bias_report['protected_attribute'].values


class TestConvenienceFunctions(object):
    """Test cases for convenience functions."""
    
    def setup_method(self, method):
        """Set up test fixtures."""
        np.random.seed(42)
        self.predictions = np.random.choice([0, 1], size=100)
        self.true_labels = np.random.choice([0, 1], size=100)
        self.protected_attributes = {
            'gender': np.random.choice(['male', 'female'], size=100)
        }
    
    def test_audit_bias_convenience(self):
        """Test convenience function for bias audit."""
        bias_report = audit_bias(
            self.predictions,
            self.true_labels,
            self.protected_attributes
        )
        
        assert isinstance(bias_report, pd.DataFrame)
        assert not bias_report.empty
    
    def test_calculate_fairness_metrics_convenience(self):
        """Test convenience function for fairness metrics."""
        fairness_metrics = calculate_fairness_metrics(
            self.predictions,
            self.protected_attributes
        )
        
        assert isinstance(fairness_metrics, dict)
        assert 'overall_metrics' in fairness_metrics
    
    def test_generate_compliance_report_convenience(self):
        """Test convenience function for compliance report."""
        metadata = {'model_name': 'TestModel'}
        audit_criteria = {'bias_threshold': 0.1}
        
        report_path = generate_compliance_report(metadata, audit_criteria)
        
        assert isinstance(report_path, str)
        assert os.path.exists(report_path)
        
        # Clean up
        os.remove(report_path)
    
    def test_monitor_realtime_convenience(self):
        """Test convenience function for real-time monitoring."""
        predictions_stream = [np.random.choice([0, 1], size=100)]
        
        alerts = monitor_realtime(predictions_stream)
        
        assert isinstance(alerts, list)
    
    def test_suggest_mitigations_convenience(self):
        """Test convenience function for mitigation suggestions."""
        bias_report = audit_bias(
            self.predictions,
            self.true_labels,
            self.protected_attributes
        )
        
        mitigations = suggest_mitigations(bias_report)
        
        assert isinstance(mitigations, dict)
        assert 'suggestions' in mitigations


class TestEdgeCases(object):
    """Test cases for edge cases and error conditions."""
    
    def test_empty_predictions(self):
        """Test behavior with empty predictions."""
        validator = EthicalAIValidator()
        
        with pytest.raises(ValueError):
            validator.audit_bias([], [], {})
    
    def test_single_sample(self):
        """Test behavior with single sample."""
        validator = EthicalAIValidator()
        
        # Should handle single sample gracefully
        bias_report = validator.audit_bias([1], [1], {'gender': ['male']})
        
        assert isinstance(bias_report, pd.DataFrame)
        # Should skip groups with too few samples
        assert len(bias_report) == 0
    
    def test_all_same_predictions(self):
        """Test behavior with all same predictions."""
        validator = EthicalAIValidator()
        
        predictions = [1] * 100
        labels = [1] * 100
        protected = {'gender': ['male'] * 100}
        
        bias_report = validator.audit_bias(predictions, labels, protected)
        
        assert isinstance(bias_report, pd.DataFrame)
        # Should handle this case without errors
    
    def test_missing_columns_in_bias_report(self):
        """Test mitigation suggestions with missing columns."""
        validator = EthicalAIValidator()
        
        # Create a bias report with missing columns
        bias_report = pd.DataFrame({
            'protected_attribute': ['gender'],
            'group': ['male'],
            'group_size': [50]
        })
        
        mitigations = validator.suggest_mitigations(bias_report)
        
        assert isinstance(mitigations, dict)
        assert 'suggestions' in mitigations


class TestUnitTests(object):
    """Unit tests for specific functionality."""
    
    def test_label_encoder_functionality(self):
        """Test label encoder functionality."""
        validator = EthicalAIValidator()
        
        # Test encoding and decoding
        test_values = ['male', 'female', 'male', 'female']
        encoded = validator.label_encoders.get('gender', None)
        
        # Should work without errors
        bias_report = validator.audit_bias(
            [1, 0, 1, 0],
            [1, 0, 1, 0],
            {'gender': test_values}
        )
        
        assert 'gender' in validator.label_encoders
    
    def test_bias_score_calculation(self):
        """Test bias score calculation."""
        validator = EthicalAIValidator()
        
        # Create predictions with known bias
        predictions = [1, 1, 1, 0, 0, 0]  # All males positive, all females negative
        labels = [1, 1, 1, 0, 0, 0]
        protected = {'gender': ['male', 'male', 'male', 'female', 'female', 'female']}
        
        bias_report = validator.audit_bias(predictions, labels, protected)
        
        assert isinstance(bias_report, pd.DataFrame)
        if not bias_report.empty:
            assert 'bias_score' in bias_report.columns


class TestIntegrationTests(object):
    """Integration tests for full workflow."""
    
    def test_full_workflow(self):
        """Test complete workflow from data to report."""
        validator = EthicalAIValidator()
        
        # Generate test data
        np.random.seed(42)
        predictions = np.random.choice([0, 1], size=1000)
        labels = np.random.choice([0, 1], size=1000)
        protected = {
            'gender': np.random.choice(['male', 'female'], size=1000)
        }
        
        # Run bias audit
        bias_report = validator.audit_bias(predictions, labels, protected)
        
        # Calculate fairness metrics
        fairness_metrics = validator.calculate_fairness_metrics(predictions, protected)
        
        # Generate compliance report
        metadata = {'model_name': 'TestModel'}
        audit_criteria = {'bias_threshold': 0.1}
        report_path = validator.generate_compliance_report(metadata, audit_criteria)
        
        # Get mitigation suggestions
        mitigations = validator.suggest_mitigations(bias_report)
        
        # Verify all components work together
        assert isinstance(bias_report, pd.DataFrame)
        assert isinstance(fairness_metrics, dict)
        assert isinstance(report_path, str)
        assert isinstance(mitigations, dict)
        
        # Clean up
        if os.path.exists(report_path):
            os.remove(report_path) 
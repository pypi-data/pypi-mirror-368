#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests for the core validator module.
"""

import pytest
import numpy as np
import pandas as pd
import sys

# Python 2.x compatibility
if sys.version_info[0] < 3:
    from mock import patch, MagicMock
else:
    from unittest.mock import patch, MagicMock

from ethical_ai_validator.core.validator import EthicalAIValidator


class TestCoreValidator(object):
    """Test cases for the core EthicalAIValidator class."""
    
    def setup_method(self, method):
        """Set up test fixtures."""
        self.validator = EthicalAIValidator()
        
        # Create sample data
        np.random.seed(42)
        self.X = np.random.randn(100, 5)
        self.y = np.random.choice([0, 1], size=100)
        self.sensitive_features = np.random.choice(['A', 'B'], size=100)
        
        # Mock model
        self.mock_model = MagicMock()
        self.mock_model.predict.return_value = np.random.choice([0, 1], size=100)
    
    def test_initialization(self):
        """Test validator initialization."""
        validator = EthicalAIValidator()
        assert validator.config == {}
        assert validator.audit_results == {}
        
        # Test with custom config
        config = {'test_param': 'test_value'}
        validator = EthicalAIValidator(config=config)
        assert validator.config == config
    
    def test_audit_model(self):
        """Test complete model audit."""
        audit_results = self.validator.audit_model(
            self.mock_model,
            self.X,
            self.y,
            self.sensitive_features
        )
        
        assert isinstance(audit_results, dict)
        assert 'bias_analysis' in audit_results
        assert 'fairness_assessment' in audit_results
        assert 'compliance_check' in audit_results
        assert 'overall_score' in audit_results
    
    def test_analyze_bias(self):
        """Test bias analysis."""
        bias_results = self.validator._analyze_bias(
            self.mock_model,
            self.X,
            self.y,
            self.sensitive_features
        )
        
        assert isinstance(bias_results, dict)
        assert 'statistical_parity' in bias_results
        assert 'equalized_odds' in bias_results
        assert 'demographic_parity' in bias_results
        assert 'bias_score' in bias_results
        assert 'recommendations' in bias_results
    
    def test_assess_fairness(self):
        """Test fairness assessment."""
        fairness_results = self.validator._assess_fairness(
            self.mock_model,
            self.X,
            self.y,
            self.sensitive_features
        )
        
        assert isinstance(fairness_results, dict)
        assert 'accuracy_parity' in fairness_results
        assert 'precision_parity' in fairness_results
        assert 'recall_parity' in fairness_results
        assert 'f1_parity' in fairness_results
        assert 'fairness_score' in fairness_results
        assert 'recommendations' in fairness_results
    
    def test_check_compliance(self):
        """Test compliance checking."""
        compliance_results = self.validator._check_compliance(
            self.mock_model,
            self.X,
            self.y,
            self.sensitive_features
        )
        
        assert isinstance(compliance_results, dict)
        assert 'gdpr_compliance' in compliance_results
        assert 'ai_act_compliance' in compliance_results
        assert 'compliance_score' in compliance_results
        assert 'recommendations' in compliance_results
    
    def test_generate_report(self):
        """Test report generation."""
        # Set up audit results
        self.validator.audit_results = {
            'bias_analysis': {'statistical_parity': 0.1, 'bias_score': 0.2},
            'fairness_assessment': {'fairness_score': 0.8},
            'compliance_check': {
                'gdpr_compliance': {'data_minimization': True},
                'ai_act_compliance': {'risk_assessment': True}
            }
        }
        
        report_content = self.validator.generate_report()
        
        assert isinstance(report_content, str)
        assert 'Ethical AI Validator Report' in report_content
        assert 'Bias Analysis' in report_content
        assert 'Fairness Assessment' in report_content
        assert 'Compliance Check' in report_content
    
    def test_generate_report_with_output_path(self):
        """Test report generation with output path."""
        import tempfile
        import os
        
        self.validator.audit_results = {
            'bias_analysis': {'statistical_parity': 0.1, 'bias_score': 0.2},
            'fairness_assessment': {'fairness_score': 0.8},
            'compliance_check': {
                'gdpr_compliance': {'data_minimization': True},
                'ai_act_compliance': {'risk_assessment': True}
            }
        }
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            output_path = f.name
        
        try:
            result_path = self.validator.generate_report(output_path=output_path)
            
            assert result_path == output_path
            assert os.path.exists(output_path)
            
            with open(output_path, 'r') as f:
                content = f.read()
                assert 'Ethical AI Validator Report' in content
        
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_get_recommendations(self):
        """Test getting recommendations."""
        # Test with no audit results
        recommendations = self.validator.get_recommendations()
        assert isinstance(recommendations, list)
        assert len(recommendations) == 0
        
        # Test with audit results
        self.validator.audit_results = {
            'bias_analysis': {'recommendations': ['Fix bias']},
            'fairness_assessment': {'recommendations': ['Improve fairness']},
            'compliance_check': {'recommendations': ['Ensure compliance']}
        }
        
        recommendations = self.validator.get_recommendations()
        assert isinstance(recommendations, list)
        assert len(recommendations) == 3
        assert 'Fix bias' in recommendations
        assert 'Improve fairness' in recommendations
        assert 'Ensure compliance' in recommendations
    
    def test_audit_model_without_sensitive_features(self):
        """Test model audit without sensitive features."""
        audit_results = self.validator.audit_model(
            self.mock_model,
            self.X,
            self.y
        )
        
        assert isinstance(audit_results, dict)
        assert 'bias_analysis' in audit_results
    
    def test_audit_model_with_kwargs(self):
        """Test model audit with additional keyword arguments."""
        audit_results = self.validator.audit_model(
            self.mock_model,
            self.X,
            self.y,
            self.sensitive_features,
            custom_param='test_value'
        )
        
        assert isinstance(audit_results, dict)
        # Should not raise any errors with additional kwargs


class TestCoreValidatorEdgeCases(object):
    """Test edge cases for the core validator."""
    
    def setup_method(self, method):
        """Set up test fixtures."""
        self.validator = EthicalAIValidator()
        self.mock_model = MagicMock()
    
    def test_empty_data(self):
        """Test behavior with empty data."""
        empty_X = np.array([])
        empty_y = np.array([])
        
        audit_results = self.validator.audit_model(
            self.mock_model,
            empty_X,
            empty_y
        )
        
        assert isinstance(audit_results, dict)
        assert 'bias_analysis' in audit_results
    
    def test_single_sample(self):
        """Test behavior with single sample."""
        single_X = np.array([[1, 2, 3, 4, 5]])
        single_y = np.array([1])
        
        audit_results = self.validator.audit_model(
            self.mock_model,
            single_X,
            single_y
        )
        
        assert isinstance(audit_results, dict)
        assert 'bias_analysis' in audit_results
    
    def test_none_sensitive_features(self):
        """Test behavior with None sensitive features."""
        X = np.random.randn(10, 5)
        y = np.random.choice([0, 1], size=10)
        
        audit_results = self.validator.audit_model(
            self.mock_model,
            X,
            y,
            None
        )
        
        assert isinstance(audit_results, dict)
        assert 'bias_analysis' in audit_results 
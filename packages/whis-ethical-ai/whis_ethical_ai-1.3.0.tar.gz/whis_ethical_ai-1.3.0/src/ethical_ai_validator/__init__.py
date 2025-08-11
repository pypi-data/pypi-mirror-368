"""
Ethical AI Validator

A comprehensive Python package for ethical AI validation and auditing,
designed to detect bias, assess fairness, and ensure compliance with
regulations like GDPR and AI Act.

This package provides a complete solution for organizations seeking to
ensure their AI systems are fair, unbiased, and compliant with regulatory
requirements. It implements all five functional requirements (FR-001 to FR-005)
for comprehensive ethical AI validation.

Key Features:
- Bias Detection: Statistical parity, equalized odds, individual fairness
- Fairness Assessment: Demographic parity, equal opportunity, predictive rate parity
- Compliance Reporting: Automated GDPR and AI Act compliance reports
- Real-time Monitoring: Continuous bias detection with automated alerts
- Mitigation Suggestions: Intelligent recommendations for bias reduction

The package is designed to work with Python 2.7+ and Python 3.x, making it
compatible with a wide range of environments and existing codebases.

Author: WHIS (muhammadabdullahinbox@gmail.com)
Version: 1.3.0
License: MIT
Repository: https://github.com/whis-19/ethical-ai
Documentation: https://whis-19.github.io/ethical-ai/

Example:
    >>> from ethical_ai_validator import EthicalAIValidator
    >>> validator = EthicalAIValidator()
    >>> bias_report = validator.audit_bias(predictions, labels, protected_attrs)
    >>> fairness_metrics = validator.calculate_fairness_metrics(predictions, protected_attrs)
    >>> compliance_report = validator.generate_compliance_report(metadata, criteria)
"""

__version__ = "1.3.0"
__author__ = "Ethical AI Team"
__email__ = "muhammadabdullahinbox@gmail.com"

# Import main classes and functions
from .ethical_ai_validator import (
    EthicalAIValidator,
    audit_bias,
    calculate_fairness_metrics,
    generate_compliance_report,
    monitor_realtime,
    suggest_mitigations
)

# Import convenience functions
from .ethical_ai_validator import (
    audit_bias as audit_bias_fn,
    calculate_fairness_metrics as calculate_fairness_metrics_fn,
    generate_compliance_report as generate_compliance_report_fn,
    monitor_realtime as monitor_realtime_fn,
    suggest_mitigations as suggest_mitigations_fn
)

__all__ = [
    "EthicalAIValidator",
    "audit_bias",
    "calculate_fairness_metrics", 
    "generate_compliance_report",
    "monitor_realtime",
    "suggest_mitigations",
    # Convenience functions
    "audit_bias_fn",
    "calculate_fairness_metrics_fn",
    "generate_compliance_report_fn",
    "monitor_realtime_fn",
    "suggest_mitigations_fn"
] 
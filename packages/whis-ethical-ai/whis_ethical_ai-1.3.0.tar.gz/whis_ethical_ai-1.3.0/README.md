# Ethical AI (eai)

A comprehensive Python package for ethical AI validation and auditing, designed with a modular structure similar to scikit-learn.

## Features

- **Bias Detection**: Identify and measure bias in AI models across different demographic groups
- **Fairness Assessment**: Evaluate model fairness using various metrics and statistical tests
- **GDPR Compliance**: Check for data privacy and consent requirements
- **AI Act Compliance**: Validate compliance with EU AI Act regulations
- **Comprehensive Reporting**: Generate detailed audit reports with visualizations
- **Multiple Model Support**: Works with scikit-learn, TensorFlow, and PyTorch models

## Installation

### From PyPI (Recommended)

```bash
pip install whis-ethical-ai
```

### From Source

```bash
git clone https://github.com/whis-19/ethical-ai.git
cd ethical-ai
pip install -e .
```

## Quick Start

### Basic Usage

```python
from ethical_ai_validator import EthicalAIValidator
import numpy as np
import pandas as pd

# Create sample data
predictions = np.array([1, 0, 1, 0, 1, 0, 1, 1, 0, 1])
true_labels = np.array([1, 0, 1, 1, 0, 0, 1, 1, 0, 1])
protected_attributes = {
    'gender': ['male', 'female', 'male', 'female', 'male', 'female', 'male', 'female', 'male', 'female'],
    'race': ['white', 'black', 'white', 'black', 'white', 'black', 'white', 'black', 'white', 'black']
}

# Initialize validator
validator = EthicalAIValidator()

# Detect bias
bias_report = validator.audit_bias(predictions, true_labels, protected_attributes)
print("Bias Report:")
print(bias_report)

# Calculate fairness metrics
fairness_metrics = validator.calculate_fairness_metrics(predictions, protected_attributes)
print("Fairness Metrics:")
print(fairness_metrics)
```

### Advanced Usage

```python
# Generate compliance report
metadata = {'model_name': 'RandomForest', 'version': '1.0'}
audit_criteria = {'bias_threshold': 0.1, 'fairness_threshold': 0.8}
report_path = validator.generate_compliance_report(metadata, audit_criteria)

# Real-time monitoring
predictions_stream = [
    np.random.choice([0, 1], size=1000),
    np.random.choice([0, 1], size=1000)
]
alerts = validator.monitor_realtime(predictions_stream)

# Suggest mitigations
mitigations = validator.suggest_mitigations(bias_report)
print("Mitigation Suggestions:")
print(mitigations)
```

### Using Convenience Functions

```python
from ethical_ai_validator import (
    audit_bias, calculate_fairness_metrics, generate_compliance_report,
    monitor_realtime, suggest_mitigations
)

# Direct function calls
bias_report = audit_bias(predictions, true_labels, protected_attributes)
fairness_metrics = calculate_fairness_metrics(predictions, protected_attributes)
report_path = generate_compliance_report(metadata, audit_criteria)
alerts = monitor_realtime(predictions_stream)
mitigations = suggest_mitigations(bias_report)
```

## Development Setup

### Prerequisites

- Python 2.7 or higher
- Git
- pip

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/whis-19/ethical-ai.git
cd ethical-ai
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e .[dev]
   ```

4. **Run tests**
   ```bash
   pytest
   ```

5. **Check code coverage**
   ```bash
   pytest --cov=ethical_ai_validator --cov-report=html
   ```

### VS Code Setup

1. Install recommended extensions:
   - Python (ms-python.python)
   - Pylance (ms-python.vscode-pylance)
   - Python Test Explorer (littlefoxteam.vscode-python-test-adapter)

2. Configure settings in `.vscode/settings.json` (already included)

## Project Structure

```
ethical-ai/
├── src/
│   └── ethical_ai_validator/
│       ├── __init__.py
│       ├── core/
│       ├── validators/
│       ├── metrics/
│       └── reporting/
├── tests/
├── docs/
├── requirements.txt
├── pyproject.toml
├── README.md
└── SETUP.md
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ethical_ai_validator --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Style

This project uses:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking
- **Pre-commit** hooks for automated checks

Run pre-commit hooks:
```bash
pre-commit install
pre-commit run --all-files
```

## Documentation

- [User Guide](https://whis-19.github.io/ethical-ai/)
- [Contributing Guide](CONTRIBUTING.md)

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for complete details.

### License Summary

**✅ Permitted:**
- Commercial use
- Modification and distribution
- Private and public use
- Patent use

**❌ Limitations:**
- No warranty provided
- No liability for damages

**📋 Requirements:**
- Include copyright notice
- Include license text
- State any modifications

### License Compatibility

The MIT License is compatible with:
- GPL (v2 and v3)
- Apache License 2.0
- BSD Licenses
- Most other open-source licenses

This makes it suitable for use in both open-source and commercial projects.

### Third-Party Dependencies

All dependencies are BSD-3-Clause licensed and compatible with MIT:
- numpy, pandas, scikit-learn, reportlab

For detailed license information, see the [LICENSE](LICENSE) file.

## Support

- **Issues**: [GitHub Issues](https://github.com/whis-19/ethical-ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/whis-19/ethical-ai/discussions)
- **Email**: muhammadabdullahinbox@gmail.com

## Acknowledgments

- Inspired by the need for ethical AI development
- Built with support from the open-source community
- Special thanks to contributors and maintainers ([WHIS-19](https://github.com/whis-19/))
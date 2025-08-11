# Changelog

All notable changes to this project will be documented in this file.

## [1.3.0] - 2025-08-11
### Added
- Scenario and hyperparameters sections in the generated PDF report, including an automatic summary of likely contributing factors based on metrics and parameter heuristics.
- CLI flags `--scenario` and `--hyperparameters` (JSON) to display scenario and hyperparameters alongside metrics output, and to include them in a generated report when `--output` is provided.

### Changed
- Bumped package version to 1.3.0 across code and packaging metadata.

### Notes
- This is a compatibility-preserving enhancement; existing report generation calls continue to work. Provide `metadata['scenario']` and `metadata['hyperparameters']` to populate the new sections.

---

## [1.1.0] - 2025-08-08
### Added
- Support for specifying `output_path` in `generate_compliance_report`, allowing direct saving to a custom location and automatic directory creation.
- Modal popup in `index.html` to display experiment PDF reports from the GitHub repo, with embedded PDF viewer.
- Adaptive, professional PDF report tables and improved visual design.

### Changed
- Compliance report now includes actual bias/fairness results, realistic compliance status, and dynamic recommendations.
- Version updated to 1.1.0 in all relevant files (`LICENSE`, `README.md`, `pyproject.toml`, `setup.py`, etc).

### Fixed
- Reports now save directly to the correct folder without needing to move files after generation.
- Improved error handling for PDF saving (clear error if save fails).

---

## [1.0.0] - Initial release
- Initial implementation of Ethical AI Validator with bias/fairness/compliance audit and reporting.
 
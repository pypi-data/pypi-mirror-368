#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Additional tests to improve coverage:
- CLI main with scenario/hyperparameters and with output path
- eai.compliance, eai.fairness, eai.monitoring modules
"""

import os
import sys
import json
import tempfile
import numpy as np
import pandas as pd
import pytest

# Ensure src on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ethical_ai_validator.cli import main as cli_main  # type: ignore
from ethical_ai_validator.ethical_ai_validator import EthicalAIValidator  # type: ignore
from eai.compliance import (
    generate_compliance_report as eai_generate_report,
    check_gdpr_compliance,
    check_ai_act_compliance,
    generate_compliance_summary,
)  # type: ignore
from eai.fairness import calculate_fairness_metrics as eai_calc_fairness  # type: ignore
from eai.monitoring import monitor_realtime as eai_monitor  # type: ignore


class TestCLI:
    def test_cli_prints_scenario_and_hyperparameters(self, monkeypatch, capsys):
        # Simulate: whis-ethical-ai --scenario X --hyperparameters '{"a":1}' with verbose
        argv = [
            'prog',
            '--scenario', 'Scenario-X',
            '--hyperparameters', json.dumps({'a': 1, 'b': 'c'}),
            '--verbose'
        ]
        monkeypatch.setattr(sys, 'argv', argv)
        exit_code = cli_main()
        assert exit_code == 0
        out = capsys.readouterr().out
        assert 'Scenario: Scenario-X' in out
        assert 'Hyperparameters:' in out
        assert 'Ethical AI Validator initialized successfully' in out

    def test_cli_handles_invalid_hyperparameters_json(self, monkeypatch, capsys):
        argv = [
            'prog', '--hyperparameters', '{invalid-json:}', '--scenario', 'Y']
        monkeypatch.setattr(sys, 'argv', argv)
        exit_code = cli_main()
        assert exit_code == 0
        out = capsys.readouterr().out
        # Should not crash and should still print the CLI header
        assert 'Ethical AI Validator CLI' in out

    def test_cli_generates_report_with_output(self, monkeypatch, tmp_path, capsys):
        out_path = tmp_path / 'cli_report.pdf'
        argv = [
            'prog',
            '--scenario', 'CLI-Scenario',
            '--hyperparameters', json.dumps({'max_depth': 5}),
            '--output', str(out_path)
        ]
        monkeypatch.setattr(sys, 'argv', argv)
        exit_code = cli_main()
        assert exit_code == 0
        assert out_path.exists()

    def test_cli_version_flag(self, monkeypatch):
        # The version action raises SystemExit; assert it exits cleanly
        argv = ['prog', '--version']
        monkeypatch.setattr(sys, 'argv', argv)
        with pytest.raises(SystemExit) as exc:
            cli_main()
        assert exc.value.code == 0


class TestEaiModules:
    def test_eai_compliance_report_and_checks(self):
        metadata = {'model_name': 'EAI-Model', 'version': '1.0'}
        criteria = {'bias_threshold': 0.1, 'fairness_threshold': 0.8}
        path = eai_generate_report(metadata, criteria)
        assert isinstance(path, str) and path.endswith('.pdf')
        assert os.path.exists(path)
        os.remove(path)

        gdpr = check_gdpr_compliance({'model': 'x'})
        ai = check_ai_act_compliance({'model': 'x'})
        assert isinstance(gdpr, dict) and isinstance(ai, dict)
        summary = generate_compliance_summary(gdpr, ai)
        assert 'overall_compliance_score' in summary
        assert 'recommendations' in summary

    def test_eai_fairness_and_monitoring(self):
        preds = [0, 1, 0, 1, 1, 0]
        protected = {'gender': ['m', 'f', 'm', 'f', 'm', 'f']}
        fairness = eai_calc_fairness(preds, protected)
        assert isinstance(fairness, dict)
        assert 'fairness_scores' in fairness

        alerts = eai_monitor([[0, 1, 0, 1], [1, 1, 1, 1]])
        assert isinstance(alerts, list)
        assert all(isinstance(a, dict) for a in alerts)

    def test_realtime_monitor_reset_and_history(self):
        from eai.monitoring import RealTimeMonitor
        monitor = RealTimeMonitor({'bias_threshold': 0.05})
        _ = monitor.monitor([[1, 1, 1], [0, 0, 0]])
        hist = monitor.get_history()
        assert isinstance(hist, list) and len(hist) > 0
        monitor.reset()
        assert monitor.get_history() == []


class TestValidatorFeatureDisparities:
    def test_report_with_feature_disparities_section(self, tmp_path):
        # Minimal smoke test: pass a fabricated feature_disparities structure
        validator = EthicalAIValidator()
        metadata = {
            'model_name': 'FD-Model',
            'feature_disparities': {
                'gender': [
                    {'feature': 'f1', 'disparity': 0.5, 'top_group': 'm', 'bottom_group': 'f'}
                ]
            }
        }
        criteria = {'bias_threshold': 0.1, 'fairness_threshold': 0.8}
        out_file = tmp_path / 'fd_report.pdf'
        path = validator.generate_compliance_report(metadata, criteria, output_path=str(out_file))
        assert os.path.exists(path)


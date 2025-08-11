"""
Basic integration tests for GitHub Actions AI Analyzer
"""

from pathlib import Path

import pytest


def test_integration_directory_exists():
    """Test that integration test directory exists"""
    assert Path("tests/integration").exists()


def test_basic_import():
    """Test that main modules can be imported"""
    try:
        # Import modules to test they exist
        # Note: Import is used for testing module existence
        import github_actions_ai_analyzer.core.analyzer  # noqa: F401

        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import modules: {e}")


def test_analyzer_initialization():
    """Test that analyzer can be initialized"""
    from github_actions_ai_analyzer.core.analyzer import GitHubActionsAnalyzer

    analyzer = GitHubActionsAnalyzer()
    assert analyzer is not None
    assert hasattr(analyzer, "analyze_log_file")

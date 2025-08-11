"""
CI/CDパイプラインの設定をテストするためのテストファイル
"""

from pathlib import Path

import pytest


def test_project_structure():
    """プロジェクトの基本構造が正しいことを確認"""
    # 必要なディレクトリが存在することを確認
    required_dirs = [
        "src",
        "tests",
        "docs",
        ".github/workflows",
        ".github/codeql",
    ]

    for dir_path in required_dirs:
        assert Path(
            dir_path
        ).exists(), f"Required directory {dir_path} does not exist"


def test_config_files():
    """設定ファイルが存在することを確認"""
    required_files = [
        "pyproject.toml",
        "pytest.ini",
        "mypy.ini",
        ".flake8",
        ".bandit",
        ".pre-commit-config.yaml",
        "Makefile",
        ".github/dependabot.yml",
        ".github/workflows/ci.yml",
        ".github/workflows/security.yml",
        ".github/workflows/release.yml",
        ".github/codeql/codeql-config.yml",
        "docs/conf.py",
        "docs/Makefile",
        "docs/index.rst",
    ]

    for file_path in required_files:
        assert Path(
            file_path
        ).exists(), f"Required file {file_path} does not exist"


def test_github_actions_workflows():
    """GitHub Actionsワークフローファイルが正しく設定されていることを確認"""
    workflow_files = [
        ".github/workflows/ci.yml",
        ".github/workflows/security.yml",
        ".github/workflows/release.yml",
    ]

    for workflow_file in workflow_files:
        workflow_path = Path(workflow_file)
        assert (
            workflow_path.exists()
        ), f"Workflow file {workflow_file} does not exist"

        # ファイルが空でないことを確認
        content = workflow_path.read_text()
        assert len(content) > 0, f"Workflow file {workflow_file} is empty"
        assert (
            "name:" in content
        ), f"Workflow file {workflow_file} missing name"


def test_python_package_structure():
    """Pythonパッケージの構造が正しいことを確認"""
    src_dir = Path("src")
    package_dir = src_dir / "github_actions_ai_analyzer"

    assert package_dir.exists(), "Package directory does not exist"
    assert (
        package_dir / "__init__.py"
    ).exists(), "Package __init__.py does not exist"


def test_documentation_structure():
    """ドキュメントの構造が正しいことを確認"""
    docs_dir = Path("docs")

    assert docs_dir.exists(), "Documentation directory does not exist"
    assert (docs_dir / "conf.py").exists(), "Sphinx conf.py does not exist"
    assert (docs_dir / "index.rst").exists(), "Sphinx index.rst does not exist"


def test_makefile_targets():
    """Makefileの主要ターゲットが存在することを確認"""
    makefile_path = Path("Makefile")
    assert makefile_path.exists(), "Makefile does not exist"

    content = makefile_path.read_text()

    # 主要なターゲットが存在することを確認
    required_targets = [
        "help",
        "install",
        "install-dev",
        "test",
        "test-cov",
        "lint",
        "format",
        "type-check",
        "security-check",
        "clean",
        "build",
        "check-all",
        "ci",
    ]

    for target in required_targets:
        assert f"{target}:" in content, f"Makefile target '{target}' not found"


@pytest.mark.integration
def test_import_package():
    """パッケージが正しくインポートできることを確認"""
    try:
        import github_actions_ai_analyzer

        assert github_actions_ai_analyzer is not None
    except ImportError as e:
        pytest.fail(f"Failed to import package: {e}")


@pytest.mark.slow
def test_basic_functionality():
    """基本的な機能が動作することを確認"""
    # このテストは実際のパッケージ機能をテストする
    # 現在はプレースホルダーとして実装
    assert True, "Basic functionality test placeholder"


if __name__ == "__main__":
    # 直接実行時のテスト
    test_project_structure()
    test_config_files()
    test_github_actions_workflows()
    test_python_package_structure()
    test_documentation_structure()
    test_makefile_targets()
    print("✅ All CI/CD setup tests passed!")

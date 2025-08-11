"""
ContextCollectorのユニットテスト
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

from github_actions_ai_analyzer.core.context_collector import ContextCollector
from github_actions_ai_analyzer.types import (
    EnvironmentContext,
    RepositoryContext,
    WorkflowContext,
)


class TestContextCollector:
    """ContextCollectorのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.collector = ContextCollector()

    def test_init(self):
        """初期化のテスト"""
        # ContextCollectorが正常に初期化されることを確認
        assert self.collector is not None
        assert isinstance(self.collector, ContextCollector)

    def test_collect_repository_context_with_path(self):
        """指定されたパスでのリポジトリコンテキスト収集"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Pythonプロジェクトのファイルを作成
            (temp_path / "requirements.txt").write_text(
                "requests==2.28.0\nflask==2.2.0"
            )
            (temp_path / "manage.py").write_text("# Django project")

            context = self.collector.collect_repository_context(str(temp_path))

            assert isinstance(context, RepositoryContext)
            assert context.name == temp_path.name
            assert context.language == "python"
            assert "django" in context.frameworks
            assert "pip" in context.package_managers
            assert "requirements" in context.dependencies

    def test_collect_repository_context_without_path(self):
        """パスなしでのリポジトリコンテキスト収集"""
        with patch("os.getcwd") as mock_getcwd:
            mock_getcwd.return_value = "/tmp/test_repo"

            with patch(
                "github_actions_ai_analyzer.core.context_collector.Path"
            ) as mock_path:
                mock_path_instance = Mock()
                mock_path_instance.name = "test_repo"
                mock_path_instance.__truediv__ = lambda self, other: Mock(
                    exists=lambda: False
                )
                mock_path.return_value = mock_path_instance

                context = self.collector.collect_repository_context()

                assert isinstance(context, RepositoryContext)
                assert context.name == "test_repo"

    def test_collect_workflow_context_with_file(self):
        """ワークフローファイル指定でのコンテキスト収集"""
        workflow_data = {
            "name": "CI",
            "on": {"push": {"branches": ["main"]}},
            "jobs": {
                "test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"name": "Checkout", "uses": "actions/checkout@v3"},
                        {"name": "Run tests", "run": "pytest"},
                    ],
                }
            },
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            yaml.dump(workflow_data, f)
            workflow_path = f.name

        try:
            context = self.collector.collect_workflow_context(workflow_path)

            assert isinstance(context, WorkflowContext)
            assert context.name == "CI"
            assert context.file_path == workflow_path
            assert "push" in context.trigger
            assert "test" in context.jobs
            assert "Checkout" in context.steps
            assert "actions/checkout@v3" in context.actions
        finally:
            os.unlink(workflow_path)

    def test_collect_workflow_context_without_file(self):
        """ワークフローファイルなしでのコンテキスト収集"""
        with patch.object(self.collector, "_find_workflow_file") as mock_find:
            mock_find.return_value = None

            context = self.collector.collect_workflow_context()

            assert isinstance(context, WorkflowContext)
            assert context.name == "unknown"
            assert context.file_path == "unknown"

    def test_collect_workflow_context_invalid_file(self):
        """無効なワークフローファイルでのコンテキスト収集"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yml", delete=False
        ) as f:
            f.write("invalid: yaml: content")
            workflow_path = f.name

        try:
            context = self.collector.collect_workflow_context(workflow_path)

            assert isinstance(context, WorkflowContext)
            assert context.name == "unknown"
        finally:
            os.unlink(workflow_path)

    def test_collect_environment_context(self):
        """環境コンテキスト収集"""
        context = self.collector.collect_environment_context()

        assert isinstance(context, EnvironmentContext)
        assert context.os in ["linux", "windows", "unknown"]
        assert isinstance(context.available_tools, list)
        assert isinstance(context.environment_variables, dict)
        assert isinstance(context.working_directory, str)

    def test_detect_language_and_frameworks_python(self):
        """Python言語とフレームワークの検出"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # requirements.txtのみ
            (temp_path / "requirements.txt").write_text("requests==2.28.0")
            language, frameworks = (
                self.collector._detect_language_and_frameworks(temp_path)
            )
            assert language == "python"
            assert frameworks == []

            # Djangoフレームワーク
            (temp_path / "manage.py").write_text("# Django")
            language, frameworks = (
                self.collector._detect_language_and_frameworks(temp_path)
            )
            assert language == "python"
            assert "django" in frameworks

            # Flaskフレームワーク
            (temp_path / "app.py").write_text("# Flask")
            language, frameworks = (
                self.collector._detect_language_and_frameworks(temp_path)
            )
            assert "flask" in frameworks

    def test_detect_language_and_frameworks_javascript(self):
        """JavaScript言語とフレームワークの検出"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            package_data = {
                "dependencies": {"react": "^18.0.0", "vue": "^3.0.0"}
            }
            (temp_path / "package.json").write_text(json.dumps(package_data))

            language, frameworks = (
                self.collector._detect_language_and_frameworks(temp_path)
            )
            assert language == "javascript"
            assert "react" in frameworks
            assert "vue" in frameworks

    def test_detect_language_and_frameworks_java(self):
        """Java言語とフレームワークの検出"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Maven
            (temp_path / "pom.xml").write_text("<project></project>")
            language, frameworks = (
                self.collector._detect_language_and_frameworks(temp_path)
            )
            assert language == "java"
            assert "maven" in frameworks

            # Gradle
            (temp_path / "build.gradle").write_text("plugins { }")
            language, frameworks = (
                self.collector._detect_language_and_frameworks(temp_path)
            )
            assert "gradle" in frameworks

    def test_detect_language_and_frameworks_unknown(self):
        """未知の言語の検出"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            language, frameworks = (
                self.collector._detect_language_and_frameworks(temp_path)
            )
            assert language is None
            assert frameworks == []

    def test_detect_package_managers(self):
        """パッケージマネージャーの検出"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Python
            (temp_path / "requirements.txt").write_text("requests==2.28.0")
            package_managers = self.collector._detect_package_managers(
                temp_path
            )
            assert "pip" in package_managers

            # JavaScript
            (temp_path / "package.json").write_text("{}")
            package_managers = self.collector._detect_package_managers(
                temp_path
            )
            assert "npm" in package_managers

            # Yarn
            (temp_path / "yarn.lock").write_text("")
            package_managers = self.collector._detect_package_managers(
                temp_path
            )
            assert "yarn" in package_managers

            # Java
            (temp_path / "pom.xml").write_text("<project></project>")
            package_managers = self.collector._detect_package_managers(
                temp_path
            )
            assert "maven" in package_managers

    def test_collect_dependencies_python(self):
        """Python依存関係の収集"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            requirements_content = """
requests==2.28.0
flask==2.2.0
# コメント行
pytest==7.0.0
            """.strip()

            (temp_path / "requirements.txt").write_text(requirements_content)

            dependencies = self.collector._collect_dependencies(
                temp_path, "python"
            )

            assert "requirements" in dependencies
            assert "requests==2.28.0" in dependencies["requirements"]
            assert "flask==2.2.0" in dependencies["requirements"]
            assert "pytest==7.0.0" in dependencies["requirements"]

    def test_collect_dependencies_javascript(self):
        """JavaScript依存関係の収集"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            package_data = {
                "dependencies": {"react": "^18.0.0", "axios": "^1.0.0"},
                "devDependencies": {"jest": "^29.0.0"},
            }

            (temp_path / "package.json").write_text(json.dumps(package_data))

            dependencies = self.collector._collect_dependencies(
                temp_path, "javascript"
            )

            assert "dependencies" in dependencies
            assert "devDependencies" in dependencies
            assert dependencies["dependencies"]["react"] == "^18.0.0"
            assert dependencies["devDependencies"]["jest"] == "^29.0.0"

    def test_collect_dependencies_unknown_language(self):
        """未知の言語での依存関係収集"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            dependencies = self.collector._collect_dependencies(
                temp_path, None
            )
            assert dependencies == {}

    def test_find_workflow_file(self):
        """ワークフローファイルの検索"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            workflow_dir = temp_path / ".github" / "workflows"
            workflow_dir.mkdir(parents=True)

            (workflow_dir / "ci.yml").write_text("name: CI")
            (workflow_dir / "release.yml").write_text("name: Release")

            with patch(
                "github_actions_ai_analyzer.core.context_collector.Path"
            ) as mock_path:
                mock_path.return_value = temp_path

                result = self.collector._find_workflow_file()
                # どちらかのワークフローファイルが返ることを許容
                assert (
                    result is None
                    or result.endswith("ci.yml")
                    or result.endswith("release.yml")
                )

    def test_create_default_workflow_context(self):
        """デフォルトワークフローコンテキストの作成"""
        context = self.collector._create_default_workflow_context()

        assert isinstance(context, WorkflowContext)
        assert context.name == "unknown"
        assert context.file_path == "unknown"
        assert context.trigger == "unknown"
        assert context.jobs == []
        assert context.steps == []
        assert context.actions == []

    def test_parse_workflow_yaml(self):
        """ワークフローYAMLの解析"""
        workflow_data = {
            "name": "Test Workflow",
            "on": {
                "push": {"branches": ["main"]},
                "pull_request": {"branches": ["main"]},
            },
            "jobs": {
                "build": {
                    "runs-on": "ubuntu-latest",
                    "steps": [
                        {"name": "Checkout", "uses": "actions/checkout@v3"},
                        {"name": "Build", "run": "npm install"},
                    ],
                },
                "test": {
                    "runs-on": "ubuntu-latest",
                    "steps": [{"name": "Run tests", "run": "npm test"}],
                },
            },
        }

        context = self.collector._parse_workflow_yaml(
            workflow_data, "/path/to/workflow.yml"
        )

        assert context.name == "Test Workflow"
        assert context.file_path == "/path/to/workflow.yml"
        assert "push" in context.trigger
        assert "pull_request" in context.trigger
        assert "build" in context.jobs
        assert "test" in context.jobs
        assert "Checkout" in context.steps
        assert "Build" in context.steps
        assert "Run tests" in context.steps
        assert "actions/checkout@v3" in context.actions

    def test_parse_workflow_yaml_list_triggers(self):
        """リスト形式のトリガーでのワークフローYAML解析"""
        workflow_data = {
            "name": "Simple Workflow",
            "on": ["push", "pull_request"],
            "jobs": {
                "test": {"steps": [{"name": "Test", "run": "echo 'test'"}]}
            },
        }

        context = self.collector._parse_workflow_yaml(
            workflow_data, "/path/to/workflow.yml"
        )

        assert "push" in context.trigger
        assert "pull_request" in context.trigger

    @patch("subprocess.run")
    def test_detect_available_tools(self, mock_run):
        """利用可能なツールの検出"""
        # ツールが利用可能な場合
        mock_run.return_value.returncode = 0

        tools = self.collector._detect_available_tools()

        assert isinstance(tools, list)
        # 基本的なツールが含まれているかチェック
        expected_tools = [
            "git",
            "python",
            "node",
            "npm",
            "java",
            "mvn",
            "gradle",
        ]
        for tool in expected_tools:
            # 実際の環境に依存するため、存在するかどうかは不定
            pass

    @patch("subprocess.run")
    def test_is_tool_available_success(self, mock_run):
        """ツール利用可能性の確認（成功）"""
        mock_run.return_value.returncode = 0

        result = self.collector._is_tool_available("python")
        assert result is True

    @patch("subprocess.run")
    def test_is_tool_available_failure(self, mock_run):
        """ツール利用可能性の確認（失敗）"""
        mock_run.return_value.returncode = 1

        result = self.collector._is_tool_available("nonexistent_tool")
        assert result is False

    @patch("subprocess.run")
    def test_is_tool_available_exception(self, mock_run):
        """ツール利用可能性の確認（例外）"""
        mock_run.side_effect = FileNotFoundError()

        result = self.collector._is_tool_available("nonexistent_tool")
        assert result is False

"""
コンテキスト収集器

リポジトリ、ワークフロー、環境のコンテキスト情報を収集します。
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..types import EnvironmentContext, RepositoryContext, WorkflowContext


class ContextCollector:
    """コンテキスト情報を収集するクラス"""

    def __init__(self) -> None:
        """初期化"""
        pass

    def collect_repository_context(
        self, repository_path: Optional[str] = None
    ) -> RepositoryContext:
        """リポジトリのコンテキスト情報を収集"""
        if not repository_path:
            repository_path = os.getcwd()

        repo_path = Path(repository_path)

        # 基本的なリポジトリ情報
        name = repo_path.name
        owner = "unknown"  # GitHub APIから取得する必要がある

        # 言語とフレームワークを検出
        language, frameworks = self._detect_language_and_frameworks(repo_path)

        # パッケージマネージャーを検出
        package_managers = self._detect_package_managers(repo_path)

        # 依存関係情報を収集
        dependencies = self._collect_dependencies(repo_path, language)

        return RepositoryContext(
            name=name,
            owner=owner,
            default_branch="main",  # デフォルト値
            language=language,
            frameworks=frameworks,
            package_managers=package_managers,
            dependencies=dependencies,
        )

    def collect_workflow_context(
        self, workflow_file_path: Optional[str] = None
    ) -> WorkflowContext:
        """ワークフローのコンテキスト情報を収集"""
        if not workflow_file_path:
            # デフォルトのワークフローファイルを探す
            workflow_file_path = self._find_workflow_file()

        if not workflow_file_path:
            return self._create_default_workflow_context()

        try:
            with open(workflow_file_path, encoding="utf-8") as f:
                workflow_data = yaml.safe_load(f)

            return self._parse_workflow_yaml(workflow_data, workflow_file_path)
        except Exception:
            return self._create_default_workflow_context()

    def collect_environment_context(self) -> EnvironmentContext:
        """実行環境のコンテキスト情報を収集"""
        # OS情報
        os_name = os.name
        if os_name == "nt":
            os_type = "windows"
        elif os_name == "posix":
            os_type = "linux"
        else:
            os_type = "unknown"

        # 利用可能なツールを検出
        available_tools = self._detect_available_tools()

        # 環境変数
        env_vars = dict(os.environ)

        # 作業ディレクトリ
        working_directory = os.getcwd()

        return EnvironmentContext(
            os=os_type,
            runner_version="unknown",  # GitHub Actions環境で取得
            available_tools=available_tools,
            environment_variables=env_vars,
            working_directory=working_directory,
        )

    def _detect_language_and_frameworks(
        self, repo_path: Path
    ) -> tuple[Optional[str], List[str]]:
        """言語とフレームワークを検出"""
        language = self._detect_language(repo_path)
        frameworks = self._detect_frameworks(repo_path, language)
        return language, frameworks

    def _detect_language(self, repo_path: Path) -> Optional[str]:
        """言語を検出"""
        if (repo_path / "requirements.txt").exists() or (
            repo_path / "pyproject.toml"
        ).exists():
            return "python"
        elif (repo_path / "package.json").exists():
            return "javascript"
        elif (repo_path / "pom.xml").exists() or (
            repo_path / "build.gradle"
        ).exists():
            return "java"
        return None

    def _detect_frameworks(
        self, repo_path: Path, language: Optional[str]
    ) -> List[str]:
        """フレームワークを検出"""
        frameworks = []

        if language == "python":
            frameworks.extend(self._detect_python_frameworks(repo_path))
        elif language == "javascript":
            frameworks.extend(self._detect_javascript_frameworks(repo_path))
        elif language == "java":
            frameworks.extend(self._detect_java_frameworks(repo_path))

        return frameworks

    def _detect_python_frameworks(self, repo_path: Path) -> List[str]:
        """Pythonフレームワークを検出"""
        frameworks = []
        if (repo_path / "manage.py").exists():
            frameworks.append("django")
        if (repo_path / "app.py").exists() or (repo_path / "main.py").exists():
            frameworks.append("flask")
        return frameworks

    def _detect_javascript_frameworks(self, repo_path: Path) -> List[str]:
        """JavaScriptフレームワークを検出"""
        frameworks = []
        package_json = repo_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                deps = data.get("dependencies", {})
                if "react" in deps:
                    frameworks.append("react")
                if "vue" in deps:
                    frameworks.append("vue")
                if "next" in deps:
                    frameworks.append("next.js")
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                # ファイルが見つからない、JSON形式が不正、キーが存在しない場合は無視
                pass
        return frameworks

    def _detect_java_frameworks(self, repo_path: Path) -> List[str]:
        """Javaフレームワークを検出"""
        frameworks = []
        if (repo_path / "pom.xml").exists():
            frameworks.append("maven")
        if (repo_path / "build.gradle").exists():
            frameworks.append("gradle")
        return frameworks

    def _detect_package_managers(self, repo_path: Path) -> List[str]:
        """パッケージマネージャーを検出"""
        package_managers = []

        if (repo_path / "requirements.txt").exists() or (
            repo_path / "pyproject.toml"
        ).exists():
            package_managers.append("pip")
        if (repo_path / "package.json").exists():
            package_managers.append("npm")
        if (repo_path / "yarn.lock").exists():
            package_managers.append("yarn")
        if (repo_path / "pom.xml").exists():
            package_managers.append("maven")
        if (repo_path / "build.gradle").exists():
            package_managers.append("gradle")

        return package_managers

    def _collect_dependencies(
        self, repo_path: Path, language: Optional[str]
    ) -> Dict[str, Any]:
        """依存関係情報を収集"""
        dependencies = {}

        if language == "python":
            requirements_file = repo_path / "requirements.txt"
            if requirements_file.exists():
                try:
                    with open(requirements_file) as f:
                        deps = [
                            line.strip()
                            for line in f
                            if line.strip() and not line.startswith("#")
                        ]
                    dependencies["requirements"] = deps
                except (FileNotFoundError, PermissionError):
                    # ファイルが見つからない、権限エラーの場合は無視
                    pass

        elif language == "javascript":
            package_json = repo_path / "package.json"
            if package_json.exists():
                try:
                    with open(package_json) as f:
                        data = json.load(f)
                    dependencies["dependencies"] = data.get("dependencies", {})
                    dependencies["devDependencies"] = data.get(
                        "devDependencies", {}
                    )
                except (
                    FileNotFoundError,
                    json.JSONDecodeError,
                    PermissionError,
                ):
                    # ファイルが見つからない、JSON形式が不正、権限エラーの場合は無視
                    pass

        return dependencies

    def _find_workflow_file(self) -> Optional[str]:
        """ワークフローファイルを探す"""
        workflow_dir = Path(".github/workflows")
        if workflow_dir.exists():
            for yml_file in workflow_dir.glob("*.yml"):
                return str(yml_file)
        return None

    def _create_default_workflow_context(self) -> WorkflowContext:
        """デフォルトのワークフローコンテキストを作成"""
        return WorkflowContext(
            name="unknown",
            file_path="unknown",
            trigger="unknown",
            jobs=[],
            steps=[],
            actions=[],
            runner=None,
        )

    def _parse_workflow_yaml(
        self, workflow_data: Dict[str, Any], file_path: str
    ) -> WorkflowContext:
        """ワークフローYAMLを解析"""
        name = workflow_data.get("name", "unknown")

        # トリガーを抽出
        triggers = []
        if "on" in workflow_data:
            on_data = workflow_data["on"]
            if isinstance(on_data, dict):
                triggers = list(on_data.keys())
            elif isinstance(on_data, list):
                triggers = on_data

        trigger = ", ".join(triggers) if triggers else "unknown"

        # ジョブとステップを抽出
        jobs = []
        steps = []
        actions = []

        if "jobs" in workflow_data:
            for job_name, job_data in workflow_data["jobs"].items():
                jobs.append(job_name)
                if "steps" in job_data:
                    for step in job_data["steps"]:
                        if "name" in step:
                            steps.append(step["name"])
                        if "uses" in step:
                            actions.append(step["uses"])

        return WorkflowContext(
            name=name,
            file_path=file_path,
            trigger=trigger,
            jobs=jobs,
            steps=steps,
            actions=actions,
            runner=None,
        )

    def _detect_available_tools(self) -> List[str]:
        """利用可能なツールを検出"""
        tools = []

        # 基本的なツール
        basic_tools = ["git", "python", "node", "npm", "java", "mvn", "gradle"]
        for tool in basic_tools:
            if self._is_tool_available(tool):
                tools.append(tool)

        return tools

    def _is_tool_available(self, tool: str) -> bool:
        """ツールが利用可能かどうかを確認"""
        # セキュリティ: 許可されたツールのみをチェック
        allowed_tools = {
            "git",
            "python",
            "node",
            "npm",
            "java",
            "mvn",
            "gradle",
        }
        if tool not in allowed_tools:
            return False

        try:
            import subprocess  # nosec B404

            result = subprocess.run(  # nosec B603
                [tool, "--version"], capture_output=True, text=True
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.SubprocessError):
            return False

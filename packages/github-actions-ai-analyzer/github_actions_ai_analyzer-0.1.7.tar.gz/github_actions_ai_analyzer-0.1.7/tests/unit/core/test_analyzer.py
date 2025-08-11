"""
GitHubActionsAnalyzerのユニットテスト
"""

import tempfile
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from github_actions_ai_analyzer.core.analyzer import GitHubActionsAnalyzer
from github_actions_ai_analyzer.types import (
    ErrorAnalysis,
    LogEntry,
    LogLevel,
    LogSource,
    PatternMatch,
    SolutionProposal,
)
from github_actions_ai_analyzer.types.pattern_types import (
    ErrorPattern,
    PatternCategory,
)


class TestGitHubActionsAnalyzer:
    """GitHubActionsAnalyzerのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.analyzer = GitHubActionsAnalyzer()

    def test_init(self):
        """初期化のテスト"""
        assert self.analyzer.log_processor is not None
        assert self.analyzer.pattern_matcher is not None
        assert self.analyzer.context_collector is not None
        assert self.analyzer.ai_prompt_optimizer is not None

    def test_read_log_file_success(self):
        """ログファイル読み込み成功"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("Test log content")
            log_file_path = f.name

        try:
            content = self.analyzer._read_log_file(log_file_path)
            assert content == "Test log content"
        finally:
            import os

            os.unlink(log_file_path)

    def test_read_log_file_not_found(self):
        """ログファイルが見つからない場合"""
        with pytest.raises(FileNotFoundError):
            self.analyzer._read_log_file("nonexistent_file.txt")

    def test_read_log_file_encoding_error(self):
        """ログファイルのエンコーディングエラー"""
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as f:
            f.write(b"\xff\xfe\x00\x00")  # 無効なUTF-8
            log_file_path = f.name

        try:
            with pytest.raises(Exception):
                self.analyzer._read_log_file(log_file_path)
        finally:
            import os

            os.unlink(log_file_path)

    def test_analyze_log_file_basic(self):
        """基本的なログファイル解析"""
        # テスト用のログファイルを作成
        log_content = """
2024-01-01T12:00:00.000Z Step 1: Install dependencies
2024-01-01T12:00:01.000Z error: ModuleNotFoundError: No module named 'requests'
2024-01-01T12:00:02.000Z Step 2: Run tests
"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(log_content)
            log_file_path = f.name

        try:
            with patch.object(
                self.analyzer.log_processor, "process_log_file"
            ) as mock_process:
                mock_process.return_value = []

                with patch.object(
                    self.analyzer.log_processor, "filter_by_level"
                ) as mock_filter:
                    mock_filter.return_value = []

                    with patch.object(
                        self.analyzer.pattern_matcher, "match_patterns"
                    ) as mock_match:
                        mock_match.return_value = []

                        result = self.analyzer.analyze_log_file(log_file_path)

                        assert result is not None
                        assert result.analysis_id is not None
                        assert result.error_analyses == []
                        assert result.solution_proposals == []
        finally:
            import os

            os.unlink(log_file_path)

    def test_analyze_errors_empty(self):
        """空のエラー解析"""
        log_entries = []
        pattern_matches = []

        result = self.analyzer._analyze_errors(log_entries, pattern_matches)
        assert result == []

    def test_analyze_errors_with_matches(self):
        """マッチがある場合のエラー解析"""
        # テスト用のログエントリを作成
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="ModuleNotFoundError: No module named 'requests'",
            step_name="Install dependencies",
        )

        # テスト用のパターンマッチを作成
        from github_actions_ai_analyzer.types import (
            ErrorPattern,
            PatternCategory,
        )

        pattern = ErrorPattern(
            id="dep_missing_package",
            name="Missing Package",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=r"ModuleNotFoundError",
            description="Pythonパッケージが見つからない",
            severity="error",
            language="python",
        )

        match = PatternMatch(
            pattern=pattern,
            matched_text="ModuleNotFoundError: No module named 'requests'",
            start_pos=0,
            end_pos=47,
            confidence=0.8,
            context={"log_entry": entry},
        )

        result = self.analyzer._analyze_errors([entry], [match])

        assert len(result) == 1
        analysis = result[0]
        assert analysis.error_id.startswith("error_dep_missing_package")
        assert (
            analysis.root_cause
            == "Pythonパッケージが見つからない (ステップ: Install dependencies)"
        )
        assert analysis.severity == "error"
        assert "Install dependencies" in analysis.affected_steps

    def test_estimate_root_cause(self):
        """根本原因の推定"""
        pattern = Mock()
        pattern.description = "テストエラー"

        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="Test error",
            step_name="Test step",
        )

        result = self.analyzer._estimate_root_cause(pattern, [entry])
        assert result == "テストエラー (ステップ: Test step)"

    def test_estimate_root_cause_no_step(self):
        """ステップ名がない場合の根本原因推定"""
        pattern = Mock()
        pattern.description = "テストエラー"

        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="Test error",
        )

        result = self.analyzer._estimate_root_cause(pattern, [entry])
        assert result == "テストエラー"

    def test_determine_severity(self):
        """重要度の決定"""
        # エラーレベルのマッチ
        error_match = Mock()
        error_match.pattern.severity = "error"

        result = self.analyzer._determine_severity([error_match])
        assert result == "error"

        # 警告レベルのマッチ
        warning_match = Mock()
        warning_match.pattern.severity = "warning"

        result = self.analyzer._determine_severity([warning_match])
        assert result == "warning"

        # 複数のマッチ（最も高い重要度を返す）
        fatal_match = Mock()
        fatal_match.pattern.severity = "fatal"

        result = self.analyzer._determine_severity([error_match, fatal_match])
        assert result == "fatal"

    def test_identify_affected_steps(self):
        """影響を受けるステップの特定"""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.ERROR,
                source=LogSource.SYSTEM,
                message="Error 1",
                step_name="Step 1",
            ),
            LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.ERROR,
                source=LogSource.SYSTEM,
                message="Error 2",
                step_name="Step 2",
            ),
            LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.ERROR,
                source=LogSource.SYSTEM,
                message="Error 3",
                step_name="Step 1",  # 重複
            ),
        ]

        result = self.analyzer._identify_affected_steps(entries)
        assert len(result) == 2
        assert "Step 1" in result
        assert "Step 2" in result

    def test_identify_related_files(self):
        """関連ファイルの特定"""
        entries = [
            LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.ERROR,
                source=LogSource.SYSTEM,
                message="Error in app.py",
            ),
            LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.ERROR,
                source=LogSource.SYSTEM,
                message="Error in config.yml",
            ),
            LogEntry(
                timestamp=datetime.now(),
                level=LogLevel.ERROR,
                source=LogSource.SYSTEM,
                message="Error in script.js",
            ),
        ]

        result = self.analyzer._identify_related_files(entries)
        assert "*.py" in result
        assert "*.yml" in result
        assert "*.js" in result

    def test_generate_solutions_empty(self):
        """空の解決策生成"""
        result = self.analyzer._generate_solutions([])
        assert result == []

    def test_generate_solutions_with_analysis(self):
        """解析結果がある場合の解決策生成"""
        # テスト用のエラー解析を作成
        pattern = ErrorPattern(
            id="dep_missing_package",
            name="Missing Package",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=r"ModuleNotFoundError",
            description="Pythonパッケージが見つからない",
            severity="error",
            language="python",
        )

        match = PatternMatch(
            pattern=pattern,
            matched_text="test",
            start_pos=0,
            end_pos=4,
            confidence=0.8,
            context={},
        )

        analysis = ErrorAnalysis(
            error_id="test_error",
            log_entries=[],
            pattern_matches=[match],
            root_cause="Test error",
            severity="error",
            affected_steps=[],
            related_files=[],
        )

        result = self.analyzer._generate_solutions([analysis])

        assert len(result) == 1
        solution = result[0]
        assert solution.solution_id.startswith("sol_dep_missing_package")
        assert solution.title == "Missing Packageの解決"
        assert solution.confidence == 0.7

    def test_create_solution_from_pattern_dependency(self):
        """依存関係パターンからの解決策作成"""
        pattern = ErrorPattern(
            id="dep_missing_package",
            name="Missing Package",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=r"ModuleNotFoundError",
            description="Pythonパッケージが見つからない",
            severity="error",
            language="python",
        )

        match = PatternMatch(
            pattern=pattern,
            matched_text="test",
            start_pos=0,
            end_pos=4,
            confidence=0.8,
            context={},
        )

        analysis = ErrorAnalysis(
            error_id="test_error",
            log_entries=[],
            pattern_matches=[match],
            root_cause="Test error",
            severity="error",
            affected_steps=[],
            related_files=[],
        )

        result = self.analyzer._create_solution_from_pattern(match, analysis)

        assert result is not None
        assert result.solution_id.startswith("sol_dep_missing_package")
        assert result.title == "Missing Packageの解決"
        assert len(result.steps) == 3

    def test_create_solution_from_pattern_unknown_category(self):
        """未知のカテゴリを渡した場合はValidationError例外が発生する"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            ErrorPattern(
                id="unknown_pattern",
                name="Unknown Pattern",
                category="unknown",  # 存在しないカテゴリを直接指定
                regex_pattern=r"unknown",
                description="未知のパターン",
                severity="error",
            )

    def test_generate_summary_no_errors(self):
        """エラーがない場合のサマリー生成"""
        result = self.analyzer._generate_summary([], [])
        assert result == "エラーは検出されませんでした。"

    def test_generate_summary_with_errors(self):
        """エラーがある場合のサマリー生成"""
        # テスト用のエラー解析を作成
        pattern = ErrorPattern(
            id="dep_missing_package",
            name="Missing Package",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=r"ModuleNotFoundError",
            description="Pythonパッケージが見つからない",
            severity="error",
            language="python",
        )

        match = PatternMatch(
            pattern=pattern,
            matched_text="test",
            start_pos=0,
            end_pos=4,
            confidence=0.8,
            context={},
        )

        analysis = ErrorAnalysis(
            error_id="test_error",
            log_entries=[],
            pattern_matches=[match],
            root_cause="Test error",
            severity="error",
            affected_steps=[],
            related_files=[],
        )

        solution = SolutionProposal(
            solution_id="test_solution",
            title="Test Solution",
            description="Test description",
            steps=[],
            code_examples=[],
            confidence=0.8,
            estimated_time="5分",
            prerequisites=[],
        )

        result = self.analyzer._generate_summary([analysis], [solution])
        assert (
            "合計1個のエラーが検出され、1個の解決策が提案されました。"
            in result
        )
        assert "dependency: 1個" in result

    def test_generate_recommendations_empty(self):
        """空の推奨事項生成"""
        result = self.analyzer._generate_recommendations([])
        assert result == []

    def test_generate_recommendations_dependency_errors(self):
        """依存関係エラーの推奨事項生成"""
        pattern = ErrorPattern(
            id="dep_missing_package",
            name="Missing Package",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=r"ModuleNotFoundError",
            description="Pythonパッケージが見つからない",
            severity="error",
            language="python",
        )

        match = PatternMatch(
            pattern=pattern,
            matched_text="test",
            start_pos=0,
            end_pos=4,
            confidence=0.8,
            context={},
        )

        analysis = ErrorAnalysis(
            error_id="test_error",
            log_entries=[],
            pattern_matches=[match],
            root_cause="Test error",
            severity="error",
            affected_steps=[],
            related_files=[],
        )

        result = self.analyzer._generate_recommendations([analysis])
        assert len(result) == 1
        assert "依存関係の管理を改善することを推奨します。" in result[0]

    def test_generate_recommendations_permission_errors(self):
        """権限エラーの推奨事項生成"""
        pattern = ErrorPattern(
            id="perm_error",
            name="Permission Error",
            category=PatternCategory.PERMISSION,
            regex_pattern=r"PermissionError",
            description="権限エラー",
            severity="error",
            language="python",
        )

        match = PatternMatch(
            pattern=pattern,
            matched_text="test",
            start_pos=0,
            end_pos=4,
            confidence=0.8,
            context={},
        )
        analysis = ErrorAnalysis(
            error_id="test_error",
            log_entries=[],
            pattern_matches=[match],
            root_cause="Test error",
            severity="error",
            affected_steps=[],
            related_files=[],
        )
        result = self.analyzer._generate_recommendations([analysis])
        assert len(result) == 1
        assert "ファイル権限の設定を確認することを推奨します。" in result[0]

    def test_generate_recommendations_multiple_errors(self):
        """複数エラーの推奨事項生成"""
        # 依存関係エラー
        dep_pattern = ErrorPattern(
            id="dep_missing_package",
            name="Missing Package",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=r"ModuleNotFoundError",
            description="Pythonパッケージが見つからない",
            severity="error",
            language="python",
        )
        dep_match = PatternMatch(
            pattern=dep_pattern,
            matched_text="test",
            start_pos=0,
            end_pos=4,
            confidence=0.8,
            context={},
        )
        dep_analysis = ErrorAnalysis(
            error_id="dep_error",
            log_entries=[],
            pattern_matches=[dep_match],
            root_cause="Dependency error",
            severity="error",
            affected_steps=[],
            related_files=[],
        )
        # 権限エラー
        perm_pattern = ErrorPattern(
            id="perm_error",
            name="Permission Error",
            category=PatternCategory.PERMISSION,
            regex_pattern=r"PermissionError",
            description="権限エラー",
            severity="error",
            language="python",
        )
        perm_match = PatternMatch(
            pattern=perm_pattern,
            matched_text="test",
            start_pos=0,
            end_pos=4,
            confidence=0.8,
            context={},
        )
        perm_analysis = ErrorAnalysis(
            error_id="perm_error",
            log_entries=[],
            pattern_matches=[perm_match],
            root_cause="Permission error",
            severity="error",
            affected_steps=[],
            related_files=[],
        )
        result = self.analyzer._generate_recommendations(
            [dep_analysis, perm_analysis]
        )
        assert len(result) == 2
        assert any("依存関係の管理を改善" in rec for rec in result)
        assert any("ファイル権限の設定を確認" in rec for rec in result)

"""
PatternMatcherのユニットテスト
"""

from datetime import datetime
from unittest.mock import Mock

from github_actions_ai_analyzer.core.pattern_matcher import PatternMatcher
from github_actions_ai_analyzer.types import (
    ErrorPattern,
    LogEntry,
    LogLevel,
    LogSource,
    PatternCategory,
)


class TestPatternMatcher:
    """PatternMatcherのテストクラス"""

    def setup_method(self):
        """テスト前のセットアップ"""
        self.matcher = PatternMatcher()

    def test_init(self):
        """初期化のテスト"""
        assert len(self.matcher.patterns) > 0
        # デフォルトパターンが読み込まれていることを確認
        pattern_ids = [p.id for p in self.matcher.patterns]
        assert "dep_missing_package" in pattern_ids
        assert "perm_denied" in pattern_ids
        assert "env_command_not_found" in pattern_ids

    def test_match_patterns_empty_entries(self):
        """空のログエントリでのマッチング"""
        matches = self.matcher.match_patterns([])
        assert matches == []

    def test_match_patterns_dependency_error(self):
        """依存関係エラーのマッチング"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="ModuleNotFoundError: No module named 'requests'",
            metadata={"language": "python"},
        )

        matches = self.matcher.match_patterns([entry])

        assert len(matches) > 0
        match = matches[0]
        assert match.pattern.id == "dep_missing_package"
        assert "ModuleNotFoundError" in match.matched_text
        assert match.confidence > 0.5

    def test_match_patterns_permission_error(self):
        """権限エラーのマッチング"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="Permission denied: /path/to/file",
        )

        matches = self.matcher.match_patterns([entry])

        assert len(matches) > 0
        match = matches[0]
        assert match.pattern.id == "perm_denied"
        assert "Permission denied" in match.matched_text

    def test_match_patterns_environment_error(self):
        """環境エラーのマッチング"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="command not found: python",
        )

        matches = self.matcher.match_patterns([entry])

        assert len(matches) > 0
        match = matches[0]
        assert match.pattern.id == "env_command_not_found"
        assert "command not found" in match.matched_text

    def test_match_patterns_network_error(self):
        """ネットワークエラーのマッチング"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="Connection timed out",
        )

        matches = self.matcher.match_patterns([entry])

        assert len(matches) > 0
        match = matches[0]
        assert match.pattern.id == "net_timeout"
        assert "Connection timed out" in match.matched_text

    def test_match_patterns_syntax_error(self):
        """構文エラーのマッチング"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="YAML syntax error at line 10",
        )

        matches = self.matcher.match_patterns([entry])

        assert len(matches) > 0
        match = matches[0]
        assert match.pattern.id == "syntax_yaml"
        assert "YAML syntax error" in match.matched_text

    def test_match_patterns_language_filtering(self):
        """言語フィルタリングのテスト"""
        # Python言語のエラー
        python_entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="ModuleNotFoundError: No module named 'requests'",
            metadata={"language": "python"},
        )

        # JavaScript言語のエラー
        js_entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="npm ERR! install failed",
            metadata={"language": "javascript"},
        )

        matches = self.matcher.match_patterns([python_entry, js_entry])

        # PythonエラーはPythonパターンにマッチ
        python_matches = [m for m in matches if m.pattern.language == "python"]
        assert len(python_matches) > 0

        # JavaScriptエラーはJavaScriptパターンにマッチ
        js_matches = [m for m in matches if m.pattern.language == "javascript"]
        assert len(js_matches) > 0

    def test_match_patterns_no_match(self):
        """マッチしないメッセージのテスト"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.INFO,
            source=LogSource.SYSTEM,
            message="This is a normal log message",
        )

        matches = self.matcher.match_patterns([entry])
        assert matches == []

    def test_calculate_confidence_error_level(self):
        """エラーレベルでの信頼度計算"""
        pattern = ErrorPattern(
            id="test_pattern",
            name="Test Pattern",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=r"test",
            description="Test pattern",
            severity="error",
        )

        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="test message",
        )

        match = Mock()
        match.group.return_value = "test"

        confidence = self.matcher._calculate_confidence(pattern, entry, match)
        assert confidence > 0.5

    def test_calculate_confidence_warning_level(self):
        """警告レベルでの信頼度計算"""
        pattern = ErrorPattern(
            id="test_pattern",
            name="Test Pattern",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=r"test",
            description="Test pattern",
            severity="warning",
        )

        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.WARNING,
            source=LogSource.SYSTEM,
            message="test message",
        )

        match = Mock()
        match.group.return_value = "test"

        confidence = self.matcher._calculate_confidence(pattern, entry, match)
        assert confidence > 0.5

    def test_calculate_confidence_exact_match(self):
        """完全一致での信頼度計算"""
        pattern = ErrorPattern(
            id="test_pattern",
            name="Test Pattern",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=r"exact message",
            description="Test pattern",
            severity="error",
        )

        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="exact message",
        )

        match = Mock()
        match.group.return_value = "exact message"

        confidence = self.matcher._calculate_confidence(pattern, entry, match)
        assert confidence > 0.7  # 完全一致により信頼度が上がる

    def test_calculate_confidence_detailed_pattern(self):
        """詳細なパターンでの信頼度計算"""
        # 長いパターン
        long_pattern = "a" * 60
        pattern = ErrorPattern(
            id="test_pattern",
            name="Test Pattern",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=long_pattern,
            description="Test pattern",
            severity="error",
        )

        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="test message",
        )

        match = Mock()
        match.group.return_value = "test"

        confidence = self.matcher._calculate_confidence(pattern, entry, match)
        assert confidence > 0.5

    def test_add_pattern(self):
        """パターンの追加"""
        initial_count = len(self.matcher.patterns)

        new_pattern = ErrorPattern(
            id="custom_pattern",
            name="Custom Pattern",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=r"custom error",
            description="Custom error pattern",
            severity="error",
        )

        self.matcher.add_pattern(new_pattern)

        assert len(self.matcher.patterns) == initial_count + 1
        assert new_pattern in self.matcher.patterns

    def test_get_patterns_by_category(self):
        """カテゴリ別パターン取得"""
        dependency_patterns = self.matcher.get_patterns_by_category(
            PatternCategory.DEPENDENCY
        )
        permission_patterns = self.matcher.get_patterns_by_category(
            PatternCategory.PERMISSION
        )

        assert all(
            p.category == PatternCategory.DEPENDENCY
            for p in dependency_patterns
        )
        assert all(
            p.category == PatternCategory.PERMISSION
            for p in permission_patterns
        )

    def test_get_patterns_by_language(self):
        """言語別パターン取得"""
        python_patterns = self.matcher.get_patterns_by_language("python")
        js_patterns = self.matcher.get_patterns_by_language("javascript")

        assert all(p.language == "python" for p in python_patterns)
        assert all(p.language == "javascript" for p in js_patterns)

    def test_remove_pattern(self):
        """パターンの削除"""
        # カスタムパターンを追加
        custom_pattern = ErrorPattern(
            id="to_remove",
            name="To Remove",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=r"remove me",
            description="Pattern to remove",
            severity="error",
        )

        self.matcher.add_pattern(custom_pattern)
        initial_count = len(self.matcher.patterns)

        # パターンを削除
        result = self.matcher.remove_pattern("to_remove")

        assert result is True
        assert len(self.matcher.patterns) == initial_count - 1
        assert custom_pattern not in self.matcher.patterns

    def test_remove_pattern_not_found(self):
        """存在しないパターンの削除"""
        result = self.matcher.remove_pattern("nonexistent_pattern")
        assert result is False

    def test_match_entry_multiple_matches(self):
        """単一エントリでの複数マッチ"""
        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="Permission denied: command not found",
        )

        matches = self.matcher._match_entry(entry)

        # 複数のパターンにマッチする可能性がある
        assert len(matches) >= 1
        pattern_ids = [m.pattern.id for m in matches]
        assert any(
            pid in ["perm_denied", "env_command_not_found"]
            for pid in pattern_ids
        )

    def test_match_entry_low_confidence_filtered(self):
        """低信頼度のマッチが除外される"""
        # 信頼度が低くなるようなパターンを作成
        low_confidence_pattern = ErrorPattern(
            id="low_confidence",
            name="Low Confidence",
            category=PatternCategory.DEPENDENCY,
            regex_pattern=r"test",
            description="Low confidence pattern",
            severity="info",  # エラーレベルと異なる
        )

        self.matcher.add_pattern(low_confidence_pattern)

        entry = LogEntry(
            timestamp=datetime.now(),
            level=LogLevel.ERROR,
            source=LogSource.SYSTEM,
            message="test message",
        )

        matches = self.matcher._match_entry(entry)

        # 低信頼度のパターンは除外される
        low_confidence_matches = [
            m for m in matches if m.pattern.id == "low_confidence"
        ]
        assert len(low_confidence_matches) == 0

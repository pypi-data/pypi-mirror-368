"""
GitHub Actions Analyzer

メインの解析エンジン。他のコンポーネントを統合してGitHub Actionsのログを解析します。
"""

import uuid
from typing import Dict, List, Optional

from ..types import (
    AnalysisResult,
    ErrorAnalysis,
    ErrorPattern,
    LogEntry,
    LogLevel,
    PatternMatch,
    SolutionProposal,
)
from .ai_prompt_optimizer import AIPromptOptimizer
from .context_collector import ContextCollector
from .log_processor import LogProcessor
from .pattern_matcher import PatternMatcher


class GitHubActionsAnalyzer:
    """GitHub Actionsのログ解析を行うメインクラス"""

    def __init__(self) -> None:
        self.log_processor = LogProcessor()
        self.pattern_matcher = PatternMatcher()
        self.context_collector = ContextCollector()
        self.ai_prompt_optimizer = AIPromptOptimizer()

    def analyze_log_file(
        self,
        log_file_path: str,
        workflow_file_path: Optional[str] = None,
        repository_path: Optional[str] = None,
        min_log_level: LogLevel = LogLevel.WARNING,
    ) -> AnalysisResult:
        """ログファイルを解析して結果を返す"""

        # ログファイルを読み込み
        log_content = self._read_log_file(log_file_path)

        # ログを前処理
        log_entries = self.log_processor.process_log_file(log_content)

        # ログレベルでフィルタリング
        filtered_entries = self.log_processor.filter_by_level(
            log_entries, min_log_level
        )

        # パターンマッチング
        pattern_matches = self.pattern_matcher.match_patterns(filtered_entries)

        # コンテキスト情報を収集
        repository_context = self.context_collector.collect_repository_context(
            repository_path
        )
        workflow_context = self.context_collector.collect_workflow_context(
            workflow_file_path
        )
        environment_context = (
            self.context_collector.collect_environment_context()
        )

        # エラー解析
        error_analyses = self._analyze_errors(
            filtered_entries, pattern_matches
        )

        # 解決策提案
        solution_proposals = self._generate_solutions(error_analyses)

        # 解析サマリー
        summary = self._generate_summary(error_analyses, solution_proposals)

        # 推奨事項
        recommendations = self._generate_recommendations(error_analyses)

        return AnalysisResult(
            analysis_id=str(uuid.uuid4()),
            repository_context=repository_context,
            workflow_context=workflow_context,
            environment_context=environment_context,
            error_analyses=error_analyses,
            solution_proposals=solution_proposals,
            summary=summary,
            recommendations=recommendations,
        )

    def _read_log_file(self, log_file_path: str) -> str:
        """ログファイルを読み込み"""
        try:
            with open(log_file_path, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(
                f"ログファイルが見つかりません: {log_file_path}"
            )
        except Exception as e:
            raise Exception(f"ログファイルの読み込みに失敗しました: {e}")

    def _analyze_errors(
        self, log_entries: List[LogEntry], pattern_matches: List[PatternMatch]
    ) -> List[ErrorAnalysis]:
        """エラーを解析"""
        error_analyses: List[ErrorAnalysis] = []

        # パターンマッチをグループ化
        matches_by_pattern: Dict[str, List[PatternMatch]] = {}
        for match in pattern_matches:
            pattern_id = match.pattern.id
            if pattern_id not in matches_by_pattern:
                matches_by_pattern[pattern_id] = []
            matches_by_pattern[pattern_id].append(match)

        # 各パターンについてエラー解析を作成
        for pattern_id, matches in matches_by_pattern.items():
            # 関連するログエントリを収集
            related_entries = []
            for match in matches:
                if "log_entry" in match.context:
                    related_entries.append(match.context["log_entry"])

            # 重複を除去
            unique_entries = list(
                {entry.timestamp: entry for entry in related_entries}.values()
            )

            # 根本原因を推定
            root_cause = self._estimate_root_cause(
                matches[0].pattern, unique_entries
            )

            # 重要度を決定
            severity = self._determine_severity(matches)

            # 影響を受けるステップを特定
            affected_steps = self._identify_affected_steps(unique_entries)

            # 関連ファイルを特定
            related_files = self._identify_related_files(unique_entries)

            error_analysis = ErrorAnalysis(
                error_id=f"error_{pattern_id}_{len(error_analyses)}",
                log_entries=unique_entries,
                pattern_matches=matches,
                root_cause=root_cause,
                severity=severity,
                affected_steps=affected_steps,
                related_files=related_files,
            )

            error_analyses.append(error_analysis)

        return error_analyses

    def _estimate_root_cause(
        self, pattern: ErrorPattern, log_entries: List[LogEntry]
    ) -> str:
        """根本原因を推定"""
        # パターンの説明を基本とする
        root_cause = pattern.description

        # ログエントリの内容から詳細を追加
        if log_entries:
            first_entry = log_entries[0]
            if first_entry.step_name:
                root_cause += f" (ステップ: {first_entry.step_name})"

        return root_cause

    def _determine_severity(self, matches: List[PatternMatch]) -> str:
        """重要度を決定"""
        # 最も高い重要度を返す
        severities = [match.pattern.severity for match in matches]
        if "fatal" in severities:
            return "fatal"
        elif "error" in severities:
            return "error"
        elif "warning" in severities:
            return "warning"
        else:
            return "info"

    def _identify_affected_steps(
        self, log_entries: List[LogEntry]
    ) -> List[str]:
        """影響を受けるステップを特定"""
        steps = set()
        for entry in log_entries:
            if entry.step_name:
                steps.add(entry.step_name)
        return list(steps)

    def _identify_related_files(
        self, log_entries: List[LogEntry]
    ) -> List[str]:
        """関連ファイルを特定"""
        files = set()
        for entry in log_entries:
            # メッセージからファイル名を抽出
            if ".py" in entry.message:
                files.add("*.py")
            if ".js" in entry.message:
                files.add("*.js")
            if ".yml" in entry.message or ".yaml" in entry.message:
                files.add("*.yml")
        return list(files)

    def _generate_solutions(
        self, error_analyses: List[ErrorAnalysis]
    ) -> List[SolutionProposal]:
        """解決策を生成"""
        solutions = []

        for analysis in error_analyses:
            # パターンに基づいて解決策を生成
            for match in analysis.pattern_matches:
                solution = self._create_solution_from_pattern(match, analysis)
                if solution:
                    solutions.append(solution)

        return solutions

    def _create_solution_from_pattern(
        self, match: PatternMatch, analysis: ErrorAnalysis
    ) -> Optional[SolutionProposal]:
        """パターンから解決策を作成"""
        pattern = match.pattern

        # 基本的な解決策テンプレート
        if pattern.category == "dependency":
            return SolutionProposal(
                solution_id=(
                    f"sol_{pattern.id}_{len(analysis.pattern_matches)}"
                ),
                title=f"{pattern.name}の解決",
                description=f"{pattern.description}を解決するための手順",
                steps=[
                    "依存関係ファイルを確認",
                    "パッケージマネージャーで再インストール",
                    "バージョン互換性を確認",
                ],
                code_examples=[],
                confidence=0.7,
                estimated_time="5-10分",
                prerequisites=[],
            )

        return None

    def _generate_summary(
        self,
        error_analyses: List[ErrorAnalysis],
        solutions: List[SolutionProposal],
    ) -> str:
        """解析サマリーを生成"""
        total_errors = len(error_analyses)
        total_solutions = len(solutions)

        if total_errors == 0:
            return "エラーは検出されませんでした。"

        summary = f"合計{total_errors}個のエラーが検出され、{total_solutions}個の解決策が提案されました。"

        # エラーの種類別サマリー
        categories: Dict[str, int] = {}
        for analysis in error_analyses:
            for match in analysis.pattern_matches:
                category = match.pattern.category
                categories[category] = categories.get(category, 0) + 1

        if categories:
            summary += " エラーの種類: " + ", ".join(
                [f"{cat}: {count}個" for cat, count in categories.items()]
            )

        return summary

    def _generate_recommendations(
        self, error_analyses: List[ErrorAnalysis]
    ) -> List[str]:
        """推奨事項を生成"""
        recommendations = []

        # エラーの種類に基づいて推奨事項を生成
        dependency_errors = [
            a
            for a in error_analyses
            if any(
                m.pattern.category == "dependency" for m in a.pattern_matches
            )
        ]

        if dependency_errors:
            recommendations.append(
                "依存関係の管理を改善することを推奨します。"
            )

        permission_errors = [
            a
            for a in error_analyses
            if any(
                m.pattern.category == "permission" for m in a.pattern_matches
            )
        ]

        if permission_errors:
            recommendations.append(
                "ファイル権限の設定を確認することを推奨します。"
            )

        return recommendations

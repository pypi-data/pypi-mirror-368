"""
AI プロンプト最適化器

構造化されたエラー情報をAIが理解しやすい形式に変換します。
"""

from typing import Any, Dict, List

from ..types import AnalysisResult, ErrorAnalysis, SolutionProposal


class AIPromptOptimizer:
    """AI用のプロンプト最適化を行うクラス"""

    def __init__(self) -> None:
        """初期化"""
        self.template_cache: Dict[str, str] = {}
        self.optimization_history: List[Dict[str, Any]] = []

    def generate_error_analysis_prompt(
        self, analysis_result: AnalysisResult
    ) -> str:
        """エラー解析用のプロンプトを生成"""
        template = self._get_error_analysis_template()

        # エラー情報を構造化
        error_summary = self._format_error_summary(
            analysis_result.error_analyses
        )
        context_info = self._format_context_info(analysis_result)

        return template.format(
            error_summary=error_summary,
            context_info=context_info,
            repository_name=analysis_result.repository_context.name,
            workflow_name=analysis_result.workflow_context.name,
        )

    def generate_solution_prompt(self, analysis_result: AnalysisResult) -> str:
        """解決策生成用のプロンプトを生成"""
        template = self._get_solution_generation_template()

        # エラー詳細を構造化
        error_details = self._format_error_details(
            analysis_result.error_analyses
        )
        existing_solutions = self._format_existing_solutions(
            analysis_result.solution_proposals
        )

        return template.format(
            error_details=error_details,
            existing_solutions=existing_solutions,
            repository_language=analysis_result.repository_context.language
            or "unknown",
        )

    def generate_best_practices_prompt(
        self, analysis_result: AnalysisResult
    ) -> str:
        """ベストプラクティス提案用のプロンプトを生成"""
        template = self._get_best_practices_template()

        # 現在の設定を構造化
        current_setup = self._format_current_setup(analysis_result)
        error_patterns = self._format_error_patterns(
            analysis_result.error_analyses
        )

        return template.format(
            current_setup=current_setup,
            error_patterns=error_patterns,
            repository_name=analysis_result.repository_context.name,
        )

    def _format_error_summary(
        self, error_analyses: List[ErrorAnalysis]
    ) -> str:
        """エラーサマリーをフォーマット"""
        if not error_analyses:
            return "エラーは検出されませんでした。"

        summary_parts = []
        for analysis in error_analyses:
            summary_parts.append(
                f"- {analysis.root_cause} (重要度: {analysis.severity})"
            )
            if analysis.affected_steps:
                summary_parts.append(
                    f"  影響ステップ: {', '.join(analysis.affected_steps)}"
                )
            if analysis.related_files:
                summary_parts.append(
                    f"  関連ファイル: {', '.join(analysis.related_files)}"
                )

        return "\n".join(summary_parts)

    def _format_context_info(self, analysis_result: AnalysisResult) -> str:
        """コンテキスト情報をフォーマット"""
        repo = analysis_result.repository_context
        workflow = analysis_result.workflow_context
        env = analysis_result.environment_context

        context_parts = [
            f"リポジトリ: {repo.name}",
            f"主要言語: {repo.language or 'unknown'}",
            (
                f"フレームワーク: "
                f"{', '.join(repo.frameworks) if repo.frameworks else 'none'}"
            ),
            f"パッケージマネージャー: {', '.join(repo.package_managers)}",
            f"ワークフロー: {workflow.name}",
            f"トリガー: {workflow.trigger}",
            f"OS: {env.os}",
        ]

        return "\n".join(context_parts)

    def _format_error_details(
        self, error_analyses: List[ErrorAnalysis]
    ) -> str:
        """エラー詳細をフォーマット"""
        if not error_analyses:
            return "エラーは検出されませんでした。"

        details_parts = []
        for analysis in error_analyses:
            details_parts.append(f"## エラー: {analysis.root_cause}")
            details_parts.append(f"重要度: {analysis.severity}")

            if analysis.log_entries:
                details_parts.append("関連ログ:")
                for entry in analysis.log_entries[:3]:  # 最初の3つまで
                    details_parts.append(f"- {entry.message}")

            if analysis.pattern_matches:
                details_parts.append("検出されたパターン:")
                for match in analysis.pattern_matches:
                    details_parts.append(
                        f"- {match.pattern.name}: {match.matched_text}"
                    )

            details_parts.append("")  # 空行

        return "\n".join(details_parts)

    def _format_existing_solutions(
        self, solutions: List[SolutionProposal]
    ) -> str:
        """既存の解決策をフォーマット"""
        if not solutions:
            return "既存の解決策はありません。"

        solution_parts = []
        for solution in solutions:
            solution_parts.append(f"## {solution.title}")
            solution_parts.append(f"説明: {solution.description}")
            solution_parts.append(f"信頼度: {solution.confidence}")

            if solution.steps:
                solution_parts.append("手順:")
                for i, step in enumerate(solution.steps, 1):
                    solution_parts.append(f"{i}. {step}")

            solution_parts.append("")  # 空行

        return "\n".join(solution_parts)

    def _format_current_setup(self, analysis_result: AnalysisResult) -> str:
        """現在の設定をフォーマット"""
        repo = analysis_result.repository_context
        workflow = analysis_result.workflow_context

        setup_parts = [
            f"リポジトリ名: {repo.name}",
            f"主要言語: {repo.language or 'unknown'}",
            (
                f"使用フレームワーク: "
                f"{', '.join(repo.frameworks) if repo.frameworks else 'none'}"
            ),
            f"パッケージマネージャー: {', '.join(repo.package_managers)}",
            f"ワークフロー名: {workflow.name}",
            f"トリガー条件: {workflow.trigger}",
        ]

        return "\n".join(setup_parts)

    def _format_error_patterns(
        self, error_analyses: List[ErrorAnalysis]
    ) -> str:
        """エラーパターンをフォーマット"""
        if not error_analyses:
            return "エラーパターンは検出されませんでした。"

        patterns = {}
        for analysis in error_analyses:
            for match in analysis.pattern_matches:
                category = match.pattern.category.value
                if category not in patterns:
                    patterns[category] = 0
                patterns[category] += 1

        pattern_parts = []
        for category, count in patterns.items():
            pattern_parts.append(f"- {category}: {count}個")

        return "\n".join(pattern_parts)

    def _get_error_analysis_template(self) -> str:
        """エラー解析用テンプレート"""
        return """
GitHub Actionsのワークフロー実行で発生したエラーを解析してください。

## エラーサマリー
{error_summary}

## コンテキスト情報
{context_info}

## 解析要求
1. 各エラーの根本原因を特定してください
2. エラー間の関連性を分析してください
3. 最も重要なエラーを優先度順に並べてください
4. エラーの影響範囲を評価してください

## 出力形式
- 根本原因の分析
- エラーの優先度
- 推奨される対応順序
- 追加で必要な情報
"""

    def _get_solution_generation_template(self) -> str:
        """解決策生成用テンプレート"""
        return """
GitHub Actionsのエラーに対する具体的な解決策を提案してください。

## エラー詳細
{error_details}

## 既存の解決策
{existing_solutions}

## 技術環境
- 主要言語: {repository_language}

## 解決策要求
1. 各エラーに対する具体的な解決手順を提案してください
2. コード例や設定例を含めてください
3. 解決策の実行順序を明確にしてください
4. 予防策も含めてください

## 出力形式
- エラー別の解決手順
- コード例・設定例
- 実行順序
- 予防策
"""

    def _get_best_practices_template(self) -> str:
        """ベストプラクティス用テンプレート"""
        return """
GitHub Actionsのワークフロー改善のためのベストプラクティスを提案してください。

## 現在の設定
{current_setup}

## 検出されたエラーパターン
{error_patterns}

## 改善要求
1. 現在の設定の問題点を指摘してください
2. ベストプラクティスに基づく改善案を提案してください
3. 具体的な設定例やコード例を提供してください
4. 段階的な改善計画を立ててください

## 出力形式
- 問題点の分析
- 改善案の提案
- 具体的な実装例
- 改善計画
"""

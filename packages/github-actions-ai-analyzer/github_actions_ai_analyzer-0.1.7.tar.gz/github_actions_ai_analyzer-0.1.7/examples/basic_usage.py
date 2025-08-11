"""
基本的な使用例

GitHub Actions AI Analyzerの基本的な使用方法を示します。
"""

import os
import tempfile

from github_actions_ai_analyzer import GitHubActionsAnalyzer
from github_actions_ai_analyzer.types import LogLevel


def create_sample_log():
    """サンプルログファイルを作成"""
    log_content = """
2024-01-01T12:00:00.000Z Step 1: Checkout code
2024-01-01T12:00:01.000Z Step 2: Setup Python
2024-01-01T12:00:02.000Z Step 3: Install dependencies
2024-01-01T12:00:03.000Z error: ModuleNotFoundError: No module named 'requests'
2024-01-01T12:00:04.000Z error: pip install failed
2024-01-01T12:00:05.000Z Step 4: Run tests
2024-01-01T12:00:06.000Z warning: Deprecated feature used
2024-01-01T12:00:07.000Z Step 5: Build
2024-01-01T12:00:08.000Z error: Permission denied: /tmp/build
"""

    # 一時ファイルを作成
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".log", delete=False
    ) as f:
        f.write(log_content)
        return f.name


def main():
    """メイン関数"""
    print("GitHub Actions AI Analyzer - 基本使用例")
    print("=" * 50)

    # サンプルログファイルを作成
    log_file = create_sample_log()
    print(f"サンプルログファイルを作成: {log_file}")

    try:
        # アナライザーを作成
        analyzer = GitHubActionsAnalyzer()

        # ログファイルを解析
        print("\nログファイルを解析中...")
        result = analyzer.analyze_log_file(
            log_file_path=log_file, min_log_level=LogLevel.WARNING
        )

        # 結果を表示
        print("\n解析結果:")
        print(f"解析ID: {result.analysis_id}")
        print(f"サマリー: {result.summary}")

        print(f"\nエラー分析数: {len(result.error_analyses)}")
        for i, error in enumerate(result.error_analyses, 1):
            print(f"\nエラー {i}:")
            print(f"  ID: {error.error_id}")
            print(f"  根本原因: {error.root_cause}")
            print(f"  重要度: {error.severity}")
            affected_steps = (
                ", ".join(error.affected_steps)
                if error.affected_steps
                else "なし"
            )
            print(f"  影響ステップ: {affected_steps}")
            related_files = (
                ", ".join(error.related_files)
                if error.related_files
                else "なし"
            )
            print(f"  関連ファイル: {related_files}")

        print(f"\n解決策提案数: {len(result.solution_proposals)}")
        for i, solution in enumerate(result.solution_proposals, 1):
            print(f"\n解決策 {i}:")
            print(f"  タイトル: {solution.title}")
            print(f"  説明: {solution.description}")
            print(f"  信頼度: {solution.confidence:.1%}")
            print(f"  推定時間: {solution.estimated_time or '不明'}")

        print(f"\n推奨事項数: {len(result.recommendations)}")
        for i, recommendation in enumerate(result.recommendations, 1):
            print(f"  {i}. {recommendation}")

        # AIプロンプトを生成
        print("\n" + "=" * 50)
        print("AIプロンプト生成:")

        prompt_optimizer = analyzer.ai_prompt_optimizer

        # エラー解析用プロンプト
        error_prompt = prompt_optimizer.generate_error_analysis_prompt(result)
        print("\nエラー解析用プロンプト:")
        print("-" * 30)
        print(
            error_prompt[:500] + "..."
            if len(error_prompt) > 500
            else error_prompt
        )

        # 解決策生成用プロンプト
        solution_prompt = prompt_optimizer.generate_solution_prompt(result)
        print("\n解決策生成用プロンプト:")
        print("-" * 30)
        print(
            solution_prompt[:500] + "..."
            if len(solution_prompt) > 500
            else solution_prompt
        )

    finally:
        # 一時ファイルを削除
        os.unlink(log_file)
        print(f"\n一時ファイルを削除: {log_file}")


if __name__ == "__main__":
    main()

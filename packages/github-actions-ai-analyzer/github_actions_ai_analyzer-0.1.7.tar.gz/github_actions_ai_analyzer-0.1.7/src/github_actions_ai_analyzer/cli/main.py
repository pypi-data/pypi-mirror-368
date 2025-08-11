"""
CLI メインエントリーポイント

GitHub Actions AI Analyzerのコマンドラインインターフェースのメイン関数です。
"""

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from github_actions_ai_analyzer.core.analyzer import GitHubActionsAnalyzer
from github_actions_ai_analyzer.types import AnalysisResult, LogLevel

console = Console()


@click.group()
@click.version_option(version="0.1.7")
def main() -> None:
    """GitHub Actions AI Analyzer - エラーログ解析ツール"""
    pass


@main.command()
@click.argument("log_file", type=click.Path(exists=True))
@click.option(
    "--workflow",
    "-w",
    type=click.Path(exists=True),
    help="ワークフローファイルのパス",
)
@click.option(
    "--repository", "-r", type=click.Path(exists=True), help="リポジトリのパス"
)
@click.option(
    "--min-level",
    "-l",
    type=click.Choice(["debug", "info", "warning", "error", "fatal"]),
    default="warning",
    help="最小ログレベル",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["text", "json", "yaml"]),
    default="text",
    help="出力形式",
)
def analyze(
    log_file: str, workflow: str, repository: str, min_level: str, output: str
) -> None:
    """ログファイルを解析してエラー分析を実行"""
    try:
        console.print("[bold blue]GitHub Actions AI Analyzer[/bold blue]")
        console.print(f"ログファイル: {log_file}")

        # ログレベルを変換
        valid_levels = [level.value for level in LogLevel]
        if min_level in valid_levels:
            log_level = LogLevel(min_level)
        else:
            log_level = LogLevel.WARNING

        # アナライザーを作成
        analyzer = GitHubActionsAnalyzer()

        # 解析実行
        with console.status("[bold green]解析中..."):
            result = analyzer.analyze_log_file(
                log_file_path=log_file,
                workflow_file_path=workflow,
                repository_path=repository,
                min_log_level=log_level,
            )

        # 結果を表示
        _display_analysis_result(result, output)

    except Exception as e:
        console.print(f"[bold red]エラー: {e}[/bold red]")
        raise click.Abort()


def _check_timeout_settings(jobs: dict) -> list[str]:
    """タイムアウト設定をチェック"""
    issues = []
    for job_name, job_config in jobs.items():
        if (
            isinstance(job_config, dict)
            and "timeout-minutes" not in job_config
        ):
            issues.append(
                f"ジョブ '{job_name}' にタイムアウト設定がありません"
            )
    return issues


def _check_permissions(jobs: dict) -> list[str]:
    """権限設定をチェック"""
    issues = []
    for job_name, job_config in jobs.items():
        if isinstance(job_config, dict) and "permissions" not in job_config:
            issues.append(f"ジョブ '{job_name}' に権限設定がありません")
    return issues


def _check_deprecated_actions(jobs: dict) -> list[str]:
    """非推奨アクションをチェック"""
    deprecated_actions = []
    deprecated_patterns = [
        ("actions/checkout@v2", "actions/checkout@v4"),
        ("actions/setup-python@v2", "actions/setup-python@v4"),
        ("actions/setup-python@v3", "actions/setup-python@v4"),
        ("github/codeql-action/init@v2", "github/codeql-action/init@v3"),
        (
            "github/codeql-action/autobuild@v2",
            "github/codeql-action/autobuild@v3",
        ),
        ("github/codeql-action/analyze@v2", "github/codeql-action/analyze@v3"),
        (
            "github/codeql-action/upload-sarif@v2",
            "github/codeql-action/upload-sarif@v3",
        ),
        ("actions/upload-artifact@v2", "actions/upload-artifact@v4"),
        ("actions/download-artifact@v2", "actions/download-artifact@v4"),
        ("actions/cache@v2", "actions/cache@v4"),
        ("actions/github-script@v6", "actions/github-script@v7"),
    ]

    for job_name, job_config in jobs.items():
        if isinstance(job_config, dict) and "steps" in job_config:
            steps = job_config["steps"]
            if isinstance(steps, list):
                for step in steps:
                    if isinstance(step, dict) and "uses" in step:
                        action = step["uses"]
                        for deprecated, recommended in deprecated_patterns:
                            if action == deprecated:
                                deprecated_actions.append(
                                    f"'{action}' → '{recommended}'"
                                )
                                break

    return deprecated_actions[:3]


def _check_best_practices(jobs: dict) -> list[str]:
    """ベストプラクティスをチェック"""
    best_practices = []

    # タイムアウト設定の確認
    best_practices.extend(_check_timeout_settings(jobs))

    # 権限設定の確認
    best_practices.extend(_check_permissions(jobs))

    # 非推奨アクションの確認
    deprecated_actions = _check_deprecated_actions(jobs)
    if deprecated_actions:
        best_practices.extend(deprecated_actions)

    return best_practices


def _validate_workflow_file(workflow_file: str) -> dict | None:
    """ワークフローファイルを読み込み・検証"""
    try:
        with open(workflow_file, encoding="utf-8") as f:
            workflow_data = yaml.safe_load(f)

        if not isinstance(workflow_data, dict):
            console.print(
                "[bold red]エラー: ワークフローファイルが有効なYAMLではありません。[/bold red]"
            )
            return None

        return workflow_data
    except FileNotFoundError:
        console.print(
            f"[bold red]エラー: ワークフローファイルが見つかりません: {workflow_file}[/bold red]"
        )
        return None
    except yaml.YAMLError as e:
        console.print(
            f"[bold red]エラー: ワークフローファイルのYAML構文エラー: {e}[/bold red]"
        )
        return None
    except Exception as e:
        console.print(
            f"[bold red]エラー: ワークフローファイルの検証中に予期せぬエラーが発生しました: {e}[/bold red]"
        )
        return None


def _validate_workflow_structure(workflow_data: dict) -> tuple[bool, dict]:
    """ワークフロー構造を検証"""
    # 必須フィールドの確認
    required_fields = ["name", "on", "jobs"]
    missing_fields = [
        field for field in required_fields if field not in workflow_data
    ]

    # YAMLの読み込み問題を考慮して、実際のフィールドを確認
    actual_fields = list(workflow_data.keys())
    if "on" not in actual_fields and True in actual_fields:
        # onフィールドがTrueとして読み込まれている場合
        workflow_data["on"] = workflow_data[True]
        del workflow_data[True]
        missing_fields = [
            field for field in required_fields if field not in workflow_data
        ]

    if missing_fields:
        console.print(
            f"[bold red]エラー: 必須フィールドが不足しています: "
            f"{', '.join(missing_fields)}[/bold red]"
        )
        console.print(
            f"[yellow]利用可能なフィールド: {list(workflow_data.keys())}[/yellow]"
        )
        return False, {}

    # ジョブの存在を確認
    jobs = workflow_data["jobs"]
    if not isinstance(jobs, dict) or not jobs:
        console.print(
            "[bold red]エラー: ワークフローファイルに有効な'jobs'セクションが見つかりません。[/bold red]"
        )
        return False, {}

    return True, jobs


def _create_validation_table() -> Table:
    """検証結果テーブルを作成"""
    table = Table(title="ワークフローファイル検証結果")
    table.add_column("項目", style="cyan")
    table.add_column("状態", style="green")
    table.add_column("詳細", style="white")
    return table


def _validate_jobs_details(jobs: dict, table: Table) -> int:
    """ジョブの詳細を検証"""
    # ジョブ名重複チェック
    job_names = list(jobs.keys())
    if len(job_names) != len(set(job_names)):
        table.add_row(
            "ジョブ名重複", "❌ エラー", "重複したジョブ名が見つかりました"
        )
    else:
        table.add_row(
            "ジョブ名重複", "✅ 正常", "重複したジョブ名はありません"
        )

    # 各ジョブの検証
    total_steps = 0
    for job_name, job_config in jobs.items():
        if not isinstance(job_config, dict):
            table.add_row(
                f"ジョブ '{job_name}'", "❌ エラー", "無効なジョブ設定"
            )
            continue

        # ステップの確認
        steps = job_config.get("steps", [])
        if not isinstance(steps, list):
            table.add_row(
                f"ジョブ '{job_name}'",
                "❌ エラー",
                "stepsがリスト形式ではありません",
            )
            continue

        total_steps += len(steps)
        table.add_row(
            f"ジョブ '{job_name}'", "✅ 正常", f"{len(steps)}個のステップ"
        )

    return total_steps


@main.command()
@click.argument("workflow_file", type=click.Path(exists=True))
def validate(workflow_file: str) -> None:
    """ワークフローファイルを検証"""
    console.print("[bold blue]ワークフローファイル検証[/bold blue]")
    console.print(f"ファイル: {workflow_file}")

    # ファイル読み込み・検証
    workflow_data = _validate_workflow_file(workflow_file)
    if workflow_data is None:
        return

    # ワークフロー構造検証
    is_valid, jobs = _validate_workflow_structure(workflow_data)
    if not is_valid:
        return

    # テーブル作成
    table = _create_validation_table()

    # 基本情報
    required_fields = ["name", "on", "jobs"]
    table.add_row("YAML構文", "✅ 正常", "有効なYAML形式です")
    table.add_row(
        "必須フィールド",
        "✅ 正常",
        f"すべての必須フィールドが存在します: {', '.join(required_fields)}",
    )
    table.add_row(
        "ジョブ数", "✅ 正常", f"{len(jobs)}個のジョブが定義されています"
    )

    # ジョブ詳細検証
    total_steps = _validate_jobs_details(jobs, table)
    table.add_row("総ステップ数", "✅ 正常", f"{total_steps}個のステップ")

    # ベストプラクティス確認
    best_practices = _check_best_practices(jobs)
    if best_practices:
        table.add_row(
            "ベストプラクティス", "⚠️ 警告", "; ".join(best_practices[:3])
        )
    else:
        table.add_row(
            "ベストプラクティス", "✅ 正常", "推奨設定が適用されています"
        )

    console.print(table)
    console.print("[green]ワークフローファイルの検証が完了しました。[/green]")


@main.command()
@click.argument("directory", type=click.Path(exists=True))
@click.option("--interval", "-i", type=int, default=30, help="監視間隔（秒）")
def watch(directory: str, interval: int) -> None:
    """ディレクトリを監視してログファイルの変更を自動解析"""
    console.print("[bold blue]ログファイル監視[/bold blue]")
    console.print(f"ディレクトリ: {directory}")
    console.print(f"監視間隔: {interval}秒")

    # TODO: ファイル監視機能を実装
    console.print("[yellow]ファイル監視機能は未実装です[/yellow]")


def _display_analysis_result(
    result: AnalysisResult, output_format: str
) -> None:
    """解析結果を表示"""
    if output_format == "text":
        _display_text_result(result)
    elif output_format == "json":
        _display_json_result(result)
    elif output_format == "yaml":
        _display_yaml_result(result)


def _display_text_result(result: AnalysisResult) -> None:
    """テキスト形式で結果を表示"""
    # サマリー
    summary_panel = Panel(
        Text(result.summary, style="bold green"),
        title="解析サマリー",
        border_style="green",
    )
    console.print(summary_panel)

    # エラー分析
    if result.error_analyses:
        error_table = Table(title="エラー分析結果")
        error_table.add_column("ID", style="cyan")
        error_table.add_column("根本原因", style="red")
        error_table.add_column("重要度", style="yellow")
        error_table.add_column("影響ステップ", style="blue")

        for analysis in result.error_analyses:
            error_table.add_row(
                analysis.error_id,
                analysis.root_cause,
                analysis.severity,
                (
                    ", ".join(analysis.affected_steps)
                    if analysis.affected_steps
                    else "なし"
                ),
            )

        console.print(error_table)

    # 解決策提案
    if result.solution_proposals:
        solution_table = Table(title="解決策提案")
        solution_table.add_column("タイトル", style="cyan")
        solution_table.add_column("説明", style="white")
        solution_table.add_column("信頼度", style="green")
        solution_table.add_column("推定時間", style="yellow")

        for solution in result.solution_proposals:
            solution_table.add_row(
                solution.title,
                solution.description,
                f"{solution.confidence:.1%}",
                solution.estimated_time or "不明",
            )

        console.print(solution_table)

    # 推奨事項
    if result.recommendations:
        recommendations_panel = Panel(
            "\n".join([f"• {rec}" for rec in result.recommendations]),
            title="推奨事項",
            border_style="blue",
        )
        console.print(recommendations_panel)


def _display_json_result(result: AnalysisResult) -> None:
    """JSON形式で結果を表示"""
    import json

    console.print(
        json.dumps(result.model_dump(), indent=2, ensure_ascii=False)
    )


def _display_yaml_result(result: AnalysisResult) -> None:
    """YAML形式で結果を表示"""
    import yaml

    console.print(
        yaml.dump(
            result.model_dump(), default_flow_style=False, allow_unicode=True
        )
    )


if __name__ == "__main__":
    main()

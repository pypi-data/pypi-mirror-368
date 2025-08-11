"""
コンテキスト関連の型定義

リポジトリ、ワークフロー、環境のコンテキスト情報を定義します。
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RepositoryContext(BaseModel):
    """リポジトリのコンテキスト情報"""

    name: str = Field(..., description="リポジトリ名")
    owner: str = Field(..., description="リポジトリオーナー")
    default_branch: str = Field(..., description="デフォルトブランチ")
    language: Optional[str] = Field(None, description="主要言語")
    frameworks: List[str] = Field(
        default_factory=list, description="使用フレームワーク"
    )
    package_managers: List[str] = Field(
        default_factory=list, description="パッケージマネージャー"
    )
    dependencies: Dict[str, Any] = Field(
        default_factory=dict, description="依存関係情報"
    )


class WorkflowContext(BaseModel):
    """ワークフローのコンテキスト情報"""

    name: str = Field(..., description="ワークフロー名")
    file_path: str = Field(..., description="ワークフローファイルのパス")
    trigger: str = Field(..., description="トリガー条件")
    jobs: List[str] = Field(default_factory=list, description="ジョブ名リスト")
    steps: List[str] = Field(
        default_factory=list, description="ステップ名リスト"
    )
    actions: List[str] = Field(
        default_factory=list, description="使用アクションリスト"
    )
    runner: Optional[str] = Field(None, description="使用ランナー")


class EnvironmentContext(BaseModel):
    """実行環境のコンテキスト情報"""

    os: str = Field(..., description="オペレーティングシステム")
    runner_version: str = Field(..., description="ランナーバージョン")
    available_tools: List[str] = Field(
        default_factory=list, description="利用可能ツール"
    )
    environment_variables: Dict[str, str] = Field(
        default_factory=dict, description="環境変数"
    )
    working_directory: str = Field(..., description="作業ディレクトリ")

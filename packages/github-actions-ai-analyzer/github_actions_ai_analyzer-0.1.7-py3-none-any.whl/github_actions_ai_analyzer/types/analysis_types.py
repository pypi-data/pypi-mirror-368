"""
解析結果関連の型定義

解析結果と解決策提案を定義します。
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from .context_types import (
    EnvironmentContext,
    RepositoryContext,
    WorkflowContext,
)
from .log_types import LogEntry
from .pattern_types import PatternMatch


class ErrorAnalysis(BaseModel):
    """エラー解析結果"""

    error_id: str = Field(..., description="エラーID")
    log_entries: List[LogEntry] = Field(..., description="関連ログエントリ")
    pattern_matches: List[PatternMatch] = Field(
        ..., description="マッチしたパターン"
    )
    root_cause: str = Field(..., description="推定される根本原因")
    severity: str = Field(..., description="重要度")
    affected_steps: List[str] = Field(
        default_factory=list, description="影響を受けるステップ"
    )
    related_files: List[str] = Field(
        default_factory=list, description="関連ファイル"
    )


class SolutionProposal(BaseModel):
    """解決策提案"""

    solution_id: str = Field(..., description="解決策ID")
    title: str = Field(..., description="解決策タイトル")
    description: str = Field(..., description="解決策の説明")
    steps: List[str] = Field(..., description="実行手順")
    code_examples: List[str] = Field(
        default_factory=list, description="コード例"
    )
    confidence: float = Field(..., description="信頼度")
    estimated_time: Optional[str] = Field(None, description="推定所要時間")
    prerequisites: List[str] = Field(
        default_factory=list, description="前提条件"
    )


class AnalysisResult(BaseModel):
    """解析結果"""

    analysis_id: str = Field(..., description="解析ID")
    repository_context: RepositoryContext = Field(
        ..., description="リポジトリコンテキスト"
    )
    workflow_context: WorkflowContext = Field(
        ..., description="ワークフローコンテキスト"
    )
    environment_context: EnvironmentContext = Field(
        ..., description="環境コンテキスト"
    )
    error_analyses: List[ErrorAnalysis] = Field(
        ..., description="エラー解析結果"
    )
    solution_proposals: List[SolutionProposal] = Field(
        ..., description="解決策提案"
    )
    summary: str = Field(..., description="解析サマリー")
    recommendations: List[str] = Field(
        default_factory=list, description="推奨事項"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="追加メタデータ"
    )

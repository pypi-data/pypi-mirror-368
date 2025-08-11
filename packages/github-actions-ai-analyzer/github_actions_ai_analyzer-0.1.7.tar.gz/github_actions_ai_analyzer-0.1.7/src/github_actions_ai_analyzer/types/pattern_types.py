"""
パターン関連の型定義

エラーパターンとマッチング結果を定義します。
"""

from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class PatternCategory(str, Enum):
    """エラーパターンのカテゴリ"""

    DEPENDENCY = "dependency"
    PERMISSION = "permission"
    ENVIRONMENT = "environment"
    NETWORK = "network"
    SYNTAX = "syntax"
    LANGUAGE_SPECIFIC = "language_specific"


class ErrorPattern(BaseModel):
    """エラーパターン定義"""

    id: str = Field(..., description="パターンID")
    name: str = Field(..., description="パターン名")
    category: PatternCategory = Field(..., description="パターンカテゴリ")
    regex_pattern: str = Field(..., description="正規表現パターン")
    description: str = Field(..., description="パターンの説明")
    severity: str = Field(..., description="重要度")
    language: Optional[str] = Field(None, description="対象言語")
    framework: Optional[str] = Field(None, description="対象フレームワーク")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="追加メタデータ"
    )

    class Config:
        use_enum_values = True


class PatternMatch(BaseModel):
    """パターンマッチング結果"""

    pattern: ErrorPattern = Field(..., description="マッチしたパターン")
    matched_text: str = Field(..., description="マッチしたテキスト")
    start_pos: int = Field(..., description="開始位置")
    end_pos: int = Field(..., description="終了位置")
    confidence: float = Field(..., description="信頼度")
    context: Dict[str, Any] = Field(
        default_factory=dict, description="マッチングコンテキスト"
    )

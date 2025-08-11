"""
型定義パッケージ

GitHub Actions AI Analyzerで使用する型定義を提供します。
"""

from .analysis_types import AnalysisResult, ErrorAnalysis, SolutionProposal
from .context_types import (
    EnvironmentContext,
    RepositoryContext,
    WorkflowContext,
)
from .log_types import LogEntry, LogLevel, LogSource
from .pattern_types import ErrorPattern, PatternCategory, PatternMatch

__all__ = [
    # log_types
    "LogEntry",
    "LogLevel",
    "LogSource",
    # context_types
    "RepositoryContext",
    "WorkflowContext",
    "EnvironmentContext",
    # pattern_types
    "ErrorPattern",
    "PatternMatch",
    "PatternCategory",
    # analysis_types
    "AnalysisResult",
    "ErrorAnalysis",
    "SolutionProposal",
]

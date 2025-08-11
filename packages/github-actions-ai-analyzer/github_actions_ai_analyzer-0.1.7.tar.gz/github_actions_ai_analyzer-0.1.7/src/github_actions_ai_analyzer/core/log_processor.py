"""
ログプロセッサー

GitHub Actionsのログを前処理し、ノイズを除去して構造化します。
"""

import re
from datetime import datetime
from typing import Dict, List, Optional

from ..types import LogEntry, LogLevel, LogSource


class LogProcessor:
    """GitHub Actionsログの前処理を行うクラス"""

    def __init__(self) -> None:
        """初期化"""
        self.log_levels = {
            "DEBUG": LogLevel.DEBUG,
            "INFO": LogLevel.INFO,
            "WARNING": LogLevel.WARNING,
            "ERROR": LogLevel.ERROR,
            "FATAL": LogLevel.FATAL,
        }
        self.noise_patterns = [
            r"^::debug::",  # デバッグメッセージ
            r"^::notice::",  # 通知メッセージ
            r"^::warning::",  # 警告メッセージ
            r"^::error::",  # エラーメッセージ
            r"^##\[group\]",  # グループ開始
            r"^##\[endgroup\]",  # グループ終了
            r"^##\[command\]",  # コマンド実行
        ]
        self.noise_regex = re.compile("|".join(self.noise_patterns))

        # ログレベルを判定するパターン
        self.level_patterns = {
            LogLevel.ERROR: [
                r"error:",
                r"Error:",
                r"ERROR:",
                r"failed",
                r"Failed",
                r"FAILED",
                r"exception",
                r"Exception",
                r"EXCEPTION",
            ],
            LogLevel.WARNING: [
                r"warning:",
                r"Warning:",
                r"WARNING:",
                r"deprecated",
                r"Deprecated",
                r"DEPRECATED",
            ],
            LogLevel.INFO: [
                r"info:",
                r"Info:",
                r"INFO:",
            ],
        }

        self.level_regex = {}
        for level, patterns in self.level_patterns.items():
            self.level_regex[level] = re.compile("|".join(patterns))

    def process_log_file(self, log_content: str) -> List[LogEntry]:
        """ログファイルを処理して構造化されたログエントリのリストを返す"""
        lines = log_content.split("\n")
        processed_entries = []

        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue

            # ノイズ除去
            if self._is_noise(line):
                continue

            # ログエントリを作成
            entry = self._create_log_entry(line, line_num)
            if entry:
                processed_entries.append(entry)

        return processed_entries

    def _is_noise(self, line: str) -> bool:
        """行がノイズかどうかを判定"""
        return bool(self.noise_regex.match(line.strip()))

    def _create_log_entry(
        self, line: str, line_num: int
    ) -> Optional[LogEntry]:
        """ログエントリを作成"""
        # タイムスタンプを抽出
        timestamp = self._extract_timestamp(line)
        if not timestamp:
            timestamp = datetime.now()

        # ログレベルを判定
        level = self._determine_log_level(line)

        # メッセージをクリーンアップ
        message = self._clean_message(line)

        # ソースを判定
        source = self._determine_source(line)

        # ステップ名とアクション名を抽出
        step_name = self._extract_step_name(line)
        action_name = self._extract_action_name(line)

        return LogEntry(
            timestamp=timestamp,
            level=level,
            source=source,
            message=message,
            step_name=step_name,
            action_name=action_name,
            metadata={"line_number": line_num},
        )

    def _extract_timestamp(self, line: str) -> Optional[datetime]:
        """タイムスタンプを抽出"""
        # GitHub Actionsのタイムスタンプ形式を検出
        timestamp_pattern = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z)"
        match = re.search(timestamp_pattern, line)
        if match:
            try:
                return datetime.fromisoformat(
                    match.group(1).replace("Z", "+00:00")
                )
            except ValueError:
                pass
        return None

    def _determine_log_level(self, line: str) -> LogLevel:
        """ログレベルを判定"""
        for level, patterns in self.level_regex.items():
            if patterns.search(line):
                return level

        # デフォルトはINFO
        return LogLevel.INFO

    def _clean_message(self, line: str) -> str:
        """メッセージをクリーンアップ"""
        # タイムスタンプを除去
        timestamp_pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z\s*"
        cleaned = re.sub(timestamp_pattern, "", line)
        # GitHub Actionsの特殊記号を除去
        cleaned = re.sub(r"^::[^:]*::", "", cleaned)
        # 先頭の空白を除去
        cleaned = cleaned.strip()
        return cleaned

    def _determine_source(self, line: str) -> LogSource:
        """ログの発生源を判定"""
        if "::debug::" in line or "::notice::" in line:
            return LogSource.SYSTEM
        elif "::command::" in line:
            return LogSource.STEP
        elif "action" in line.lower():
            return LogSource.ACTION
        elif "workflow" in line.lower():
            return LogSource.WORKFLOW
        else:
            return LogSource.USER

    def _extract_step_name(self, line: str) -> Optional[str]:
        """ステップ名を抽出"""
        # ステップ名のパターンを検出
        step_pattern = r"Step (\d+): (.+)"
        match = re.search(step_pattern, line)
        if match:
            return match.group(2)
        return None

    def _extract_action_name(self, line: str) -> Optional[str]:
        """アクション名を抽出"""
        # アクション名のパターンを検出
        action_pattern = r"uses: (.+)"
        match = re.search(action_pattern, line)
        if match:
            return match.group(1)
        return None

    def filter_by_level(
        self, entries: List[LogEntry], min_level: LogLevel
    ) -> List[LogEntry]:
        """指定されたレベル以上のログエントリをフィルタリング"""
        level_order = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.FATAL: 4,
        }

        min_level_value = level_order.get(min_level, 0)
        return [
            entry
            for entry in entries
            if level_order.get(entry.level, 0) >= min_level_value
        ]

    def group_by_step(
        self, entries: List[LogEntry]
    ) -> Dict[str, List[LogEntry]]:
        """ステップごとにログエントリをグループ化"""
        grouped: dict[str, list[LogEntry]] = {}
        for entry in entries:
            step_name = entry.step_name or "unknown"
            if step_name not in grouped:
                grouped[step_name] = []
            grouped[step_name].append(entry)
        return grouped

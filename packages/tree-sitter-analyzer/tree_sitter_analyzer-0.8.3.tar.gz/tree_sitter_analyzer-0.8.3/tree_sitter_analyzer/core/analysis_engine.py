#!/usr/bin/env python3
"""
Unified Analysis Engine - Common Analysis System for CLI and MCP (Fixed Version)

This module provides a unified engine that serves as the center of all analysis processing.
It is commonly used by CLI, MCP, and other interfaces.

Roo Code compliance:
- Type hints: Required for all functions
- MCP logging: Log output at each step
- docstring: Google Style docstring
- Performance-focused: Singleton pattern and cache sharing
"""

import hashlib
import threading
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from ..models import AnalysisResult
from ..plugins.base import LanguagePlugin as BaseLanguagePlugin
from ..plugins.manager import PluginManager
from ..security import SecurityValidator
from ..utils import log_debug, log_error, log_info, log_performance
from .cache_service import CacheService


class UnsupportedLanguageError(Exception):
    """Unsupported language error"""

    pass


class PluginRegistry(Protocol):
    """Protocol for plugin registration management"""

    def get_plugin(self, language: str) -> Optional["LanguagePlugin"]:
        """Get language plugin"""
        ...


class LanguagePlugin(Protocol):
    """Language plugin protocol"""

    async def analyze_file(
        self, file_path: str, request: "AnalysisRequest"
    ) -> AnalysisResult:
        """File analysis"""
        ...


class PerformanceMonitor:
    """Performance monitoring (simplified version)"""

    def __init__(self) -> None:
        self._last_duration: float = 0.0
        self._monitoring_active: bool = False
        self._operation_stats: dict[str, Any] = {}
        self._total_operations: int = 0

    def measure_operation(self, operation_name: str) -> "PerformanceContext":
        """Return measurement context for operation"""
        return PerformanceContext(operation_name, self)

    def get_last_duration(self) -> float:
        """Get last operation time"""
        return self._last_duration

    def _set_duration(self, duration: float) -> None:
        """Set operation time (internal use)"""
        self._last_duration = duration

    def start_monitoring(self) -> None:
        """Start performance monitoring"""
        self._monitoring_active = True
        log_info("Performance monitoring started")

    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        self._monitoring_active = False
        log_info("Performance monitoring stopped")

    def get_operation_stats(self) -> dict[str, Any]:
        """Get operation statistics"""
        return self._operation_stats.copy()

    def get_performance_summary(self) -> dict[str, Any]:
        """Get performance summary"""
        return {
            "total_operations": self._total_operations,
            "monitoring_active": self._monitoring_active,
            "last_duration": self._last_duration,
            "operation_count": len(self._operation_stats),
        }

    def record_operation(self, operation_name: str, duration: float) -> None:
        """Record operation"""
        if self._monitoring_active:
            if operation_name not in self._operation_stats:
                self._operation_stats[operation_name] = {
                    "count": 0,
                    "total_time": 0.0,
                    "avg_time": 0.0,
                    "min_time": float("inf"),
                    "max_time": 0.0,
                }

            stats = self._operation_stats[operation_name]
            stats["count"] += 1
            stats["total_time"] += duration
            stats["avg_time"] = stats["total_time"] / stats["count"]
            stats["min_time"] = min(stats["min_time"], duration)
            stats["max_time"] = max(stats["max_time"], duration)

            self._total_operations += 1

    def clear_metrics(self) -> None:
        """メトリクスをクリア"""
        self._operation_stats.clear()
        self._total_operations = 0
        self._last_duration = 0.0
        log_info("Performance metrics cleared")


class PerformanceContext:
    """パフォーマンス測定コンテキスト"""

    def __init__(self, operation_name: str, monitor: PerformanceMonitor) -> None:
        self.operation_name = operation_name
        self.monitor = monitor
        self.start_time: float = 0.0

    def __enter__(self) -> "PerformanceContext":
        import time

        self.start_time = time.time()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        import time

        duration = time.time() - self.start_time
        self.monitor._set_duration(duration)
        self.monitor.record_operation(self.operation_name, duration)
        log_performance(self.operation_name, duration, "Operation completed")


@dataclass(frozen=True)
class AnalysisRequest:
    """
    解析リクエスト

    Attributes:
        file_path: 解析対象ファイルパス
        language: プログラミング言語（Noneの場合は自動検出）
        include_complexity: 複雑度計算を含むか
        include_details: 詳細情報を含むか
        format_type: 出力フォーマット
    """

    file_path: str
    language: str | None = None
    include_complexity: bool = True
    include_details: bool = False
    format_type: str = "json"

    @classmethod
    def from_mcp_arguments(cls, arguments: dict[str, Any]) -> "AnalysisRequest":
        """
        MCP引数から解析リクエストを作成

        Args:
            arguments: MCP引数辞書

        Returns:
            解析リクエスト
        """
        return cls(
            file_path=arguments.get("file_path", ""),
            language=arguments.get("language"),
            include_complexity=arguments.get("include_complexity", True),
            include_details=arguments.get("include_details", False),
            format_type=arguments.get("format_type", "json"),
        )


# SimplePluginRegistry removed - now using PluginManager


class UnifiedAnalysisEngine:
    """
    統一解析エンジン（修正版）

    CLI・MCP・その他のインターフェースから共通して使用される
    中央集権的な解析エンジン。シングルトンパターンで実装し、
    リソースの効率的な利用とキャッシュの共有を実現。

    修正点：
    - デストラクタでの非同期処理問題を解決
    - 明示的なクリーンアップメソッドを提供

    Attributes:
        _cache_service: キャッシュサービス
        _plugin_manager: プラグイン管理
        _performance_monitor: パフォーマンス監視
    """

    _instances: Dict[str, "UnifiedAnalysisEngine"] = {}
    _lock: threading.Lock = threading.Lock()

    def __new__(cls, project_root: str = None) -> "UnifiedAnalysisEngine":
        """シングルトンパターンでインスタンス共有 (project_root aware)"""
        # Create a key based on project_root for different instances
        instance_key = project_root or "default"

        if instance_key not in cls._instances:
            with cls._lock:
                if instance_key not in cls._instances:
                    instance = super().__new__(cls)
                    cls._instances[instance_key] = instance
                    # Mark as not initialized for this instance
                    instance._initialized = False

        return cls._instances[instance_key]

    def __init__(self, project_root: str = None) -> None:
        """初期化（一度のみ実行）"""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._cache_service = CacheService()
        self._plugin_manager = PluginManager()
        self._performance_monitor = PerformanceMonitor()
        self._security_validator = SecurityValidator(project_root)
        self._project_root = project_root

        # プラグインを自動ロード
        self._load_plugins()

        self._initialized = True

        log_info(f"UnifiedAnalysisEngine initialized with project root: {project_root}")

    def _load_plugins(self) -> None:
        """利用可能なプラグインを自動ロード"""
        log_info("Loading plugins using PluginManager...")

        try:
            # PluginManagerの自動ロード機能を使用
            loaded_plugins = self._plugin_manager.load_plugins()

            final_languages = [plugin.get_language_name() for plugin in loaded_plugins]
            log_info(
                f"Successfully loaded {len(final_languages)} language plugins: {', '.join(final_languages)}"
            )
        except Exception as e:
            log_error(f"Failed to load plugins: {e}")
            import traceback

            log_error(f"Plugin loading traceback: {traceback.format_exc()}")

    async def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """
        統一解析メソッド

        Args:
            request: 解析リクエスト

        Returns:
            解析結果

        Raises:
            UnsupportedLanguageError: サポートされていない言語
            FileNotFoundError: ファイルが見つからない
        """
        log_info(f"Starting analysis for {request.file_path}")

        # Security validation
        is_valid, error_msg = self._security_validator.validate_file_path(request.file_path)
        if not is_valid:
            log_error(f"Security validation failed for file path: {request.file_path} - {error_msg}")
            raise ValueError(f"Invalid file path: {error_msg}")

        # キャッシュチェック（CLI・MCP間で共有）
        cache_key = self._generate_cache_key(request)
        cached_result = await self._cache_service.get(cache_key)
        if cached_result:
            log_info(f"Cache hit for {request.file_path}")
            return cached_result  # type: ignore

        # 言語検出
        language = request.language or self._detect_language(request.file_path)
        log_debug(f"Detected language: {language}")

        # デバッグ：登録されているプラグインを確認
        supported_languages = self._plugin_manager.get_supported_languages()
        log_debug(f"Supported languages: {supported_languages}")
        log_debug(f"Looking for plugin for language: {language}")

        # プラグイン取得
        plugin = self._plugin_manager.get_plugin(language)
        if not plugin:
            error_msg = f"Language {language} not supported"
            log_error(error_msg)
            raise UnsupportedLanguageError(error_msg)

        log_debug(f"Found plugin for {language}: {type(plugin)}")

        # 解析実行（パフォーマンス監視付き）
        with self._performance_monitor.measure_operation(f"analyze_{language}"):
            log_debug(f"Calling plugin.analyze_file for {request.file_path}")
            result = await plugin.analyze_file(request.file_path, request)
            log_debug(
                f"Plugin returned result: success={result.success}, elements={len(result.elements) if result.elements else 0}"
            )

        # 言語情報を確実に設定
        if result.language == "unknown" or not result.language:
            result.language = language

        # キャッシュ保存
        await self._cache_service.set(cache_key, result)

        log_performance(
            "unified_analysis",
            self._performance_monitor.get_last_duration(),
            f"Analyzed {request.file_path} ({language})",
        )

        return result

    async def analyze_file(self, file_path: str) -> AnalysisResult:
        """
        Backward compatibility method for analyze_file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Analysis result
        """
        # Security validation
        is_valid, error_msg = self._security_validator.validate_file_path(file_path)
        if not is_valid:
            log_error(f"Security validation failed for file path: {file_path} - {error_msg}")
            raise ValueError(f"Invalid file path: {error_msg}")

        request = AnalysisRequest(
            file_path=file_path,
            language=None,  # Auto-detect
            include_complexity=True,
            include_details=True,
        )
        return await self.analyze(request)

    def _generate_cache_key(self, request: AnalysisRequest) -> str:
        """
        キャッシュキーを生成

        Args:
            request: 解析リクエスト

        Returns:
            ハッシュ化されたキャッシュキー
        """
        # 一意なキーを生成するための文字列を構築
        key_components = [
            request.file_path,
            str(request.language),
            str(request.include_complexity),
            str(request.include_details),
            request.format_type,
        ]

        key_string = ":".join(key_components)

        # SHA256でハッシュ化
        return hashlib.sha256(key_string.encode("utf-8")).hexdigest()

    def _detect_language(self, file_path: str) -> str:
        """
        言語検出

        Args:
            file_path: ファイルパス

        Returns:
            検出された言語
        """
        # 簡易的な拡張子ベース検出
        import os

        _, ext = os.path.splitext(file_path)

        language_map = {
            ".java": "java",
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".c": "c",
            ".cpp": "cpp",
            ".cc": "cpp",
            ".cxx": "cpp",
            ".rs": "rust",
            ".go": "go",
        }

        detected = language_map.get(ext.lower(), "unknown")
        log_debug(f"Language detection: {file_path} -> {detected}")
        return detected

    def clear_cache(self) -> None:
        """キャッシュクリア（テスト用）"""
        self._cache_service.clear()
        log_info("Analysis engine cache cleared")

    def register_plugin(self, language: str, plugin: BaseLanguagePlugin) -> None:
        """
        プラグインを登録

        Args:
            language: 言語名（互換性のため保持、実際は使用されない）
            plugin: 言語プラグイン
        """
        self._plugin_manager.register_plugin(plugin)

    def get_supported_languages(self) -> list[str]:
        """
        サポートされている言語一覧を取得

        Returns:
            サポート言語のリスト
        """
        return self._plugin_manager.get_supported_languages()

    def get_cache_stats(self) -> dict[str, Any]:
        """
        キャッシュ統計を取得

        Returns:
            キャッシュ統計情報
        """
        return self._cache_service.get_stats()

    async def invalidate_cache_pattern(self, pattern: str) -> int:
        """
        パターンに一致するキャッシュを無効化

        Args:
            pattern: 無効化するキーのパターン

        Returns:
            無効化されたキー数
        """
        return await self._cache_service.invalidate_pattern(pattern)

    def measure_operation(self, operation_name: str) -> "PerformanceContext":
        """
        パフォーマンス計測のためのコンテキストマネージャ

        Args:
            operation_name: 操作名

        Returns:
            パフォーマンス測定コンテキスト
        """
        return self._performance_monitor.measure_operation(operation_name)

    def start_monitoring(self) -> None:
        """パフォーマンス監視を開始"""
        self._performance_monitor.start_monitoring()

    def stop_monitoring(self) -> None:
        """パフォーマンス監視を停止"""
        self._performance_monitor.stop_monitoring()

    def get_operation_stats(self) -> dict[str, Any]:
        """操作統計を取得"""
        return self._performance_monitor.get_operation_stats()

    def get_performance_summary(self) -> dict[str, Any]:
        """パフォーマンス要約を取得"""
        return self._performance_monitor.get_performance_summary()

    def clear_metrics(self) -> None:
        """
        収集したパフォーマンスメトリクスをクリア

        パフォーマンス監視で収集されたメトリクスをリセットします。
        テストやデバッグ時に使用されます。
        """
        # 新しいパフォーマンスモニターインスタンスを作成してリセット
        self._performance_monitor = PerformanceMonitor()
        log_info("Performance metrics cleared")

    def cleanup(self) -> None:
        """
        明示的なリソースクリーンアップ

        テスト終了時などに明示的に呼び出してリソースをクリーンアップします。
        デストラクタでの非同期処理問題を避けるため、明示的な呼び出しが必要です。
        """
        try:
            if hasattr(self, "_cache_service"):
                self._cache_service.clear()
            if hasattr(self, "_performance_monitor"):
                self._performance_monitor.clear_metrics()
            log_debug("UnifiedAnalysisEngine cleaned up")
        except Exception as e:
            log_error(f"Error during UnifiedAnalysisEngine cleanup: {e}")

    def __del__(self) -> None:
        """
        デストラクタ - 非同期コンテキストでの問題を避けるため最小限の処理

        デストラクタでは何もしません。これは非同期コンテキストでの
        ガベージコレクション時に発生する問題を避けるためです。
        明示的なクリーンアップはcleanup()メソッドを使用してください。
        """
        # デストラクタでは何もしない（非同期コンテキストでの問題を避けるため）
        pass


# 簡易的なプラグイン実装（テスト用）
class MockLanguagePlugin:
    """テスト用のモックプラグイン"""

    def __init__(self, language: str) -> None:
        self.language = language

    def get_language_name(self) -> str:
        """言語名を取得"""
        return self.language

    def get_file_extensions(self) -> list[str]:
        """ファイル拡張子を取得"""
        return [f".{self.language}"]

    def create_extractor(self) -> None:
        """エクストラクタを作成（モック）"""
        return None

    async def analyze_file(
        self, file_path: str, request: AnalysisRequest
    ) -> AnalysisResult:
        """モック解析実装"""
        log_info(f"Mock analysis for {file_path} ({self.language})")

        # 簡易的な解析結果を返す
        return AnalysisResult(
            file_path=file_path,
            line_count=10,  # 新しいアーキテクチャ用
            elements=[],  # 新しいアーキテクチャ用
            node_count=5,  # 新しいアーキテクチャ用
            query_results={},  # 新しいアーキテクチャ用
            source_code="// Mock source code",  # 新しいアーキテクチャ用
            language=self.language,  # 言語を設定
            package=None,
            imports=[],
            classes=[],
            methods=[],
            fields=[],
            annotations=[],
            analysis_time=0.1,
            success=True,
            error_message=None,
        )


def get_analysis_engine(project_root: str = None) -> UnifiedAnalysisEngine:
    """
    統一解析エンジンのインスタンスを取得

    Args:
        project_root: Project root directory for security validation

    Returns:
        統一解析エンジンのシングルトンインスタンス
    """
    return UnifiedAnalysisEngine(project_root)

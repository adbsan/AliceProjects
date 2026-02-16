"""
Error Handling Module
全ファイルのエラーハンドリングを統合管理

全モジュールから呼び出され、エラーログ・通知・回復処理を行います
"""

import sys
import traceback
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Any
import logging
from functools import wraps


class ErrorHandler:
    """エラーハンドリングクラス"""
    
    def __init__(self):
        """初期化"""
        self.log_dir = Path(__file__).parent.parent.parent / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.log_file = self.log_dir / f"alice_{datetime.now().strftime('%Y%m%d')}.log"
        
        # ロガーの設定
        self._setup_logger()
        
        # エラーカウント
        self.error_count = {
            "critical": 0,
            "error": 0,
            "warning": 0,
            "info": 0
        }
    
    def _setup_logger(self):
        """ロガーをセットアップ"""
        self.logger = logging.getLogger("AliceProject")
        self.logger.setLevel(logging.DEBUG)
        
        # ファイルハンドラ
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # コンソールハンドラ
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # フォーマッター
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def log_error(
        self, 
        error: Exception, 
        context: str = "",
        level: str = "error"
    ):
        """
        エラーをログに記録
        
        Args:
            error: 例外オブジェクト
            context: エラーのコンテキスト
            level: ログレベル (critical/error/warning/info)
        """
        error_msg = f"[{context}] {type(error).__name__}: {str(error)}"
        trace = traceback.format_exc()
        
        # レベル別ログ
        if level == "critical":
            self.logger.critical(error_msg)
            self.logger.critical(trace)
            self.error_count["critical"] += 1
        elif level == "error":
            self.logger.error(error_msg)
            self.logger.error(trace)
            self.error_count["error"] += 1
        elif level == "warning":
            self.logger.warning(error_msg)
            self.error_count["warning"] += 1
        else:
            self.logger.info(error_msg)
            self.error_count["info"] += 1
    
    def log_info(self, message: str, context: str = ""):
        """
        情報ログを記録
        
        Args:
            message: メッセージ
            context: コンテキスト
        """
        log_msg = f"[{context}] {message}" if context else message
        self.logger.info(log_msg)
    
    def log_warning(self, message: str, context: str = ""):
        """
        警告ログを記録
        
        Args:
            message: メッセージ
            context: コンテキスト
        """
        log_msg = f"[{context}] {message}" if context else message
        self.logger.warning(log_msg)
        self.error_count["warning"] += 1
    
    def handle_exception(
        self,
        error: Exception,
        context: str = "",
        user_message: Optional[str] = None,
        recovery_action: Optional[Callable] = None
    ) -> bool:
        """
        例外を処理
        
        Args:
            error: 例外オブジェクト
            context: エラーコンテキスト
            user_message: ユーザー向けメッセージ
            recovery_action: 回復処理関数
            
        Returns:
            回復成功時True
        """
        # エラーログ
        self.log_error(error, context)
        
        # ユーザー通知
        if user_message:
            print(f"\n⚠️  {user_message}")
        
        # 回復処理
        if recovery_action:
            try:
                recovery_action()
                self.log_info(f"回復処理成功: {context}")
                return True
            except Exception as recovery_error:
                self.log_error(recovery_error, f"{context} - 回復処理失敗")
                return False
        
        return False
    
    def safe_execute(
        self,
        func: Callable,
        *args,
        context: str = "",
        default_return: Any = None,
        **kwargs
    ) -> Any:
        """
        安全に関数を実行
        
        Args:
            func: 実行する関数
            *args: 位置引数
            context: コンテキスト
            default_return: エラー時の戻り値
            **kwargs: キーワード引数
            
        Returns:
            関数の戻り値またはdefault_return
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.log_error(e, context or func.__name__)
            return default_return
    
    def get_error_summary(self) -> dict:
        """
        エラーサマリーを取得
        
        Returns:
            エラー統計辞書
        """
        return {
            "log_file": str(self.log_file),
            "error_counts": self.error_count.copy(),
            "total_errors": sum(self.error_count.values())
        }
    
    def clear_error_counts(self):
        """エラーカウントをクリア"""
        for key in self.error_count:
            self.error_count[key] = 0
        self.log_info("エラーカウントをリセットしました")
    
    def export_error_log(self, output_path: Optional[Path] = None) -> str:
        """
        エラーログをエクスポート
        
        Args:
            output_path: 出力パス
            
        Returns:
            エクスポートファイルパス
        """
        if output_path is None:
            output_path = self.log_dir / f"error_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.log_info(f"エラーログをエクスポート: {output_path}")
            return str(output_path)
        except Exception as e:
            self.log_error(e, "エラーログエクスポート")
            return ""


def error_handler_decorator(context: str = ""):
    """
    エラーハンドリングデコレーター
    
    Args:
        context: エラーコンテキスト
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            handler = get_error_handler()
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler.log_error(e, context or func.__name__)
                raise
        return wrapper
    return decorator


# シングルトンインスタンス
_error_handler_instance = None


def get_error_handler() -> ErrorHandler:
    """
    エラーハンドラーのシングルトンインスタンスを取得
    
    Returns:
        ErrorHandlerインスタンス
    """
    global _error_handler_instance
    if _error_handler_instance is None:
        _error_handler_instance = ErrorHandler()
    return _error_handler_instance

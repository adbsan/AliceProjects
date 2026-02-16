"""
Alice Project - Parts Module
機能モジュールパッケージ
"""

__version__ = "0.1.0"
__author__ = "Alice Project Team"

# モジュールのインポート
from .parts_model import PartsModel, get_model_manager
from .errorhandling import ErrorHandler, get_error_handler, error_handler_decorator
from .image_gen import ImageGenerator
from .expression import ExpressionGenerator
from .character import CharacterManager
from .dialogue import DialogueSystem
from .learning import LearningSupport

__all__ = [
    "PartsModel",
    "get_model_manager",
    "ErrorHandler",
    "get_error_handler",
    "error_handler_decorator",
    "ImageGenerator",
    "ExpressionGenerator",
    "CharacterManager",
    "DialogueSystem",
    "LearningSupport",
]

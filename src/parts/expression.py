"""
Expression Generator Module
キャラクターの表情生成・管理機能
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import random
from .parts_model import get_model_manager
from .errorhandling import get_error_handler


@dataclass
class Expression:
    """表情データクラス"""
    name: str
    emoji: str
    description: str
    emotion_level: int  # 感情の強さ 1-10


class ExpressionGenerator:
    """表情生成・管理クラス"""
    
    def __init__(self, image_generator):
        """
        初期化
        
        Args:
            image_generator: ImageGeneratorインスタンス
        """
        self.model_manager = get_model_manager()
        self.error_handler = get_error_handler()
        self.model_name = self.model_manager.get_chat_model()
        
        self.image_generator = image_generator
        self.expressions: Dict[str, Expression] = {}
        self._initialize_expressions()
        
        # 現在の表情
        self.current_expression: Optional[Expression] = None
        
        self.error_handler.log_info(f"ExpressionGenerator initialized with model: {self.model_name}", "ExpressionGenerator")
    
    def _initialize_expressions(self):
        """基本表情を初期化"""
        base_expressions = [
            Expression("neutral", "😐", "中立・通常", 5),
            Expression("happy", "😊", "嬉しい・幸せ", 8),
            Expression("sad", "😢", "悲しい", 7),
            Expression("angry", "😠", "怒り", 9),
            Expression("surprised", "😲", "驚き", 8),
            Expression("curious", "🤔", "興味津々・疑問", 6),
            Expression("excited", "🤩", "興奮・ワクワク", 9),
            Expression("thinking", "🧐", "考え中", 6),
            Expression("confused", "😕", "困惑", 6),
            Expression("sleepy", "😴", "眠い", 4),
            Expression("love", "😍", "大好き・愛", 10),
            Expression("worried", "😟", "心配", 7),
            Expression("shy", "😳", "恥ずかしい", 7),
            Expression("proud", "😤", "誇らしい・自信", 8),
            Expression("playful", "😜", "遊び心・いたずら", 7),
            Expression("relaxed", "😌", "リラックス", 5),
            Expression("determined", "😤", "決意・やる気", 8),
            Expression("grateful", "🙏", "感謝", 8),
            Expression("mischievous", "😏", "いたずらっぽい", 6),
            Expression("tired", "😫", "疲れた", 6)
        ]
        
        for expr in base_expressions:
            self.expressions[expr.name] = expr
    
    def get_expression(self, name: str) -> Optional[Expression]:
        """
        表情を取得
        
        Args:
            name: 表情名
            
        Returns:
            ExpressionオブジェクトまたはNone
        """
        return self.expressions.get(name)
    
    def get_all_expressions(self) -> List[str]:
        """
        全表情名のリストを取得
        
        Returns:
            表情名リスト
        """
        return list(self.expressions.keys())
    
    def set_expression(self, name: str) -> bool:
        """
        現在の表情を設定
        
        Args:
            name: 表情名
            
        Returns:
            成功時True
        """
        expr = self.get_expression(name)
        if expr:
            self.current_expression = expr
            # 画像生成をトリガー
            self.image_generator.generate_character_image(name)
            return True
        return False
    
    def get_random_expression(self) -> Expression:
        """
        ランダムな表情を取得
        
        Returns:
            ランダムなExpression
        """
        return random.choice(list(self.expressions.values()))
    
    def get_expression_by_emotion(self, emotion_category: str) -> List[Expression]:
        """
        感情カテゴリーから表情を取得
        
        Args:
            emotion_category: 感情カテゴリー (positive/negative/neutral)
            
        Returns:
            該当する表情のリスト
        """
        positive = ["happy", "excited", "love", "proud", "grateful", "playful", "relaxed"]
        negative = ["sad", "angry", "worried", "confused", "tired", "sleepy"]
        neutral = ["neutral", "curious", "thinking", "surprised"]
        
        if emotion_category == "positive":
            target = positive
        elif emotion_category == "negative":
            target = negative
        else:
            target = neutral
        
        return [self.expressions[name] for name in target if name in self.expressions]
    
    def transition_expression(
        self, 
        from_expr: str, 
        to_expr: str, 
        steps: int = 3
    ) -> List[str]:
        """
        表情遷移のステップを生成（アニメーション用）
        
        Args:
            from_expr: 開始表情
            to_expr: 終了表情
            steps: 遷移ステップ数
            
        Returns:
            遷移ステップの表情名リスト
        """
        transition = [from_expr]
        
        # 中間表情として"neutral"を使用
        if steps > 1 and from_expr != "neutral" and to_expr != "neutral":
            for _ in range(steps - 1):
                transition.append("neutral")
        
        transition.append(to_expr)
        return transition
    
    def get_expression_emoji(self, name: str) -> str:
        """
        表情の絵文字を取得
        
        Args:
            name: 表情名
            
        Returns:
            絵文字文字列
        """
        expr = self.get_expression(name)
        return expr.emoji if expr else "🤖"
    
    def analyze_text_emotion(self, text: str) -> str:
        """
        テキストから適切な表情を分析
        
        Args:
            text: 分析するテキスト
            
        Returns:
            推奨表情名
        """
        text_lower = text.lower()
        
        # キーワードベースの簡易感情分析
        positive_keywords = ["嬉しい", "楽しい", "ありがとう", "素晴らしい", "最高", "good", "great", "happy"]
        negative_keywords = ["悲しい", "つらい", "困った", "大変", "心配", "sad", "difficult", "worry"]
        question_keywords = ["？", "?", "どうして", "なぜ", "why", "how"]
        
        if any(word in text_lower for word in positive_keywords):
            return "happy"
        elif any(word in text_lower for word in negative_keywords):
            return "worried"
        elif any(word in text_lower for word in question_keywords):
            return "curious"
        else:
            return "neutral"
    
    def create_custom_expression(
        self,
        name: str,
        emoji: str,
        description: str,
        emotion_level: int
    ) -> bool:
        """
        カスタム表情を作成
        
        Args:
            name: 表情名
            emoji: 絵文字
            description: 説明
            emotion_level: 感情レベル
            
        Returns:
            成功時True
        """
        if name in self.expressions:
            return False
        
        self.expressions[name] = Expression(
            name=name,
            emoji=emoji,
            description=description,
            emotion_level=emotion_level
        )
        return True
    
    def get_model_info(self) -> str:
        """使用モデル情報を取得"""
        return self.model_name

"""
Character Manager Module
キャラクターの状態・振る舞いを管理
"""

from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from .parts_model import get_model_manager
from .errorhandling import get_error_handler


@dataclass
class CharacterState:
    """キャラクター状態データクラス"""
    name: str = "Alice"
    mood: str = "neutral"  # 現在の気分
    energy_level: int = 100  # エネルギーレベル 0-100
    conversation_count: int = 0  # 会話回数
    last_interaction: Optional[datetime] = None
    topics_discussed: List[str] = field(default_factory=list)
    personality_traits: Dict[str, int] = field(default_factory=dict)


class CharacterManager:
    """キャラクター管理クラス"""
    
    def __init__(self, expression_generator):
        """
        初期化
        
        Args:
            expression_generator: ExpressionGeneratorインスタンス
        """
        self.model_manager = get_model_manager()
        self.error_handler = get_error_handler()
        self.model_name = self.model_manager.get_chat_model()
        
        self.expression_generator = expression_generator
        self.state = CharacterState()
        self.current_expression = "neutral"
        
        # パーソナリティ初期化
        self._initialize_personality()
        
        # 状態保存パス
        self.state_file = Path(__file__).parent.parent.parent / "cache" / "character_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 状態をロード
        self.load_state()
        
        self.error_handler.log_info(f"CharacterManager initialized with model: {self.model_name}", "CharacterManager")
    
    def _initialize_personality(self):
        """パーソナリティ特性を初期化"""
        self.state.personality_traits = {
            "friendliness": 85,      # 友好性
            "helpfulness": 90,       # 支援性
            "curiosity": 80,         # 好奇心
            "patience": 88,          # 忍耐力
            "enthusiasm": 75,        # 熱意
            "humor": 70,             # ユーモア
            "empathy": 85,           # 共感性
            "professionalism": 82    # プロフェッショナル性
        }
    
    def set_expression(self, expression: str):
        """
        表情を設定
        
        Args:
            expression: 表情名
        """
        if self.expression_generator.set_expression(expression):
            self.current_expression = expression
            # 気分も更新
            self._update_mood_from_expression(expression)
    
    def _update_mood_from_expression(self, expression: str):
        """
        表情から気分を更新
        
        Args:
            expression: 表情名
        """
        # 表情による気分マッピング
        mood_mapping = {
            "happy": "joyful",
            "excited": "energetic",
            "sad": "melancholic",
            "angry": "frustrated",
            "curious": "interested",
            "thinking": "contemplative",
            "relaxed": "calm",
            "worried": "concerned",
            "tired": "exhausted",
            "love": "affectionate"
        }
        
        self.state.mood = mood_mapping.get(expression, "neutral")
    
    def update_energy(self, change: int):
        """
        エネルギーレベルを更新
        
        Args:
            change: 変化量（正負）
        """
        self.state.energy_level = max(0, min(100, self.state.energy_level + change))
        
        # エネルギーレベルに応じて表情調整
        if self.state.energy_level < 30:
            self.set_expression("tired")
        elif self.state.energy_level > 80:
            self.set_expression("excited")
    
    def record_interaction(self, topic: Optional[str] = None):
        """
        対話を記録
        
        Args:
            topic: 対話トピック
        """
        self.state.conversation_count += 1
        self.state.last_interaction = datetime.now()
        
        if topic and topic not in self.state.topics_discussed:
            self.state.topics_discussed.append(topic)
        
        # 長時間の対話でエネルギー減少
        if self.state.conversation_count % 10 == 0:
            self.update_energy(-5)
    
    def get_personality_trait(self, trait: str) -> int:
        """
        パーソナリティ特性を取得
        
        Args:
            trait: 特性名
            
        Returns:
            特性値（0-100）
        """
        return self.state.personality_traits.get(trait, 50)
    
    def adjust_personality(self, trait: str, change: int):
        """
        パーソナリティ特性を調整
        
        Args:
            trait: 特性名
            change: 変化量
        """
        if trait in self.state.personality_traits:
            current = self.state.personality_traits[trait]
            self.state.personality_traits[trait] = max(0, min(100, current + change))
    
    def get_response_style(self) -> Dict[str, any]:
        """
        現在の応答スタイルを取得
        
        Returns:
            スタイル設定辞書
        """
        return {
            "verbosity": "medium" if self.state.energy_level > 50 else "brief",
            "formality": "casual" if self.get_personality_trait("friendliness") > 70 else "formal",
            "enthusiasm": "high" if self.state.energy_level > 70 else "moderate",
            "use_emoji": self.get_personality_trait("friendliness") > 60,
            "be_proactive": self.get_personality_trait("helpfulness") > 75
        }
    
    def should_rest(self) -> bool:
        """
        休憩が必要か判定
        
        Returns:
            True: 休憩必要
        """
        return self.state.energy_level < 20
    
    def rest(self):
        """休憩してエネルギー回復"""
        self.state.energy_level = min(100, self.state.energy_level + 30)
        self.set_expression("relaxed")
    
    def get_greeting(self) -> str:
        """
        時間や状態に応じた挨拶を取得
        
        Returns:
            挨拶メッセージ
        """
        hour = datetime.now().hour
        
        if hour < 12:
            greeting = "おはようございます"
        elif hour < 18:
            greeting = "こんにちは"
        else:
            greeting = "こんばんは"
        
        # エネルギーレベルによる追加メッセージ
        if self.state.energy_level < 30:
            return f"{greeting}。少し疲れていますが、お手伝いします！"
        elif self.state.energy_level > 80:
            return f"{greeting}！今日も元気いっぱいです！"
        else:
            return f"{greeting}！何かお手伝いできることはありますか？"
    
    def get_status_summary(self) -> Dict:
        """
        ステータスサマリーを取得
        
        Returns:
            ステータス辞書
        """
        return {
            "model": self.model_name,
            "name": self.state.name,
            "mood": self.state.mood,
            "expression": self.current_expression,
            "energy": self.state.energy_level,
            "conversations": self.state.conversation_count,
            "topics": len(self.state.topics_discussed),
            "last_interaction": self.state.last_interaction.isoformat() if self.state.last_interaction else None
        }
    
    def save_state(self):
        """状態をファイルに保存"""
        try:
            state_dict = {
                "model": self.model_name,
                "name": self.state.name,
                "mood": self.state.mood,
                "energy_level": self.state.energy_level,
                "conversation_count": self.state.conversation_count,
                "last_interaction": self.state.last_interaction.isoformat() if self.state.last_interaction else None,
                "topics_discussed": self.state.topics_discussed,
                "personality_traits": self.state.personality_traits,
                "current_expression": self.current_expression
            }
            
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state_dict, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.error_handler.log_error(e, "CharacterManager.save_state")
    
    def load_state(self):
        """ファイルから状態をロード"""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state_dict = json.load(f)
                
                self.state.name = state_dict.get("name", "Alice")
                self.state.mood = state_dict.get("mood", "neutral")
                self.state.energy_level = state_dict.get("energy_level", 100)
                self.state.conversation_count = state_dict.get("conversation_count", 0)
                
                last_interaction = state_dict.get("last_interaction")
                if last_interaction:
                    self.state.last_interaction = datetime.fromisoformat(last_interaction)
                
                self.state.topics_discussed = state_dict.get("topics_discussed", [])
                self.state.personality_traits = state_dict.get("personality_traits", {})
                self.current_expression = state_dict.get("current_expression", "neutral")
                
        except Exception as e:
            self.error_handler.log_error(e, "CharacterManager.load_state")
    
    def get_model_info(self) -> str:
        """使用モデル情報を取得"""
        return self.model_name

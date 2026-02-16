"""
Dialogue System Module
AIとの対話・会話生成機能
"""

from typing import List, Dict, Optional
from datetime import datetime
import random
import re
from .parts_model import get_model_manager
from .errorhandling import get_error_handler


class DialogueSystem:
    """対話システムクラス"""
    
    def __init__(self):
        """初期化"""
        self.model_manager = get_model_manager()
        self.error_handler = get_error_handler()
        self.model_name = self.model_manager.get_chat_model()
        
        self.conversation_history: List[Dict[str, str]] = []
        self.context_memory: Dict[str, any] = {}
        
        # 応答テンプレート
        self.response_templates = self._initialize_templates()
        
        # トピック分類
        self.topics = {
            "greeting": ["こんにちは", "はじめまして", "hello", "hi", "おはよう", "こんばんは"],
            "gratitude": ["ありがとう", "感謝", "thanks", "thank you"],
            "question": ["？", "?", "どうして", "なぜ", "what", "why", "how", "いつ", "どこ"],
            "help": ["助けて", "手伝って", "help", "困った", "サポート"],
            "learning": ["勉強", "学習", "教えて", "learn", "study", "覚える"],
            "farewell": ["さようなら", "バイバイ", "またね", "goodbye", "bye", "じゃあね"]
        }
        
        self.error_handler.log_info(f"DialogueSystem initialized with model: {self.model_name}", "DialogueSystem")
    
    def _initialize_templates(self) -> Dict[str, List[str]]:
        """応答テンプレートを初期化"""
        return {
            "greeting": [
                "こんにちは！今日も一緒に頑張りましょう！✨",
                "やあ！何かお手伝いできることはありますか？😊",
                "こんにちは！どんなことに興味がありますか？🤔",
                "お会いできて嬉しいです！何でも聞いてくださいね！💫"
            ],
            "gratitude": [
                "どういたしまして！いつでもサポートしますよ！😊",
                "お役に立てて嬉しいです！他に何かありますか？✨",
                "喜んでお手伝いします！遠慮なくどうぞ！💖",
                "それは良かったです！何か他にも聞きたいことはありますか？🌟"
            ],
            "question": [
                "面白い質問ですね！一緒に考えてみましょう。🤔",
                "それについて詳しく教えてください。もっと知りたいです！✨",
                "なるほど！そういう視点もありますね。🧐",
                "興味深いですね！一緒に探求してみましょう！🔍"
            ],
            "help": [
                "大丈夫ですよ！一緒に解決しましょう。💪",
                "もちろん手伝います！具体的に教えてください。😊",
                "心配しないでください。一つずつやっていきましょう。🤝",
                "お任せください！どんなサポートが必要ですか？✨"
            ],
            "learning": [
                "学びたい気持ち、素晴らしいですね！一緒に勉強しましょう。📚",
                "わかりました！どの部分から始めますか？✏️",
                "学習のサポート、任せてください！🎓",
                "素敵な向上心ですね！私も一緒に学びたいです！🌟"
            ],
            "farewell": [
                "またお話ししましょうね！楽しみにしています！👋",
                "さようなら！いつでも戻ってきてくださいね。😊",
                "お疲れ様でした！また会いましょう！✨",
                "それでは、また次回！良い一日を！🌈"
            ],
            "default": [
                "なるほど、それは興味深いですね。もっと詳しく聞かせてください！🤔",
                "面白いお話ですね！他にも教えてもらえますか？✨",
                "もっと知りたいです！続けてください！😊",
                "そうですね、一緒に考えてみましょう。💡",
                "それについてもっとお話ししたいです！🌟"
            ]
        }
    
    def generate_response(self, user_message: str) -> str:
        """
        ユーザーメッセージに対する応答を生成
        
        Args:
            user_message: ユーザーからのメッセージ
            
        Returns:
            応答メッセージ
        """
        # 会話履歴に追加
        self.add_to_history("user", user_message)
        
        # トピック分類
        topic = self._classify_topic(user_message)
        
        # 応答生成
        response = self._generate_contextual_response(user_message, topic)
        
        # 会話履歴に追加
        self.add_to_history("alice", response)
        
        return response
    
    def _classify_topic(self, message: str) -> str:
        """
        メッセージをトピック分類
        
        Args:
            message: メッセージ
            
        Returns:
            トピック名
        """
        message_lower = message.lower()
        
        for topic, keywords in self.topics.items():
            if any(keyword in message_lower for keyword in keywords):
                return topic
        
        return "default"
    
    def _generate_contextual_response(self, message: str, topic: str) -> str:
        """
        コンテキストを考慮した応答を生成
        
        Args:
            message: ユーザーメッセージ
            topic: トピック
            
        Returns:
            応答メッセージ
        """
        # テンプレートから基本応答を選択
        if topic in self.response_templates:
            base_response = random.choice(self.response_templates[topic])
        else:
            base_response = random.choice(self.response_templates["default"])
        
        # 特定のキーワードに対する特別な応答
        response = self._add_specific_knowledge(message, base_response)
        
        # パーソナライズ
        response = self._personalize_response(response)
        
        return response
    
    def _add_specific_knowledge(self, message: str, base_response: str) -> str:
        """
        特定の知識を追加
        
        Args:
            message: ユーザーメッセージ
            base_response: 基本応答
            
        Returns:
            知識追加後の応答
        """
        message_lower = message.lower()
        
        # プログラミング関連
        if any(word in message_lower for word in ["python", "プログラミング", "コード", "コーディング"]):
            return f"{base_response}\nPythonは素晴らしい言語ですよね！何か具体的に作りたいものはありますか？🐍"
        
        # 数学関連
        elif any(word in message_lower for word in ["数学", "計算", "math", "算数"]):
            return f"{base_response}\n数学は論理的思考の基礎ですね。どの分野に興味がありますか？📐"
        
        # 勉強方法
        elif any(word in message_lower for word in ["勉強方法", "学習方法", "how to study", "効率"]):
            return f"{base_response}\n効果的な学習には、目標設定、反復、実践が大切です。一緒に計画を立てましょう！📝"
        
        # AI・機械学習
        elif any(word in message_lower for word in ["ai", "機械学習", "深層学習", "ニューラル"]):
            return f"{base_response}\nAIの分野は日進月歩ですね！具体的にどんなことを知りたいですか？🤖"
        
        # 英語学習
        elif any(word in message_lower for word in ["英語", "english", "語学"]):
            return f"{base_response}\n語学学習はコツコツが大事ですね。毎日少しずつ続けましょう！🌍"
        
        return base_response
    
    def _personalize_response(self, response: str) -> str:
        """
        応答をパーソナライズ
        
        Args:
            response: 応答メッセージ
            
        Returns:
            パーソナライズ後の応答
        """
        # 会話回数に応じて親密度を調整
        conversation_count = len(self.conversation_history)
        
        if conversation_count > 20:
            # 親しみを込めた表現
            response = response.replace("です", "ですよ")
            response = response.replace("ます", "ますね")
        
        return response
    
    def add_to_history(self, sender: str, message: str):
        """
        会話履歴に追加
        
        Args:
            sender: 送信者
            message: メッセージ
        """
        self.conversation_history.append({
            "sender": sender,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # 履歴が長くなりすぎたら古いものを削除
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
    
    def get_conversation_summary(self) -> Dict:
        """
        会話のサマリーを取得
        
        Returns:
            サマリー辞書
        """
        total_messages = len(self.conversation_history)
        user_messages = len([h for h in self.conversation_history if h["sender"] == "user"])
        alice_messages = len([h for h in self.conversation_history if h["sender"] == "alice"])
        
        return {
            "model": self.model_name,
            "total_messages": total_messages,
            "user_messages": user_messages,
            "alice_messages": alice_messages,
            "start_time": self.conversation_history[0]["timestamp"] if self.conversation_history else None,
            "last_time": self.conversation_history[-1]["timestamp"] if self.conversation_history else None
        }
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        テキストからキーワードを抽出
        
        Args:
            text: テキスト
            
        Returns:
            キーワードリスト
        """
        # 簡易的な実装：名詞っぽい単語を抽出
        words = re.findall(r'\b\w+\b', text)
        # 3文字以上の単語を抽出
        keywords = [w for w in words if len(w) >= 3]
        return keywords[:5]  # 上位5つ
    
    def get_context_summary(self) -> str:
        """
        現在のコンテキストサマリーを取得
        
        Returns:
            コンテキストサマリー文字列
        """
        if not self.conversation_history:
            return "まだ会話が始まっていません。"
        
        recent = self.conversation_history[-5:]
        topics = set()
        
        for entry in recent:
            keywords = self.extract_keywords(entry["message"])
            topics.update(keywords)
        
        return f"最近のトピック: {', '.join(list(topics)[:5])}"
    
    def clear_history(self):
        """会話履歴をクリア"""
        self.conversation_history.clear()
        self.context_memory.clear()
    
    def save_context(self, key: str, value: any):
        """
        コンテキスト情報を保存
        
        Args:
            key: キー
            value: 値
        """
        self.context_memory[key] = value
    
    def get_context(self, key: str) -> Optional[any]:
        """
        コンテキスト情報を取得
        
        Args:
            key: キー
            
        Returns:
            値またはNone
        """
        return self.context_memory.get(key)
    
    def get_model_info(self) -> str:
        """使用モデル情報を取得"""
        return self.model_name

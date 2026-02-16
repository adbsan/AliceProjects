"""
Learning Support Module
学習・教育サポート機能
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import random
from .parts_model import get_model_manager
from .errorhandling import get_error_handler


@dataclass
class LearningTopic:
    """学習トピックデータクラス"""
    name: str
    category: str
    difficulty: int  # 1-5
    resources: List[str]
    keywords: List[str]


class LearningSupport:
    """学習サポートクラス"""
    
    def __init__(self):
        """初期化"""
        self.model_manager = get_model_manager()
        self.error_handler = get_error_handler()
        self.model_name = self.model_manager.get_chat_model()
        
        self.learning_topics: Dict[str, LearningTopic] = {}
        self.user_progress: Dict[str, Dict] = {}
        self.study_sessions: List[Dict] = []
        
        # 学習トピックを初期化
        self._initialize_topics()
        
        self.error_handler.log_info(f"LearningSupport initialized with model: {self.model_name}", "LearningSupport")
    
    def _initialize_topics(self):
        """学習トピックを初期化"""
        topics = [
            LearningTopic(
                name="Python基礎",
                category="プログラミング",
                difficulty=2,
                resources=["変数", "データ型", "制御構文", "関数", "クラス"],
                keywords=["python", "プログラミング", "コーディング", "コード"]
            ),
            LearningTopic(
                name="データ構造",
                category="プログラミング",
                difficulty=3,
                resources=["リスト", "辞書", "セット", "タプル", "スタック", "キュー"],
                keywords=["データ構造", "リスト", "配列", "辞書"]
            ),
            LearningTopic(
                name="アルゴリズム",
                category="プログラミング",
                difficulty=4,
                resources=["ソート", "探索", "動的計画法", "グラフ理論"],
                keywords=["アルゴリズム", "algorithm", "最適化", "計算量"]
            ),
            LearningTopic(
                name="数学基礎",
                category="数学",
                difficulty=2,
                resources=["算数", "代数", "幾何学", "確率統計"],
                keywords=["数学", "計算", "math", "算数"]
            ),
            LearningTopic(
                name="英語学習",
                category="語学",
                difficulty=2,
                resources=["文法", "語彙", "リスニング", "スピーキング", "ライティング"],
                keywords=["英語", "english", "語学", "英会話"]
            ),
            LearningTopic(
                name="Web開発",
                category="プログラミング",
                difficulty=3,
                resources=["HTML", "CSS", "JavaScript", "React", "Node.js"],
                keywords=["web", "ウェブ", "html", "css", "javascript"]
            ),
            LearningTopic(
                name="機械学習",
                category="AI・データサイエンス",
                difficulty=4,
                resources=["教師あり学習", "教師なし学習", "ニューラルネットワーク", "深層学習"],
                keywords=["機械学習", "ai", "深層学習", "ニューラル"]
            )
        ]
        
        for topic in topics:
            self.learning_topics[topic.name] = topic
    
    def needs_support(self, message: str) -> bool:
        """
        学習サポートが必要か判定
        
        Args:
            message: メッセージ
            
        Returns:
            True: サポート必要
        """
        message_lower = message.lower()
        
        # 学習関連キーワード
        learning_keywords = [
            "教えて", "勉強", "学習", "わからない", "難しい",
            "どうやって", "方法", "学ぶ", "理解", "覚える",
            "teach", "learn", "study", "understand", "explain"
        ]
        
        return any(keyword in message_lower for keyword in learning_keywords)
    
    def provide_support(self, message: str) -> str:
        """
        学習サポートを提供
        
        Args:
            message: メッセージ
            
        Returns:
            サポートメッセージ
        """
        # トピック特定
        topic = self._identify_topic(message)
        
        if topic:
            return self._generate_topic_support(topic, message)
        else:
            return self._generate_general_support(message)
    
    def _identify_topic(self, message: str) -> Optional[LearningTopic]:
        """
        メッセージから学習トピックを特定
        
        Args:
            message: メッセージ
            
        Returns:
            LearningTopicまたはNone
        """
        message_lower = message.lower()
        
        for topic in self.learning_topics.values():
            if any(keyword in message_lower for keyword in topic.keywords):
                return topic
        
        return None
    
    def _generate_topic_support(self, topic: LearningTopic, message: str) -> str:
        """
        特定トピックのサポートを生成
        
        Args:
            topic: 学習トピック
            message: メッセージ
            
        Returns:
            サポートメッセージ
        """
        support_parts = []
        
        # トピック紹介
        support_parts.append(f"【{topic.name}】について一緒に学習しましょう！")
        
        # 難易度情報
        difficulty_text = "⭐" * topic.difficulty
        support_parts.append(f"難易度: {difficulty_text}")
        
        # リソース提案
        if topic.resources:
            resources_text = "、".join(topic.resources[:3])
            support_parts.append(f"学習項目: {resources_text}")
        
        # 学習アドバイス
        advice = self._get_learning_advice(topic.difficulty)
        support_parts.append(advice)
        
        return "\n".join(support_parts)
    
    def _generate_general_support(self, message: str) -> str:
        """
        一般的な学習サポートを生成
        
        Args:
            message: メッセージ
            
        Returns:
            サポートメッセージ
        """
        support_messages = [
            "学習の秘訣は、小さなステップを積み重ねることです！一歩ずつ進みましょう。📚",
            "わからないことがあったら、具体的に質問してくださいね。一緒に解決しましょう！💡",
            "反復練習が上達への近道です。一緒に頑張りましょう！✨",
            "まずは基礎をしっかり固めることが大切ですよ。焦らず進めましょう。🌱",
            "実際に手を動かして試してみることをお勧めします！実践が一番の学びです。💪",
            "目標を小さく分割して、一つずつクリアしていくのが効果的です！🎯"
        ]
        
        return random.choice(support_messages)
    
    def _get_learning_advice(self, difficulty: int) -> str:
        """
        難易度に応じた学習アドバイス
        
        Args:
            difficulty: 難易度(1-5)
            
        Returns:
            アドバイスメッセージ
        """
        if difficulty <= 2:
            return "💡 基礎から丁寧に学べば、必ず理解できます！一緒に頑張りましょう。"
        elif difficulty <= 3:
            return "💡 少し難しいですが、段階的に進めていきましょう。焦らず着実に！"
        else:
            return "💡 高度な内容ですが、基礎がしっかりしていれば大丈夫です！挑戦しましょう。"
    
    def create_study_plan(
        self, 
        topic_name: str, 
        duration_days: int = 7
    ) -> Dict:
        """
        学習計画を作成
        
        Args:
            topic_name: トピック名
            duration_days: 学習期間（日数）
            
        Returns:
            学習計画辞書
        """
        topic = self.learning_topics.get(topic_name)
        if not topic:
            return {"error": "トピックが見つかりません"}
        
        # 日割りの学習項目を作成
        daily_items = self._split_resources(topic.resources, duration_days)
        
        plan = {
            "model": self.model_name,
            "topic": topic_name,
            "duration": duration_days,
            "difficulty": topic.difficulty,
            "daily_plan": daily_items,
            "created_at": datetime.now().isoformat()
        }
        
        return plan
    
    def _split_resources(
        self, 
        resources: List[str], 
        days: int
    ) -> List[Dict]:
        """
        リソースを日数で分割
        
        Args:
            resources: リソースリスト
            days: 日数
            
        Returns:
            日別計画リスト
        """
        daily_plan = []
        items_per_day = max(1, len(resources) // days)
        
        for day in range(1, days + 1):
            start_idx = (day - 1) * items_per_day
            end_idx = start_idx + items_per_day
            
            if day == days:  # 最終日は残り全部
                day_resources = resources[start_idx:]
            else:
                day_resources = resources[start_idx:end_idx]
            
            daily_plan.append({
                "day": day,
                "items": day_resources,
                "goals": f"Day {day}: " + ", ".join(day_resources)
            })
        
        return daily_plan
    
    def record_study_session(
        self,
        topic: str,
        duration_minutes: int,
        notes: str = ""
    ):
        """
        学習セッションを記録
        
        Args:
            topic: トピック
            duration_minutes: 学習時間（分）
            notes: メモ
        """
        session = {
            "model": self.model_name,
            "topic": topic,
            "duration": duration_minutes,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        self.study_sessions.append(session)
        
        # 進捗を更新
        if topic not in self.user_progress:
            self.user_progress[topic] = {
                "total_time": 0,
                "session_count": 0
            }
        
        self.user_progress[topic]["total_time"] += duration_minutes
        self.user_progress[topic]["session_count"] += 1
    
    def get_progress_report(self, topic: Optional[str] = None) -> Dict:
        """
        学習進捗レポートを取得
        
        Args:
            topic: 特定トピック（Noneで全体）
            
        Returns:
            レポート辞書
        """
        if topic:
            progress = self.user_progress.get(topic, {})
            return {
                "model": self.model_name,
                "topic": topic,
                "total_time": progress.get("total_time", 0),
                "sessions": progress.get("session_count", 0)
            }
        else:
            # 全体の進捗
            total_time = sum(p.get("total_time", 0) for p in self.user_progress.values())
            total_sessions = sum(p.get("session_count", 0) for p in self.user_progress.values())
            
            return {
                "model": self.model_name,
                "total_time": total_time,
                "total_sessions": total_sessions,
                "topics_studied": len(self.user_progress),
                "progress_by_topic": self.user_progress
            }
    
    def get_quiz_question(self, topic_name: str) -> Optional[Dict]:
        """
        クイズ問題を生成
        
        Args:
            topic_name: トピック名
            
        Returns:
            問題辞書またはNone
        """
        topic = self.learning_topics.get(topic_name)
        if not topic:
            return None
        
        # 簡易的なクイズ生成
        if topic.resources:
            resource = random.choice(topic.resources)
            return {
                "model": self.model_name,
                "topic": topic_name,
                "question": f"{resource}について説明してください。",
                "type": "open",
                "hint": f"{topic.category}の基本概念です。"
            }
        
        return None
    
    def get_learning_tips(self) -> List[str]:
        """
        学習のヒントを取得
        
        Returns:
            ヒントリスト
        """
        tips = [
            "🎯 明確な目標を設定しましょう",
            "📅 毎日少しずつでも継続することが大切です",
            "✍️ 学んだことをアウトプットしてみましょう",
            "🔄 定期的に復習を行いましょう",
            "👥 わからないことは積極的に質問しましょう",
            "💪 失敗を恐れず、チャレンジしましょう",
            "🧠 理解度を確認しながら進めましょう",
            "⏰ 集中できる時間帯を見つけましょう",
            "📝 ノートを取る習慣をつけましょう",
            "🎉 小さな成功を祝いましょう"
        ]
        
        return random.sample(tips, min(3, len(tips)))
    
    def get_model_info(self) -> str:
        """使用モデル情報を取得"""
        return self.model_name

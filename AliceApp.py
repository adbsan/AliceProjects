"""
Alice Project - Main Application
AIキャラクターとの対話システム メインアプリケーション
"""

import sys
import os
from pathlib import Path
import tkinter as tk
from tkinter import ttk, scrolledtext
from typing import Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.parts import (
    get_model_manager,
    get_error_handler,
    CharacterManager,
    ExpressionGenerator,
    DialogueSystem,
    ImageGenerator,
    LearningSupport
)


class AliceApplication:
    """Aliceアプリケーション メインクラス"""
    
    def __init__(self, root: tk.Tk):
        """初期化"""
        self.root = root
        
        # モデルマネージャーとエラーハンドラー
        self.model_manager = get_model_manager()
        self.error_handler = get_error_handler()
        self.model_name = self.model_manager.get_chat_model()
        
        self.root.title("Alice - AI Character Chat System")
        self.root.geometry("1000x750")
        
        self.error_handler.log_info("Application initialized", "AliceApp")
        
        # コンポーネントの初期化
        self.image_generator: Optional[ImageGenerator] = None
        self.expression_generator: Optional[ExpressionGenerator] = None
        self.character_manager: Optional[CharacterManager] = None
        self.dialogue_system: Optional[DialogueSystem] = None
        self.learning_support: Optional[LearningSupport] = None
        
        # UI初期化
        self._setup_ui()
        
        # 非同期初期化
        self.root.after(100, self._async_init)
    
    def _setup_ui(self):
        """UIのセットアップ"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ヘッダー情報
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(
            header_frame,
            text="Alice AI Chat System",
            font=("Arial", 16, "bold")
        ).pack(side=tk.LEFT)
        
        ttk.Label(
            header_frame,
            text=f"Model: {self.model_name}",
            font=("Arial", 9),
            foreground="gray"
        ).pack(side=tk.RIGHT)
        
        # キャラクター表示エリア
        self.character_frame = ttk.LabelFrame(main_frame, text="🤖 Alice", padding="10")
        self.character_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.character_label = ttk.Label(
            self.character_frame, 
            text="キャラクター読込中...",
            font=("Arial", 12)
        )
        self.character_label.pack()
        
        # 表情状態表示
        self.expression_label = ttk.Label(
            self.character_frame,
            text="表情: 初期化中",
            font=("Arial", 10),
            foreground="blue"
        )
        self.expression_label.pack()
        
        # 対話履歴エリア
        history_frame = ttk.LabelFrame(main_frame, text="💬 対話履歴", padding="10")
        history_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.history_text = scrolledtext.ScrolledText(
            history_frame,
            wrap=tk.WORD,
            width=80,
            height=25,
            font=("Arial", 10)
        )
        self.history_text.pack(fill=tk.BOTH, expand=True)
        self.history_text.config(state=tk.DISABLED)
        
        # 入力エリア
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(input_frame, text="メッセージ:").pack(side=tk.LEFT, padx=5)
        
        self.input_entry = ttk.Entry(input_frame, width=60)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.input_entry.bind("<Return>", lambda e: self._send_message())
        
        self.send_button = ttk.Button(
            input_frame,
            text="送信",
            command=self._send_message
        )
        self.send_button.pack(side=tk.LEFT, padx=5)
        
        # ステータスバー
        self.status_var = tk.StringVar(value="初期化中...")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # グリッド設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def _async_init(self):
        """非同期初期化処理"""
        try:
            self._add_to_history("System", f"Aliceを初期化しています... (Model: {self.model_name})")
            self.error_handler.log_info("Starting async initialization", "AliceApp")
            
            # 各コンポーネントの初期化
            self.image_generator = ImageGenerator()
            self.expression_generator = ExpressionGenerator(self.image_generator)
            self.character_manager = CharacterManager(self.expression_generator)
            self.dialogue_system = DialogueSystem()
            self.learning_support = LearningSupport()
            
            # 初期表情の生成
            self.character_manager.set_expression("neutral")
            self._update_character_display()
            
            self._add_to_history("System", "✅ 初期化完了！Aliceとチャットを開始できます。")
            self.status_var.set("準備完了")
            self.error_handler.log_info("Initialization completed successfully", "AliceApp")
            
            # Aliceからの最初のメッセージ（AIが主体的に話す）
            self._alice_speak(
                "こんにちは！私はAliceです。今日はどんなことをお手伝いしましょうか？\n"
                "プログラミング、勉強、雑談... 何でも話しかけてくださいね！😊",
                "happy"
            )
            
        except Exception as e:
            self.error_handler.log_error(e, "AliceApp._async_init", level="critical")
            self._add_to_history("Error", f"❌ 初期化エラー: {str(e)}")
            self.status_var.set("エラー発生")
    
    def _send_message(self):
        """メッセージ送信処理"""
        message = self.input_entry.get().strip()
        if not message:
            return
        
        # 入力をクリア
        self.input_entry.delete(0, tk.END)
        
        # ユーザーメッセージを表示
        self._add_to_history("You", message)
        self.status_var.set("Aliceが考えています...")
        
        # Aliceの応答を生成（非同期）
        self.root.after(100, lambda: self._generate_response(message))
    
    def _generate_response(self, user_message: str):
        """Aliceの応答を生成"""
        try:
            # キャラクターの対話を記録
            self.character_manager.record_interaction()
            
            # 対話システムで応答生成
            response = self.dialogue_system.generate_response(user_message)
            
            # 学習サポートが必要か判定
            if self.learning_support.needs_support(user_message):
                support = self.learning_support.provide_support(user_message)
                response += f"\n\n💡 {support}"
            
            # 表情を決定
            expression = self._determine_expression(user_message, response)
            
            # Aliceが話す
            self._alice_speak(response, expression)
            
            # エネルギーレベルをチェック
            if self.character_manager.should_rest():
                self.root.after(1000, lambda: self._alice_speak(
                    "ちょっと疲れてきたので、少し休憩しますね💤",
                    "sleepy"
                ))
                self.character_manager.rest()
            
            self.status_var.set("準備完了")
            
        except Exception as e:
            self.error_handler.log_error(e, "AliceApp._generate_response")
            self._add_to_history("Error", f"❌ 応答生成エラー: {str(e)}")
            self.status_var.set("エラー発生")
    
    def _alice_speak(self, message: str, expression: str = "neutral"):
        """Aliceが話す"""
        # 表情を更新
        self.character_manager.set_expression(expression)
        self._update_character_display()
        
        # メッセージを表示
        self._add_to_history("Alice", message)
    
    def _determine_expression(self, user_message: str, response: str) -> str:
        """メッセージから適切な表情を決定"""
        user_lower = user_message.lower()
        
        # キーワードベースの表情判定
        if any(word in user_lower for word in ["ありがとう", "thanks", "素晴らしい", "最高", "嬉しい"]):
            return "happy"
        elif any(word in user_lower for word in ["悲しい", "つらい", "困った", "心配", "大変"]):
            return "worried"
        elif any(word in user_lower for word in ["怒", "むかつく", "最悪", "イライラ"]):
            return "sad"
        elif any(word in user_lower for word in ["？", "?", "どうして", "なぜ", "わからない"]):
            return "curious"
        elif any(word in user_lower for word in ["難しい", "複雑", "考える"]):
            return "thinking"
        elif any(word in user_lower for word in ["勉強", "学習", "教えて"]):
            return "excited"
        elif any(word in user_lower for word in ["こんにちは", "はじめまして", "hello"]):
            return "happy"
        elif any(word in user_lower for word in ["さようなら", "またね", "バイバイ"]):
            return "sad"
        else:
            return "neutral"
    
    def _update_character_display(self):
        """キャラクター表示を更新"""
        current_expression = self.character_manager.current_expression
        emoji = self.expression_generator.get_expression_emoji(current_expression)
        
        self.character_label.config(text=f"{emoji} Alice (AI Character)")
        self.expression_label.config(text=f"表情: {current_expression} | 気分: {self.character_manager.state.mood}")
    
    def _add_to_history(self, sender: str, message: str):
        """対話履歴に追加"""
        self.history_text.config(state=tk.NORMAL)
        
        # 送信者によって色分け
        if sender == "You":
            tag = "user"
            prefix = "👤 You: "
        elif sender == "Alice":
            tag = "alice"
            prefix = "🤖 Alice: "
        else:
            tag = "system"
            prefix = f"⚙️  {sender}: "
        
        self.history_text.insert(tk.END, f"{prefix}{message}\n\n")
        
        # タグ設定
        self.history_text.tag_config("user", foreground="blue")
        self.history_text.tag_config("alice", foreground="green")
        self.history_text.tag_config("system", foreground="gray")
        
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)


def main():
    """メイン実行関数"""
    print("=" * 60)
    print("Alice Project - AI Character Chat System")
    print("Model: claude-sonnet-4-20250514")
    print("=" * 60)
    
    # Tkinterのルートウィンドウ作成
    root = tk.Tk()
    
    # アプリケーション起動
    app = AliceApplication(root)
    
    # イベントループ開始
    root.mainloop()
    
    print("\nAliceを終了しました。またお会いしましょう！")


if __name__ == "__main__":
    main()

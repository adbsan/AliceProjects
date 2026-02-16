"""
Parts Model Module
音声・画像・解析モデルのダウンロードと管理

このモジュールは各パーツから呼び出され、必要なモデルを提供します
"""

import os
import requests
from pathlib import Path
from typing import Dict, Optional
import json


class PartsModel:
    """モデル管理クラス"""
    
    # モデル定義
    MODELS = {
        "chat": {
            "name": "claude-sonnet-4-20250514",
            "type": "chat",
            "provider": "anthropic"
        },
        "image_generation": {
            "name": "stable-diffusion-xl",
            "type": "image",
            "provider": "stability",
            "url": "https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0"
        },
        "speech_recognition": {
            "name": "whisper-base",
            "type": "audio",
            "provider": "openai",
            "url": "https://huggingface.co/openai/whisper-base"
        },
        "text_analysis": {
            "name": "bert-base-multilingual",
            "type": "nlp",
            "provider": "huggingface",
            "url": "https://huggingface.co/bert-base-multilingual-cased"
        },
        "emotion_detection": {
            "name": "emotion-english-distilroberta-base",
            "type": "nlp",
            "provider": "huggingface",
            "url": "https://huggingface.co/j-hartmann/emotion-english-distilroberta-base"
        }
    }
    
    def __init__(self):
        """初期化"""
        self.models_dir = Path(__file__).parent.parent.parent / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.cache_file = self.models_dir / "model_cache.json"
        self.loaded_models: Dict[str, any] = {}
        
        # キャッシュをロード
        self._load_cache()
    
    def _load_cache(self):
        """モデルキャッシュをロード"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.model_cache = json.load(f)
            except Exception as e:
                print(f"キャッシュロードエラー: {e}")
                self.model_cache = {}
        else:
            self.model_cache = {}
    
    def _save_cache(self):
        """モデルキャッシュを保存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.model_cache, f, indent=2)
        except Exception as e:
            print(f"キャッシュ保存エラー: {e}")
    
    def get_model(self, model_key: str) -> Optional[str]:
        """
        モデル情報を取得
        
        Args:
            model_key: モデルキー（chat, image_generation, etc.）
            
        Returns:
            モデル名またはNone
        """
        model_info = self.MODELS.get(model_key)
        if model_info:
            return model_info["name"]
        return None
    
    def get_chat_model(self) -> str:
        """チャットモデルを取得"""
        return self.MODELS["chat"]["name"]
    
    def get_image_model(self) -> str:
        """画像生成モデルを取得"""
        return self.MODELS["image_generation"]["name"]
    
    def get_speech_model(self) -> str:
        """音声認識モデルを取得"""
        return self.MODELS["speech_recognition"]["name"]
    
    def get_analysis_model(self) -> str:
        """テキスト解析モデルを取得"""
        return self.MODELS["text_analysis"]["name"]
    
    def get_emotion_model(self) -> str:
        """感情検出モデルを取得"""
        return self.MODELS["emotion_detection"]["name"]
    
    def download_model(self, model_key: str) -> bool:
        """
        モデルをダウンロード
        
        Args:
            model_key: モデルキー
            
        Returns:
            成功時True
        """
        model_info = self.MODELS.get(model_key)
        if not model_info:
            print(f"❌ 不明なモデル: {model_key}")
            return False
        
        # URLが存在しない場合（APIベースのモデル）
        if "url" not in model_info:
            print(f"ℹ️  {model_info['name']} はAPIベースのモデルです")
            return True
        
        model_dir = self.models_dir / model_key
        model_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📥 {model_info['name']} をダウンロード中...")
        print(f"   URL: {model_info['url']}")
        
        try:
            # TODO: 実際のモデルダウンロード実装
            # 現在はプレースホルダー
            placeholder_file = model_dir / "model_info.txt"
            with open(placeholder_file, 'w') as f:
                f.write(f"Model: {model_info['name']}\n")
                f.write(f"Type: {model_info['type']}\n")
                f.write(f"Provider: {model_info['provider']}\n")
                f.write(f"URL: {model_info.get('url', 'N/A')}\n")
            
            # キャッシュに記録
            self.model_cache[model_key] = {
                "name": model_info["name"],
                "path": str(model_dir),
                "downloaded": True
            }
            self._save_cache()
            
            print(f"✅ {model_info['name']} のダウンロード完了")
            return True
            
        except Exception as e:
            print(f"❌ ダウンロードエラー: {e}")
            return False
    
    def download_all_models(self) -> Dict[str, bool]:
        """
        全モデルをダウンロード
        
        Returns:
            各モデルのダウンロード結果
        """
        results = {}
        print("=" * 60)
        print("全モデルのダウンロードを開始します")
        print("=" * 60)
        
        for model_key in self.MODELS.keys():
            results[model_key] = self.download_model(model_key)
        
        print("\n" + "=" * 60)
        print("ダウンロード結果:")
        for key, success in results.items():
            status = "✅ 成功" if success else "❌ 失敗"
            print(f"  {key}: {status}")
        print("=" * 60)
        
        return results
    
    def is_model_downloaded(self, model_key: str) -> bool:
        """
        モデルがダウンロード済みか確認
        
        Args:
            model_key: モデルキー
            
        Returns:
            ダウンロード済みの場合True
        """
        return model_key in self.model_cache and self.model_cache[model_key].get("downloaded", False)
    
    def get_model_info(self, model_key: str) -> Optional[Dict]:
        """
        モデル情報を取得
        
        Args:
            model_key: モデルキー
            
        Returns:
            モデル情報辞書
        """
        return self.MODELS.get(model_key)
    
    def get_all_models_info(self) -> Dict:
        """
        全モデル情報を取得
        
        Returns:
            全モデルの情報辞書
        """
        return {
            "models": self.MODELS,
            "cache": self.model_cache,
            "models_dir": str(self.models_dir)
        }
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self.model_cache.clear()
        self._save_cache()
        print("✅ キャッシュをクリアしました")
    
    def remove_model(self, model_key: str) -> bool:
        """
        モデルを削除
        
        Args:
            model_key: モデルキー
            
        Returns:
            成功時True
        """
        model_dir = self.models_dir / model_key
        
        if model_dir.exists():
            try:
                import shutil
                shutil.rmtree(model_dir)
                
                if model_key in self.model_cache:
                    del self.model_cache[model_key]
                    self._save_cache()
                
                print(f"✅ {model_key} を削除しました")
                return True
            except Exception as e:
                print(f"❌ 削除エラー: {e}")
                return False
        else:
            print(f"ℹ️  {model_key} は存在しません")
            return False


# シングルトンインスタンス
_model_instance = None


def get_model_manager() -> PartsModel:
    """
    モデルマネージャーのシングルトンインスタンスを取得
    
    Returns:
        PartsModelインスタンス
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = PartsModel()
    return _model_instance

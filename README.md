# Alice Project

## 概要
AliceはAI画像生成による表情豊かなキャラクターとのインタラクティブな対話システムです。
AIが主体的にユーザーとコミュニケーションを取りながら、学習サポートを提供します。

## 特徴
- AI画像生成による表情豊かなキャラクター
- 喜怒哀楽を含む多彩な表情表現（20種類以上）
- AIが積極的に話しかける対話スタイル
- 自動学習・サポート機能
- モジュール化された拡張可能な設計

## システム要件
- Python 3.11
- venv (venvAlice)

## プロジェクト構造
```
AliceProject/
├── AliceApp.py              # メインアプリケーション（実行ファイル）
├── Code.py                  # コード解析ツール（高性能版）
├── library_manager.py       # ライブラリ管理ツール
├── requirements.txt         # 依存関係リスト
├── README.md               # このファイル
├── .gitignore              # Git除外設定
├── venvAlice/              # 仮想環境（ユーザーが作成）
├── models/                 # AIモデル格納ディレクトリ（自動生成）
├── logs/                   # ログファイル（自動生成）
└── src/
    └── parts/              # 機能モジュール
        ├── __init__.py
        ├── parts_model.py      # モデル管理（NEW!）
        ├── errorhandling.py    # エラーハンドリング（NEW!）
        ├── image_gen.py        # AI画像生成
        ├── expression.py       # 表情生成・管理
        ├── character.py        # キャラクター管理
        ├── dialogue.py         # 対話システム
        └── learning.py         # 学習サポート機能
```

## セットアップ手順

### 1. 仮想環境の作成
```bash
cd AliceProject
python -m venv venvAlice
```

### 2. 仮想環境の有効化
**Windows:**
```bash
venvAlice\Scripts\activate
```

**Mac/Linux:**
```bash
source venvAlice/bin/activate
```

### 3. 依存関係のインストール
```bash
python library_manager.py install
```

### 4. アプリケーション起動
```bash
python AliceApp.py
```

## ライブラリ管理

### ライブラリのインストール
```bash
python library_manager.py install
```

### ライブラリの更新
```bash
python library_manager.py update
```

### インストール済みライブラリの確認
```bash
python library_manager.py list
```

### 依存関係のチェック
```bash
python library_manager.py check
```

### pipのアップグレード
```bash
python library_manager.py upgrade-pip
```

## 開発ガイドライン
- **メインブロック**: `if __name__ == "__main__":` はAliceApp.pyのみに記載
- **新機能追加**: `src/parts/`配下にモジュールとして追加
- **画像生成**: 全てAI生成により動的に作成（事前準備不要）
- **表情管理**: expression.pyで20種類以上の表情を管理

## 使用技術
- **GUI**: Tkinter
- **AI画像生成**: Stable Diffusion XL (Hugging Face)
- **音声認識**: Whisper Base (OpenAI) →　VOCEBOX(変更予定)
- **テキスト解析**: BERT Multilingual
- **感情検出**: DistilRoBERTa
- **チャットモデル**: Claude Sonnet 4 (claude-sonnet-4-20250514)
- **言語**: Python 3.11
- **パッケージ管理**: pip + requirements.txt
- **エラーハンドリング**: 統合エラーハンドリングシステム
- **コード品質**: 高性能コード解析ツール

## コード解析
```bash
# プロジェクト全体を解析
python Code.py
```

解析内容:
- 静的コード解析
- コード品質メトリクス
- 潜在的なバグ検出
- パフォーマンス最適化提案
- ベストプラクティスチェック

## モデル管理
各モジュールは `parts_model.py` を通じてモデル情報を取得します。

使用モデル:
- **Chat**: claude-sonnet-4-20250514
- **Image**: stable-diffusion-xl-base-1.0
- **Speech**: whisper-base
- **Analysis**: bert-base-multilingual-cased
- **Emotion**: emotion-english-distilroberta-base

## バージョン履歴

### v0.2.0 - 2024-02-16 (アーキテクチャ改善)
- モデル管理システム追加 (parts_model.py)
- エラーハンドリングシステム追加 (errorhandling.py)
- 高性能コード解析ツール追加 (Code.py)
- 全モジュールの統合改善

### v0.1.0 - 2024-02-16 (初期リリース)
- プロジェクト初期構成
- 基本的な対話システム実装
- 表情管理システム（20種類）
- 学習サポート機能
- キャラクター状態管理
- ライブラリ管理ツール

## 更新履歴

### 2024-02-16 (v0.2.0) - アーキテクチャ改善
- **新規追加**: `src/parts/parts_model.py` - モデル管理システム
  - 全モジュールから呼び出し可能な統一モデル管理
  - 音声・画像・解析モデルのダウンロード機能
  - モデル情報の一元管理
- **新規追加**: `src/parts/errorhandling.py` - エラーハンドリングシステム
  - 全ファイルのエラーを統合管理
  - ログ記録・通知・回復処理
  - エラーサマリー・レポート機能
- **新規追加**: `Code.py` - 高性能コード解析ツール
  - 静的コード解析
  - コード品質メトリクス計算
  - 潜在的なバグ検出
  - パフォーマンス最適化提案
  - ベストプラクティスチェック
- **修正**: 全partsモジュール
  - `parts_model.py`からモデル情報を取得するように変更
  - `errorhandling.py`でエラーハンドリングを統一
  - 各モジュールのMODEL定数を削除し、動的取得に変更
- **修正**: `AliceApp.py`
  - モデルマネージャー統合
  - エラーハンドラー統合
  - ログ記録の強化

### 2024-02-16 (v0.1.0) - 初期リリース
- プロジェクト初期構成
- 基本的な対話システム実装
- 表情管理システム（20種類）
- 学習サポート機能
- キャラクター状態管理
- ライブラリ管理ツール

## ライセンス
MIT License

---

**Created by Claude AI**

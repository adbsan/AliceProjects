"""
Library Manager for Alice Project
依存関係のインストール・更新・管理を行うツール

Model: claude-sonnet-4-20250514
"""

import subprocess
import sys
import os
from pathlib import Path


class LibraryManager:
    """ライブラリ管理クラス"""
    
    MODEL = "claude-sonnet-4-20250514"
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.requirements_file = self.project_root / "requirements.txt"
        self.venv_path = self.project_root / "venvAlice"
        
    def check_venv(self):
        """仮想環境が有効化されているか確認"""
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        
        if not in_venv:
            print("⚠️  警告: 仮想環境が有効化されていません")
            print(f"次のコマンドで仮想環境を有効化してください:")
            if os.name == 'nt':  # Windows
                print(f"  {self.venv_path}\\Scripts\\activate")
            else:  # Mac/Linux
                print(f"  source {self.venv_path}/bin/activate")
            return False
        return True
    
    def install_libraries(self):
        """requirements.txtから全ライブラリをインストール"""
        print("=" * 60)
        print(f"Alice Project Library Manager")
        print(f"Model: {self.MODEL}")
        print("=" * 60)
        print("\n📦 ライブラリをインストール中...")
        
        if not self.requirements_file.exists():
            print(f"❌ エラー: {self.requirements_file} が見つかりません")
            return False
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", 
                str(self.requirements_file)
            ])
            print("\n✅ すべてのライブラリのインストールが完了しました")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n❌ インストール中にエラーが発生しました: {e}")
            return False
    
    def update_libraries(self):
        """インストール済みライブラリを最新版に更新"""
        print("=" * 60)
        print(f"Alice Project Library Manager")
        print(f"Model: {self.MODEL}")
        print("=" * 60)
        print("\n🔄 ライブラリを更新中...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--upgrade", "-r",
                str(self.requirements_file)
            ])
            print("\n✅ すべてのライブラリの更新が完了しました")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n❌ 更新中にエラーが発生しました: {e}")
            return False
    
    def list_installed(self):
        """インストール済みライブラリの一覧を表示"""
        print("=" * 60)
        print(f"Alice Project Library Manager")
        print(f"Model: {self.MODEL}")
        print("=" * 60)
        print("\n📋 インストール済みライブラリ:")
        print("-" * 60)
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list"],
                capture_output=True,
                text=True,
                check=True
            )
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"❌ エラー: {e}")
    
    def upgrade_pip(self):
        """pipを最新版にアップグレード"""
        print("=" * 60)
        print(f"Alice Project Library Manager")
        print(f"Model: {self.MODEL}")
        print("=" * 60)
        print("\n🔧 pipを最新版にアップグレード中...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--upgrade", "pip"
            ])
            print("\n✅ pipのアップグレードが完了しました")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n❌ アップグレード中にエラーが発生しました: {e}")
            return False
    
    def check_dependencies(self):
        """依存関係の整合性をチェック"""
        print("=" * 60)
        print(f"Alice Project Library Manager")
        print(f"Model: {self.MODEL}")
        print("=" * 60)
        print("\n🔍 依存関係をチェック中...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "check"
            ])
            print("\n✅ 依存関係に問題はありません")
            return True
        except subprocess.CalledProcessError:
            print("\n⚠️  依存関係に問題が見つかりました")
            return False
    
    def show_help(self):
        """ヘルプメッセージを表示"""
        help_text = f"""
{"=" * 60}
🤖 Alice Project - Library Manager
Model: {self.MODEL}
{"=" * 60}

使用方法:
  python library_manager.py [command]

コマンド:
  install     requirements.txtから全ライブラリをインストール
  update      インストール済みライブラリを最新版に更新
  list        インストール済みライブラリの一覧を表示
  check       依存関係の整合性をチェック
  upgrade-pip pipを最新版にアップグレード
  help        このヘルプメッセージを表示

例:
  python library_manager.py install
  python library_manager.py update
  python library_manager.py list
        """
        print(help_text)


def main():
    """メイン処理"""
    manager = LibraryManager()
    
    # コマンドライン引数の取得
    args = sys.argv[1:] if len(sys.argv) > 1 else ['help']
    command = args[0].lower()
    
    # 仮想環境チェック（helpコマンド以外）
    if command != 'help':
        if not manager.check_venv():
            print("\n⚠️  仮想環境を有効化してから再度実行してください")
            sys.exit(1)
    
    # コマンドの実行
    commands = {
        'install': manager.install_libraries,
        'update': manager.update_libraries,
        'list': manager.list_installed,
        'check': manager.check_dependencies,
        'upgrade-pip': manager.upgrade_pip,
        'help': manager.show_help,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"❌ 不明なコマンド: {command}")
        manager.show_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Breadcrumb Address Bar

PySide6/PyQt6用のパンくずリスト型アドレスバーライブラリです。ファイルマネージャー向けに階層的なナビゲーションを提供します。

## 特徴

- 🚀 **簡単な組み込み**: 既存のQWidgetレイアウトに数行で追加可能
- 🎨 **カスタマイズ可能**: テーマ、サイズ、スタイルを自由に調整
- ⌨️ **キーボード対応**: Tab移動、矢印キー、Enter確定
- 📁 **フォルダ選択**: 最下層ボタンクリックでフォルダ選択ポップアップ
- ⏪ **履歴機能**: 戻る/進むボタン（オプション）
- 🎯 **マルチプラットフォーム**: Windows, macOS, Linux対応

## インストール

```bash
pip install breadcrumb-addressbar
```

**注意**: このライブラリは `qt-theme-manager` に依存しています。テーマ機能を使用する場合は以下もインストールしてください：

```bash
pip install qt-theme-manager
```

## 基本的な使用方法

```python
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from breadcrumb_addressbar import BreadcrumbAddressBar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Breadcrumb Address Bar Demo")
        
        # メインウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # パンくずリスト型アドレスバーを追加
        self.addressbar = BreadcrumbAddressBar()
        self.addressbar.pathChanged.connect(self.on_path_changed)
        layout.addWidget(self.addressbar)
        
        # 初期パスを設定
        self.addressbar.setPath("/home/user/documents")
    
    def on_path_changed(self, path):
        print(f"パスが変更されました: {path}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
```

## 設定例

```python
# 見た目のカスタマイズ
addressbar.setButtonHeight(40)
addressbar.setFontSize(14)
addressbar.setSeparator(" > ")

# テーマ統合（qt-theme-manager使用）
from breadcrumb_addressbar import get_theme_manager
from theme_manager import ThemeController

theme_manager = get_theme_manager()
theme_controller = ThemeController()

# 利用可能なテーマを確認
available_themes = theme_controller.get_available_themes()
print(f"利用可能なテーマ: {list(available_themes.keys())}")

# テーマを切り替え
theme_controller.set_theme("dark")  # ダークテーマに切り替え

# 機能の有効化
addressbar.enableHistory(True)
addressbar.enableBookmarks(True)
```

## デモ

プロジェクトには包括的なデモが含まれています：

### 包括的デモ（推奨）
```bash
python -m breadcrumb_addressbar.examples.comprehensive_demo
```

このデモは以下の機能を統合しています：
- 📋 **基本機能**: パンくずリストの基本的な使用方法
- 🎨 **テーマ管理**: qt-theme-managerとの統合
- 🚀 **高度な機能**: フォルダ選択ポップアップ、キーボードナビゲーション
- ⚙️ **動的カスタマイズ**: セパレーター、サイズ、カスタムラベルの変更

## 開発・リリース

### 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/scottlz0310/BreadcrumbAddressbar.git
cd BreadcrumbAddressbar

# 仮想環境を作成
python -m venv venv
source venv/bin/activate  # Linux/macOS
# または
venv\Scripts\activate  # Windows

# 開発依存関係をインストール
pip install -e ".[dev]"
```

### テスト実行

```bash
# 全テストを実行
pytest tests/ -v

# リントチェック
black --check breadcrumb_addressbar/ tests/ examples/
isort --check-only breadcrumb_addressbar/ tests/ examples/
flake8 breadcrumb_addressbar/ tests/ examples/
```

### リリース

リリース手順の詳細は [RELEASE.md](RELEASE.md) を参照してください。

```bash
# リリーススクリプトを使用（推奨）
python scripts/release.py 1.0.0

# または手動でタグを作成
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actionsが自動的に以下を実行します：
- 全Pythonバージョンでのテスト
- リントチェック
- PyPIへの自動公開
- GitHub Releaseの作成

## 既知の問題

### WSL2環境での制限事項

WSL2（Windows Subsystem for Linux 2）環境では、PySide6のQComboBoxドロップダウンが正常に閉じない問題が確認されています。これはWSL2のGUIレンダリング（WSLg）の制限によるものです。

**影響を受ける機能:**
- デモスクリプト内のQComboBoxドロップダウン（テーマ選択、セパレーター選択、サイズ選択）
- ドロップダウンリストが選択後も表示されたままになる

**回避策:**
- Windowsネイティブ環境での実行を推奨
- または、Ubuntu等のネイティブLinux環境での実行を推奨

**注意:** この問題はBreadcrumbAddressBarライブラリ自体の問題ではなく、WSL2環境の制限です。ライブラリの機能は正常に動作します。



## 開発

### セットアップ

```bash
git clone https://github.com/scottlz0310/BreadcrumbAddressbar.git
cd BreadcrumbAddressbar
pip install -e ".[dev]"
```

### テスト実行

```bash
pytest
```

### コードフォーマット

```bash
black .
isort .
```

## 機能一覧

### ✅ Phase 1 (完了)
- 基本的なパンくずリスト表示
- クリックナビゲーション
- 省略表示機能
- 基本スタイリング

### ✅ Phase 2 (完了)
- フォルダ選択ポップアップ
- キーボードナビゲーション
- テーマ対応（qt-theme-manager統合）
- 設定可能なボタンサイズ・フォント

### 🔄 Phase 3 (予定)
- 履歴機能
- 右クリックメニュー
- ドラッグ&ドロップ
- パス直接入力モード

### 🔄 Phase 4 (予定)
- お気に入り機能
- 非同期処理
- パフォーマンス最適化
- 高度なエラーハンドリング

## ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

## 貢献

プルリクエストやイシューの報告を歓迎します！

### 開発ガイドライン
- コードは `.cursorrules` に従ってください
- 新機能追加時は段階的実装を心がけてください
- テストの追加をお願いします 
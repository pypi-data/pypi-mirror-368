# Breadcrumb Address Bar 使用方法

## インストール

### 開発環境のセットアップ

```bash
# リポジトリをクローン
git clone https://github.com/scottlz0310/BreadcrumbAddressbar.git
cd BreadcrumbAddressbar

# 仮想環境を作成
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# または
venv\Scripts\activate     # Windows

# 依存関係をインストール
pip install -e .
```

### デモの実行

```bash
# 包括的デモ（推奨）
python -m breadcrumb_addressbar.examples.comprehensive_demo
```

### 基本的な使用方法

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

## 主要機能

### 1. パス設定・取得

```python
# パスを設定
addressbar.setPath("/home/user/documents")

# 現在のパスを取得
current_path = addressbar.getPath()
```

### 2. 表示設定

```python
# 最大表示項目数
addressbar.setMaxItems(5)

# ボタン高さ
addressbar.setButtonHeight(32)

# フォントサイズ
addressbar.setFontSize(10)

# セパレーター
addressbar.setSeparator(" > ")
```

### 3. カスタムラベル

```python
# 特定のパスにカスタムラベルを設定
custom_labels = {
    "/home": "ホーム",
    "/home/user": "ユーザー",
    "/home/user/documents": "ドキュメント"
}
addressbar.setCustomLabels(custom_labels)
```

### 4. シグナル

```python
# パス変更時のシグナル
addressbar.pathChanged.connect(self.on_path_changed)

# フォルダ選択時のシグナル
addressbar.folderSelected.connect(self.on_folder_selected)

def on_path_changed(self, path):
    print(f"パス変更: {path}")

def on_folder_selected(self, path):
    print(f"フォルダ選択: {path}")
```

## デモの実行

```bash
# 基本的なデモ
python demo.py

# 詳細なサンプル
python examples/basic_example.py
```

## テストの実行

```bash
# 全テストを実行
pytest

# 詳細な出力でテスト実行
pytest -v

# 特定のテストファイルを実行
pytest tests/test_core.py
```

## プロジェクト構造

```
BreadcrumbAddressbar/
├── breadcrumb_addressbar/     # メインライブラリ
│   ├── __init__.py           # パッケージ初期化
│   ├── core.py               # メインクラス
│   └── widgets.py            # ウィジェットクラス
├── tests/                    # テスト
│   ├── __init__.py
│   └── test_core.py
├── examples/                 # 使用例
│   └── basic_example.py
├── docs/                     # ドキュメント
├── demo.py                   # デモスクリプト
├── setup.py                  # パッケージ設定
├── pyproject.toml           # プロジェクト設定（依存関係含む）
└── README.md               # プロジェクト説明
```

## 開発ガイド

### 新しい機能の追加

1. `breadcrumb_addressbar/core.py` にメソッドを追加
2. `tests/test_core.py` にテストケースを追加
3. `examples/` に使用例を追加
4. ドキュメントを更新

### コードスタイル

```bash
# コードフォーマット
black breadcrumb_addressbar/ tests/ examples/

# リントチェック
flake8 breadcrumb_addressbar/ tests/ examples/
```

## トラブルシューティング

### QApplication エラー

テスト実行時に `QApplication singleton` エラーが発生する場合：

```python
# 既存のQApplicationインスタンスを確認
app = QApplication.instance()
if app is None:
    app = QApplication([])
```

### インポートエラー

```bash
# 仮想環境が有効になっているか確認
source venv/bin/activate

# パッケージがインストールされているか確認
pip list | grep breadcrumb
```

## ライセンス

MIT License

## 貢献

プルリクエストやイシューの報告を歓迎します！ 
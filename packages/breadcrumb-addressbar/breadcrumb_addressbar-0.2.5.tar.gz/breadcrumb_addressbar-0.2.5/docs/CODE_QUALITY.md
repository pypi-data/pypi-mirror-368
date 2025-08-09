# コード品質ガイドライン

## 概要

このドキュメントは、BreadcrumbAddressbarプロジェクトのコード品質を確保するためのガイドラインとベストプラクティスを説明します。

## 品質チェックツール

### 必須ツール

1. **black** - コードフォーマッター
   - 行長: 79文字
   - 設定: `pyproject.toml`で管理

2. **isort** - import整理
   - blackプロファイル使用
   - 設定: `pyproject.toml`で管理

3. **flake8** - リント
   - 行長: 79文字
   - 無視ルール: E203, W503

4. **mypy** - 型チェック
   - 設定: `pyproject.toml`で管理
   - PySide6モジュールは無視

5. **pytest** - テスト実行
   - カバレッジレポート生成
   - Qtテストは除外

### セキュリティツール

1. **bandit** - セキュリティ脆弱性チェック
   - 中・高リスク問題を検出
   - デモコードの一時的な問題は適切に処理

2. **safety** - 依存関係の脆弱性チェック
   - 既知の脆弱性を検出

## CI/CDパイプライン

### GitHub Actions

- **test**: 複数Pythonバージョンでのテスト実行
- **lint**: コード品質チェック
- **build**: パッケージビルド
- **quality-gate**: 総合品質チェック

### 実行順序

1. テスト実行（カバレッジ付き）
2. リントチェック
3. セキュリティチェック
4. パッケージビルド
5. 品質ゲート

## コーディング規約

### 命名規則

- **ファイル名**: スネークケース (`core.py`, `logger_setup.py`)
- **クラス名**: パスカルケース (`BreadcrumbAddressBar`)
- **変数・関数名**: スネークケース (`current_path`, `update_display`)
- **定数**: 大文字スネークケース (`DEFAULT_THEME`)
- **プライベートメンバー**: アンダースコアプレフィックス (`_internal_state`)

### 型ヒント

- 関数の引数・戻り値は必須
- クラスメソッドは必須
- 変数宣言時は推奨（複雑な型の場合）

### Import規約

```python
# 標準ライブラリ
import os
import sys
from typing import List, Optional

# サードパーティ
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget

# 自作モジュール
from .themes import ThemeManager
from .logger_setup import get_logger
```

### ログ管理

- `print`関数は禁止
- `logging`モジュールまたは専用ロガーを使用
- ログレベルは適切に使い分け

## テスト戦略

### テストカバレッジ

- 目標: 80%以上
- カバレッジレポート: XML形式で出力
- Codecovとの連携

### テスト分類

1. **ユニットテスト**: 個別機能のテスト
2. **統合テスト**: モジュール間の連携テスト
3. **Qtテスト**: GUIコンポーネントのテスト（pytest-qt使用）

## セキュリティベストプラクティス

### ファイルパス処理

- ハードコーディングされたパスは避ける
- `os.path.join()`を使用
- 一時ファイルは適切に処理

### 依存関係管理

- 定期的な脆弱性チェック
- 最新バージョンの使用
- 不要な依存関係の削除

## 品質メトリクス

### 現在の状態

- ✅ テスト: 12テスト全て成功
- ✅ リント: エラーなし
- ✅ 型チェック: エラーなし
- ✅ セキュリティ: 問題なし
- ✅ カバレッジ: 適切な範囲

### 継続的改善

1. **定期的なレビュー**: 月次でのコード品質レビュー
2. **メトリクス追跡**: カバレッジ、複雑度の追跡
3. **自動化**: CI/CDパイプラインの継続的改善

## トラブルシューティング

### よくある問題

1. **行長超過**: blackで自動修正
2. **import順序**: isortで自動修正
3. **型エラー**: mypyで詳細確認
4. **セキュリティ警告**: banditで詳細確認

### 解決方法

```bash
# フォーマット修正
black breadcrumb_addressbar/

# import整理
isort breadcrumb_addressbar/

# リントチェック
flake8 breadcrumb_addressbar/

# 型チェック
mypy breadcrumb_addressbar/

# セキュリティチェック
bandit -r breadcrumb_addressbar/
```

## 参考資料

- [PEP 8](https://www.python.org/dev/peps/pep-0008/) - Pythonコーディング規約
- [Black Documentation](https://black.readthedocs.io/) - コードフォーマッター
- [MyPy Documentation](https://mypy.readthedocs.io/) - 型チェッカー
- [Bandit Documentation](https://bandit.readthedocs.io/) - セキュリティチェッカー 
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.4] - 2025-08-09

## [0.2.5] - 2025-08-09

### Added
- `tests/` に以下を追加しカバレッジを向上（合計 86%）
  - `test_core.py`, `test_widgets.py`, `test_logger_setup.py`, `test_themes.py`

### Changed
- Black/flake8/isort/mypy の設定に完全準拠するようテストを調整
- `logger_setup.py` ラッパーログ関数のテスト追加で 100% カバレッジ達成
- `widgets.py` のキーイベント分岐・サイズヒントをテストでカバーし 100% カバレッジ達成

### Fixed
- CI での Black/isort のチェック不一致を解消（line-length=79 に統一、import順修正）
- isort/flake8 の指摘（E501/W391 など）を解消

### Changed
- Popup方式を`QToolButton + QMenu`に更新（WSLg環境での自動消去安定化）
- `FolderSelectionPopup`に`populateForPath`と`exec_`エイリアスを追加
- `BreadcrumbItem`を`QToolButton`ベースに変更

### Fixed
- テスト安定化と軽微な不具合修正

## [0.2.3] - 2025-08-04

### Added
- **Code Quality Guidelines**: 包括的なコード品質ガイドラインの追加
  - `docs/CODE_QUALITY.md`の作成
  - コーディング規約、ベストプラクティス、トラブルシューティングを含む
- **Security Tools**: セキュリティチェックツールの統合
  - banditによるセキュリティ脆弱性チェック
  - safetyによる依存関係の脆弱性チェック
- **Enhanced CI/CD**: CI/CDパイプラインの強化
  - セキュリティチェックの追加
  - カバレッジレポートの生成
  - 品質ゲートの追加

### Changed
- **CI/CD Pipeline**: GitHub Actionsワークフローの改善
  - テスト実行にカバレッジレポートを追加
  - セキュリティチェック（bandit, safety）を追加
  - パッケージ検証（twine check）を追加
  - 品質ゲートジョブの追加

### Fixed
- **Code Quality**: コード品質の問題を修正
  - flake8エラー（行長超過）を修正
  - セキュリティ警告（ハードコーディングされたパス）を修正
  - 末尾の空白文字を削除
- **Security**: セキュリティベストプラクティスの適用
  - `/tmp`ディレクトリのハードコーディング問題を修正
  - `os.path.join()`を使用した安全なパス構築に変更

## [0.2.2] - 2025-08-03

### Added
- **Comprehensive Demo**: 包括的なデモスクリプトの作成
  - `comprehensive_demo.py`で全機能を統合
  - タブ形式のUIで基本機能、テーマ管理、高度な機能を分類
  - 動的カスタマイズ機能の統合
  - ログ表示機能の追加
- **Examples Package**: デモスクリプトのパッケージ化
  - `examples`ディレクトリを`breadcrumb_addressbar`パッケージ内に移動
  - pipインストール後でもデモスクリプトが実行可能に
  - `python -m breadcrumb_addressbar.examples.comprehensive_demo`で実行可能
- **Package Structure**: パッケージ構造の改善
  - `breadcrumb_addressbar/examples/__init__.py`を追加
  - モジュールとして正しく認識されるように設定

### Changed
- **Demo Consolidation**: デモスクリプトの統合
  - `basic_example.py`, `qt_theme_demo.py`, `phase2_example.py`を統合
  - WSL2問題のある`dropdown_test.py`, `dropdown_test_fix.py`を削除
  - 単一の包括的デモで全機能を紹介

### Fixed
- **Module Import**: デモスクリプトのモジュールインポート問題を解決
  - `ModuleNotFoundError: No module named 'breadcrumb_addressbar.examples'`を修正
  - パッケージ構造の統一化

## [0.2.1] - 2025-08-01

### Added
- **CI/CD Pipeline**: 完全なCI/CDパイプラインの構築
  - GitHub Actionsによる自動テスト・リント・ビルド
  - 複数Pythonバージョン（3.8-3.12）でのテスト実行
  - 自動PyPI公開機能
  - GitHub Release自動生成
- **Code Quality Tools**: コード品質向上ツールの統合
  - Black（コードフォーマット）
  - isort（import整理）
  - flake8（リント）
  - mypy（型チェック）
- **Release Automation**: リリース自動化スクリプト
  - `scripts/release.py`による自動リリースプロセス
  - バージョン管理の自動化
  - CHANGELOG.mdの自動更新

### Changed
- **Project Configuration**: プロジェクト設定の統一
  - `pyproject.toml`での一元管理
  - 79文字行長での統一フォーマット
  - 開発依存関係の整理
- **CI Workflow**: CIワークフローの改善
  - テストとlintingの分離
  - 効率的な並列実行
  - 適切な権限設定

### Fixed
- **CI Issues**: CI/CDパイプラインの問題を解決
  - mypyの設定とPySide6型スタブの問題を解決
  - GitHub Actionsの権限設定を修正
  - リリースワークフローの安定化
- **Code Formatting**: コードフォーマットの統一
  - 行の長さを79文字に統一
  - import文の整理
  - 一貫したコーディングスタイル
## [0.2.0] - 2025-07-29

### Added
- **Phase 2 Features**: フォルダ選択ポップアップ機能
  - 最下層ボタンクリックでサブフォルダ一覧表示
  - `FolderSelectionPopup`クラスの実装
  - フォルダ選択時のシグナル発火
- **Theme Integration**: `qt-theme-manager`との統合
  - 動的テーマ切り替え対応
  - ボタンスタイルの自動更新
  - セパレーター色のテーマ追従
- **Enhanced UI**: 改善されたユーザーインターフェース
  - ボタンサイズの動的変更
  - フォントサイズの動的変更
  - セパレーター文字の動的変更
- **Debug Support**: デバッグ機能の強化
  - 詳細なログ出力
  - テーマ変更時のデバッグ情報
  - ポップアップ表示時のデバッグ情報

### Changed
- **Theme System**: 内部テーマ管理から`qt-theme-manager`統合に変更
- **Signal Enhancement**: `BreadcrumbItem`のシグナルを拡張（`clicked_with_info`）
- **API Updates**: テーマ関連のAPIを`qt-theme-manager`に合わせて更新

### Fixed
- **Popup Display**: `QMenu.popup`メソッドの引数エラーを修正
- **Theme Updates**: テーマ変更時のボタン色更新問題を解決
- **Import Issues**: `QAction`のインポートエラーを修正

## [0.1.0] - 2025-07-29

### Added
- **Phase 1 Features**: 基本的なパンくずリスト機能
  - 階層ナビゲーション表示
  - クリックナビゲーション
  - 省略表示機能
  - 基本スタイリング
- **Core Components**: 主要コンポーネントの実装
  - `BreadcrumbAddressBar`: メインウィジェット
  - `BreadcrumbItem`: 個別ボタンコンポーネント
  - `ThemeManager`: テーマ管理システム
- **Project Structure**: プロジェクト基盤の構築
  - 標準的なPythonライブラリ構造
  - テスト環境の構築
  - ドキュメントの整備 
#!/usr/bin/env python3
"""
Comprehensive Demo for Breadcrumb Address Bar

This demo combines all the features from basic_example.py, qt_theme_demo.py,
and phase2_example.py:
- Basic breadcrumb functionality
- Qt Theme Manager integration
- Phase 2 features (folder selection popup, keyboard navigation)
- Dynamic customization
- File manager integration
"""

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from breadcrumb_addressbar import BreadcrumbAddressBar
from breadcrumb_addressbar.logger_setup import get_logger


class ComprehensiveDemoWindow(QMainWindow):
    """Comprehensive demo window combining all features."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Breadcrumb Address Bar - Comprehensive Demo")
        self.setGeometry(100, 100, 1200, 600)

        # ロガーをセットアップ
        self.logger = get_logger(__name__)

        # メインウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 上段: 説明セクション
        self.setup_description_section(layout)

        # 中段: コントロールセクション
        self.setup_control_section(layout)

        # 下段: アドレスバーセクション
        self.setup_addressbar_section(layout)

        # テーママネージャーをセットアップ
        self.setup_theme_manager()

        # 初期パスを設定
        self.addressbar.setPath(os.path.expanduser("~"))

        # 初期テーマを適用
        self.apply_initial_theme()

    def setup_description_section(self, layout) -> None:
        """上段: 説明セクションをセットアップ"""
        # タイトル
        self.title_label = QLabel("Breadcrumb Address Bar - 包括的デモ")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold; margin: 10px;"
        )
        layout.addWidget(self.title_label)

        # 詳細説明（スクロール可能なテキストボックス）
        from PySide6.QtWidgets import QTextEdit

        self.description_text = QTextEdit()
        self.description_text.setMaximumHeight(150)
        self.description_text.setReadOnly(True)
        html_content = """
        <div style="font-family: Arial, sans-serif; font-size: 11px;
                    line-height: 1.4; padding: 10px;">
            <h3 style="margin-top: 0;">📋 Breadcrumb Address Bar 機能説明</h3>

            <h4 style="margin: 15px 0 5px 0;">🎯 基本機能</h4>
            <p style="margin: 5px 0;">• <strong>階層ナビゲーション</strong>:
               パスを階層的に表示し、各レベルをクリックして移動</p>
            <p style="margin: 5px 0;">• <strong>フォルダ選択</strong>:
               「📁 フォルダ選択」ボタンでQFileDialogを使用したフォルダ選択</p>
            <p style="margin: 5px 0;">• <strong>パス表示</strong>:
               現在のパスをリアルタイムで表示・更新</p>

            <h4 style="margin: 15px 0 5px 0;">🎨 テーマ管理機能</h4>
            <p style="margin: 5px 0;">• <strong>qt-theme-manager統合</strong>:
               動的テーマ切り替えと自動テーマ検出</p>
            <p style="margin: 5px 0;">• <strong>一貫したスタイリング</strong>:
               ボタン色、セパレーター色のテーマ追従</p>
            <p style="margin: 5px 0;">• <strong>テーマ情報表示</strong>:
               利用可能なテーマ一覧と現在のテーマ表示</p>

            <h4 style="margin: 15px 0 5px 0;">🚀 高度な機能</h4>
            <p style="margin: 5px 0;">• <strong>フォルダ選択ポップアップ</strong>:
               最下層ボタンクリックでサブフォルダ一覧表示</p>
            <p style="margin: 5px 0;">• <strong>キーボードナビゲーション</strong>:
               Tab(移動) | Enter/Space(選択) | 矢印キー(移動) | Esc(フォーカス外)</p>
            <p style="margin: 5px 0;">• <strong>シグナル接続</strong>:
               pathChanged, folderSelectedイベントの処理</p>

            <h4 style="margin: 15px 0 5px 0;">⚙️ 動的カスタマイズ</h4>
            <p style="margin: 5px 0;">• <strong>セパレーター設定</strong>:
               なし、 > 、 / 、 \\ から選択</p>
            <p style="margin: 5px 0;">• <strong>ボタンサイズ</strong>:
               28px、32px、36px、40pxから選択</p>
            <p style="margin: 5px 0;">• <strong>最大表示項目数</strong>:
               3、5、7、10から選択</p>
            <p style="margin: 5px 0;">• <strong>カスタムラベル</strong>:
               特定のパスにアイコン付きカスタムラベル設定</p>

            <h4 style="margin: 15px 0 5px 0;">📊 操作ログ</h4>
            <p style="margin: 5px 0;">• <strong>リアルタイムログ</strong>:
               全ての操作をログ表示エリアに記録</p>
            <p style="margin: 5px 0;">• <strong>デバッグ情報</strong>:
               テーマ変更、パス変更、設定変更の詳細情報</p>
        </div>
        """
        self.description_text.setHtml(html_content)
        self.description_text.setStyleSheet(
            "QTextEdit { border-radius: 8px; margin: 5px; }"
        )
        layout.addWidget(self.description_text)

    def setup_control_section(self, layout) -> None:
        """中段: コントロールセクションをセットアップ"""
        # メインコントロールレイアウト
        controls_layout = QVBoxLayout()

        # 第1行: フォルダ選択とパス表示
        row1_layout = QHBoxLayout()

        # フォルダ選択ボタン
        self.browse_button = QPushButton("📁 フォルダ選択")
        self.browse_button.clicked.connect(self.browse_folder)
        button_style = (
            "QPushButton { padding: 10px 20px; font-weight: bold; "
            "font-size: 12px; }"
        )
        self.browse_button.setStyleSheet(button_style)
        row1_layout.addWidget(self.browse_button)

        # 現在のパス表示
        self.path_label = QLabel("パス: ")
        self.path_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        row1_layout.addWidget(self.path_label)

        row1_layout.addStretch()
        controls_layout.addLayout(row1_layout)

        # 第2行: テーマ管理
        row2_layout = QHBoxLayout()

        self.theme_label = QLabel("テーマ:")
        self.theme_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        row2_layout.addWidget(self.theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.activated.connect(self.on_theme_activated)
        self.theme_combo.setStyleSheet(
            "QComboBox { padding: 5px; font-size: 12px; }"
        )
        row2_layout.addWidget(self.theme_combo)

        # テーマ情報表示
        self.themes_label = QLabel("利用可能なテーマ: 読み込み中...")
        self.themes_label.setStyleSheet(
            "padding: 8px; border-radius: 5px; font-size: 11px;"
        )
        self.themes_label.setWordWrap(True)
        row2_layout.addWidget(self.themes_label)

        row2_layout.addStretch()
        controls_layout.addLayout(row2_layout)

        # 第3行: セパレーターとサイズ設定
        row3_layout = QHBoxLayout()

        self.separator_label = QLabel("セパレーター:")
        self.separator_label.setStyleSheet(
            "font-weight: bold; font-size: 12px;"
        )
        row3_layout.addWidget(self.separator_label)

        self.separator_combo = QComboBox()
        self.separator_combo.addItems(["なし", " > ", " / ", " \\ "])
        self.separator_combo.activated.connect(self.on_separator_activated)
        self.separator_combo.setStyleSheet(
            "QComboBox { padding: 5px; font-size: 12px; }"
        )
        row3_layout.addWidget(self.separator_combo)

        self.size_label = QLabel("ボタンサイズ:")
        self.size_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        row3_layout.addWidget(self.size_label)

        self.size_combo = QComboBox()
        self.size_combo.addItems(["28px", "32px", "36px", "40px"])
        self.size_combo.setCurrentText("32px")
        self.size_combo.activated.connect(self.on_size_activated)
        self.size_combo.setStyleSheet(
            "QComboBox { padding: 5px; font-size: 12px; }"
        )
        row3_layout.addWidget(self.size_combo)

        row3_layout.addStretch()
        controls_layout.addLayout(row3_layout)

        # 第4行: 高度な設定
        row4_layout = QHBoxLayout()

        # カスタムラベル設定
        self.custom_button = QPushButton("🏠 カスタムラベル設定")
        self.custom_button.clicked.connect(self.set_custom_labels)
        self.custom_button.setStyleSheet(
            "QPushButton { padding: 8px 16px; font-size: 12px; }"
        )
        row4_layout.addWidget(self.custom_button)

        # 最大表示項目数
        self.max_items_label = QLabel("最大表示項目:")
        self.max_items_label.setStyleSheet(
            "font-weight: bold; font-size: 12px;"
        )
        row4_layout.addWidget(self.max_items_label)

        self.max_items_combo = QComboBox()
        self.max_items_combo.addItems(["3", "5", "7", "10"])
        self.max_items_combo.setCurrentText("5")
        self.max_items_combo.activated.connect(self.on_max_items_activated)
        self.max_items_combo.setStyleSheet(
            "QComboBox { padding: 5px; font-size: 12px; }"
        )
        row4_layout.addWidget(self.max_items_combo)

        # 現在のテーマ情報
        self.current_theme_label = QLabel("現在のテーマ: 読み込み中...")
        self.current_theme_label.setStyleSheet(
            "padding: 8px; border-radius: 5px; font-size: 11px;"
        )
        self.current_theme_label.setWordWrap(True)
        row4_layout.addWidget(self.current_theme_label)

        row4_layout.addStretch()
        controls_layout.addLayout(row4_layout)

        layout.addLayout(controls_layout)

    def setup_addressbar_section(self, layout) -> None:
        """下段: アドレスバーセクションをセットアップ"""
        # アドレスバー
        self.addressbar = BreadcrumbAddressBar()
        self.addressbar.pathChanged.connect(self.on_path_changed)
        self.addressbar.folderSelected.connect(self.on_folder_selected)
        layout.addWidget(self.addressbar)

        # ログ表示
        self.log_label = QLabel("ログ: 操作ログがここに表示されます")
        log_style = (
            "padding: 10px; border-radius: 5px; font-size: 11px; "
            "margin-top: 10px;"
        )
        self.log_label.setStyleSheet(log_style)
        self.log_label.setWordWrap(True)
        layout.addWidget(self.log_label)

    def setup_theme_manager(self) -> None:
        """テーママネージャーをセットアップ"""
        try:
            try:
                # 新しいバージョン (1.0.0+) を試す
                from qt_theme_manager import ThemeController
            except ImportError:
                # 古いバージョン (0.2.x) を試す
                from theme_manager import ThemeController

            # ThemeControllerを直接使用
            self.theme_controller = ThemeController()

            # 利用可能なテーマを取得
            available_themes = self.theme_controller.get_available_themes()
            theme_names = list(available_themes.keys())

            # テーマ選択コンボボックスに追加
            self.theme_combo.addItems(theme_names)

            # 現在のテーマを設定
            current_theme = self.theme_controller.get_current_theme_name()
            if current_theme in theme_names:
                self.theme_combo.setCurrentText(current_theme)

            # テーマ情報を更新
            self.update_theme_info()

        except Exception as e:
            self.logger.error(f"テーママネージャーのセットアップに失敗: {e}")
            self.themes_label.setText("テーママネージャーが利用できません")

    def update_theme_info(self) -> None:
        """テーマ情報を更新"""
        try:
            available_themes = self.theme_controller.get_available_themes()
            current_theme = self.theme_controller.get_current_theme_name()

            themes_text = (
                f"利用可能なテーマ: {', '.join(available_themes.keys())}"
            )
            self.themes_label.setText(themes_text)
            self.current_theme_label.setText(f"現在のテーマ: {current_theme}")

        except Exception as e:
            self.logger.error(f"テーマ情報の更新に失敗: {e}")

    def apply_initial_theme(self) -> None:
        """初期テーマを適用"""
        try:
            if hasattr(self, "theme_controller"):
                # アプリケーション全体にテーマを適用
                app = QApplication.instance()
                self.theme_controller.apply_theme_to_application(app)

                # ウィンドウ自体にもテーマを適用
                self.theme_controller.apply_theme_to_widget(self)

                self.logger.info("初期テーマを適用しました")
        except Exception as e:
            self.logger.error(f"初期テーマの適用に失敗: {e}")

    def browse_folder(self) -> None:
        """フォルダ選択ダイアログを表示"""
        folder = QFileDialog.getExistingDirectory(
            self, "フォルダを選択", self.addressbar.getPath()
        )
        if folder:
            self.addressbar.setPath(folder)
            self.log_message(f"フォルダを選択: {folder}")

    def on_path_changed(self, path: str) -> None:
        """パス変更時の処理"""
        self.path_label.setText(f"パス: {path}")
        self.log_message(f"パスが変更されました: {path}")

    def on_folder_selected(self, path: str) -> None:
        """フォルダ選択時の処理"""
        self.log_message(f"フォルダが選択されました: {path}")

    def on_theme_activated(self, index: int) -> None:
        """テーマ選択時の処理"""
        theme_name = self.theme_combo.currentText()
        try:
            # テーマを設定
            self.theme_controller.set_theme(theme_name)

            # アプリケーション全体にテーマを適用
            app = QApplication.instance()
            self.theme_controller.apply_theme_to_application(app)

            # ウィンドウ自体にもテーマを適用
            self.theme_controller.apply_theme_to_widget(self)

            self.update_theme_info()
            self.log_message(f"テーマを変更しました: {theme_name}")
        except Exception as e:
            self.logger.error(f"テーマ変更に失敗: {e}")

    def on_separator_activated(self, index: int) -> None:
        """セパレーター選択時の処理"""
        separators = ["", " > ", " / ", " \\ "]
        separator = separators[index]
        self.addressbar.setSeparator(separator)
        self.log_message(f"セパレーターを変更しました: '{separator}'")

    def on_size_activated(self, index: int) -> None:
        """サイズ選択時の処理"""
        sizes = [28, 32, 36, 40]
        size = sizes[index]
        self.addressbar.setButtonHeight(size)
        self.log_message(f"ボタンサイズを変更しました: {size}px")

    def on_max_items_activated(self, index: int) -> None:
        """最大表示項目数選択時の処理"""
        max_items = [3, 5, 7, 10]
        items = max_items[index]
        self.addressbar.setMaxItems(items)
        self.log_message(f"最大表示項目数を変更しました: {items}")

    def set_custom_labels(self) -> None:
        """カスタムラベルを設定"""
        custom_labels = {
            os.path.expanduser("~"): "🏠 ホーム",
            "/": "💻 ルート",
            os.path.join(os.path.sep, "tmp"): "📁 一時ファイル",  # nosec B108
        }
        self.addressbar.setCustomLabels(custom_labels)
        self.log_message("カスタムラベルを設定しました")

    def log_message(self, message: str) -> None:
        """ログメッセージを表示"""
        self.log_label.setText(f"ログ: {message}")
        self.logger.info(message)


def main():
    """メイン関数"""
    app = QApplication(sys.argv)

    # アプリケーション情報
    app.setApplicationName("Breadcrumb Address Bar - Comprehensive Demo")
    app.setApplicationVersion("0.2.4")
    app.setOrganizationName("Your Organization")

    # ウィンドウを作成して表示
    window = ComprehensiveDemoWindow()
    window.show()

    # イベントループを開始
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Manual Test Demo for BreadcrumbAddressBar

This demo is designed to test the issues found in manual testing:
1. Dropdown list scrolling issue
2. Parent folder button behavior
3. General functionality
"""

import os
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from breadcrumb_addressbar import BreadcrumbAddressBar
from breadcrumb_addressbar.logger_setup import get_logger

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


logger = get_logger("manual_test_demo")


class ManualTestDemo(QMainWindow):
    """Manual test demo window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BreadcrumbAddressBar - Manual Test Demo")
        self.setGeometry(100, 100, 800, 400)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout
        layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("BreadcrumbAddressBar Manual Test Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            "font-size: 18px; font-weight: bold; margin: 10px;"
        )
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "テスト項目:\n"
            "1. ドロップダウンリストのスクロール: 多くのフォルダがある場合のスクロール動作\n"
            "2. 親フォルダボタン: クリック時の即座の移動動作\n"
            "3. 現在フォルダボタン: ポップアップメニューの表示\n"
            "4. キーボードナビゲーション: Tab移動、矢印キー、Enter確定"
        )
        instructions.setStyleSheet(
            "background-color: #f0f0f0; padding: 10px; border-radius: 5px;"
        )
        layout.addWidget(instructions)

        # Breadcrumb widget
        self.breadcrumb = BreadcrumbAddressBar()
        self.breadcrumb.setPath("/home/hiro/Repository/BreadcrumbAddressbar")
        self.breadcrumb.pathChanged.connect(self.on_path_changed)
        self.breadcrumb.folderSelected.connect(self.on_folder_selected)
        layout.addWidget(self.breadcrumb)

        # Control buttons
        control_layout = QHBoxLayout()

        # Test path button
        test_path_btn = QPushButton("テストパスに変更")
        test_path_btn.clicked.connect(self.set_test_path)
        control_layout.addWidget(test_path_btn)

        # Home path button
        home_btn = QPushButton("ホームに移動")
        home_btn.clicked.connect(self.go_home)
        control_layout.addWidget(home_btn)

        # Root path button
        root_btn = QPushButton("ルートに移動")
        root_btn.clicked.connect(self.go_root)
        control_layout.addWidget(root_btn)

        # Toggle popup setting
        self.popup_toggle_btn = QPushButton("全ボタンポップアップ: ON")
        self.popup_toggle_btn.clicked.connect(self.toggle_popup_setting)
        control_layout.addWidget(self.popup_toggle_btn)

        layout.addLayout(control_layout)

        # Status display
        self.status_label = QLabel("現在のパス: " + self.breadcrumb.getPath())
        self.status_label.setStyleSheet(
            "background-color: #e8f4f8; padding: 5px; border: 1px solid #ccc;"
        )
        layout.addWidget(self.status_label)

        # Event log
        self.log_label = QLabel("イベントログ:")
        self.log_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.log_label)

        self.event_log = QLabel("")
        self.event_log.setStyleSheet(
            "background-color: #f8f8f8; padding: 5px; "
            "border: 1px solid #ddd; font-family: monospace;"
        )
        self.event_log.setWordWrap(True)
        layout.addWidget(self.event_log)

        # Initialize popup setting display
        self.update_popup_setting_display()

        logger.info("Manual test demo initialized")

    def set_test_path(self):
        """Set a test path with many folders."""
        test_path = "/usr/share/doc"
        self.breadcrumb.setPath(test_path)
        self.log_event(f"テストパスに変更: {test_path}")

    def go_home(self):
        """Go to home directory."""
        home_path = str(Path.home())
        self.breadcrumb.setPath(home_path)
        self.log_event(f"ホームに移動: {home_path}")

    def go_root(self):
        """Go to root directory."""
        self.breadcrumb.setPath("/")
        self.log_event("ルートに移動: /")

    def toggle_popup_setting(self):
        """Toggle the popup for all buttons setting."""
        current_setting = self.breadcrumb.getShowPopupForAllButtons()
        new_setting = not current_setting
        self.breadcrumb.setShowPopupForAllButtons(new_setting)
        self.update_popup_setting_display()
        self.log_event(
            f"ポップアップ設定変更: {'ON' if new_setting else 'OFF'}"
        )

    def update_popup_setting_display(self):
        """Update the popup setting button display."""
        setting = self.breadcrumb.getShowPopupForAllButtons()
        self.popup_toggle_btn.setText(
            f"全ボタンポップアップ: {'ON' if setting else 'OFF'}"
        )

    def on_path_changed(self, new_path):
        """Handle path change events."""
        self.status_label.setText(f"現在のパス: {new_path}")
        self.log_event(f"パス変更: {new_path}")

    def on_folder_selected(self, folder_path):
        """Handle folder selection events."""
        self.log_event(f"フォルダ選択: {folder_path}")

    def log_event(self, message):
        """Log an event to the event log."""
        current_log = self.event_log.text()
        timestamp = QApplication.instance().property("start_time")
        if not timestamp:
            timestamp = "00:00"

        new_entry = f"[{timestamp}] {message}"
        if current_log:
            new_log = current_log + "\n" + new_entry
        else:
            new_log = new_entry

        # Keep only last 10 entries
        entries = new_log.split("\n")
        if len(entries) > 10:
            entries = entries[-10:]
            new_log = "\n".join(entries)

        self.event_log.setText(new_log)
        logger.info(f"Manual test event: {message}")


def main():
    """Main function."""
    app = QApplication(sys.argv)

    # Set start time for logging
    from PySide6.QtCore import QTime

    start_time = QTime.currentTime().toString("mm:ss")
    app.setProperty("start_time", start_time)

    # Create and show the demo window
    demo = ManualTestDemo()
    demo.show()

    logger.info("Manual test demo started")

    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

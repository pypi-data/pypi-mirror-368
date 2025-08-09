"""
Breadcrumb Item Widget

Individual breadcrumb button widget for the address bar.
"""

from typing import Optional

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QToolButton, QWidget

from .logger_setup import get_logger


class BreadcrumbItem(QToolButton):
    """
    Individual breadcrumb button widget.

    Represents a single folder level in the breadcrumb address bar.
    """

    # シグナル
    clicked_with_path = Signal(str)  # パス付きクリックシグナル
    clicked_with_info = Signal(
        str, bool
    )  # パスと最下層フラグ付きクリックシグナル

    def __init__(
        self,
        text: str,
        path: str,
        is_current: bool = False,
        parent: Optional[QWidget] = None,
    ):
        """
        Initialize the breadcrumb item.

        Args:
            text: Display text for the button
            path: Full path this button represents
            is_current: Whether this is the current folder
            parent: Parent widget
        """
        super().__init__(parent)
        self.setText(text)
        self._path = path
        self._is_current = is_current
        self._logger = get_logger("breadcrumb_addressbar.widgets")
        self._setup_ui()
        self._setup_connections()
        self._logger.debug(f"BreadcrumbItem created: {text} -> {path}")

    def _setup_ui(self) -> None:
        """Setup the UI appearance."""
        # 基本設定
        self.setAutoRaise(True)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setToolButtonStyle(Qt.ToolButtonTextOnly)

        # フォント設定
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

        # サイズ設定
        self.setMinimumHeight(32)
        self.setMaximumHeight(40)

        # スタイル設定
        self._update_style()

    def _setup_connections(self) -> None:
        """Setup signal connections."""
        self.clicked.connect(self._on_clicked)

    def keyPressEvent(self, event) -> None:
        """Handle key press events."""
        key = event.key()

        if key == Qt.Key_Return or key == Qt.Key_Enter:
            # Enterキーでクリックと同じ動作
            self._on_clicked()
            event.accept()
        elif key == Qt.Key_Space:
            # スペースキーでクリックと同じ動作
            self._on_clicked()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _on_clicked(self) -> None:
        """Handle button click."""
        self.clicked_with_path.emit(self._path)
        self.clicked_with_info.emit(self._path, self._is_current)
        self._logger.debug(
            f"Button clicked: path='{self._path}', "
            f"is_current={self._is_current}"
        )

    def _update_style(self) -> None:
        """Update the button style based on current state."""
        from .themes import get_theme_manager

        theme_manager = get_theme_manager()
        stylesheet = theme_manager.get_button_stylesheet(self._is_current)

        # スタイルを強制的に更新
        self.setStyleSheet("")  # 既存のスタイルをクリア
        self.setStyleSheet(stylesheet)  # 新しいスタイルを適用

        # ウィジェットを強制的に再描画
        self.update()

        # デバッグ: 現在のスタイルを確認
        from .logger_setup import get_logger

        logger = get_logger("breadcrumb_addressbar.widgets")
        logger.debug(
            f"Applied stylesheet for '{self.text()}': {stylesheet[:100]}..."
        )

    def refresh_theme(self) -> None:
        """Refresh the button style when theme changes."""
        from .logger_setup import get_logger

        logger = get_logger("breadcrumb_addressbar.widgets")
        logger.debug(
            f"Refreshing theme for button: {self.text()} "
            f"(is_current: {self._is_current})"
        )
        self._update_style()

    @property
    def path(self) -> str:
        """Get the path this button represents."""
        return self._path

    @property
    def is_current(self) -> bool:
        """Get whether this is the current folder."""
        return self._is_current

    @is_current.setter
    def is_current(self, value: bool) -> None:
        """Set whether this is the current folder."""
        self._is_current = value
        self._update_style()

    def set_text(self, text: str) -> None:
        """Set the display text."""
        self.setText(text)

    def set_path(self, path: str) -> None:
        """Set the path this button represents."""
        self._path = path

    def sizeHint(self) -> QSize:
        """Get the recommended size for this widget."""
        # テキストに応じて適切なサイズを計算
        text_width = self.fontMetrics().horizontalAdvance(self.text())
        return QSize(text_width + 20, 32)  # パディングを考慮

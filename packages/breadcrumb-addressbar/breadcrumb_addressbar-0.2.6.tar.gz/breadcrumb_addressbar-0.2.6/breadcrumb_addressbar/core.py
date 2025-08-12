"""
Breadcrumb Address Bar Core

Main breadcrumb address bar widget for file manager navigation.
"""

import os
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QHBoxLayout, QLabel, QWidget

from .logger_setup import get_logger
from .popup import FolderSelectionPopup
from .widgets import BreadcrumbItem


class BreadcrumbAddressBar(QWidget):
    """
    Main breadcrumb address bar widget.

    Provides hierarchical navigation for file managers with clickable
    breadcrumb buttons representing folder paths.
    """

    # シグナル
    pathChanged = Signal(str)  # パス変更通知
    folderSelected = Signal(str)  # フォルダ選択通知

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the breadcrumb address bar.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)

        # 内部状態
        self._current_path = ""
        self._max_items = 5
        self._button_height = 32
        self._font_size = 10
        self._separator = ""
        self._custom_labels: Dict[str, str] = {}

        # 新しい設定オプション
        self._show_popup_for_all_buttons = (
            True  # どのボタンでもポップアップを表示
        )
        self._popup_position_offset = (0, 2)  # ポップアップの位置オフセット

        # ポップアップ実装の選択（デフォルトはQMenu）
        self._use_combo_popup = False
        self._use_list_popup = False

        # ロガー
        self._logger = get_logger("breadcrumb_addressbar.core")

        # UI要素
        self._layout = QHBoxLayout(self)
        self._breadcrumb_items: List[BreadcrumbItem] = []

        # ポップアップインスタンス（シンプルに戻す）
        self._popup: Optional[FolderSelectionPopup] = None

        # レイアウト設定
        self._setup_layout()

        # 初期化
        self._update_display()
        self._logger.debug("BreadcrumbAddressBar initialized")

    def _setup_layout(self) -> None:
        """Setup the widget layout."""
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(2)
        self._layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def setPath(self, path: str) -> None:
        """
        Set the current path and update the breadcrumb display.

        Args:
            path: The path to set
        """
        if path != self._current_path:
            self._logger.info(f"Setting path: {path}")
            self._current_path = path
            self._update_display()
            self.pathChanged.emit(path)

    def getPath(self) -> str:
        """
        Get the current path.

        Returns:
            Current path string
        """
        return self._current_path

    def setMaxItems(self, count: int) -> None:
        """
        Set the maximum number of breadcrumb items to display.

        Args:
            count: Maximum number of items
        """
        if count > 0 and count != self._max_items:
            self._max_items = count
            self._update_display()

    def setButtonHeight(self, height: int) -> None:
        """
        Set the height of breadcrumb buttons.

        Args:
            height: Button height in pixels
        """
        if height > 0 and height != self._button_height:
            self._button_height = height
            self._update_button_sizes()

    def setShowPopupForAllButtons(self, enabled: bool) -> None:
        """
        Set whether to show popup for all buttons or only the current folder
        button.

        Args:
            enabled: True to show popup for all buttons, False for current
                     folder only
        """
        if enabled != self._show_popup_for_all_buttons:
            self._show_popup_for_all_buttons = enabled
            self._logger.debug(f"Show popup for all buttons: {enabled}")

    def getShowPopupForAllButtons(self) -> bool:
        """
        Get whether popup is shown for all buttons.

        Returns:
            True if popup is shown for all buttons, False if only for current
            folder
        """
        return self._show_popup_for_all_buttons

    def setPopupPositionOffset(self, offset: Tuple[int, int]) -> None:
        """
        Set the popup position offset.

        Args:
            offset: Tuple of (x, y) offset values
        """
        if offset != self._popup_position_offset:
            self._popup_position_offset = offset
            self._logger.debug(f"Popup position offset set to: {offset}")

    def getPopupPositionOffset(self) -> Tuple[int, int]:
        """
        Get the current popup position offset.

        Returns:
            Tuple of (x, y) offset values
        """
        return self._popup_position_offset

    def refresh_theme(self) -> None:
        """
        Refresh the theme for all breadcrumb items.
        This should be called when the theme changes.
        """
        self._logger.info("Refreshing theme for breadcrumb items")

        # 既存のボタンにテーマを適用
        for item in self._breadcrumb_items:
            item.refresh_theme()

        # セパレーターの色も更新
        self._update_separator_colors()

        # 全体を強制的に再描画
        self.update()

    def _update_separator_colors(self) -> None:
        """Update separator colors to match current theme."""
        from .themes import get_theme_manager

        theme_manager = get_theme_manager()
        separator_color = theme_manager.get_separator_color()

        # レイアウト内のセパレーターラベルを更新
        for i in range(self._layout.count()):
            child = self._layout.itemAt(i)
            if child and child.widget():
                widget = child.widget()
                if isinstance(widget, QLabel) and widget.text() in [
                    " > ",
                    " / ",
                    " \\ ",
                ]:
                    widget.setStyleSheet(f"color: {separator_color};")

    def setFontSize(self, size: int) -> None:
        """
        Set the font size for breadcrumb buttons.

        Args:
            size: Font size in points
        """
        if size > 0 and size != self._font_size:
            self._font_size = size
            self._update_fonts()

    def setSeparator(self, separator: str) -> None:
        """
        Set the separator between breadcrumb items.

        Args:
            separator: Separator string (e.g., " > ", " / ")
        """
        if separator != self._separator:
            self._separator = separator
            self._update_display()

    def setCustomLabels(self, labels: Dict[str, str]) -> None:
        """
        Set custom display labels for specific paths.

        Args:
            labels: Dictionary mapping paths to custom labels
        """
        self._custom_labels = labels.copy()
        self._update_display()

    def _update_display(self) -> None:
        """Update the breadcrumb display based on current path."""
        # 既存のアイテムをクリア
        self._clear_items()

        if not self._current_path:
            return

        # パスを分割
        path_parts = self._split_path(self._current_path)

        # 表示するアイテムを決定（省略表示対応）
        display_items = self._get_display_items(path_parts)

        # アイテムを作成
        for i, (text, path, is_current) in enumerate(display_items):
            item = BreadcrumbItem(text, path, is_current, self)
            item.clicked_with_info.connect(self._on_item_clicked_with_info)

            # サイズとフォントを設定
            item.setMinimumHeight(self._button_height)
            item.setMaximumHeight(self._button_height)

            font = QFont()
            font.setPointSize(self._font_size)
            item.setFont(font)

            # テーマを適用
            item.refresh_theme()

            self._breadcrumb_items.append(item)
            self._layout.addWidget(item)

            # セパレーターを追加（最後のアイテム以外）
            if i < len(display_items) - 1 and self._separator:
                separator_label = QLabel(self._separator)
                separator_label.setAlignment(Qt.AlignCenter)
                font = QFont()
                font.setPointSize(self._font_size)
                separator_label.setFont(font)

                # セパレーターの色をテーマに合わせる
                from .themes import get_theme_manager

                theme_manager = get_theme_manager()
                separator_color = theme_manager.get_separator_color()
                separator_label.setStyleSheet(f"color: {separator_color};")

                self._layout.addWidget(separator_label)

    def _clear_items(self) -> None:
        """Clear all breadcrumb items from the layout."""
        # 既存のアイテムを削除
        for item in self._breadcrumb_items:
            self._layout.removeWidget(item)
            item.deleteLater()
        self._breadcrumb_items.clear()

        # セパレーターも削除
        while self._layout.count() > 0:
            child = self._layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _split_path(self, path: str) -> List[tuple]:
        """
        Split path into parts with display text and full path.

        Args:
            path: Path to split

        Returns:
            List of tuples (display_text, full_path)
        """
        parts = []

        # ルートディレクトリの処理
        if path.startswith("/"):
            parts.append(("/", "/"))
            path = path[1:]
        elif path.startswith("C:\\"):
            parts.append(("C:\\", "C:\\"))
            path = path[3:]

        # 残りのパスを分割
        if path:
            # Windowsパスの場合はバックスラッシュを保持
            if "\\" in path:
                path_parts = path.split("\\")
                current_path = parts[0][1] if parts else ""

                for part in path_parts:
                    if part:
                        if current_path.endswith("\\"):
                            current_path = current_path + part
                        else:
                            current_path = current_path + "\\" + part
                        display_text = self._get_display_text(
                            part, current_path
                        )
                        parts.append((display_text, current_path))
            else:
                # Unixパスの場合
                path_parts = path.split("/")
                current_path = parts[0][1] if parts else ""

                for part in path_parts:
                    if part:
                        current_path = os.path.join(
                            current_path, part
                        ).replace("\\", "/")
                        display_text = self._get_display_text(
                            part, current_path
                        )
                        parts.append((display_text, current_path))

        return parts

    def _get_display_text(self, part: str, full_path: str) -> str:
        """
        Get display text for a path part.

        Args:
            part: Path part
            full_path: Full path

        Returns:
            Display text
        """
        # カスタムラベルをチェック
        if full_path in self._custom_labels:
            return self._custom_labels[full_path]

        # 長い名前の省略
        if len(part) > 20:
            return part[:17] + "..."

        return part

    def _get_display_items(self, path_parts: List[tuple]) -> List[tuple]:
        """
        Get items to display with ellipsis handling.

        Args:
            path_parts: All path parts

        Returns:
            List of tuples (display_text, full_path, is_current)
        """
        if len(path_parts) <= self._max_items:
            # 全アイテムを表示
            return [
                (text, path, i == len(path_parts) - 1)
                for i, (text, path) in enumerate(path_parts)
            ]

        # 省略表示: 最初 + ... + 最後の2つ
        items = []

        # 最初のアイテム
        items.append((path_parts[0][0], path_parts[0][1], False))

        # 省略記号
        items.append(("...", "", False))

        # 最後の2つのアイテム
        for i in range(len(path_parts) - 2, len(path_parts)):
            text, path = path_parts[i]
            is_current = i == len(path_parts) - 1
            items.append((text, path, is_current))

        return items

    def _on_item_clicked_with_info(self, path: str, is_current: bool) -> None:
        """
        Handle breadcrumb item click with additional info.

        Args:
            path: Clicked path
            is_current: Whether this is the current folder button
        """
        self._logger.debug(
            f"Item clicked: path='{path}', is_current={is_current}, "
            f"current_path='{self._current_path}'"
        )

        if path:
            # 設定に応じてポップアップを表示
            if self._show_popup_for_all_buttons:
                # どのボタンでもポップアップを表示
                self._logger.debug("Showing folder popup for clicked button")
                self._show_folder_popup(path)
            else:
                # 従来の動作: 最下層ボタン（現在のフォルダ）の場合はポップアップを表示
                if is_current:
                    self._logger.debug("Showing folder popup for current path")
                    self._show_folder_popup(path)
                else:
                    self._logger.debug(f"Navigating to path: {path}")
                    self.setPath(path)

    def _show_folder_popup(self, path: str) -> None:
        """
        Show folder selection popup for the specified path.

        Args:
            path: Folder path to show popup for
        """
        try:
            # クリックされたボタンを特定
            clicked_item = None
            for item in self._breadcrumb_items:
                if item.path == path:
                    clicked_item = item
                    break

            # ボタンが見つからない場合は最後のボタンを使用
            if not clicked_item and self._breadcrumb_items:
                clicked_item = self._breadcrumb_items[-1]

            if clicked_item:
                # QMenuベースのポップアップを使用（QToolButtonにアタッチ）
                if not self._popup:
                    self._popup = FolderSelectionPopup(self)
                    self._popup.folderSelected.connect(
                        self._on_folder_selected
                    )

                # メニュー内容を準備してからボタンにアタッチ
                self._popup.populateForPath(path)
                clicked_item.setMenu(self._popup)

                # QToolButtonのメニュー表示（グローバル座標の補正が必要な場合は手動表示）
                if self._popup_position_offset == (0, 0):
                    clicked_item.showMenu()
                else:
                    pos = clicked_item.mapToGlobal(
                        clicked_item.rect().bottomLeft()
                    )
                    pos.setX(pos.x() + self._popup_position_offset[0])
                    pos.setY(pos.y() + self._popup_position_offset[1])
                    self._popup.popup(pos)

                self._logger.debug(f"Showing menu popup for path: {path}")
        except Exception as e:
            self._logger.error(f"Failed to show folder popup: {e}")

    def _on_folder_selected(self, folder_path: str) -> None:
        """
        Handle folder selection from popup.

        Args:
            folder_path: Selected folder path
        """
        if folder_path and folder_path != self._current_path:
            self.setPath(folder_path)
            self.folderSelected.emit(folder_path)
            self._logger.info(f"Folder selected from popup: {folder_path}")

    def _update_button_sizes(self) -> None:
        """Update button sizes for all breadcrumb items."""
        for item in self._breadcrumb_items:
            item.setMinimumHeight(self._button_height)
            item.setMaximumHeight(self._button_height)

    def _update_fonts(self) -> None:
        """Update fonts for all breadcrumb items."""
        font = QFont()
        font.setPointSize(self._font_size)

        for item in self._breadcrumb_items:
            item.setFont(font)

    def sizeHint(self) -> QSize:
        """Get the recommended size for this widget."""
        return QSize(400, self._button_height + 8)  # パディングを考慮

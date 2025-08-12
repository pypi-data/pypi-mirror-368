"""
Folder Selection Popup Menu

Popup menu for folder selection in the breadcrumb address bar.
"""

import os
from typing import List, Optional, Tuple

from PySide6.QtCore import QPoint, Signal
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import QMenu, QWidget

from .logger_setup import get_logger


class FolderSelectionPopup(QMenu):
    """
    Popup menu for folder selection.

    Displays a list of folders in the current directory for selection.
    """

    # シグナル
    folderSelected = Signal(str)  # フォルダ選択通知

    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the folder selection popup.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self._logger = get_logger("breadcrumb_addressbar.popup")
        self._current_path = ""
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Setup the popup menu UI."""
        self.setMinimumWidth(300)
        self.setMaximumHeight(400)

        # フォント設定
        font = QFont()
        font.setPointSize(10)
        self.setFont(font)

        # スクロール可能なメニューにするための設定
        self.setStyleSheet(
            """
            QMenu {
                max-height: 400px;
            }
            QMenu::item {
                padding: 4px 8px;
            }
        """
        )

    def exec_(self) -> int:  # PySide6互換: テスト用のエイリアス
        """Alias for exec() to match test expectations."""
        return self.exec()

    def populateForPath(self, path: str) -> None:
        """Populate actions for the given path without showing the menu.

        Args:
            path: Path to prepare folder actions for
        """
        self._current_path = path
        self._logger.debug(f"Populating popup for path: {path}")

        # 既存のアクションをクリア
        self.clear()

        # フォルダ一覧を取得
        folders: List[Tuple[str, str]] = self._get_folders(path)

        if not folders:
            # フォルダが見つからない場合
            no_folders_action = QAction("フォルダが見つかりません", self)
            no_folders_action.setEnabled(False)
            self.addAction(no_folders_action)
        else:
            # フォルダ一覧を表示
            for folder_name, folder_path in folders:
                action = QAction(folder_name, self)
                action.setData(folder_path)
                action.triggered.connect(
                    lambda checked, p=folder_path: self._on_folder_selected(p)
                )
                self.addAction(action)

    def showForPath(
        self, path: str, position: Optional[Tuple[int, int]] = None
    ) -> None:
        """
        Show the popup menu for a specific path.

        Args:
            path: Path to show folders for
            position: Position to show the popup (x, y)
        """
        self._logger.debug(f"Showing popup for path: {path}")
        self.populateForPath(path)

        # ポップアップを表示
        if position:
            pos = QPoint(position[0], position[1])
            self.popup(pos)
        else:
            self.exec_()

    def _get_folders(self, path: str) -> List[Tuple[str, str]]:
        """
        Get list of folders in the specified path.

        Args:
            path: Path to scan for folders

        Returns:
            List of tuples (folder_name, folder_path)
        """
        folders = []

        try:
            if not os.path.exists(path):
                self._logger.warning(f"Path does not exist: {path}")
                return folders

            if not os.path.isdir(path):
                self._logger.warning(f"Path is not a directory: {path}")
                return folders

            # ディレクトリ内のアイテムを取得
            items = os.listdir(path)

            for item in items:
                item_path = os.path.join(path, item)

                # ディレクトリのみを対象とする
                if os.path.isdir(item_path):
                    # 隠しフォルダを除外（オプション）
                    if not item.startswith("."):
                        folders.append((item, item_path))

            # 名前順にソート
            folders.sort(key=lambda x: x[0].lower())

            self._logger.debug(f"Found {len(folders)} folders in {path}")

        except PermissionError:
            self._logger.error(f"Permission denied accessing path: {path}")
        except Exception as e:
            self._logger.error(f"Error scanning path {path}: {e}")

        return folders

    def _on_folder_selected(self, folder_path: str) -> None:
        """
        Handle folder selection.

        Args:
            folder_path: Selected folder path
        """
        self._logger.info(f"Folder selected: {folder_path}")
        self.folderSelected.emit(folder_path)

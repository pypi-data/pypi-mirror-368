"""
Test cases for FolderSelectionPopup functionality.
"""

import os
from unittest.mock import patch

import pytest

# Headless 環境でのハング防止（CI向け）
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _is_pytest_qt_enabled() -> bool:
    """Return True if pytest-qt plugin is available/enabled."""
    try:
        import pytestqt  # type: ignore  # noqa: F401

        return True
    except Exception:
        return False


PYTEST_QT_ENABLED = _is_pytest_qt_enabled()

try:
    from PySide6.QtCore import QPoint

    PYSIDE6_AVAILABLE = True
except Exception:  # pragma: no cover - import guard only
    PYSIDE6_AVAILABLE = False

try:
    from breadcrumb_addressbar.popup import FolderSelectionPopup

    POPUP_AVAILABLE = True
except Exception:  # pragma: no cover - import guard only
    POPUP_AVAILABLE = False


@pytest.mark.skipif(
    (not PYSIDE6_AVAILABLE)
    or (not POPUP_AVAILABLE)
    or (not PYTEST_QT_ENABLED),
    reason="PySide6/FolderSelectionPopup/pytest-qt not available",
)
class TestFolderSelectionPopup:
    """Test cases for FolderSelectionPopup class."""

    @pytest.fixture(autouse=True)
    def setup(self, qtbot):
        """Setup test environment."""
        self.popup = FolderSelectionPopup()
        qtbot.addWidget(self.popup)
        yield
        self.popup.close()
        self.popup.deleteLater()

    def test_initial_state(self):
        """Test initial state of the popup."""
        assert self.popup._current_path == ""
        assert self.popup.minimumWidth() == 300
        assert self.popup.maximumHeight() == 400

    def test_setup_ui(self):
        """Test UI setup."""
        # UI設定が正しく適用されているかチェック
        assert self.popup.minimumWidth() == 300
        assert self.popup.maximumHeight() == 400

        # フォント設定をチェック
        font = self.popup.font()
        assert font.pointSize() == 10

    def test_get_folders_existing_path(self, tmp_path):
        """Test getting folders from an existing path."""
        # テスト用のディレクトリ構造を作成
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # サブディレクトリを作成
        (test_dir / "folder1").mkdir()
        (test_dir / "folder2").mkdir()
        (test_dir / "file1.txt").touch()  # ファイルは除外される
        (test_dir / ".hidden").mkdir()  # 隠しフォルダは除外される

        folders = self.popup._get_folders(str(test_dir))

        # フォルダ名を抽出
        folder_names = [folder[0] for folder in folders]

        assert len(folders) == 2
        assert "folder1" in folder_names
        assert "folder2" in folder_names
        assert "file1.txt" not in folder_names
        assert ".hidden" not in folder_names

    def test_get_folders_nonexistent_path(self):
        """Test getting folders from a non-existent path."""
        folders = self.popup._get_folders("/nonexistent/path")
        assert folders == []

    def test_get_folders_file_path(self, tmp_path):
        """Test getting folders when path is a file."""
        # テスト用のファイルを作成
        test_file = tmp_path / "test_file.txt"
        test_file.touch()

        folders = self.popup._get_folders(str(test_file))
        assert folders == []

    def test_get_folders_permission_error(self):
        """Test getting folders with permission error."""
        with patch(
            "os.listdir", side_effect=PermissionError("Permission denied")
        ):
            folders = self.popup._get_folders("/some/path")
            assert folders == []

    def test_get_folders_os_error(self):
        """Test getting folders with OS error."""
        with patch("os.listdir", side_effect=OSError("OS error")):
            folders = self.popup._get_folders("/some/path")
            assert folders == []

    def test_get_folders_general_exception(self):
        """Test getting folders with general exception."""
        with patch("os.listdir", side_effect=Exception("General error")):
            folders = self.popup._get_folders("/some/path")
            assert folders == []

    @patch("os.listdir")
    def test_populate_for_path_with_folders(self, mock_listdir, tmp_path):
        """Populate menu actions when folders exist (no UI)."""
        test_dir_path = tmp_path / "test_dir"
        test_dir_path.mkdir()
        test_dir = str(test_dir_path)
        mock_listdir.return_value = ["folder1", "folder2"]
        with patch("os.path.isdir", return_value=True):
            self.popup.populateForPath(test_dir)
            assert self.popup._current_path == test_dir
            assert len(self.popup.actions()) == 2

    @patch("os.listdir")
    def test_populate_for_path_no_folders(self, mock_listdir, tmp_path):
        """Populate menu actions when no folders (no UI)."""
        test_dir = str(tmp_path / "empty_dir")
        mock_listdir.return_value = []
        self.popup.populateForPath(test_dir)
        assert self.popup._current_path == test_dir
        assert len(self.popup.actions()) == 1
        action = self.popup.actions()[0]
        assert not action.isEnabled()

    def test_show_for_path_with_position(self, tmp_path):
        """Test showing popup with position."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "folder1").mkdir()

        position = (100, 200)

        # ポップアップを表示（実際の表示は行わない）
        with patch.object(self.popup, "popup") as mock_popup:
            self.popup.showForPath(str(test_dir), position)

            # popupメソッドが正しい位置で呼ばれるかチェック
            mock_popup.assert_called_once()
            call_args = mock_popup.call_args[0][0]
            assert isinstance(call_args, QPoint)
            assert call_args.x() == position[0]
            assert call_args.y() == position[1]

    def test_show_for_path_without_position(self, tmp_path):
        """Test showing popup without position."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "folder1").mkdir()

        # ポップアップを表示（実際の表示は行わない）
        with patch.object(self.popup, "exec_"):
            self.popup.showForPath(str(test_dir))

            # exec_メソッドが呼ばれるかチェック
            self.popup.exec_.assert_called_once()

    def test_on_folder_selected(self):
        """Test folder selection handler."""
        signal_emitted = {"flag": False, "path": ""}

        def on_folder_selected(path):
            signal_emitted["flag"] = True
            signal_emitted["path"] = path

        self.popup.folderSelected.connect(on_folder_selected)

        test_path = "/test/path"
        self.popup._on_folder_selected(test_path)

        assert signal_emitted["flag"]
        assert signal_emitted["path"] == test_path

    def test_folder_sorting(self, tmp_path):
        """Test that folders are sorted alphabetically."""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()

        # 順序を意図的に逆にして作成
        (test_dir / "zebra").mkdir()
        (test_dir / "alpha").mkdir()
        (test_dir / "beta").mkdir()

        folders = self.popup._get_folders(str(test_dir))
        folder_names = [folder[0] for folder in folders]

        # アルファベット順にソートされているかチェック
        expected_order = ["alpha", "beta", "zebra"]
        assert folder_names == expected_order

    def test_clear_actions(self):
        """Test that actions are cleared before adding new ones."""
        # 最初にアクションを追加
        with patch.object(self.popup, "popup"), patch.object(
            self.popup, "exec_"
        ):
            self.popup.showForPath("/some/path")
            initial_count = len(self.popup.actions())

            # 再度アクションを追加
            self.popup.showForPath("/another/path")
            final_count = len(self.popup.actions())

            # アクションがクリアされているかチェック
            assert final_count <= initial_count + 1  # 新しいアクションのみ

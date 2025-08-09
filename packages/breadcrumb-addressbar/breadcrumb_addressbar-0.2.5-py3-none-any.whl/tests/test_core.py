"""
Tests for `breadcrumb_addressbar.core` (BreadcrumbAddressBar).
"""

import os

import pytest

# Headless 対応
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _is_pytest_qt_enabled() -> bool:
    try:
        import pytestqt  # type: ignore  # noqa: F401

        return True
    except Exception:
        return False


PYTEST_QT_ENABLED = _is_pytest_qt_enabled()

try:
    from breadcrumb_addressbar.core import BreadcrumbAddressBar

    CORE_AVAILABLE = True
except Exception:  # pragma: no cover - import guard only
    CORE_AVAILABLE = False

try:
    from PySide6.QtWidgets import QWidget

    PYSIDE6_AVAILABLE = True
except Exception:  # pragma: no cover - import guard only
    PYSIDE6_AVAILABLE = False


class _FakeThemeManager:
    def get_button_stylesheet(self, is_current: bool = False) -> str:
        if is_current:
            return "QPushButton { background-color: #000; }"
        return "QPushButton { background-color: #fff; }"

    def get_separator_color(self) -> str:
        return "#123456"


@pytest.mark.skipif(
    (not PYSIDE6_AVAILABLE) or (not CORE_AVAILABLE) or (not PYTEST_QT_ENABLED),
    reason="PySide6/core/pytest-qt not available",
)
class TestBreadcrumbAddressBar:
    @pytest.fixture(autouse=True)
    def setup(self, qtbot, monkeypatch):
        # テーママネージャをフェイク
        from breadcrumb_addressbar import themes as themes_mod

        monkeypatch.setattr(
            themes_mod,
            "get_theme_manager",
            lambda: _FakeThemeManager(),
            raising=True,
        )

        self.parent = QWidget()
        qtbot.addWidget(self.parent)
        self.widget = BreadcrumbAddressBar(parent=self.parent)
        qtbot.addWidget(self.widget)

        yield

        self.widget.deleteLater()
        self.parent.deleteLater()

    def test_set_and_get_path_emits_signal(self, qtbot):
        received = {"path": None}

        def on_changed(p: str) -> None:
            received["path"] = p

        self.widget.pathChanged.connect(on_changed)
        self.widget.setPath("/a/b/c")
        assert self.widget.getPath() == "/a/b/c"
        assert received["path"] == "/a/b/c"

    def test_display_items_and_style_updates(self):
        self.widget.setSeparator(" / ")
        self.widget.setFontSize(12)
        self.widget.setButtonHeight(28)
        self.widget.setPath("/root/longfolder/child")

        # ボタン群が生成される
        assert len(self.widget._breadcrumb_items) >= 2
        # 各ボタンに高さが反映される
        assert all(
            btn.minimumHeight() == 28 for btn in self.widget._breadcrumb_items
        )

    def test_max_items_and_ellipsis_logic(self):
        parts = [(str(i), f"/{i}") for i in range(6)]
        items = self.widget._get_display_items(parts)  # default max=5
        # 6要素 -> 省略が入る
        assert any(text == "..." for text, _path, _cur in items)

        self.widget.setMaxItems(10)
        items2 = self.widget._get_display_items(parts)
        assert not any(text == "..." for text, _path, _cur in items2)

    def test_split_path_unix_and_windows(self):
        unix = self.widget._split_path("/a/b/c")
        assert unix[0] == ("/", "/")
        assert unix[-1][1].replace("\\", "/") == "/a/b/c"

        win = self.widget._split_path("C:\\Users\\Test")
        assert win[0] == ("C:\\", "C:\\")
        assert win[-1][1] == "C:\\Users\\Test"

    def test_toggle_popup_settings(self):
        assert self.widget.getShowPopupForAllButtons() is True
        self.widget.setShowPopupForAllButtons(False)
        assert self.widget.getShowPopupForAllButtons() is False

        self.widget.setPopupPositionOffset((3, 4))
        assert self.widget.getPopupPositionOffset() == (3, 4)

    def test_on_item_clicked_behavior(self, monkeypatch):
        called = {"show": None, "set": None}

        monkeypatch.setattr(
            self.widget,
            "_show_folder_popup",
            lambda p: called.__setitem__("show", p),
        )
        monkeypatch.setattr(
            self.widget, "setPath", lambda p: called.__setitem__("set", p)
        )

        # どのボタンでもポップアップ
        self.widget.setShowPopupForAllButtons(True)
        self.widget._on_item_clicked_with_info("/some/path", is_current=False)
        assert called["show"] == "/some/path"

        # 最下層のみポップアップ、非最下層は遷移
        called["show"] = None
        self.widget.setShowPopupForAllButtons(False)
        self.widget._on_item_clicked_with_info("/go/here", is_current=False)
        assert called["set"] == "/go/here"

    def test_refresh_theme_runs(self):
        # 例外なく実行されること
        self.widget.setPath("/a/b")
        self.widget.refresh_theme()

    def test_custom_labels_and_clear_items(self):
        # カスタムラベルの適用
        self.widget.setSeparator(" > ")
        self.widget.setPath("/root/child")
        self.widget.setCustomLabels({"/root": "ROOT"})
        assert any(
            btn.text() in ("ROOT", "child")
            for btn in self.widget._breadcrumb_items
        )

        # アイテムクリアが動く（内部関数呼出し）
        prev_count = self.widget._layout.count()
        self.widget._clear_items()
        assert self.widget._layout.count() == 0
        assert prev_count >= 0

"""
Tests for `breadcrumb_addressbar.widgets` (BreadcrumbItem).
"""

import os
from typing import Any

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
    from breadcrumb_addressbar.widgets import BreadcrumbItem

    WIDGETS_AVAILABLE = True
except Exception:  # pragma: no cover - import guard only
    WIDGETS_AVAILABLE = False

try:
    from PySide6.QtWidgets import QWidget

    PYSIDE6_AVAILABLE = True
except Exception:  # pragma: no cover - import guard only
    PYSIDE6_AVAILABLE = False


class _FakeThemeManager:
    def get_button_stylesheet(self, is_current: bool = False) -> str:
        return "QPushButton { /* fake */ }"


@pytest.mark.skipif(
    (not PYSIDE6_AVAILABLE)
    or (not WIDGETS_AVAILABLE)
    or (not PYTEST_QT_ENABLED),
    reason="PySide6/widgets/pytest-qt not available",
)
class TestBreadcrumbItem:
    @pytest.fixture(autouse=True)
    def setup(self, qtbot, monkeypatch):
        # テーマ取得関数をフェイクに差し替え
        from breadcrumb_addressbar import themes as themes_mod

        monkeypatch.setattr(
            themes_mod,
            "get_theme_manager",
            lambda: _FakeThemeManager(),
            raising=True,
        )

        # 最小親ウィジェット
        self.parent = QWidget()
        qtbot.addWidget(self.parent)

        yield

        self.parent.deleteLater()

    def test_click_signals_emitted(self, qtbot):
        item = BreadcrumbItem(
            "home",
            "/home",
            is_current=False,
            parent=self.parent,
        )
        qtbot.addWidget(item)

        received = {"path": None, "info": None}

        def on_path(p: str) -> None:
            received["path"] = p

        def on_info(p: str, is_current: bool) -> None:
            received["info"] = (p, is_current)

        item.clicked_with_path.connect(on_path)
        item.clicked_with_info.connect(on_info)

        item.click()

        assert received["path"] == "/home"
        assert received["info"] == ("/home", False)

    def test_is_current_updates_style(self, qtbot):
        item = BreadcrumbItem(
            "a",
            "/a",
            is_current=False,
            parent=self.parent,
        )
        qtbot.addWidget(item)

        item.is_current = True
        assert item.is_current is True

    def test_setters(self, qtbot):
        item = BreadcrumbItem("x", "/x", parent=self.parent)
        qtbot.addWidget(item)

        item.set_text("root")
        item.set_path("/")
        assert item.text() == "root"
        assert item.path == "/"

    def test_size_hint_and_key_events(self, qtbot):
        item = BreadcrumbItem("enter", "/e", parent=self.parent)
        qtbot.addWidget(item)

        # sizeHint を呼んで描画系コード行をカバー
        sh = item.sizeHint()
        assert sh.width() > 0 and sh.height() > 0

        # Enter/Space キーでクリック相当のシグナルが出る
        received = {"count": 0}

        def on_click(*_args: Any, **_kwargs: Any) -> None:
            received["count"] += 1

        item.clicked_with_path.connect(on_click)
        qtbot.keyClick(item, "\r")  # Return
        qtbot.keyClick(item, " ")  # Space
        # その他のキーで else 分岐（super 呼び出し）
        qtbot.keyClick(item, "A")
        assert received["count"] >= 2

"""
Tests for `breadcrumb_addressbar.themes` ThemeManager.
"""

import os

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _import_themes_module():
    import importlib

    import breadcrumb_addressbar.themes as themes

    return importlib.reload(themes)


def test_get_theme_manager_singleton():
    themes = _import_themes_module()
    m1 = themes.get_theme_manager()
    m2 = themes.get_theme_manager()
    assert m1 is m2


def test_methods_raise_when_theme_manager_unavailable(monkeypatch):
    themes = _import_themes_module()

    # 強制的に未導入状態に見せる
    monkeypatch.setattr(themes, "THEME_MANAGER_AVAILABLE", False, raising=True)
    tm = themes.get_theme_manager()
    tm._theme_controller = None

    # 例外を投げるAPI群
    with pytest.raises(RuntimeError):
        tm.get_current_theme_name()
    with pytest.raises(RuntimeError):
        tm.get_available_themes()
    with pytest.raises(RuntimeError):
        tm.set_theme("Dark")
    with pytest.raises(RuntimeError):
        tm.get_button_stylesheet()
    with pytest.raises(RuntimeError):
        tm.get_separator_color()
    with pytest.raises(RuntimeError):
        tm.get_combo_box_stylesheet()
    with pytest.raises(RuntimeError):
        tm.get_combo_item_colors()

    # False を返すAPI
    assert tm.apply_theme_to_widget(object()) is False


def test_private_helpers_fallbacks():
    themes = _import_themes_module()
    tm = themes.get_theme_manager()
    tm._theme_controller = None

    # _lighten_color の境界
    assert tm._lighten_color("#000000", 0.5) == "#7f7f7f"
    assert tm._lighten_color("#ffffff", 0.5) == "#ffffff"
    # 不正フォーマットはそのまま返す
    assert tm._lighten_color("zzz", 0.3) == "zzz"

    # _get_light_border_color は THEME_MANAGER がなしでもフォールバック動作
    assert tm._get_light_border_color("#000000") == "#cccccc"
    assert tm._get_light_border_color("#ffffff") == "#666666"
    assert tm._get_light_border_color("#777777") == "#999999"


def test_apply_theme_to_widget_success_path(monkeypatch):
    themes = _import_themes_module()

    # 疑似 ThemeController と apply 関数を注入
    class FakeController:
        def get_current_theme_name(self):  # noqa: D401
            return "Fake"

        def get_available_themes(self):  # noqa: D401
            return {"Fake": {"button": {}, "textColor": "#111111"}}

    def fake_apply(widget, theme_name=None):  # noqa: D401
        return True

    monkeypatch.setattr(themes, "THEME_MANAGER_AVAILABLE", True, raising=True)
    tm = themes.get_theme_manager()
    tm._theme_controller = FakeController()
    monkeypatch.setattr(
        themes,
        "apply_theme_to_widget",
        fake_apply,
        raising=True,
    )

    assert tm.apply_theme_to_widget(object(), None) is True


def test_get_button_stylesheet_and_separator_and_combo_colors(monkeypatch):
    themes = _import_themes_module()

    class FakeController:
        def get_current_theme_name(self):  # noqa: D401
            return "Fake"

        def get_available_themes(self):  # noqa: D401
            return {
                "Fake": {
                    "textColor": "#222222",
                    "primaryColor": "#333333",
                    "button": {
                        "background": "#010101",
                        "text": "#fafafa",
                        "border": "#010101",
                        "hover": "#020202",
                        "pressed": "#030303",
                        "focus": "#040404",
                    },
                    "backgroundColor": "#ffffff",
                    "borderColor": "#cccccc",
                    "focusColor": "#3399ff",
                }
            }

    monkeypatch.setattr(themes, "THEME_MANAGER_AVAILABLE", True, raising=True)
    tm = themes.get_theme_manager()
    tm._theme_controller = FakeController()

    css_current = tm.get_button_stylesheet(is_current=True)
    css_normal = tm.get_button_stylesheet(is_current=False)
    sep = tm.get_separator_color()
    combo_css = tm.get_combo_box_stylesheet()
    colors = tm.get_combo_item_colors()

    assert "QPushButton" in css_current and "QPushButton" in css_normal
    assert isinstance(sep, str) and sep.startswith("#")
    assert "QComboBox" in combo_css
    assert {
        "combo_item_bg",
        "combo_text_color",
        "combo_item_selected_bg",
        "combo_item_selected_text_color",
    }.issubset(colors.keys())

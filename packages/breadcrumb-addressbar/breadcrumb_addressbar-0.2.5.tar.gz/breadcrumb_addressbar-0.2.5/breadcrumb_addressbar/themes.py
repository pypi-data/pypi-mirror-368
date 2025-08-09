"""
Theme System for Breadcrumb Address Bar

Integrates with qt-theme-manager for consistent theming.
"""

from typing import Optional

# PySide6 の読み込みはCI等の環境で失敗することがあるため、例外時はスタブで代替
try:  # pragma: no cover - import guard
    from PySide6.QtCore import QObject
    from PySide6.QtWidgets import QWidget

    PYSIDE6_AVAILABLE = True
except Exception:  # pragma: no cover - import guard only
    PYSIDE6_AVAILABLE = False

    class QObject:  # type: ignore
        def __init__(self, *args, **kwargs) -> None:
            pass

    class QWidget:  # type: ignore
        def __init__(self, *args, **kwargs) -> None:
            pass


# qt-theme-managerのインポート（オプショナル）
try:  # pragma: no cover - import guard
    from theme_manager import ThemeController, apply_theme_to_widget

    THEME_MANAGER_AVAILABLE = True
except ImportError:  # pragma: no cover - import guard only
    THEME_MANAGER_AVAILABLE = False
    ThemeController = None
    apply_theme_to_widget = None

from .logger_setup import get_logger


class ThemeManager(QObject):
    """
    Theme manager for the breadcrumb address bar.

    Integrates with qt-theme-manager for consistent theming.
    """

    def __init__(self):
        """Initialize the theme manager."""
        super().__init__()
        self._logger = get_logger("breadcrumb_addressbar.themes")

        if THEME_MANAGER_AVAILABLE:
            self._theme_controller = ThemeController()
        else:
            self._theme_controller = None
            self._logger.warning("qt-theme-manager is not available")

    def apply_theme_to_widget(
        self, widget: QWidget, theme_name: Optional[str] = None
    ) -> bool:
        """
        Apply theme to a widget using qt-theme-manager.

        Args:
            widget: Widget to apply theme to
            theme_name: Name of theme to apply (uses current theme if None)

        Returns:
            True if theme was successfully applied
        """
        if not THEME_MANAGER_AVAILABLE:
            self._logger.warning("qt-theme-manager is not available")
            return False

        try:
            return apply_theme_to_widget(widget, theme_name)
        except Exception as e:
            self._logger.error(f"Failed to apply theme: {e}")
            return False

    def get_current_theme_name(self) -> str:
        """
        Get the current theme name.

        Returns:
            Current theme name
        """
        if not THEME_MANAGER_AVAILABLE or self._theme_controller is None:
            raise RuntimeError("qt-theme-manager is not available")
        return self._theme_controller.get_current_theme_name()

    def get_available_themes(self) -> dict:
        """
        Get available themes.

        Returns:
            Dictionary of available themes
        """
        if not THEME_MANAGER_AVAILABLE or self._theme_controller is None:
            raise RuntimeError("qt-theme-manager is not available")
        return self._theme_controller.get_available_themes()

    def set_theme(self, theme_name: str) -> bool:
        """
        Set the current theme.

        Args:
            theme_name: Name of theme to set

        Returns:
            True if theme was successfully set
        """
        if not THEME_MANAGER_AVAILABLE or self._theme_controller is None:
            raise RuntimeError("qt-theme-manager is not available")

        try:
            self._theme_controller.set_theme(theme_name)
            self._logger.info(f"Theme changed to: {theme_name}")
            return True
        except Exception as e:
            self._logger.error(f"Failed to set theme: {e}")
            return False

    def refresh_widget_styles(self, widget) -> None:
        """
        Refresh styles for a widget after theme change.

        Args:
            widget: Widget to refresh styles for
        """
        try:
            # ウィジェットに新しいスタイルを適用
            self.apply_theme_to_widget(widget)
            self._logger.debug(f"Refreshed styles for widget: {widget}")
        except Exception as e:
            self._logger.error(f"Failed to refresh widget styles: {e}")

    def get_button_stylesheet(self, is_current: bool = False) -> str:
        """
        Get button stylesheet that adapts to the current theme.

        Args:
            is_current: Whether this is the current folder button

        Returns:
            CSS stylesheet string
        """
        if not THEME_MANAGER_AVAILABLE or self._theme_controller is None:
            raise RuntimeError("qt-theme-manager is not available")

        # qt-theme-managerのテーマ情報を取得
        current_theme = self._theme_controller.get_current_theme_name()
        themes = self._theme_controller.get_available_themes()

        if current_theme in themes:
            theme_data = themes[current_theme]
            button_data = theme_data.get("button", {})

            # デバッグログ
            self._logger.debug(
                f"Generating stylesheet for theme: {current_theme}, "
                f"is_current: {is_current}"
            )
            self._logger.debug(f"Theme data keys: {list(theme_data.keys())}")
            self._logger.debug(f"Button data: {button_data}")

            # テキスト色の取得を改善
            text_color = theme_data.get("textColor", "#333333")
            if not text_color or text_color == "#333333":
                # フォールバック: テーマのprimaryColorを使用
                text_color = theme_data.get("primaryColor", "#333333")

            self._logger.debug(f"Using text color: {text_color}")

            if is_current:
                bg_color = button_data.get("background", "#0078d4")
                text_color_btn = button_data.get("text", "#ffffff")
                border_color = button_data.get("border", "#0078d4")
                hover_color = button_data.get("hover", "#106ebe")
                pressed_color = button_data.get("pressed", "#005a9e")

                return f"""
                    QPushButton {{
                        background-color: {bg_color};
                        color: {text_color_btn};
                        border: 1px solid {border_color};
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-weight: bold;
                    }}
                    QPushButton:hover {{
                        background-color: {hover_color};
                        border-color: {hover_color};
                    }}
                    QPushButton:pressed {{
                        background-color: {pressed_color};
                        border-color: {pressed_color};
                    }}
                """
            else:
                # 非選択ボタン用のより詳細なスタイル
                hover_bg = button_data.get("hover", "#f0f0f0")
                hover_border = button_data.get("border", "#d0d0d0")
                pressed_bg = button_data.get("pressed", "#e0e0e0")
                focus_color = button_data.get("focus", "#0078d4")

                # 非選択ボタン用の軽い枠色を計算
                # テキスト色をベースに、透明度を下げた色を使用
                light_border = self._get_light_border_color(text_color)

                self._logger.debug(
                    f"Non-current button colors - text: "
                    f"{text_color}, hover_bg: {hover_bg}, "
                    f"light_border: {light_border}"
                )

                return f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {text_color};
                        border: 1px solid {light_border};
                        border-radius: 4px;
                        padding: 4px 8px;
                        font-weight: normal;
                    }}
                    QPushButton:hover {{
                        background-color: {hover_bg};
                        border-color: {hover_border};
                        color: {text_color};
                    }}
                    QPushButton:pressed {{
                        background-color: {pressed_bg};
                        border-color: {pressed_bg};
                        color: {text_color};
                    }}
                    QPushButton:focus {{
                        border-color: {focus_color};
                        outline: none;
                        color: {text_color};
                    }}
                """

        # フォールバック: システムパレットを使用
        if is_current:
            return """
                QPushButton {
                    background-color: palette(highlight);
                    color: palette(highlighted-text);
                    border: 1px solid palette(highlight);
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: palette(light);
                    border-color: palette(light);
                }
                QPushButton:pressed {
                    background-color: palette(dark);
                    border-color: palette(dark);
                }
            """
        else:
            return """
                QPushButton {
                    background-color: transparent;
                    color: palette(text);
                    border: 1px solid palette(mid);
                    border-radius: 4px;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: palette(light);
                    border-color: palette(mid);
                }
                QPushButton:pressed {
                    background-color: palette(mid);
                    border-color: palette(dark);
                }
                QPushButton:focus {
                    border-color: palette(highlight);
                    outline: none;
                }
            """

    def get_separator_color(self) -> str:
        """
        Get separator color that adapts to the current theme.

        Returns:
            Color string
        """
        if not THEME_MANAGER_AVAILABLE or self._theme_controller is None:
            raise RuntimeError("qt-theme-manager is not available")

        current_theme = self._theme_controller.get_current_theme_name()
        themes = self._theme_controller.get_available_themes()

        if current_theme in themes:
            theme_data = themes[current_theme]
            return theme_data.get("textColor", "#cccccc")

        return "palette(mid)"

    def get_combo_box_stylesheet(self) -> str:
        """
        Get QComboBox stylesheet that adapts to the current theme.

        Returns:
            QComboBox stylesheet string
        """
        if not THEME_MANAGER_AVAILABLE or self._theme_controller is None:
            raise RuntimeError("qt-theme-manager is not available")

        current_theme = self._theme_controller.get_current_theme_name()
        themes = self._theme_controller.get_available_themes()

        if current_theme in themes:
            theme_data = themes[current_theme]

            # テーマから色を取得（フォールバック付き）
            bg_color = theme_data.get("backgroundColor", "#ffffff")
            text_color = theme_data.get("textColor", "#000000")
            border_color = theme_data.get("borderColor", "#cccccc")
            focus_color = theme_data.get("focusColor", "#3399ff")

            # ホバー色の計算
            hover_bg = theme_data.get("hoverBackgroundColor", "#f0f0f0")
            if not hover_bg:
                # 背景色を少し明るくする
                hover_bg = self._lighten_color(bg_color, 0.1)

            return f"""
                QComboBox {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: 1px solid {border_color};
                    border-radius: 4px;
                    padding: 4px 8px;
                    min-width: 300px;
                }}
                QComboBox:hover {{
                    background-color: {hover_bg};
                    border-color: {focus_color};
                }}
                QComboBox:focus {{
                    border-color: {focus_color};
                    outline: none;
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 20px;
                }}
                QComboBox::down-arrow {{
                    image: none;
                    border-left: 5px solid transparent;
                    border-right: 5px solid transparent;
                    border-top: 5px solid {text_color};
                    margin-right: 5px;
                }}
                QComboBox QAbstractItemView {{
                    background-color: {bg_color};
                    color: {text_color};
                    border: 1px solid {border_color};
                    selection-background-color: {focus_color};
                    selection-color: {bg_color};
                    outline: none;
                }}
            """

        # フォールバック: システムパレットを使用
        return """
            QComboBox {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
                border-radius: 4px;
                padding: 4px 8px;
                min-width: 300px;
            }
            QComboBox:hover {
                background-color: palette(light);
                border-color: palette(highlight);
            }
            QComboBox:focus {
                border-color: palette(highlight);
                outline: none;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid palette(text);
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
                outline: none;
            }
        """

    def get_combo_item_colors(self) -> dict:
        """
        Get QComboBox item colors for delegate rendering.

        Returns:
            Dictionary with color values
        """
        if not THEME_MANAGER_AVAILABLE or self._theme_controller is None:
            raise RuntimeError("qt-theme-manager is not available")

        current_theme = self._theme_controller.get_current_theme_name()
        themes = self._theme_controller.get_available_themes()

        if current_theme in themes:
            theme_data = themes[current_theme]

            return {
                "combo_item_bg": theme_data.get("backgroundColor", "#ffffff"),
                "combo_text_color": theme_data.get("textColor", "#000000"),
                "combo_item_selected_bg": theme_data.get(
                    "focusColor", "#3399ff"
                ),
                "combo_item_selected_text_color": theme_data.get(
                    "backgroundColor", "#ffffff"
                ),
            }

        # フォールバック
        return {
            "combo_item_bg": "#ffffff",
            "combo_text_color": "#000000",
            "combo_item_selected_bg": "#3399ff",
            "combo_item_selected_text_color": "#ffffff",
        }

    def _lighten_color(self, color: str, factor: float) -> str:
        """
        Lighten a color by a given factor.

        Args:
            color: Color in hex format (#RRGGBB)
            factor: Lightening factor (0.0 to 1.0)

        Returns:
            Lightened color in hex format
        """
        try:
            # #RRGGBB形式をRGBに変換
            if color.startswith("#"):
                color = color[1:]

            r = int(color[0:2], 16)
            g = int(color[2:4], 16)
            b = int(color[4:6], 16)

            # 色を明るくする
            r = min(255, int(r + (255 - r) * factor))
            g = min(255, int(g + (255 - g) * factor))
            b = min(255, int(b + (255 - b) * factor))

            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return color

    def _get_light_border_color(self, text_color: str) -> str:
        """
        Get a light border color based on the text color.
        First tries to use existing theme colors, then falls back to
        calculation.

        Args:
            text_color: Base text color (hex format)

        Returns:
            Light border color (hex format)
        """
        try:
            # まず、テーマの既存の色を優先的に使用
            if THEME_MANAGER_AVAILABLE and self._theme_controller is not None:
                current_theme = self._theme_controller.get_current_theme_name()
                themes = self._theme_controller.get_available_themes()

                if current_theme in themes:
                    theme_data = themes[current_theme]
                    button_data = theme_data.get("button", {})

                    # 優先順位1: ボタンのborder色（非選択状態用）
                    if "border" in button_data:
                        border_color = button_data["border"]
                        self._logger.debug(
                            f"テーマのボタンborder色を使用: {border_color}"
                        )
                        return border_color

                    # 優先順位2: panelのborder色を使用
                    panel_data = theme_data.get("panel", {})
                    if "border" in panel_data:
                        panel_border_color = panel_data["border"]
                        self._logger.debug(
                            f"panelのborder色を使用: " f"{panel_border_color}"
                        )
                        return panel_border_color

                    # 優先順位3: セパレーター色を使用
                    separator_color = theme_data.get("textColor", "#cccccc")
                    # テキスト色と異なる場合
                    if separator_color != text_color:
                        self._logger.debug(
                            f"セパレーター色を使用: " f"{separator_color}"
                        )
                        return separator_color

            # フォールバック: テキスト色に基づく計算
            if text_color.startswith("#"):
                hex_color = text_color[1:]  # '#'を除去
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)

                    # 明度を計算（0-255の範囲で）
                    brightness = (r + g + b) / 3

                    # デバッグログを追加
                    self._logger.debug(
                        f"色計算: RGB({r},{g},{b}) -> 明度: {brightness:.1f}"
                    )

                    # 明度に基づいて適切な枠色を決定
                    if brightness > 200:  # 明るい色（白に近い）
                        # 暗いグレーを使用
                        result = "#666666"
                        self._logger.debug(f"明るい色 -> 暗いグレー: {result}")
                        return result
                    elif brightness > 100:  # 中間の明度
                        # 中程度のグレーを使用
                        result = "#999999"
                        self._logger.debug(
                            f"中間の明度 -> 中程度のグレー: {result}"
                        )
                        return result
                    else:  # 暗い色（黒に近い）
                        # 明るいグレーを使用
                        result = "#cccccc"
                        self._logger.debug(f"暗い色 -> 明るいグレー: {result}")
                        return result

            # フォールバック: デフォルトの軽いグレー
            return "#cccccc"

        except (ValueError, IndexError):
            # エラーが発生した場合はデフォルトの軽いグレー
            return "#cccccc"


# グローバルテーママネージャーインスタンス
_theme_manager = ThemeManager()


def get_theme_manager() -> ThemeManager:
    """
    Get the global theme manager instance.

    Returns:
        Theme manager instance
    """
    return _theme_manager

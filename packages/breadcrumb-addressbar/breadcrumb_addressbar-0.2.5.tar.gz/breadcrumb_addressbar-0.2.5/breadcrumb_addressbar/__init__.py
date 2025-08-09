"""
Breadcrumb Address Bar Library

A breadcrumb-style address bar for PySide6/PyQt6 file managers.

注意: パッケージのインポート時に不要な副作用（Qtのロード等）が発生しないよう、
サブモジュールは遅延ロード（PEP 562）で提供します。
"""

from importlib import import_module
from typing import Any, List

__version__ = "0.2.5"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__: List[str] = [
    "BreadcrumbAddressBar",
    "BreadcrumbItem",
    "FolderSelectionPopup",
    "ThemeManager",
    "get_theme_manager",
]


def __getattr__(name: str) -> Any:  # PEP 562 lazy export
    if name == "BreadcrumbAddressBar":
        return getattr(import_module(".core", __name__), name)
    if name == "BreadcrumbItem":
        return getattr(import_module(".widgets", __name__), name)
    if name == "FolderSelectionPopup":
        return getattr(import_module(".popup", __name__), name)
    if name in {"ThemeManager", "get_theme_manager"}:
        return getattr(import_module(".themes", __name__), name)
    raise AttributeError(f"module {__name__} has no attribute {name}")


def __dir__() -> List[str]:
    return sorted(list(globals().keys()) + __all__)

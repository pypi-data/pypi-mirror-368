# QComboBox × QStyledItemDelegate によるテーマ追従実装計画

## 🧭 概要

`qt-theme-manager` を利用したアプリケーションにおいて、`QComboBox` のドロップダウンリスト部分の描画を `QStyledItemDelegate` でカスタマイズし、動的テーマ切り替え時にもスタイルが追従するように設計します。

---

## 🎯 目的

- `QComboBox` のリストアイテム描画を項目単位でカスタマイズ
- `qt-theme-manager` で設定されたテーマに応じた色・スタイルを反映
- テーマ変更時の即時反映（リアクティブ更新）

---

## 🧱 構成要素

| コンポーネント | 役割 |
|----------------|------|
| `ThemeController` | 現在のテーマ情報の取得・切替 |
| `QStyledItemDelegate` | QComboBoxリスト部分の描画責任 |
| `ThemedComboBoxDelegate` | テーママネージャ連携Delegate（拡張版） |
| `combo.view().update()` | リスト描画部分の再レンダリング呼び出し |

---

## 🧪 実装イメージ

### Delegate定義

```python
class ThemedComboBoxDelegate(QStyledItemDelegate):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller

    def paint(self, painter, option, index):
        theme = self.controller.get_current_theme()
        bg = QColor(theme.get("combo_item_bg", "#ffffff"))
        fg = QColor(theme.get("combo_text_color", "#000000"))

        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QColor(theme.get("combo_item_selected_bg", "#3399ff")))
        else:
            painter.fillRect(option.rect, bg)

        painter.setPen(fg)
        painter.drawText(option.rect, Qt.AlignVCenter | Qt.AlignLeft, index.data())
```

### ComboBox設定

```python
combo = QComboBox()
controller = ThemeController()
delegate = ThemedComboBoxDelegate(controller, combo)
combo.setItemDelegate(delegate)
```

### テーマ切替トリガー（例）

```python
controller.set_theme("cyberpunk")
combo.view().update()  # 新しいスタイルを反映
```

---

## 📦 テーマ設定項目の追加案（theme_settings.json）

```json
{
  "dark": {
    "combo_item_bg": "#1a1a1a",
    "combo_text_color": "#eeeeee",
    "combo_item_selected_bg": "#00adb5"
  }
}
```

---

## 🔁 テーマ切替反映の仕組み

- `controller.set_theme(...)` による変更を `delegate.paint()` 内部で再参照
- `view().update()` 呼び出しによりアイテム表示を強制再描画
- 必要に応じて `delegate.refresh_theme()` 実装でコントローラー再参照可能

---

## ✅ 効果と利点

- リスト表示部分も完全にテーマ管理下に置ける
- 描画制御が `QSS` に依存せず、プログラム的に柔軟
- ユーザー操作・設定変更にリアクティブに対応
- `WSLg` 等制限環境でも描画の安定性が高い

---

## 🔜 次のステップ

1. `theme_settings.json` に `combo_*` 設定項目を追加
2. `ThemeController` 経由で取得可能な構造を整備
3. `ThemedComboBoxDelegate` 実装とテスト
4. テーマ切替後の描画更新処理の自動化（フック方式検討）

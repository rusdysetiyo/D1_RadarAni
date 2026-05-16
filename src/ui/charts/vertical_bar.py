import flet as ft
import flet.canvas as cv
from .palette import (
    C_TEXT, C_TEXT2, C_TEXT3, C_SAKURA_DK, C_HOVER, C_BORDER, CHART_COLORS,
    _rgba, _cv_text_right, _cv_text_top_center
)
from .tooltip import Tooltip

class VerticalBarChart(ft.Stack):
    PAD_L = 46
    PAD_R = 12
    PAD_T = 28
    PAD_B = 72   # extra ruang untuk label X diagonal

    def __init__(self, bar_data: list, title: str, y_label: str = "", theme: dict = None):
        super().__init__(expand=True)
        self._data    = bar_data
        self._title   = title
        self._hovered = -1
        self._tooltip = Tooltip()
        self._theme   = theme
        self._w = self._h = 0

        self._canvas = cv.Canvas(shapes=[], expand=True,
                                 on_resize=self._on_resize)
        self._gd = ft.GestureDetector(
            content=ft.Container(expand=True),
            on_hover=self._on_hover,
        )
        self.controls = [self._canvas, self._gd, self._tooltip]

    def _on_resize(self, e):
        self._w, self._h = e.width, e.height
        self._redraw(self._hovered)

    def _bar_rect(self, i, w, h):
        n       = len(self._data)
        max_val = max((d["value"] for d in self._data), default=1) or 1
        area_w  = w - self.PAD_L - self.PAD_R
        area_h  = h - self.PAD_T - self.PAD_B
        slot_w  = area_w / n
        bar_w   = max(4.0, slot_w * 0.62)
        bx      = self.PAD_L + i * slot_w + (slot_w - bar_w) / 2
        val     = self._data[i]["value"]
        bar_h   = area_h * (val / max_val)
        by      = self.PAD_T + area_h - bar_h
        return bx, by, bar_w, bar_h

    def _redraw(self, hovered):
        if self._w == 0:
            return
        w, h    = self._w, self._h
        max_v   = max((d["value"] for d in self._data), default=1) or 1
        area_h  = h - self.PAD_T - self.PAD_B
        shapes  = []

        c_text       = self._theme["text_main"]        if self._theme else C_TEXT
        c_text2      = self._theme["text_secondary"]   if self._theme else C_TEXT2
        c_text3      = self._theme["text_muted"]       if self._theme else C_TEXT3
        c_border     = self._theme["border_color"]     if self._theme else C_BORDER
        c_primary    = self._theme["primary"]          if self._theme else C_SAKURA_DK
        chart_colors = self._theme.get("chart_colors", CHART_COLORS) if self._theme else CHART_COLORS
        c_hover      = self._theme["primary"]          if self._theme else C_HOVER

        grid_p = ft.Paint(style=ft.PaintingStyle.STROKE,
                          stroke_width=0.7, color="#22000000")
        for frac in [0.25, 0.5, 0.75, 1.0]:
            gy    = self.PAD_T + area_h * (1 - frac)
            label = str(int(max_v * frac))
            shapes.append(cv.Path(
                [cv.Path.MoveTo(self.PAD_L, gy),
                 cv.Path.LineTo(w - self.PAD_R, gy)],
                grid_p,
            ))
            shapes.append(_cv_text_right(
                self.PAD_L - 4, gy, label, 9, c_text3))

        for i, d in enumerate(self._data):
            bx, by, bw, bh = self._bar_rect(i, w, h)
            is_hov = (i == hovered)
            color  = c_hover if is_hov else chart_colors[i % len(chart_colors)]
            alpha  = 1.0 if (is_hov or hovered == -1) else 0.45

            shapes.append(cv.Rect(
                x=bx, y=by, width=bw, height=max(bh, 1),
                border_radius=4,
                paint=ft.Paint(style=ft.PaintingStyle.FILL,
                               color=_rgba(color, alpha)),
            ))

            # x-axis label — diagonal 45°, full text, tidak dipotong
            lbl = d["label"]
            shapes.append(cv.Text(
                x=bx + bw / 2,
                y=h - self.PAD_B + 6,
                value=lbl,
                rotate=0.785,   # 45 derajat dalam radian
                style=ft.TextStyle(
                    size=9,
                    color=c_primary if is_hov else c_text2,
                ),
            ))

        axis_p = ft.Paint(style=ft.PaintingStyle.STROKE,
                          stroke_width=1, color=c_border)
        shapes.append(cv.Path(
            [cv.Path.MoveTo(self.PAD_L, self.PAD_T),
             cv.Path.LineTo(self.PAD_L, h - self.PAD_B),
             cv.Path.LineTo(w - self.PAD_R, h - self.PAD_B)],
            axis_p,
        ))

        shapes.append(_cv_text_top_center(w / 2, 6, self._title, 12, c_text, bold=True))

        self._canvas.shapes = shapes
        self._canvas.update()

    def _on_hover(self, e):
        mx, my = e.local_position.x, e.local_position.y
        if self._w == 0:
            return
        hit = -1
        for i in range(len(self._data)):
            bx, by, bw, bh = self._bar_rect(i, self._w, self._h)
            if bx <= mx <= bx + bw and by - 4 <= my <= by + bh + 4:
                hit = i
                break
        if hit != self._hovered:
            self._hovered = hit
            self._redraw(hit)
            if hit >= 0:
                d = self._data[hit]
                rows = [("Jumlah Anime", str(d["value"]))]
                bx, by, bw, bh = self._bar_rect(hit, self._w, self._h)
                self._tooltip.show_at(bx + bw / 2, by, d["label"], rows)
            else:
                self._tooltip.hide()

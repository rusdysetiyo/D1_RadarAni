import flet as ft
import flet.canvas as cv
from .palette import (
    C_TEXT, C_TEXT2, C_TEXT3, C_SAKURA_DK, C_HOVER, C_BORDER, CHART_COLORS,
    _rgba, _cv_text_left, _cv_text_top_center
)
from .tooltip import Tooltip

class HorizontalBarChart(ft.Stack):
    PAD_L = 130
    PAD_R = 16
    PAD_T = 30
    PAD_B = 28

    def __init__(self, bar_data: list, title: str):
        super().__init__(expand=True)
        self._data    = bar_data
        self._title   = title
        self._hovered = -1
        self._tooltip = Tooltip()
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
        max_val = 10.0   # skala rating anime selalu 0–10
        area_w  = w - self.PAD_L - self.PAD_R
        area_h  = h - self.PAD_T - self.PAD_B
        slot_h  = area_h / n
        bar_h   = max(4.0, slot_h * 0.55)
        by      = self.PAD_T + i * slot_h + (slot_h - bar_h) / 2
        val     = self._data[i]["value"]
        # Selalu mulai dari 0 agar skala konsisten
        bar_w   = area_w * (val / max_val)
        return self.PAD_L, by, max(bar_w, 2.0), bar_h

    def _redraw(self, hovered):
        if self._w == 0:
            return
        w, h    = self._w, self._h
        shapes  = []
        max_val = 10.0   # skala rating anime selalu 0–10
        area_w  = w - self.PAD_L - self.PAD_R

        for i, d in enumerate(self._data):
            bx, by, bw, bh = self._bar_rect(i, w, h)
            is_hov = (i == hovered)
            color  = C_HOVER if is_hov else CHART_COLORS[i % len(CHART_COLORS)]
            alpha  = 1.0 if (is_hov or hovered == -1) else 0.45

            shapes.append(cv.Rect(
                x=bx, y=by, width=bw, height=bh,
                border_radius=4,
                paint=ft.Paint(style=ft.PaintingStyle.FILL,
                               color=_rgba(color, alpha)),
            ))

            shapes.append(_cv_text_left(
                6, by + bh / 2,
                d["label"], 9,
                C_SAKURA_DK if is_hov else C_TEXT2,
                bold=is_hov,
            ))

        # Grid vertikal + label sumbu X mulai dari 0
        grid_p = ft.Paint(style=ft.PaintingStyle.STROKE,
                          stroke_width=0.6, color="#20000000")
        for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
            gx   = self.PAD_L + area_w * frac
            gval = max_val * frac
            shapes.append(cv.Path(
                [cv.Path.MoveTo(gx, self.PAD_T),
                 cv.Path.LineTo(gx, h - self.PAD_B)],
                grid_p,
            ))
            shapes.append(_cv_text_top_center(
                gx, h - self.PAD_B + 4,
                f"{gval:.1f}", 8, C_TEXT3,
            ))

        axis_p = ft.Paint(style=ft.PaintingStyle.STROKE,
                          stroke_width=1, color=C_BORDER)
        shapes.append(cv.Path(
            [cv.Path.MoveTo(self.PAD_L, self.PAD_T),
             cv.Path.LineTo(self.PAD_L, h - self.PAD_B),
             cv.Path.LineTo(w - self.PAD_R, h - self.PAD_B)],
            axis_p,
        ))

        shapes.append(_cv_text_top_center(w / 2, 6, self._title, 12, C_TEXT, bold=True))

        self._canvas.shapes = shapes
        self._canvas.update()

    def _on_hover(self, e):
        mx, my = e.local_position.x, e.local_position.y
        if self._w == 0:
            return
        hit = -1
        for i in range(len(self._data)):
            bx, by, bw, bh = self._bar_rect(i, self._w, self._h)
            if bx <= mx <= bx + bw + 20 and by - 4 <= my <= by + bh + 4:
                hit = i
                break
        if hit != self._hovered:
            self._hovered = hit
            self._redraw(hit)
        if hit >= 0:
            d = self._data[hit]
            rows = [("Score", f"{d['value']:.2f}")]
            if d.get("extra"):
                rows.append(("Jumlah Anime", d["extra"]))
            self._tooltip.show_at(mx, my, d["label"], rows)
        else:
            self._tooltip.hide()

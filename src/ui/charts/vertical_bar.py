import flet as ft
import flet.canvas as cv
from .palette import (
    C_TEXT, C_TEXT2, C_TEXT3, C_SAKURA_DK, C_BORDER, CHART_COLORS,
    _rgba, _cv_text_right, _cv_text_left, _cv_text_top_center
)


class VerticalBarChart(ft.Container):
    """Vertical bar chart — judul dan hint sebagai ft.Text di atas canvas."""

    PAD_L = 46
    PAD_R = 12
    PAD_T = 30
    PAD_B = 72

    def __init__(self, bar_data: list, title: str, y_label: str = "",
                 theme: dict = None, tooltip=None):
        super().__init__(expand=True)
        self._data  = bar_data
        self._title = title
        self._theme = theme
        self._w = self._h = 0

        c_title = theme["text_main"] if theme else C_TEXT

        self._canvas = cv.Canvas(shapes=[], expand=True, on_resize=self._on_resize)

        title_bar = ft.Container(
            content=ft.Text(
                title, size=14, weight=ft.FontWeight.BOLD,
                color=c_title, text_align=ft.TextAlign.CENTER,
            ),
            padding=ft.padding.only(top=8, bottom=0),
            alignment=ft.alignment.Alignment.TOP_CENTER,
        )

        self.content = ft.Column(
            controls=[title_bar, ft.Stack(controls=[self._canvas], expand=True)],
            spacing=0,
        )

    def _on_resize(self, e):
        self._w, self._h = e.width, e.height
        self._redraw()

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

    def _redraw(self):
        if self._w == 0:
            return
        w, h    = self._w, self._h
        max_v   = max((d["value"] for d in self._data), default=1) or 1
        area_h  = h - self.PAD_T - self.PAD_B
        shapes  = []

        c_text2      = self._theme["text_secondary"]   if self._theme else C_TEXT2
        c_text3      = self._theme["text_secondary"]   if self._theme else C_TEXT2
        c_border     = self._theme["border_color"]     if self._theme else C_BORDER
        c_primary    = self._theme["primary"]          if self._theme else C_SAKURA_DK
        chart_colors = self._theme.get("chart_colors", CHART_COLORS) if self._theme else CHART_COLORS

        grid_p = ft.Paint(style=ft.PaintingStyle.STROKE,
                          stroke_width=0.7, color=self._theme["border_color"] if self._theme else "#22000000")
        for frac in [0.25, 0.5, 0.75, 1.0]:
            gy    = self.PAD_T + area_h * (1 - frac)
            label = str(int(max_v * frac))
            shapes.append(cv.Path(
                [cv.Path.MoveTo(self.PAD_L, gy),
                 cv.Path.LineTo(w - self.PAD_R, gy)],
                grid_p,
            ))
            shapes.append(_cv_text_right(self.PAD_L - 4, gy, label, 11, c_text3))

        for i, d in enumerate(self._data):
            bx, by, bw, bh = self._bar_rect(i, w, h)
            color = chart_colors[i % len(chart_colors)]

            shapes.append(cv.Rect(
                x=bx, y=by, width=bw, height=max(bh, 1),
                border_radius=4,
                paint=ft.Paint(style=ft.PaintingStyle.FILL, color=color),
            ))

            # Label nilai statis di atas bar
            shapes.append(_cv_text_top_center(
                bx + bw / 2, by - 15,
                str(d["value"]), 11, c_primary,
            ))

            # x-axis label — diagonal 45°
            shapes.append(cv.Text(
                x=bx + bw / 2,
                y=h - self.PAD_B + 6,
                value=d["label"],
                rotate=0.785,
                style=ft.TextStyle(size=11, color=c_text2),
            ))

        axis_p = ft.Paint(style=ft.PaintingStyle.STROKE,
                          stroke_width=1, color=c_border)
        shapes.append(cv.Path(
            [cv.Path.MoveTo(self.PAD_L, self.PAD_T),
             cv.Path.LineTo(self.PAD_L, h - self.PAD_B),
             cv.Path.LineTo(w - self.PAD_R, h - self.PAD_B)],
            axis_p,
        ))

        self._canvas.shapes = shapes
        self._canvas.update()

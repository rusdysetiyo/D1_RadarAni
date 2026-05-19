import flet as ft
import flet.canvas as cv
from .palette import (
    C_TEXT, C_TEXT2, C_TEXT3, C_SAKURA_DK, C_BORDER, CHART_COLORS,
    _rgba, _cv_text_left, _cv_text_top_center
)


class HorizontalBarChart(ft.Container):
    """Horizontal bar chart — judul sebagai ft.Text di atas canvas."""

    PAD_L = 130
    PAD_R = 56   # ruang untuk label nilai di ujung bar
    PAD_T = 6
    PAD_B = 28

    def __init__(self, bar_data: list, title: str, theme: dict = None, tooltip=None):
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
        max_val = 10.0
        area_w  = w - self.PAD_L - self.PAD_R
        area_h  = h - self.PAD_T - self.PAD_B
        slot_h  = area_h / n
        bar_h   = max(4.0, slot_h * 0.55)
        by      = self.PAD_T + i * slot_h + (slot_h - bar_h) / 2
        val     = self._data[i]["value"]
        bar_w   = area_w * (val / max_val)
        return self.PAD_L, by, max(bar_w, 2.0), bar_h

    def _redraw(self):
        if self._w == 0:
            return
        w, h    = self._w, self._h
        shapes  = []
        max_val = 10.0
        area_w  = w - self.PAD_L - self.PAD_R
        area_h  = h - self.PAD_T - self.PAD_B
        n       = len(self._data)

        c_text2      = self._theme["text_secondary"]   if self._theme else C_TEXT2
        c_text3      = self._theme["text_secondary"]   if self._theme else C_TEXT2
        c_border     = self._theme["border_color"]     if self._theme else C_BORDER
        c_primary    = self._theme["primary"]          if self._theme else C_SAKURA_DK
        chart_colors = self._theme.get("chart_colors", CHART_COLORS) if self._theme else CHART_COLORS

        slot_h = area_h / max(n, 1)

        for i, d in enumerate(self._data):
            bx, by, bw, bh = self._bar_rect(i, w, h)
            color = chart_colors[i % len(chart_colors)]

            shapes.append(cv.Rect(
                x=bx, y=by, width=bw, height=bh,
                border_radius=4,
                paint=ft.Paint(style=ft.PaintingStyle.FILL, color=color),
            ))

            # Label studio — rata kanan, sejajar vertikal tengah bar
            cy_bar = self.PAD_T + i * slot_h + slot_h / 2
            shapes.append(_cv_text_left(6, cy_bar, d["label"], 11, c_text2))

            # Label nilai statis di ujung kanan bar
            shapes.append(_cv_text_left(
                bx + bw + 5, cy_bar,
                f"{d['value']:.2f}", 11, c_primary,
            ))

        # Grid vertikal + label sumbu X
        grid_p = ft.Paint(style=ft.PaintingStyle.STROKE,
                          stroke_width=0.6, color=self._theme["border_color"] if self._theme else "#20000000")
        for frac in [0.0, 0.25, 0.5, 0.75, 1.0]:
            gx   = self.PAD_L + area_w * frac
            gval = max_val * frac
            shapes.append(cv.Path(
                [cv.Path.MoveTo(gx, self.PAD_T),
                 cv.Path.LineTo(gx, h - self.PAD_B)],
                grid_p,
            ))
            shapes.append(_cv_text_top_center(
                gx, h - self.PAD_B + 4, f"{gval:.1f}", 11, c_text3,
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

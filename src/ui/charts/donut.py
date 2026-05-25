import math
import flet as ft
import flet.canvas as cv
from .palette import (
    C_TEXT, C_TEXT2, C_SAKURA_DK, C_WHITE, CHART_COLORS,
    _rgba, _arc_points, _cv_text_left
)


class DonutChart(ft.Container):
    """Donut chart — judul ditampilkan sebagai ft.Text di luar canvas agar selalu tengah."""

    def __init__(self, data: list, title: str, theme: dict = None, tooltip=None):
        super().__init__(expand=True)
        self._data    = data
        self._title   = title
        self._theme   = theme
        self._w = self._h = 0

        c_title = theme["text_main"] if theme else C_TEXT

        self._canvas = cv.Canvas(shapes=[], expand=True, on_resize=self._on_resize)

        # Judul sebagai ft.Text → centering akurat tanpa estimasi lebar
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

    def _geometry(self):
        pie_area_w = self._w * 0.52
        cx         = pie_area_w / 2
        cy         = self._h / 2
        outer_r    = min(pie_area_w / 2 * 0.82, (self._h - 20) / 2)
        inner_r    = outer_r * 0.50
        return cx, cy, outer_r, inner_r

    def _slice_angles(self):
        total = sum(d["value"] for d in self._data) or 1
        angles, cur = [], -math.pi / 2
        for d in self._data:
            sw = 2 * math.pi * d["value"] / total
            angles.append((cur, sw))
            cur += sw
        return angles

    def _redraw(self):
        if self._w == 0:
            return
        cx, cy, outer_r, inner_r = self._geometry()
        angles = self._slice_angles()
        shapes = []

        c_text2      = self._theme["text_secondary"]   if self._theme else C_TEXT2
        c_white      = self._theme["card"]             if self._theme else C_WHITE
        chart_colors = self._theme.get("chart_colors", CHART_COLORS) if self._theme else CHART_COLORS

        for i, (d, (sa, sw)) in enumerate(zip(self._data, angles)):
            color = chart_colors[i % len(chart_colors)]

            outer_pts     = _arc_points(cx, cy, outer_r, sa, sw)
            inner_pts     = _arc_points(cx, cy, inner_r, sa, sw)
            inner_pts_rev = list(reversed(inner_pts))

            elements = [cv.Path.MoveTo(*outer_pts[0])]
            for pt in outer_pts[1:]:
                elements.append(cv.Path.LineTo(*pt))
            elements.append(cv.Path.LineTo(*inner_pts_rev[0]))
            for pt in inner_pts_rev[1:]:
                elements.append(cv.Path.LineTo(*pt))
            elements.append(cv.Path.Close())

            shapes.append(cv.Path(
                elements=elements,
                paint=ft.Paint(style=ft.PaintingStyle.FILL, color=color),
            ))
            border_els = [cv.Path.MoveTo(*outer_pts[0])]
            for pt in outer_pts[1:]:
                border_els.append(cv.Path.LineTo(*pt))
            shapes.append(cv.Path(
                elements=border_els,
                paint=ft.Paint(style=ft.PaintingStyle.STROKE,
                               stroke_width=1.5, color=c_white),
            ))

        # Legend — kanan chart
        leg_x       = self._w * 0.52 + 8
        row_h       = 20
        n           = len(self._data)
        total_leg_h = n * row_h
        leg_start_y = (self._h - total_leg_h) / 2

        for i, d in enumerate(self._data):
            color = chart_colors[i % len(chart_colors)]
            ly    = leg_start_y + i * row_h + row_h / 2
            box   = 9
            shapes.append(cv.Rect(
                x=leg_x, y=ly - box / 2,
                width=box, height=box,
                border_radius=2,
                paint=ft.Paint(style=ft.PaintingStyle.FILL, color=color),
            ))
            txt = f"{d['label']}  {d['value']} ({d['pct']:.1f}%)"
            shapes.append(_cv_text_left(leg_x + box + 5, ly, txt, 11, c_text2))

        self._canvas.shapes = shapes
        self._canvas.update()

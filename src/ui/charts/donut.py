import math
import flet as ft
import flet.canvas as cv
from .palette import (
    C_TEXT, C_TEXT2, C_SAKURA_DK, C_WHITE, CHART_COLORS,
    _rgba, _arc_points, _cv_text_left, _cv_text_top_center
)
from .tooltip import Tooltip

class DonutChart(ft.Stack):
    def __init__(self, data: list, title: str, theme: dict = None, tooltip=None):
        super().__init__(expand=True)
        self._data    = data
        self._title   = title
        self._hovered = -1
        self._theme   = theme
        self._w = self._h = 0

        self._owns_tooltip = tooltip is None
        self._tooltip      = tooltip if tooltip is not None else Tooltip()

        self._canvas = cv.Canvas(shapes=[], expand=True,
                                 on_resize=self._on_resize)
        self._gd = ft.GestureDetector(
            content=ft.Container(expand=True),
            on_hover=self._on_hover,
        )
        if self._owns_tooltip:
            self.controls = [self._canvas, self._gd, self._tooltip]
        else:
            self.controls = [self._canvas, self._gd]

    def _on_resize(self, e):
        self._w, self._h = e.width, e.height
        self._redraw(self._hovered)

    def _geometry(self):
        # Pie di setengah kiri, legend di kanan
        # cx tepat di tengah area kiri
        pie_area_w = self._w * 0.52
        cx         = pie_area_w / 2
        cy         = self._h / 2 + 8
        outer_r    = min(pie_area_w / 2 * 0.82, (self._h - 60) / 2)
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

    def _redraw(self, hovered):
        if self._w == 0:
            return
        cx, cy, outer_r, inner_r = self._geometry()
        angles = self._slice_angles()
        shapes = []

        c_text       = self._theme["text_main"]        if self._theme else C_TEXT
        c_text2      = self._theme["text_secondary"]   if self._theme else C_TEXT2
        c_white      = self._theme["card"]             if self._theme else C_WHITE
        c_primary    = self._theme["primary"]          if self._theme else C_SAKURA_DK
        chart_colors = self._theme.get("chart_colors", CHART_COLORS) if self._theme else CHART_COLORS

        for i, (d, (sa, sw)) in enumerate(zip(self._data, angles)):
            is_hov = (i == hovered)
            color  = chart_colors[i % len(chart_colors)]
            alpha  = 1.0 if (is_hov or hovered == -1) else 0.38
            expand = 7 if is_hov else 0
            mid_a  = sa + sw / 2
            ocx    = cx + expand * math.cos(mid_a)
            ocy    = cy + expand * math.sin(mid_a)


            outer_pts = _arc_points(ocx, ocy, outer_r, sa, sw)

            inner_pts = _arc_points(ocx, ocy, inner_r, sa, sw)
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
                paint=ft.Paint(style=ft.PaintingStyle.FILL,
                               color=_rgba(color, alpha)),
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
        leg_x  = self._w * 0.52 + 8
        row_h  = 20
        n      = len(self._data)

        total_leg_h = n * row_h
        leg_start_y = (self._h - total_leg_h) / 2 + 10

        for i, d in enumerate(self._data):
            is_hov   = (i == hovered)
            color    = chart_colors[i % len(chart_colors)]
            leg_alph = 1.0 if (is_hov or hovered == -1) else 0.38
            ly       = leg_start_y + i * row_h + row_h / 2

            box = 9
            shapes.append(cv.Rect(
                x=leg_x, y=ly - box / 2,
                width=box, height=box,
                border_radius=2,
                paint=ft.Paint(style=ft.PaintingStyle.FILL,
                               color=_rgba(color, leg_alph)),
            ))
            txt = f"{d['label']}  {d['value']} ({d['pct']:.1f}%)"
            shapes.append(_cv_text_left(
                leg_x + box + 5, ly, txt, 10,
                c_primary if is_hov else c_text2,
                bold=is_hov,
            ))

        # Title center atas
        shapes.append(_cv_text_top_center(
            self._w / 2, 6, self._title, 12, c_text, bold=True))

        self._canvas.shapes = shapes
        self._canvas.update()

    def _on_hover(self, e):
        mx, my = e.local_position.x, e.local_position.y
        if self._w == 0:
            return
        cx, cy, outer_r, inner_r = self._geometry()
        dx, dy = mx - cx, my - cy
        dist   = math.hypot(dx, dy)

        hit = -1
        if inner_r - 4 <= dist <= outer_r + 8:
            angle  = math.atan2(dy, dx)
            angles = self._slice_angles()
            for i, (sa, sw) in enumerate(angles):
                a_norm = (angle - sa) % (2 * math.pi)
                if 0 <= a_norm < sw:
                    hit = i
                    break

        if hit == self._hovered:
            return

        self._hovered = hit
        self._redraw(hit)
        if hit >= 0:
            d = self._data[hit]
            self._tooltip.show_at(
                e.global_position.x, e.global_position.y,
                d["label"],
                [("Jumlah", str(d["value"])),
                 ("Persen", f"{d['pct']:.1f}%")],
            )
        else:
            self._tooltip.hide()

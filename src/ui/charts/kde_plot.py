import math
import flet as ft
import flet.canvas as cv
from .palette import (
    C_TEXT, C_TEXT3, C_BORDER, C_SAKURA, C_SAKURA_DK, C_HOVER,
    _rgba, _cv_text_right, _cv_text_top_center
)
from .tooltip import Tooltip

class KDEChart(ft.Container):
    PAD_L = 36
    PAD_R = 16
    PAD_T = 16
    PAD_B = 28

    def __init__(self, animes: list, theme: dict = None):
        super().__init__(expand=True)
        self._animes = animes
        self._theme  = theme
        self._hovered_idx = -1
        self._tooltip = Tooltip()
        self._w = self._h = 0
        
        self._dim_labels = ["Global Score", "Plot", "Visual", "Audio", "Characterization", "Direction"]
        self._selected_dim = "Global Score"

        _border_color = theme["border_color"] if theme else C_BORDER
        _text_color   = theme["text_main"]    if theme else C_TEXT
        self._dropdown = ft.Dropdown(
            options=[ft.dropdown.Option(l) for l in self._dim_labels],
            value=self._selected_dim,
            width=140,
            height=32,
            text_size=11,
            content_padding=ft.padding.symmetric(horizontal=8, vertical=2),
            border_color=_border_color,
            border_radius=6,
        )
        if hasattr(self._dropdown, 'on_change'):
            self._dropdown.on_change = self._on_dim_change
        if hasattr(self._dropdown, 'on_select'):
            self._dropdown.on_select = self._on_dim_change

        self._cached_xs = []
        self._cached_ys = []

        self._canvas = cv.Canvas(shapes=[], expand=True, on_resize=self._on_resize)
        self._gd = ft.GestureDetector(
            content=ft.Container(expand=True),
            on_hover=self._on_hover,
        )
        
        _title_color = theme["text_main"] if theme else C_TEXT
        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("Rating Distribution (KDE Plot)", size=12, weight=ft.FontWeight.BOLD, color=_title_color),
                            self._dropdown,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.padding.only(left=16, right=16, top=12, bottom=0)
                ),
                ft.Stack(controls=[self._canvas, self._gd, self._tooltip], expand=True),
            ],
            spacing=0,
        )
        
        # Precompute the KDE for the initial default dimension
        self._update_kde_cache()

    def _on_dim_change(self, e):
        self._selected_dim = e.control.value
        self._update_kde_cache()
        self._redraw(-1)

    def _on_resize(self, e):
        self._w, self._h = e.width, e.height
        self._redraw(self._hovered_idx)

    def _update_kde_cache(self):
        data = self._get_data()
        self._cached_xs, self._cached_ys = self._kde(data, grid_points=60)

    def _get_data(self):
        data = []
        dim_idx = self._dim_labels.index(self._selected_dim) - 1
        for a in self._animes:
            if self._selected_dim == "Global Score":
                score = a.get("global_score")
            else:
                dims = a.get("global_score_dimensions", [0,0,0,0,0])
                score = dims[dim_idx] if dim_idx < len(dims) else 0
                
            if isinstance(score, (int, float)) and score > 0:
                data.append(float(score))
        return data

    def _kde(self, data, grid_points=100):
        n = len(data)
        if n == 0:
            return [], []
        mean = sum(data) / n
        variance = sum((x - mean)**2 for x in data) / n
        std_dev = math.sqrt(variance) if variance > 0 else 1e-6
        h = 1.06 * std_dev * (n ** -0.2)
        if h == 0: h = 1e-6

        xs = [i * 10.0 / (grid_points - 1) for i in range(grid_points)]
        ys = []
        
        constant = 1.0 / (math.sqrt(2 * math.pi) * h * n)
        for x in xs:
            density = 0
            for xi in data:
                u = (x - xi) / h
                density += math.exp(-0.5 * u * u)
            ys.append(density * constant)
            
        return xs, ys

    def _redraw(self, hover_idx=-1):
        if self._w == 0:
            return
        w, h = self._w, self._h
        area_w = w - self.PAD_L - self.PAD_R
        area_h = h - self.PAD_T - self.PAD_B
        shapes = []

        xs, ys = self._cached_xs, self._cached_ys
        
        max_y = max(ys) if ys else 1.0
        if max_y == 0: max_y = 1.0

        c_text3   = self._theme["text_muted"]   if self._theme else C_TEXT3
        c_border  = self._theme["border_color"] if self._theme else C_BORDER
        c_primary = self._theme["primary"]       if self._theme else C_SAKURA
        c_primary_dk = self._theme["primary"]   if self._theme else C_SAKURA_DK
        c_hover   = self._theme["primary"]       if self._theme else C_HOVER

        axis_p = ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=1, color=c_border)
        shapes.append(cv.Path(
            [cv.Path.MoveTo(self.PAD_L, self.PAD_T),
             cv.Path.LineTo(self.PAD_L, h - self.PAD_B),
             cv.Path.LineTo(w - self.PAD_R, h - self.PAD_B)],
            axis_p,
        ))

        grid_p = ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=0.7, color="#22000000")
        for frac in [0.0, 0.5, 1.0]:
            gy = self.PAD_T + area_h * (1 - frac)
            lbl = f"{max_y * frac:.2f}"
            shapes.append(cv.Path(
                [cv.Path.MoveTo(self.PAD_L, gy), cv.Path.LineTo(w - self.PAD_R, gy)],
                grid_p,
            ))
            shapes.append(_cv_text_right(self.PAD_L - 4, gy, lbl, 9, c_text3))

        for i in range(11):
            gx = self.PAD_L + area_w * (i / 10.0)
            shapes.append(cv.Path(
                [cv.Path.MoveTo(gx, h - self.PAD_B), cv.Path.LineTo(gx, h - self.PAD_B + 4)],
                axis_p,
            ))
            shapes.append(_cv_text_top_center(gx, h - self.PAD_B + 6, str(i), 9, c_text3))

        if not xs:
            self._canvas.shapes = shapes
            self._canvas.update()
            return

        pts = []
        for x, y in zip(xs, ys):
            px = self.PAD_L + area_w * (x / 10.0)
            py = self.PAD_T + area_h * (1 - y / max_y)
            pts.append((px, py))

        fill_els = [cv.Path.MoveTo(pts[0][0], h - self.PAD_B)]
        for px, py in pts:
            fill_els.append(cv.Path.LineTo(px, py))
        fill_els.append(cv.Path.LineTo(pts[-1][0], h - self.PAD_B))
        fill_els.append(cv.Path.Close())
        shapes.append(cv.Path(
            elements=fill_els,
            paint=ft.Paint(style=ft.PaintingStyle.FILL, color=_rgba(c_primary, 0.3)),
        ))

        stroke_els = [cv.Path.MoveTo(pts[0][0], pts[0][1])]
        for px, py in pts[1:]:
            stroke_els.append(cv.Path.LineTo(px, py))
        shapes.append(cv.Path(
            elements=stroke_els,
            paint=ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=2, color=c_primary_dk),
        ))

        if hover_idx >= 0 and hover_idx < len(xs):
            px = self.PAD_L + area_w * (xs[hover_idx] / 10.0)
            py = self.PAD_T + area_h * (1 - ys[hover_idx] / max_y)
            shapes.append(cv.Path(
                [cv.Path.MoveTo(px, self.PAD_T), cv.Path.LineTo(px, h - self.PAD_B)],
                ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=1, color=c_hover),
            ))
            shapes.append(cv.Circle(
                x=px, y=py, radius=4,
                paint=ft.Paint(style=ft.PaintingStyle.FILL, color=c_hover)
            ))
                
        self._canvas.shapes = shapes
        self._canvas.update()

    def _on_hover(self, e):
        mx, my = e.local_position.x, e.local_position.y
        if self._w == 0:
            return
            
        area_w = self._w - self.PAD_L - self.PAD_R
        area_h = self._h - self.PAD_T - self.PAD_B

        if self.PAD_L <= mx <= self._w - self.PAD_R and self.PAD_T <= my <= self._h - self.PAD_B + 10:
            xs, ys = self._cached_xs, self._cached_ys
            if xs:
                rel_x = (mx - self.PAD_L) / area_w * 10.0
                idx = int(rel_x / 10.0 * (len(xs) - 1))
                idx = max(0, min(idx, len(xs)-1))
                
                if self._hovered_idx != idx:
                    self._hovered_idx = idx
                    self._redraw(idx)
                    
                    rows = [
                        ("Score", f"{xs[idx]:.1f}"),
                        ("Density", f"{ys[idx]:.4f}")
                    ]
                    px = self.PAD_L + area_w * (xs[idx] / 10.0)
                    self._tooltip.show_at(px, my, self._selected_dim, rows)
        else:
            if self._hovered_idx != -1:
                self._hovered_idx = -1
                self._redraw(-1)
                self._tooltip.hide()

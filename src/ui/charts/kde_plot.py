import math
import flet as ft
import flet.canvas as cv
from .palette import (
    C_TEXT, C_TEXT2,C_TEXT3, C_BORDER, C_SAKURA, C_SAKURA_DK,
    _rgba, _cv_text_right, _cv_text_top_center, _cv_text_center,
    _text_w, _text_h
)


class BaseKDEChart(ft.Container):
    PAD_L = 64
    PAD_R = 16
    PAD_T = 16
    PAD_B = 44

    def __init__(self, title: str, dim_labels: list, default_dim: str, theme: dict = None, tooltip=None):
        super().__init__(expand=True)
        self._theme = theme
        self._w = self._h = 0
        self._dim_labels = dim_labels
        self._selected_dim = default_dim

        _border_color = theme["border_color"] if theme else C_BORDER
        self._title_color  = theme["text_main"]    if theme else C_TEXT

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

        _text3_color = theme["text_secondary"] if theme else C_TEXT3
        self._y_axis_label = ft.Container(
            content=ft.Text("Density", size=11, weight=ft.FontWeight.BOLD, color=_text3_color, no_wrap=True),
            rotate=ft.Rotate(-math.pi / 2, alignment=ft.Alignment(0, 0)),
            left=2, top=0, bottom=0, alignment=ft.Alignment(0, 0),
        )

        self._stats_panel = ft.Container(expand=True)
        
        # Subtitle label (e.g. for raters count)
        self._subtitle_text = ft.Text("", size=11, color=theme["text_secondary"] if theme else C_TEXT2)

        self.content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(title, size=14, weight=ft.FontWeight.BOLD, color=self._title_color),
                            self._subtitle_text,
                            ft.Container(expand=True),
                            self._dropdown,
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.only(left=16, right=16, top=12, bottom=0),
                ),
                ft.Stack(controls=[self._canvas, self._y_axis_label], expand=True),
                self._stats_panel,
            ],
            spacing=0,
        )

    def _get_data(self) -> list:
        raise NotImplementedError("Subclasses must implement _get_data()")

    def _get_item_noun(self) -> str:
        return "item" # "anime" for global, "penilai" for detail

    # ── Dim change ────────────────────────────────────────────────────────────
    def _on_dim_change(self, e):
        self._selected_dim = e.control.value
        self._update_kde_cache()
        self._redraw()
        self._refresh_stats()

    def _on_resize(self, e):
        self._w, self._h = e.width, e.height
        self._redraw()

    # ── Data & KDE ────────────────────────────────────────────────────────────
    def _update_kde_cache(self):
        data = self._get_data()
        self._cached_xs, self._cached_ys = self._kde(data, grid_points=80)

    @staticmethod
    def _kde(data: list, grid_points: int = 80):
        n = len(data)
        if n == 0:
            return [], []
        mean     = sum(data) / n
        variance = sum((x - mean) ** 2 for x in data) / n
        std_dev  = math.sqrt(variance) if variance > 0 else 1e-6
        h        = 1.06 * std_dev * (n ** -0.2) or 1e-6
        xs       = [i * 10.0 / (grid_points - 1) for i in range(grid_points)]
        constant = 1.0 / (math.sqrt(2 * math.pi) * h * n)
        
        # Optimasi matematis: hitung konstanta pembagi eksponen di luar iterasi
        inv_h2 = -0.5 / (h ** 2)
        ys = [
            sum(math.exp(inv_h2 * ((x - xi) ** 2)) for xi in data) * constant
            for x in xs
        ]
        return xs, ys

    # ── Statistik ─────────────────────────────────────────────────────────────
    def _compute_stats(self) -> dict | None:
        data = sorted(self._get_data())
        n    = len(data)
        if n == 0:
            return None

        mean     = sum(data) / n
        median   = (data[(n - 1) // 2] + data[n // 2]) / 2
        variance = sum((x - mean) ** 2 for x in data) / n
        std_dev  = math.sqrt(variance) if variance > 0 else 0.0

        if self._cached_ys:
            peak_idx = self._cached_ys.index(max(self._cached_ys))
            peak     = self._cached_xs[peak_idx]
        else:
            peak = mean

        def percentile(p: float) -> float:
            if n == 1:
                return data[0]
            k = (n - 1) * p / 100.0
            f = int(k)
            return data[f] + (k - f) * (data[min(f + 1, n - 1)] - data[f])

        return {
            "n":       n,
            "mean":    mean,
            "median":  median,
            "std_dev": std_dev,
            "min":     data[0],
            "max":     data[-1],
            "peak":    peak,
            "p25":     percentile(25),
            "p75":     percentile(75),
            "p90":     percentile(90),
            "p99":     percentile(99),
        }

    # ── Panel statistik ───────────────────────────────────────────────────────
    def _refresh_stats(self):
        stats   = self._compute_stats()
        theme   = self._theme

        c_text    = theme["text_main"]                       if theme else "#1A1A1A"
        c_text2   = theme["text_secondary"]                  if theme else "#555555"
        c_text3   = theme["text_secondary"]                  if theme else "#888888"
        c_primary = theme["primary"]                         if theme else "#C07090"
        c_bg      = theme["card"]                            if theme else "#FFFFFF"
        c_border  = theme["border_color"]                    if theme else "#E0D0D8"
        c_accent  = theme.get("primary_light", "#FDF0F5")   if theme else "#FDF0F5"
        
        noun = self._get_item_noun()

        if stats is None:
            self._subtitle_text.value = ""
            self._stats_panel.content = ft.Text(
                "Tidak ada data rating.", size=11, color=c_text3,
                text_align=ft.TextAlign.CENTER,
            )
            self._try_update(self._subtitle_text)
            self._try_update(self._stats_panel)
            return
            
        self._subtitle_text.value = f"({stats['n']} {noun})"
        self._try_update(self._subtitle_text)

        def _tile(label: str, value: str, highlight: bool = False) -> ft.Container:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(value, size=14, weight=ft.FontWeight.BOLD, color=c_primary if highlight else c_text, text_align=ft.TextAlign.CENTER),
                        ft.Text(label, size=11, color=c_text3, text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2, tight=True,
                ),
                bgcolor=c_bg, border=ft.border.all(1, c_border), border_radius=8,
                padding=ft.padding.symmetric(horizontal=8, vertical=7), expand=True,
            )

        tiles_row = ft.Row(
            controls=[
                _tile("Rata-rata",  f"{stats['mean']:.2f}"),
                _tile("Median",     f"{stats['median']:.2f}"),
                _tile("Skor Puncak", f"{stats['peak']:.2f}", highlight=True),
                _tile("Terendah",   f"{stats['min']:.1f}"),
                _tile("Tertinggi",  f"{stats['max']:.1f}"),
            ],
            spacing=5, expand=True,
        )

        lo       = max(0.0, stats["mean"] - stats["std_dev"])
        hi       = min(10.0, stats["mean"] + stats["std_dev"])
        
        verb = "memiliki rating" if noun == "anime" else "memberi rating"
        std_row = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.SHOW_CHART, color=c_primary, size=15),
                    ft.Text(
                        spans=[
                            ft.TextSpan(f"Standar deviasi ±{stats['std_dev']:.2f}", style=ft.TextStyle(weight=ft.FontWeight.BOLD, color=c_primary)),
                            ft.TextSpan(f"  →  ~68% {noun} {verb} antara {lo:.1f} – {hi:.1f}", style=ft.TextStyle(color=c_text, weight=ft.FontWeight.W_500))
                        ],
                        size=12, expand=True
                    ),
                ],
                spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=c_bg, border=ft.border.all(1, c_primary), border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
        )
        
        controls = [
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.ANALYTICS_OUTLINED, color=c_primary, size=13),
                    ft.Text(f"Ringkasan Distribusi  •  {self._selected_dim}  •  {stats['n']} {noun}", size=11, weight=ft.FontWeight.W_600, color=c_text2),
                ],
                spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            tiles_row,
            std_row
        ]
        
        # Only KDEChart (anime noun) typically shows percentiles, but we can show it for both if we want.
        # Following original behavior, only the global analytics showed percentiles section.
        if noun == "anime":
            def _pct_chip(label: str, value: float, ge: bool = True) -> ft.Container:
                val_str = f"≥ {value:.2f}" if ge else f"≤ {value:.2f}"
                return ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Text(label, size=11, color=c_text3, text_align=ft.TextAlign.CENTER),
                            ft.Text(val_str, size=11, weight=ft.FontWeight.BOLD, color=c_primary if ge else c_text2, text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=1, tight=True,
                    ),
                    bgcolor=c_bg, border=ft.border.all(1, c_border), border_radius=6,
                    padding=ft.padding.symmetric(horizontal=8, vertical=5), expand=True,
                )
            controls.append(ft.Row(
                controls=[
                    ft.Text("Persentil:", size=11, color=c_text3, weight=ft.FontWeight.W_600),
                    _pct_chip("Top 1%",      stats["p99"], ge=True),
                    _pct_chip("Top 10%",     stats["p90"], ge=True),
                    _pct_chip("Top 25%",     stats["p75"], ge=True),
                    _pct_chip("Bottom 25%",  stats["p25"], ge=False),
                ],
                spacing=5, vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ))

        self._stats_panel.content = ft.Container(
            content=ft.Column(controls=controls, spacing=6, tight=True),
            bgcolor=c_accent, border=ft.border.all(1, c_border), border_radius=10,
            padding=ft.padding.symmetric(horizontal=12, vertical=10),
            margin=ft.margin.only(left=8, right=8, bottom=10, top=4),
        )
        self._try_update(self._stats_panel)

    @staticmethod
    def _try_update(ctrl):
        try:
            ctrl.update()
        except Exception:
            pass

    # ── Render canvas ─────────────────────────────────────────────────────────
    def _redraw(self):
        if self._w == 0:
            return
        w, h   = self._w, self._h
        area_w = w - self.PAD_L - self.PAD_R
        area_h = h - self.PAD_T - self.PAD_B
        shapes = []

        xs, ys = self._cached_xs, self._cached_ys
        max_y  = max(ys) if ys else 1.0
        if max_y == 0:
            max_y = 1.0

        c_text3      = self._theme["text_secondary"]   if self._theme else C_TEXT2
        c_border     = self._theme["border_color"] if self._theme else C_BORDER
        c_primary    = self._theme["primary"]      if self._theme else C_SAKURA
        c_primary_dk = self._theme["primary"]      if self._theme else C_SAKURA_DK

        axis_p = ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=1, color=c_border)
        shapes.append(cv.Path(
            [cv.Path.MoveTo(self.PAD_L, self.PAD_T),
             cv.Path.LineTo(self.PAD_L, h - self.PAD_B),
             cv.Path.LineTo(w - self.PAD_R, h - self.PAD_B)],
            axis_p,
        ))

        grid_p = ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=0.7, color=self._theme["border_color"] if self._theme else "#22000000")
        for frac in [0.0, 0.5, 1.0]:
            gy  = self.PAD_T + area_h * (1 - frac)
            lbl = f"{max_y * frac:.2f}"
            shapes.append(cv.Path(
                [cv.Path.MoveTo(self.PAD_L, gy), cv.Path.LineTo(w - self.PAD_R, gy)],
                grid_p,
            ))
            shapes.append(_cv_text_right(self.PAD_L - 4, gy, lbl, 11, c_text3))

        for i in range(11):
            gx = self.PAD_L + area_w * (i / 10.0)
            shapes.append(cv.Path(
                [cv.Path.MoveTo(gx, h - self.PAD_B), cv.Path.LineTo(gx, h - self.PAD_B + 4)],
                axis_p,
            ))
            shapes.append(_cv_text_top_center(gx, h - self.PAD_B + 6, str(i), 11, c_text3))

        # ── Label sumbu X ────────────────────────────────────────────────
        x_label_x = self.PAD_L + area_w / 2
        x_label_y = h - 4
        shapes.append(_cv_text_top_center(
            x_label_x, x_label_y - _text_h(11), self._selected_dim, 11, c_text3, bold=True))

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
            paint=ft.Paint(style=ft.PaintingStyle.FILL, color=_rgba(c_primary, 0.30)),
        ))

        stroke_els = [cv.Path.MoveTo(pts[0][0], pts[0][1])]
        for px, py in pts[1:]:
            stroke_els.append(cv.Path.LineTo(px, py))
        shapes.append(cv.Path(
            elements=stroke_els,
            paint=ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=2, color=c_primary_dk),
        ))

        if self._cached_ys:
            peak_idx = self._cached_ys.index(max(self._cached_ys))
            peak_px  = self.PAD_L + area_w * (self._cached_xs[peak_idx] / 10.0)
            shapes.append(cv.Path(
                [cv.Path.MoveTo(peak_px, self.PAD_T),
                 cv.Path.LineTo(peak_px, h - self.PAD_B)],
                ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=1.2,
                         stroke_dash_pattern=[4, 3], color=_rgba(c_primary_dk, 0.55)),
            ))

        self._canvas.shapes = shapes
        self._canvas.update()


class KDEChart(BaseKDEChart):
    def __init__(self, animes: list, theme: dict = None, tooltip=None):
        self._animes = animes
        dim_labels = ["Global Score", "Plot", "Visual", "Audio", "Characterization", "Direction"]
        super().__init__("Rating Distribution (KDE Plot)", dim_labels, "Global Score", theme, tooltip)
        self._update_kde_cache()
        self._refresh_stats()

    def _get_data(self) -> list:
        data    = []
        dim_idx = self._dim_labels.index(self._selected_dim) - 1
        for a in self._animes:
            if self._selected_dim == "Global Score":
                score = a.get("global_score")
            else:
                dims  = a.get("global_score_dimensions", [0, 0, 0, 0, 0])
                score = dims[dim_idx] if dim_idx < len(dims) else 0
            if isinstance(score, (int, float)) and score > 0:
                data.append(float(score))
        return data

    def _get_item_noun(self) -> str:
        return "anime"


class DetailKDEChart(BaseKDEChart):
    def __init__(self, scores_by_dim: dict, theme: dict = None):
        self._scores_by_dim = scores_by_dim
        dim_labels = list(scores_by_dim.keys())
        default_dim = dim_labels[0] if dim_labels else "Average"
        super().__init__("User Rating Distribution", dim_labels, default_dim, theme)
        self._update_kde_cache()
        self._refresh_stats()

    def _get_data(self) -> list:
        return [float(v) for v in self._scores_by_dim.get(self._selected_dim, [])
                if isinstance(v, (int, float)) and v > 0]

    def _get_item_noun(self) -> str:
        return "penilai"


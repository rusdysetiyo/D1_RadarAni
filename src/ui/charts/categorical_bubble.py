import math
import flet as ft
import flet.canvas as cv
from collections import Counter
from .palette import (
    C_TEXT, C_TEXT2, C_TEXT3, C_SAKURA_DK, C_WHITE,
    _rgba, _cv_text_left, _cv_text_right, _cv_text_top_center
)
from .tooltip import Tooltip

class CategoricalBubbleChart(ft.Container):
    """
    Bubble chart kategorik:
      Sumbu X  → Top 15 Genre
      Sumbu Y  → Top 10 Studio
      Ukuran   → Jumlah anime (studio, genre)
      Warna    → Rating rata-rata (merah=rendah, hijau=tinggi)
    """
    MAX_STUDIOS = 10
    MAX_GENRES  = 15
    PAD_L = 120
    PAD_R = 16
    PAD_T = 6    # canvas tidak lagi punya judul
    PAD_B = 90

    RATING_STOPS = [
        (0.0,  "#CC2200"),
        (0.35, "#E05010"),
        (0.55, "#C8A000"),
        (0.75, "#50A830"),
        (1.0,  "#1A6B20"),
    ]

    @staticmethod
    def _rating_color(rating: float) -> str:
        t     = max(0.0, min(1.0, rating / 10.0))
        stops = CategoricalBubbleChart.RATING_STOPS
        for k in range(len(stops) - 1):
            t0, c0 = stops[k]
            t1, c1 = stops[k + 1]
            if t0 <= t <= t1:
                f = (t - t0) / (t1 - t0)
                r0, g0, b0 = int(c0[1:3],16), int(c0[3:5],16), int(c0[5:7],16)
                r1, g1, b1 = int(c1[1:3],16), int(c1[3:5],16), int(c1[5:7],16)
                r = int(r0 + f*(r1-r0))
                g = int(g0 + f*(g1-g0))
                b = int(b0 + f*(b1-b0))
                return f"#{r:02X}{g:02X}{b:02X}"
        return stops[-1][1]

    def __init__(self, animes: list, title: str, theme: dict = None, tooltip=None):
        super().__init__(expand=True)
        self._title   = title
        self._theme   = theme
        self._clicked = (-1, -1)   # (studio_idx, genre_idx) yang aktif
        self._w = self._h = 0

        studio_count: Counter = Counter()
        for a in animes:
            s = (a.get("studio") or "Unknown").strip()
            if s:
                studio_count[s] += 1
        self._studios = [s for s, _ in studio_count.most_common(self.MAX_STUDIOS)]

        genre_count: Counter = Counter()
        for a in animes:
            for g in a.get("genre", []):
                genre_count[g] += 1
        self._genres = [g for g, _ in genre_count.most_common(self.MAX_GENRES)]

        studio_set = set(self._studios)
        genre_set  = set(self._genres)

        cell: dict = {}
        for a in animes:
            s = (a.get("studio") or "Unknown").strip()
            if s not in studio_set:
                continue
            score = a.get("global_score")
            si    = self._studios.index(s)
            for g in a.get("genre", []):
                if g not in genre_set:
                    continue
                gi  = self._genres.index(g)
                key = (si, gi)
                if key not in cell:
                    cell[key] = {"count": 0, "scores": []}
                cell[key]["count"] += 1
                if isinstance(score, (int, float)):
                    cell[key]["scores"].append(float(score))

        self._bubbles = []
        max_count = 1
        for (si, gi), v in cell.items():
            cnt       = v["count"]
            avg_score = (sum(v["scores"]) / len(v["scores"])) if v["scores"] else 0.0
            self._bubbles.append({"si": si, "gi": gi, "count": cnt, "avg_score": avg_score})
            max_count = max(max_count, cnt)
        self._max_count = max_count

        self._canvas = cv.Canvas(shapes=[], expand=True, on_resize=self._on_resize)
        self._gd = ft.GestureDetector(
            content=ft.Container(expand=True),
            on_tap=self._on_tap,
        )

        self._owns_tooltip = tooltip is None
        self._tooltip      = tooltip if tooltip is not None else Tooltip()

        c_title = theme["text_main"]  if theme else C_TEXT
        c_hint  = theme["text_secondary"] if theme else C_TEXT2

        stack_controls = [self._canvas, self._gd]
        if self._owns_tooltip:
            stack_controls.append(self._tooltip)

        hint_text = (
            "Klik gelembung untuk detail  •  "
            "Ukuran = Jumlah Anime  •  "
            "Warna = Rating (merah=rendah, hijau=tinggi)"
        )
        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title, size=14, weight=ft.FontWeight.BOLD,
                            color=c_title, text_align=ft.TextAlign.CENTER),
                    ft.Text(hint_text, size=11, color=c_hint,
                            text_align=ft.TextAlign.CENTER),
                ],
                spacing=2, tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(top=8, bottom=4),
            alignment=ft.alignment.Alignment.TOP_CENTER,
        )

        self.content = ft.Column(
            controls=[header, ft.Stack(controls=stack_controls, expand=True)],
            spacing=0,
        )

        self._bubble_pos_cache: list = []
        self._bubble_lookup: dict    = {}

    def _cell_center(self, si: int, gi: int):
        n_s    = len(self._studios)
        n_g    = len(self._genres)
        area_w = self._w - self.PAD_L - self.PAD_R
        area_h = self._h - self.PAD_T - self.PAD_B
        sw     = area_w / max(n_g, 1)
        sh     = area_h / max(n_s, 1)
        cx     = self.PAD_L + gi * sw + sw / 2
        cy     = self.PAD_T + si * sh + sh / 2
        return cx, cy, min(sw, sh)

    def _bubble_radius(self, count: int, slot: float) -> float:
        max_r = slot * 0.44
        min_r = max(3.0, slot * 0.06)
        t     = (count / self._max_count) ** 0.5
        return min_r + t * (max_r - min_r)

    def _redraw(self):
        if self._w == 0 or not self._studios or not self._genres:
            return
        shapes = []
        hov_si, hov_gi = self._clicked
        n_s    = len(self._studios)
        n_g    = len(self._genres)
        area_w = self._w - self.PAD_L - self.PAD_R
        area_h = self._h - self.PAD_T - self.PAD_B
        sw     = area_w / max(n_g, 1)
        sh     = area_h / max(n_s, 1)

        c_text    = self._theme["text_main"]       if self._theme else C_TEXT
        c_text2   = self._theme["text_secondary"]  if self._theme else C_TEXT2
        c_text3   = self._theme["text_secondary"]  if self._theme else C_TEXT2
        c_primary = self._theme["primary"]         if self._theme else C_SAKURA_DK

        grid_p = ft.Paint(style=ft.PaintingStyle.STROKE,
                          stroke_width=0.5, color=self._theme["border_color"] if self._theme else "#18000000")
        for gi in range(n_g + 1):
            gx = self.PAD_L + gi * sw
            shapes.append(cv.Path(
                [cv.Path.MoveTo(gx, self.PAD_T),
                 cv.Path.LineTo(gx, self.PAD_T + area_h)],
                grid_p,
            ))
        for si in range(n_s + 1):
            gy = self.PAD_T + si * sh
            shapes.append(cv.Path(
                [cv.Path.MoveTo(self.PAD_L, gy),
                 cv.Path.LineTo(self.PAD_L + area_w, gy)],
                grid_p,
            ))

        for gi, genre in enumerate(self._genres):
            cx     = self.PAD_L + gi * sw + sw / 2
            is_hov = (gi == hov_gi)
            shapes.append(cv.Text(
                x=cx, y=self.PAD_T + area_h + 6,
                value=genre, rotate=0.785,
                style=ft.TextStyle(
                    size=11,
                    color=c_primary if is_hov else c_text2,
                    weight=ft.FontWeight.BOLD if is_hov else ft.FontWeight.NORMAL,
                ),
            ))

        for si, studio in enumerate(self._studios):
            # Tengah vertikal baris studio
            cy_row = self.PAD_T + si * sh + sh / 2
            is_hov = (si == hov_si)
            color  = c_primary if is_hov else c_text2
            # cv.Text dengan text_align RIGHT: x = PAD_L - margin, width cukup besar
            # Flet menghitung lebar aktual teks — tidak ada estimasi manual
            shapes.append(cv.Text(
                x=0,
                y=cy_row - 7,   # -7 ≈ setengah tinggi font 11
                value=studio,
                style=ft.TextStyle(
                    size=11, color=color,
                    weight=ft.FontWeight.BOLD if is_hov else ft.FontWeight.NORMAL,
                ),
                text_align=ft.TextAlign.RIGHT,
                max_lines=1,

            ))

        for b in self._bubbles:
            si, gi = b["si"], b["gi"]
            cx, cy, slot = self._cell_center(si, gi)
            r     = self._bubble_radius(b["count"], slot)
            color = self._rating_color(b["avg_score"])
            is_hov = (si == hov_si and gi == hov_gi)
            alpha  = 1.0 if (is_hov or self._clicked == (-1, -1)) else 0.35

            if is_hov:
                shapes.append(cv.Circle(x=cx, y=cy, radius=r + 7,
                    paint=ft.Paint(style=ft.PaintingStyle.FILL,
                                   color=_rgba(color, 0.25))))

            shapes.append(cv.Circle(x=cx, y=cy, radius=r,
                paint=ft.Paint(style=ft.PaintingStyle.FILL,
                               color=_rgba(color, alpha))))
            shapes.append(cv.Circle(x=cx, y=cy, radius=r,
                paint=ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=1.2,
                               color=_rgba(C_WHITE, min(alpha + 0.1, 1.0)))))

        # Color legend
        legend_x = self.PAD_L
        legend_y = self._h - 16
        bar_w    = min(area_w * 0.45, 160)
        bar_h    = 7
        steps    = 24
        for k in range(steps):
            t    = k / (steps - 1)
            c    = self._rating_color(t * 10)
            sx   = legend_x + k * bar_w / steps
            sw_k = bar_w / steps + 0.5
            shapes.append(cv.Rect(
                x=sx, y=legend_y - bar_h, width=sw_k, height=bar_h,
                paint=ft.Paint(style=ft.PaintingStyle.FILL, color=c),
            ))
        shapes.append(_cv_text_right(legend_x - 4, legend_y - bar_h / 2, "0", 11, c_text3))
        shapes.append(_cv_text_left(legend_x + bar_w + 4, legend_y - bar_h / 2, "10", 11, c_text3))
        shapes.append(_cv_text_top_center(
            legend_x + bar_w / 2, legend_y + 1, "Rating", 11, c_text3))

        self._canvas.shapes = shapes
        self._canvas.update()

    def _on_resize(self, e):
        self._w, self._h = e.width, e.height
        self._bubble_pos_cache = []
        self._bubble_lookup    = {}
        for b in self._bubbles:
            cx, cy, slot = self._cell_center(b["si"], b["gi"])
            r = self._bubble_radius(b["count"], slot)
            self._bubble_pos_cache.append((cx, cy, r, b))
            self._bubble_lookup[(b["si"], b["gi"])] = b
        self._redraw()

    def _on_tap(self, e):
        mx, my = e.local_position.x, e.local_position.y
        if self._w == 0 or not self._bubble_pos_cache:
            return

        hit       = (-1, -1)
        best_dist = float("inf")
        for cx, cy, r, b in self._bubble_pos_cache:
            d = math.hypot(mx - cx, my - cy)
            if d <= r + 4 and d < best_dist:
                best_dist = d
                hit = (b["si"], b["gi"])

        # Klik area kosong → tutup tooltip
        if hit == (-1, -1):
            self._clicked = (-1, -1)
            self._redraw()
            self._tooltip.hide()
            return

        # Toggle: klik gelembung yang sudah aktif → tutup tooltip
        if hit == self._clicked:
            self._clicked = (-1, -1)
            self._redraw()
            self._tooltip.hide()
            return

        self._clicked = hit
        self._redraw()

        si, gi    = hit
        b         = self._bubble_lookup[(si, gi)]
        score_str = f"{b['avg_score']:.2f}" if b["avg_score"] else "N/A"
        self._tooltip.show_at(
            e.global_position.x, e.global_position.y,
            f"{self._genres[gi]}  \u00d7  {self._studios[si]}",
            [
                ("Jumlah Anime", str(b["count"])),
                ("Avg Rating",   score_str),
                ("Genre",        self._genres[gi]),
                ("Studio",       self._studios[si]),
            ],
        )

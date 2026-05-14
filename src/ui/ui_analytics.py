import math
import flet as ft
import flet.canvas as cv
from collections import Counter
from itertools import combinations

# ── Palette ───────────────────────────────────────────────────────────────────
C_SAKURA    = "#C07090"
C_SAKURA_LT = "#F9F0F5"
C_SAKURA_DK = "#A05070"
C_TEXT      = "#3D2535"
C_TEXT2     = "#8B6A7A"
C_TEXT3     = "#B0909A"
C_BORDER    = "#EDE0E8"
C_WHITE     = "#FFFFFF"

CHART_COLORS = [
    "#C07090", "#D4A8C0", "#A0506A", "#E8D0DE", "#B08090",
    "#906070", "#E0B0C8", "#F0E4EB", "#C890A8", "#F4D8E8",
]
C_HOVER = "#FF5080"


def _rgba(hex_color: str, alpha: float) -> str:
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    a = int(alpha * 255)
    return f"#{a:02X}{r:02X}{g:02X}{b:02X}"


def _arc_points(cx, cy, r, angle_start, angle_sweep, steps=32):
    """
    Kembalikan list titik (x,y) di sepanjang busur.
    Digunakan untuk menggambar donut slice sebagai Polygon/LineTo chain
    karena cv.Path.Arc tidak dilanjut dari titik terakhir Path.
    """
    pts = []
    for k in range(steps + 1):
        a = angle_start + angle_sweep * k / steps
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ─────────────────────────────────────────────────────────────────────────────
# Tooltip popup
# ─────────────────────────────────────────────────────────────────────────────
class Tooltip(ft.Container):
    def __init__(self):
        super().__init__(
            visible=False,
            bgcolor=C_WHITE,
            border=ft.border.all(1, "#E0C8D4"),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            shadow=ft.BoxShadow(blur_radius=14, color="#25C07090",
                                offset=ft.Offset(0, 3)),
            left=0, top=0,
            content=ft.Column(spacing=3, tight=True),
        )

    def show_at(self, x: float, y: float, title: str, rows: list):
        self.content.controls = [
            ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=C_SAKURA_DK),
            *[ft.Row([
                ft.Text(lbl, size=11, color=C_TEXT3, expand=True),
                ft.Text(val, size=11, color=C_TEXT, weight=ft.FontWeight.W_600),
            ], spacing=8) for lbl, val in rows],
        ]
        self.left = min(x + 12, 280)
        self.top  = max(0, y - 8)
        self.visible = True
        self.update()

    def hide(self):
        if self.visible:
            self.visible = False
            self.update()


# ─────────────────────────────────────────────────────────────────────────────
# cv.Text helper — x,y selalu top-left corner di Flet canvas
# Untuk right-align  : x = target_right - estimated_width
# Untuk center-align : x = center - estimated_width/2
# Estimasi lebar teks = jumlah karakter * font_size * 0.6
# ─────────────────────────────────────────────────────────────────────────────
def _text_w(text: str, size: float) -> float:
    return len(text) * size * 0.60

def _text_h(size: float) -> float:
    return size * 1.25

def _cv_text_center(x, y, text, size, color, bold=False):
    """cv.Text dengan anchor tengah (x,y adalah center)."""
    tw = _text_w(text, size)
    th = _text_h(size)
    return cv.Text(
        x=x - tw / 2,
        y=y - th / 2,
        value=text,
        style=ft.TextStyle(
            size=size, color=color,
            weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL,
        ),
    )

def _cv_text_right(x, y, text, size, color):
    """cv.Text dengan anchor kanan-tengah (x = right edge, y = vertical center)."""
    tw = _text_w(text, size)
    th = _text_h(size)
    return cv.Text(
        x=x - tw,
        y=y - th / 2,
        value=text,
        style=ft.TextStyle(size=size, color=color),
    )

def _cv_text_left(x, y, text, size, color, bold=False):
    """cv.Text dengan anchor kiri-tengah (x = left edge, y = vertical center)."""
    th = _text_h(size)
    return cv.Text(
        x=x,
        y=y - th / 2,
        value=text,
        style=ft.TextStyle(
            size=size, color=color,
            weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL,
        ),
    )

def _cv_text_top_center(x, y, text, size, color, bold=False):
    """cv.Text dengan anchor atas-tengah (x = center, y = top)."""
    tw = _text_w(text, size)
    return cv.Text(
        x=x - tw / 2,
        y=y,
        value=text,
        style=ft.TextStyle(
            size=size, color=color,
            weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL,
        ),
    )


# ─────────────────────────────────────────────────────────────────────────────
# VerticalBarChart
# ─────────────────────────────────────────────────────────────────────────────
class VerticalBarChart(ft.Stack):
    PAD_L = 46
    PAD_R = 12
    PAD_T = 28
    PAD_B = 72   # extra ruang untuk label X diagonal

    def __init__(self, bar_data: list, title: str, y_label: str = ""):
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
                self.PAD_L - 4, gy, label, 9, C_TEXT3))

        for i, d in enumerate(self._data):
            bx, by, bw, bh = self._bar_rect(i, w, h)
            is_hov = (i == hovered)
            color  = C_HOVER if is_hov else CHART_COLORS[i % len(CHART_COLORS)]
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
                    color=C_SAKURA_DK if is_hov else C_TEXT2,
                ),
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
            if bx <= mx <= bx + bw and by - 4 <= my <= by + bh + 4:
                hit = i
                break
        if hit != self._hovered:
            self._hovered = hit
            self._redraw(hit)
        if hit >= 0:
            d = self._data[hit]
            rows = [("Jumlah Anime", str(d["value"]))]
            self._tooltip.show_at(mx, my, d["label"], rows)
        else:
            self._tooltip.hide()


# ─────────────────────────────────────────────────────────────────────────────
# HorizontalBarChart
# ─────────────────────────────────────────────────────────────────────────────
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


# ─────────────────────────────────────────────────────────────────────────────
# DonutChart
# ─────────────────────────────────────────────────────────────────────────────
class DonutChart(ft.Stack):
    def __init__(self, data: list, title: str):
        super().__init__(expand=True)
        self._data    = data
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

        for i, (d, (sa, sw)) in enumerate(zip(self._data, angles)):
            is_hov = (i == hovered)
            color  = CHART_COLORS[i % len(CHART_COLORS)]
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
                               stroke_width=1.5, color=C_WHITE),
            ))

        # Legend — kanan chart
        leg_x  = self._w * 0.52 + 8
        row_h  = 20
        n      = len(self._data)

        total_leg_h = n * row_h
        leg_start_y = (self._h - total_leg_h) / 2 + 10

        for i, d in enumerate(self._data):
            is_hov   = (i == hovered)
            color    = CHART_COLORS[i % len(CHART_COLORS)]
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
                C_SAKURA_DK if is_hov else C_TEXT2,
                bold=is_hov,
            ))

        # Title center atas
        shapes.append(_cv_text_top_center(
            self._w / 2, 6, self._title, 12, C_TEXT, bold=True))

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

        if hit != self._hovered:
            self._hovered = hit
            self._redraw(hit)
        if hit >= 0:
            d = self._data[hit]
            self._tooltip.show_at(
                mx, my, d["label"],
                [("Jumlah", str(d["value"])),
                 ("Persen", f"{d['pct']:.1f}%")],
            )
        else:
            self._tooltip.hide()


# ─────────────────────────────────────────────────────────────────────────────
# GenreNetworkGraph
# ─────────────────────────────────────────────────────────────────────────────
class GenreNetworkGraph(ft.Stack):
    """Network graph: node = genre, edge = co-occurrence frequency."""

    MAX_GENRES  = 15   # node terbanyak yang ditampilkan
    MAX_EDGES   = 40   # edge terbanyak yang ditampilkan
    MIN_EDGE_W  = 1.0  # ketebalan garis minimum
    MAX_EDGE_W  = 8.0  # ketebalan garis maksimum
    NODE_MIN_R  = 18
    NODE_MAX_R  = 36

    # CHART_COLORS yang lebih gelap & kontras agar teks putih terbaca
    NODE_COLORS = [
        "#B05880", "#8B4060", "#A06880", "#7B3858",
        "#C07090", "#904870", "#D06090", "#7A4868",
        "#A03860", "#C85880", "#985070", "#B86888",
        "#884060", "#D07898", "#A04870",
    ]

    @staticmethod
    def _luminance(hex_color: str) -> float:
        """Relative luminance (0=black, 1=white) dari hex color."""
        r = int(hex_color[1:3], 16) / 255
        g = int(hex_color[3:5], 16) / 255
        b = int(hex_color[5:7], 16) / 255
        def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

    @staticmethod
    def _fit_label(label: str, radius: float, fsize: float) -> list:
        """
        Pecah label menjadi 1 atau 2 baris yang muat di dalam lingkaran.
        Lebar maksimum setiap baris ≈ diameter × 0.85.
        Karakter rata-rata = fsize * 0.58 piksel.
        """
        max_w    = radius * 2 * 0.82          # lebar efektif dalam lingkaran
        char_w   = fsize * 0.58
        max_char = max(1, int(max_w / char_w))

        # Coba 1 baris
        if len(label) <= max_char:
            return [label]

        # Coba 2 baris — cari spasi terdekat dengan tengah
        mid = len(label) // 2
        best_sp = -1
        for d in range(mid + 1):
            for pos in [mid - d, mid + d]:
                if 0 <= pos < len(label) and label[pos] == ' ':
                    best_sp = pos
                    break
            if best_sp != -1:
                break

        if best_sp != -1:
            line1 = label[:best_sp]
            line2 = label[best_sp + 1:]
            # Pastikan tiap baris muat
            if len(line1) <= max_char and len(line2) <= max_char:
                return [line1, line2]

        # Tidak ada spasi atau baris masih terlalu panjang — truncate
        truncated = label[:max_char]
        if len(label) > max_char:
            truncated = truncated[:-1] + "…"
        return [truncated]

    def __init__(self, animes: list, title: str):
        super().__init__(expand=True)
        self._title   = title
        self._hovered_node = -1
        self._hovered_edge = -1
        self._tooltip      = Tooltip()
        self._w = self._h  = 0

        # ── Pre-process data ──────────────────────────────────────────────
        genre_counter: Counter = Counter()
        for a in animes:
            for g in a.get("genre", []):
                genre_counter[g] += 1

        top_genres = [g for g, _ in genre_counter.most_common(self.MAX_GENRES)]
        genre_set  = set(top_genres)

        pair_counter: Counter = Counter()
        for a in animes:
            gs = [g for g in a.get("genre", []) if g in genre_set]
            for g1, g2 in combinations(sorted(gs), 2):
                pair_counter[(g1, g2)] += 1

        # nodes: [{label, count, r, x, y}]
        counts  = [genre_counter[g] for g in top_genres]
        max_cnt = max(counts) if counts else 1
        self._nodes = []
        for g, cnt in zip(top_genres, counts):
            r = self.NODE_MIN_R + (self.NODE_MAX_R - self.NODE_MIN_R) * (cnt / max_cnt)
            self._nodes.append({"label": g, "count": cnt, "r": r, "x": 0.0, "y": 0.0})

        # edges: [{i, j, weight, stroke}] — top MAX_EDGES by weight
        all_edges = [
            {"i": top_genres.index(g1),
             "j": top_genres.index(g2),
             "weight": w}
            for (g1, g2), w in pair_counter.most_common(self.MAX_EDGES)
            if g1 in top_genres and g2 in top_genres
        ]
        if all_edges:
            max_w = max(e["weight"] for e in all_edges)
            min_w = min(e["weight"] for e in all_edges)
            rng   = max(max_w - min_w, 1)
            for e in all_edges:
                t = (e["weight"] - min_w) / rng
                e["stroke"] = self.MIN_EDGE_W + t * (self.MAX_EDGE_W - self.MIN_EDGE_W)
        self._edges = all_edges

        # ── Flet widgets ─────────────────────────────────────────────────
        self._canvas = cv.Canvas(shapes=[], expand=True,
                                 on_resize=self._on_resize)
        self._gd = ft.GestureDetector(
            content=ft.Container(expand=True),
            on_hover=self._on_hover,
        )
        self.controls = [self._canvas, self._gd, self._tooltip]

    # ── Layout helpers ────────────────────────────────────────────────────
    def _compute_layout(self):
        """Circular layout with slight force nudge to reduce overlap."""
        n   = len(self._nodes)
        if n == 0:
            return
        PAD = 52
        cx  = self._w / 2
        cy  = self._h / 2 + 10
        r   = min(self._w, self._h) / 2 - PAD

        for i, node in enumerate(self._nodes):
            a = 2 * math.pi * i / n - math.pi / 2
            node["x"] = cx + r * math.cos(a)
            node["y"] = cy + r * math.sin(a)

        # 3 passes of simple repulsion between adjacent nodes
        for _ in range(3):
            for ii in range(n):
                for jj in range(ii + 1, n):
                    dx = self._nodes[jj]["x"] - self._nodes[ii]["x"]
                    dy = self._nodes[jj]["y"] - self._nodes[ii]["y"]
                    d  = math.hypot(dx, dy) or 1
                    min_d = self._nodes[ii]["r"] + self._nodes[jj]["r"] + 6
                    if d < min_d:
                        push = (min_d - d) / 2
                        nx_, ny_ = dx / d, dy / d
                        self._nodes[ii]["x"] -= nx_ * push * 0.5
                        self._nodes[ii]["y"] -= ny_ * push * 0.5
                        self._nodes[jj]["x"] += nx_ * push * 0.5
                        self._nodes[jj]["y"] += ny_ * push * 0.5

    def _on_resize(self, e):
        self._w, self._h = e.width, e.height
        self._compute_layout()
        self._redraw(-1, -1)

    # ── Draw ──────────────────────────────────────────────────────────────
    def _redraw(self, hov_node: int, hov_edge: int):
        if self._w == 0 or not self._nodes:
            return
        shapes = []

        # ── Title ────────────────────────────────────────────────────────
        shapes.append(_cv_text_top_center(
            self._w / 2, 6, self._title, 12, C_TEXT, bold=True))

        # ── Legend hint ──────────────────────────────────────────────────
        hint = "Garis tebal = sering berpasangan  •  Lingkaran besar = genre populer"
        shapes.append(_cv_text_top_center(
            self._w / 2, 22, hint, 8.5, C_TEXT3))

        # ── Edges ────────────────────────────────────────────────────────
        for ei, edge in enumerate(self._edges):
            ni = self._nodes[edge["i"]]
            nj = self._nodes[edge["j"]]
            is_hov_e = (ei == hov_edge)
            is_adj   = (hov_node in (edge["i"], edge["j"]))

            if hov_node >= 0 and not is_adj:
                alpha = 0.08
            elif is_hov_e:
                alpha = 1.0
            elif is_adj:
                alpha = 0.85
            else:
                alpha = 0.30

            color = C_HOVER if (is_hov_e or is_adj) else C_SAKURA
            shapes.append(cv.Path(
                [cv.Path.MoveTo(ni["x"], ni["y"]),
                 cv.Path.LineTo(nj["x"], nj["y"])],
                ft.Paint(
                    style=ft.PaintingStyle.STROKE,
                    stroke_width=edge["stroke"],
                    color=_rgba(color, alpha),
                ),
            ))

        # ── Nodes ────────────────────────────────────────────────────────
        # Tentukan node-node yang berdekatan (tetangga) dengan hov_node
        adj_nodes: set = set()
        if hov_node >= 0:
            for edge in self._edges:
                if edge["i"] == hov_node:
                    adj_nodes.add(edge["j"])
                elif edge["j"] == hov_node:
                    adj_nodes.add(edge["i"])

        for ni, node in enumerate(self._nodes):
            is_hov_n  = (ni == hov_node)
            is_adj_n  = (ni in adj_nodes)
            color     = self.NODE_COLORS[ni % len(self.NODE_COLORS)]

            # Alpha: node hover=1.0, tetangga=1.0, tidak terkait=0.28
            if hov_node == -1 or is_hov_n or is_adj_n:
                alpha = 1.0
            else:
                alpha = 0.28

            r    = node["r"]
            x, y = node["x"], node["y"]

            # Glow ring saat hover
            if is_hov_n:
                shapes.append(cv.Circle(
                    x=x, y=y, radius=r + 7,
                    paint=ft.Paint(
                        style=ft.PaintingStyle.FILL,
                        color=_rgba(C_HOVER, 0.20),
                    ),
                ))
            # Outline tipis untuk node tetangga
            elif is_adj_n and hov_node >= 0:
                shapes.append(cv.Circle(
                    x=x, y=y, radius=r + 3,
                    paint=ft.Paint(
                        style=ft.PaintingStyle.STROKE,
                        stroke_width=1.5,
                        color=_rgba(C_SAKURA, 0.50),
                    ),
                ))

            # Fill
            shapes.append(cv.Circle(
                x=x, y=y, radius=r,
                paint=ft.Paint(
                    style=ft.PaintingStyle.FILL,
                    color=_rgba(color, alpha),
                ),
            ))
            # Border dalam (putih tipis)
            shapes.append(cv.Circle(
                x=x, y=y, radius=r,
                paint=ft.Paint(
                    style=ft.PaintingStyle.STROKE,
                    stroke_width=1.5,
                    color=_rgba(C_WHITE, min(alpha + 0.1, 1.0)),
                ),
            ))

            # ── Label di dalam node ──────────────────────────────────────
            # Pilih ukuran font berdasarkan radius
            fsize    = 7.5 if r < 22 else (9.0 if r < 28 else 10.0)
            lum      = self._luminance(color)
            txt_col  = C_TEXT if lum > 0.25 else C_WHITE

            lines = self._fit_label(node["label"], r, fsize)
            n_lines  = len(lines)
            line_h   = _text_h(fsize)           # tinggi satu baris
            gap      = 1.5                       # jarak antar baris
            total_h  = n_lines * line_h + (n_lines - 1) * gap
            # y awal teks: geser ke atas dari tengah node
            y0 = y - total_h / 2

            for li, ln in enumerate(lines):
                ty = y0 + li * (line_h + gap) + line_h / 2
                tw = _text_w(ln, fsize)
                shapes.append(cv.Text(
                    x=x - tw / 2,
                    y=ty - line_h / 2,
                    value=ln,
                    style=ft.TextStyle(
                        size=fsize,
                        color=txt_col,
                        weight=ft.FontWeight.BOLD if is_hov_n else ft.FontWeight.W_600,
                    ),
                ))

        self._canvas.shapes = shapes
        self._canvas.update()

    # ── Interaction ───────────────────────────────────────────────────────
    def _on_hover(self, e):
        mx, my = e.local_position.x, e.local_position.y
        if self._w == 0:
            return

        # Cek hover node
        hit_node = -1
        for ni, node in enumerate(self._nodes):
            if math.hypot(mx - node["x"], my - node["y"]) <= node["r"] + 4:
                hit_node = ni
                break

        # Cek hover edge (hanya jika tidak hover node)
        hit_edge = -1
        if hit_node == -1:
            for ei, edge in enumerate(self._edges):
                ni = self._nodes[edge["i"]]
                nj = self._nodes[edge["j"]]
                # Jarak titik ke segmen
                dist = self._pt_to_seg(mx, my, ni["x"], ni["y"], nj["x"], nj["y"])
                if dist <= max(edge["stroke"] / 2 + 3, 5):
                    hit_edge = ei
                    break

        if hit_node != self._hovered_node or hit_edge != self._hovered_edge:
            self._hovered_node = hit_node
            self._hovered_edge = hit_edge
            self._redraw(hit_node, hit_edge)

        if hit_node >= 0:
            node = self._nodes[hit_node]
            # Hitung semua edge yang terhubung
            conn = sum(1 for e in self._edges if hit_node in (e["i"], e["j"]))
            self._tooltip.show_at(
                mx, my, node["label"],
                [("Jumlah Anime", str(node["count"])),
                 ("Koneksi Genre", str(conn))],
            )
        elif hit_edge >= 0:
            edge  = self._edges[hit_edge]
            label = f"{self._nodes[edge['i']]['label']} × {self._nodes[edge['j']]['label']}"
            self._tooltip.show_at(
                mx, my, label,
                [("Co-occurrence", str(edge["weight"])),
                 ("Tebal garis",   f"{edge['stroke']:.1f}px")],
            )
        else:
            self._tooltip.hide()

    @staticmethod
    def _pt_to_seg(px, py, ax, ay, bx, by) -> float:
        """Jarak titik (px,py) ke segmen (ax,ay)-(bx,by)."""
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


# ─────────────────────────────────────────────────────────────────────────────
# CategoricalBubbleChart  (Studio × Genre)
# ─────────────────────────────────────────────────────────────────────────────
class CategoricalBubbleChart(ft.Stack):
    """
    Bubble chart kategorik:
      Sumbu X  → Top 15 Genre
      Sumbu Y  → Top 10 Studio
      Ukuran   → Jumlah anime (studio, genre)
      Warna    → Rating rata-rata (merah=rendah, hijau=tinggi)
    """
    MAX_STUDIOS = 10
    MAX_GENRES  = 15
    PAD_L = 120   # ruang label studio (Y-axis)
    PAD_R = 16
    PAD_T = 44    # judul + hint
    PAD_B = 90    # label genre diagonal (X-axis)

    # Gradien warna: merah (rating rendah) → kuning/emas → hijau (rating tinggi)
    # Terinspirasi warna semaphore Jepang: merah bahaya, hijau aman
    RATING_STOPS = [
        (0.0,  "#CC2200"),   # merah tua  (sangat rendah)
        (0.35, "#E05010"),   # oranye-merah
        (0.55, "#C8A000"),   # emas / kuning (sedang)
        (0.75, "#50A830"),   # hijau terang
        (1.0,  "#1A6B20"),   # hijau tua   (sangat tinggi)
    ]

    @staticmethod
    def _rating_color(rating: float) -> str:
        """Interpolasi warna untuk rating 0–10."""
        t = max(0.0, min(1.0, rating / 10.0))
        stops = CategoricalBubbleChart.RATING_STOPS
        # Cari dua stop yang mengapit t
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

    def __init__(self, animes: list, title: str):
        super().__init__(expand=True)
        self._title   = title
        self._tooltip = Tooltip()
        self._hovered = (-1, -1)   # (studio_idx, genre_idx)
        self._w = self._h = 0

        # ── Pre-process ───────────────────────────────────────────────────
        # Top 10 studios by total anime count
        studio_count: Counter = Counter()
        for a in animes:
            s = (a.get("studio") or "Unknown").strip()
            if s:
                studio_count[s] += 1
        self._studios = [s for s, _ in studio_count.most_common(self.MAX_STUDIOS)]

        # Top 15 genres by total anime count
        genre_count: Counter = Counter()
        for a in animes:
            for g in a.get("genre", []):
                genre_count[g] += 1
        self._genres = [g for g, _ in genre_count.most_common(self.MAX_GENRES)]

        studio_set = set(self._studios)
        genre_set  = set(self._genres)

        # Matrix: cell[si][gi] = {"count": int, "scores": [float]}
        cell: dict = {}
        for a in animes:
            s = (a.get("studio") or "Unknown").strip()
            if s not in studio_set:
                continue
            score = a.get("global_score")
            si = self._studios.index(s)
            for g in a.get("genre", []):
                if g not in genre_set:
                    continue
                gi = self._genres.index(g)
                key = (si, gi)
                if key not in cell:
                    cell[key] = {"count": 0, "scores": []}
                cell[key]["count"] += 1
                if isinstance(score, (int, float)):
                    cell[key]["scores"].append(float(score))

        # Flatten ke list bubble
        self._bubbles = []
        max_count = 1
        for (si, gi), v in cell.items():
            cnt = v["count"]
            avg_score = (sum(v["scores"]) / len(v["scores"])) if v["scores"] else 0.0
            self._bubbles.append({
                "si": si, "gi": gi,
                "count": cnt,
                "avg_score": avg_score,
            })
            max_count = max(max_count, cnt)
        self._max_count = max_count

        # ── Flet widgets ──────────────────────────────────────────────────
        self._canvas = cv.Canvas(shapes=[], expand=True,
                                 on_resize=self._on_resize)
        self._gd = ft.GestureDetector(
            content=ft.Container(expand=True),
            on_hover=self._on_hover,
        )
        self.controls = [self._canvas, self._gd, self._tooltip]

    # ── Geometry helpers ──────────────────────────────────────────────────
    def _cell_center(self, si: int, gi: int):
        """
        Pusat piksel dari sel.
        si = studio index (Y-axis, baris)
        gi = genre  index (X-axis, kolom)
        """
        n_s = len(self._studios)
        n_g = len(self._genres)
        area_w = self._w - self.PAD_L - self.PAD_R
        area_h = self._h - self.PAD_T - self.PAD_B
        # Genre → kolom (X)
        sw = area_w / max(n_g, 1)
        # Studio → baris (Y)
        sh = area_h / max(n_s, 1)
        cx = self.PAD_L + gi * sw + sw / 2   # gi = kolom
        cy = self.PAD_T + si * sh + sh / 2   # si = baris
        return cx, cy, min(sw, sh)

    def _bubble_radius(self, count: int, slot: float) -> float:
        max_r = slot * 0.44
        min_r = max(3.0, slot * 0.06)
        t = (count / self._max_count) ** 0.5   # sqrt untuk area proporsional
        return min_r + t * (max_r - min_r)

    # ── Draw ──────────────────────────────────────────────────────────────
    def _redraw(self):
        if self._w == 0 or not self._studios or not self._genres:
            return
        shapes = []
        hov_si, hov_gi = self._hovered
        n_s = len(self._studios)
        n_g = len(self._genres)
        area_w = self._w - self.PAD_L - self.PAD_R
        area_h = self._h - self.PAD_T - self.PAD_B
        # Genre → kolom (X), Studio → baris (Y)
        sw = area_w / max(n_g, 1)   # lebar slot per genre
        sh = area_h / max(n_s, 1)   # tinggi slot per studio

        # ── Title & hint ─────────────────────────────────────────────────
        shapes.append(_cv_text_top_center(
            self._w / 2, 6, self._title, 12, C_TEXT, bold=True))
        shapes.append(_cv_text_top_center(
            self._w / 2, 22,
            "Ukuran = Jumlah Anime  •  Warna = Rating (merah=rendah, hijau=tinggi)",
            8.5, C_TEXT3))

        # ── Grid lines ───────────────────────────────────────────────────
        grid_p = ft.Paint(style=ft.PaintingStyle.STROKE,
                          stroke_width=0.5, color="#18000000")
        # Garis vertikal — per genre (kolom)
        for gi in range(n_g + 1):
            gx = self.PAD_L + gi * sw
            shapes.append(cv.Path(
                [cv.Path.MoveTo(gx, self.PAD_T),
                 cv.Path.LineTo(gx, self.PAD_T + area_h)],
                grid_p,
            ))
        # Garis horizontal — per studio (baris)
        for si in range(n_s + 1):
            gy = self.PAD_T + si * sh
            shapes.append(cv.Path(
                [cv.Path.MoveTo(self.PAD_L, gy),
                 cv.Path.LineTo(self.PAD_L + area_w, gy)],
                grid_p,
            ))

        # ── X-axis labels (Genre) — diagonal ────────────────────────────
        for gi, genre in enumerate(self._genres):
            cx = self.PAD_L + gi * sw + sw / 2
            is_hov = (gi == hov_gi)
            shapes.append(cv.Text(
                x=cx,
                y=self.PAD_T + area_h + 6,
                value=genre,
                rotate=0.785,
                style=ft.TextStyle(
                    size=11,
                    color=C_SAKURA_DK if is_hov else C_TEXT2,
                    weight=ft.FontWeight.BOLD if is_hov else ft.FontWeight.NORMAL,
                ),
            ))

        # ── Y-axis labels (Studio) — rata kanan ──────────────────────────
        for si, studio in enumerate(self._studios):
            cy = self.PAD_T + si * sh + sh / 2
            is_hov = (si == hov_si)
            shapes.append(_cv_text_right(
                self.PAD_L - 6, cy, studio, 11,
                C_SAKURA_DK if is_hov else C_TEXT2,
            ))

        # ── Bubbles ──────────────────────────────────────────────────────
        # Buat lookup untuk akses cepat
        bubble_map = {(b["si"], b["gi"]): b for b in self._bubbles}

        for b in self._bubbles:
            si, gi = b["si"], b["gi"]
            cx, cy, slot = self._cell_center(si, gi)
            r = self._bubble_radius(b["count"], slot)
            color = self._rating_color(b["avg_score"])
            is_hov = (si == hov_si and gi == hov_gi)

            alpha = 1.0 if (is_hov or self._hovered == (-1, -1)) else 0.35

            # Glow saat hover
            if is_hov:
                shapes.append(cv.Circle(
                    x=cx, y=cy, radius=r + 7,
                    paint=ft.Paint(
                        style=ft.PaintingStyle.FILL,
                        color=_rgba(color, 0.25),
                    ),
                ))

            # Fill
            shapes.append(cv.Circle(
                x=cx, y=cy, radius=r,
                paint=ft.Paint(
                    style=ft.PaintingStyle.FILL,
                    color=_rgba(color, alpha),
                ),
            ))
            # Border putih tipis
            shapes.append(cv.Circle(
                x=cx, y=cy, radius=r,
                paint=ft.Paint(
                    style=ft.PaintingStyle.STROKE,
                    stroke_width=1.2,
                    color=_rgba(C_WHITE, min(alpha + 0.1, 1.0)),
                ),
            ))
            # Tidak ada angka di dalam bubble

        # ── Color legend (rating gradient bar) ───────────────────────────
        legend_x = self.PAD_L
        legend_y = self._h - 16
        bar_w    = min(area_w * 0.45, 160)
        bar_h    = 7
        steps    = 24
        for k in range(steps):
            t     = k / (steps - 1)
            c     = self._rating_color(t * 10)
            sx    = legend_x + k * bar_w / steps
            sw_k  = bar_w / steps + 0.5
            shapes.append(cv.Rect(
                x=sx, y=legend_y - bar_h,
                width=sw_k, height=bar_h,
                paint=ft.Paint(style=ft.PaintingStyle.FILL, color=c),
            ))
        shapes.append(_cv_text_right(
            legend_x - 4, legend_y - bar_h / 2, "0", 8, C_TEXT3))
        shapes.append(_cv_text_left(
            legend_x + bar_w + 4, legend_y - bar_h / 2, "10", 8, C_TEXT3))
        shapes.append(_cv_text_top_center(
            legend_x + bar_w / 2, legend_y + 1, "Rating", 7.5, C_TEXT3))

        self._canvas.shapes = shapes
        self._canvas.update()

    def _on_resize(self, e):
        self._w, self._h = e.width, e.height
        self._redraw()

    # ── Interaction ───────────────────────────────────────────────────────
    def _on_hover(self, e):
        mx, my = e.local_position.x, e.local_position.y
        if self._w == 0:
            return

        hit = (-1, -1)
        best_dist = float("inf")
        for b in self._bubbles:
            cx, cy, slot = self._cell_center(b["si"], b["gi"])
            r = self._bubble_radius(b["count"], slot)
            d = math.hypot(mx - cx, my - cy)
            if d <= r + 4 and d < best_dist:
                best_dist = d
                hit = (b["si"], b["gi"])

        if hit != self._hovered:
            self._hovered = hit
            self._redraw()

        if hit != (-1, -1):
            si, gi = hit
            b = next(x for x in self._bubbles if x["si"]==si and x["gi"]==gi)
            score_str = f"{b['avg_score']:.2f}" if b["avg_score"] else "N/A"
            # Clamp tooltip agar selalu dekat kursor (maks 8px offset)
            tip_x = max(0, min(mx + 8, self._w - 200))
            tip_y = max(0, min(my - 4, self._h - 100))
            self._tooltip.show_at(
                tip_x, tip_y,
                f"{self._genres[gi]}  ×  {self._studios[si]}",
                [
                    ("Jumlah Anime", str(b["count"])),
                    ("Avg Rating",   score_str),
                    ("Genre",        self._genres[gi]),
                    ("Studio",       self._studios[si]),
                ],
            )
        else:
            self._tooltip.hide()


# ─────────────────────────────────────────────────────────────────────────────
# Chart card wrapper
# ─────────────────────────────────────────────────────────────────────────────
def _chart_card(chart) -> ft.Container:
    return ft.Container(
        content=chart,
        expand=True,
        height=350,
        bgcolor=C_WHITE,
        border_radius=12,
        border=ft.border.all(1, C_BORDER),
        padding=ft.padding.all(0),
        shadow=ft.BoxShadow(blur_radius=8, color="#0A000000",
                            offset=ft.Offset(0, 2)),
    )


def _network_card(chart) -> ft.Container:
    """Card khusus untuk network graph — lebih tinggi agar node tidak berhimpit."""
    return ft.Container(
        content=chart,
        expand=True,
        height=480,
        bgcolor=C_WHITE,
        border_radius=12,
        border=ft.border.all(1, C_BORDER),
        padding=ft.padding.all(0),
        shadow=ft.BoxShadow(blur_radius=8, color="#0A000000",
                            offset=ft.Offset(0, 2)),
    )


def _bubble_card(chart) -> ft.Container:
    """Card untuk Categorical Bubble Chart — lebih tinggi agar sel tidak sempit."""
    return ft.Container(
        content=chart,
        expand=True,
        height=560,
        bgcolor=C_WHITE,
        border_radius=12,
        border=ft.border.all(1, C_BORDER),
        padding=ft.padding.all(0),
        shadow=ft.BoxShadow(blur_radius=8, color="#0A000000",
                            offset=ft.Offset(0, 2)),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────────────────────────────────────
class UIAnalytics(ft.Row):
    def __init__(self, page, data_manager, auth_manager, screen_manager):
        super().__init__()
        self.my_page        = page
        self.data_manager   = data_manager
        self.auth_manager   = auth_manager
        self.screen_manager = screen_manager
        self.expand  = True
        self.spacing = 0
        self._sidebar_open = False

        from src.ui.ui_home import _sidebar
        self._sidebar_widget = _sidebar(
            screen_manager, auth_manager,
            self._toggle_sidebar, halaman_aktif="analytics",
        )

        topbar = ft.Container(
            padding=ft.padding.symmetric(horizontal=16),
            height=55,
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=["#E6FFFFFF", "#CCFCF8FA"],
            ),
            shadow=ft.BoxShadow(blur_radius=15, color="#15000000",
                                offset=ft.Offset(0, 4)),
            content=ft.Row(
                controls=[
                    ft.IconButton(ft.Icons.MENU, icon_color=C_SAKURA,
                                  on_click=self._toggle_sidebar,
                                  tooltip="Menu"),
                    ft.Text("Analytics Dashboard", size=18,
                            color=C_SAKURA, weight=ft.FontWeight.BOLD),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self._main_content = ft.Column(
            scroll=ft.ScrollMode.AUTO, expand=True, spacing=16,
        )
        self._load_analytics()

        area_utama = ft.Container(
            content=ft.Column(
                controls=[
                    topbar,
                    ft.Container(
                        content=self._main_content,
                        padding=ft.padding.symmetric(
                            horizontal=20, vertical=16),
                        expand=True,
                    ),
                ],
                spacing=0, expand=True,
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=["#FFFFFF", "#F0F2F5"], stops=[0.4, 1.0],
            ),
            expand=True,
        )
        self.controls = [self._sidebar_widget, area_utama]

    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._sidebar_widget.update()

    def _load_analytics(self):
        animes = self.data_manager.get_semua_anime()
        users  = self.data_manager._read_json(self.data_manager.users_file) or []

        total_anime   = len(animes)
        total_users   = len(users)
        total_ratings = sum(u.get("rating_count", 0) for u in users)

        stat_card = ft.Container(
            bgcolor=C_SAKURA_LT,
            border=ft.border.all(1, "#E8D0DE"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            content=ft.Row(
                controls=[
                    self._build_stat("Total Anime",   total_anime,   ft.Icons.MOVIE),
                    ft.VerticalDivider(width=1, color=C_BORDER),
                    self._build_stat("Total Users",   total_users,   ft.Icons.PEOPLE),
                    ft.VerticalDivider(width=1, color=C_BORDER),
                    self._build_stat("Total Ratings", total_ratings, ft.Icons.STAR),
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            ),
        )

        # Chart 1 — Genre
        genres_counter = Counter()
        for a in animes:
            for g in a.get("genre", []):
                genres_counter[g] += 1
        genre_data = [{"label": g, "value": cnt, "extra": None}
                      for g, cnt in genres_counter.most_common(10)]
        chart1 = VerticalBarChart(genre_data, "Most Common Genres", y_label="Jumlah Anime")

        # Chart 2 — Episodes
        bin_labels = ["1–12", "13–24", "25–36", "37–48", "49–100", "100+"]
        bin_counts = [0] * 6
        for a in animes:
            try:
                ep = int(a.get("episodes") or 0)
            except (TypeError, ValueError):
                continue
            if   ep <= 12:  bin_counts[0] += 1
            elif ep <= 24:  bin_counts[1] += 1
            elif ep <= 36:  bin_counts[2] += 1
            elif ep <= 48:  bin_counts[3] += 1
            elif ep <= 100: bin_counts[4] += 1
            else:           bin_counts[5] += 1
        ep_data = [{"label": lbl, "value": cnt, "extra": f"{cnt} anime"}
                   for lbl, cnt in zip(bin_labels, bin_counts)]
        chart2 = VerticalBarChart(ep_data, "Episode Count Distribution",
                                  y_label="Jumlah Anime")

        # Chart 3 — Type donut
        types_counter = Counter(a.get("type", "Unknown") for a in animes)
        t_sorted = types_counter.most_common()
        t_total  = sum(v for _, v in t_sorted)
        donut_data = [{"label": lbl, "value": cnt, "pct": cnt / t_total * 100}
                      for lbl, cnt in t_sorted]
        chart3 = DonutChart(donut_data, "Show Types Proportion")

        # Chart 4 — Studios
        studio_scores: dict = {}
        for a in animes:
            studio = a.get("studio") or "Unknown"
            score  = a.get("global_score")
            if isinstance(score, (int, float)):
                studio_scores.setdefault(studio, []).append(score)
        top10 = sorted(studio_scores.items(),
                       key=lambda kv: len(kv[1]), reverse=True)[:10]
        top10 = sorted(top10, key=lambda kv: sum(kv[1]) / len(kv[1]))
        studio_data = [
            {"label": kv[0],
             "value": round(sum(kv[1]) / len(kv[1]), 2),
             "extra": f"{len(kv[1])}"}
            for kv in top10
        ]
        chart4 = HorizontalBarChart(studio_data, "Average Scores of the Top 10 Most Active Studios")

        row1 = ft.Row(
            controls=[_chart_card(chart1), _chart_card(chart2)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )
        row2 = ft.Row(
            controls=[_chart_card(chart3), _chart_card(chart4)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )

        # Chart 5 — Genre Co-occurrence Network Graph
        chart5 = GenreNetworkGraph(animes, "Genre Co-occurrence Network")

        row3 = ft.Row(
            controls=[_network_card(chart5)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )

        # Chart 6 — Studio × Genre Categorical Bubble Chart
        chart6 = CategoricalBubbleChart(
            animes, "Studio × Genre Bubble Chart"
        )
        row4 = ft.Row(
            controls=[_bubble_card(chart6)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )

        self._main_content.controls.extend([
            stat_card,
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.TOUCH_APP, color=C_TEXT3, size=14),
                    ft.Text(
                        "Hover di atas bar / slice / node / gelembung untuk detail",
                        size=11, color=C_TEXT3, italic=True,
                    ),
                ],
                spacing=6,
            ),
            row1,
            row2,
            row3,
            row4,
            ft.Container(height=24),
        ])

    def _build_stat(self, label, value, icon):
        return ft.Column(
            controls=[
                ft.Icon(icon, color=C_SAKURA, size=28),
                ft.Text(str(value), size=22, color=C_TEXT,
                        weight=ft.FontWeight.BOLD),
                ft.Text(label, size=11, color=C_TEXT2),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        )
import math
import flet as ft
import flet.canvas as cv
from collections import Counter
from itertools import combinations
from .palette import (
    C_TEXT, C_TEXT3, C_SAKURA, C_HOVER, C_WHITE,
    _rgba, _text_w, _text_h, _cv_text_top_center
)
from .tooltip import Tooltip

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

    def __init__(self, animes: list, title: str, theme: dict = None):
        super().__init__(expand=True)
        self._title   = title
        self._theme   = theme
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

        c_text    = self._theme["text_main"]  if self._theme else C_TEXT
        c_text3   = self._theme["text_muted"] if self._theme else C_TEXT3
        c_primary = self._theme["primary"]    if self._theme else C_SAKURA
        c_hover   = self._theme["primary"]    if self._theme else C_HOVER
        # Node colors: gunakan chart_colors tema jika ada, fallback ke NODE_COLORS bawaan
        node_colors = (
            self._theme.get("chart_colors", self.NODE_COLORS)
            if self._theme else self.NODE_COLORS
        )

        # ── Title ────────────────────────────────────────────────────────
        shapes.append(_cv_text_top_center(
            self._w / 2, 6, self._title, 12, c_text, bold=True))

        # ── Legend hint ──────────────────────────────────────────────────
        hint = "Garis tebal = sering berpasangan  •  Lingkaran besar = genre populer"
        shapes.append(_cv_text_top_center(
            self._w / 2, 22, hint, 8.5, c_text3))

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

            color = c_hover if (is_hov_e or is_adj) else c_primary
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
            color     = node_colors[ni % len(node_colors)]

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
                        color=_rgba(c_hover, 0.20),
                    ),
                ))
            # Outline tipis untuk node tetangga
            elif is_adj_n and hov_node >= 0:
                shapes.append(cv.Circle(
                    x=x, y=y, radius=r + 3,
                    paint=ft.Paint(
                        style=ft.PaintingStyle.STROKE,
                        stroke_width=1.5,
                        color=_rgba(c_primary, 0.50),
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
                    node["x"], node["y"], node["label"],
                    [("Jumlah Anime", str(node["count"])),
                     ("Koneksi Genre", str(conn))],
                )
            elif hit_edge >= 0:
                edge  = self._edges[hit_edge]
                label = f"{self._nodes[edge['i']]['label']} × {self._nodes[edge['j']]['label']}"
                ni = self._nodes[edge['i']]
                nj = self._nodes[edge['j']]
                mx_edge = (ni["x"] + nj["x"]) / 2
                my_edge = (ni["y"] + nj["y"]) / 2
                self._tooltip.show_at(
                    mx_edge, my_edge, label,
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

import math
import flet as ft
import flet.canvas as cv
from collections import Counter
from itertools import combinations
from .palette import (
    C_TEXT, C_TEXT3, C_SAKURA, C_HOVER, C_WHITE,
    _rgba, _text_w, _text_h, _cv_text_top_center
)

class GenreNetworkGraph(ft.Container):
    """Network graph: node = genre, edge = co-occurrence frequency."""

    MAX_GENRES  = 20
    NODE_MIN_R  = 18
    NODE_MAX_R  = 36
    HEADER_H    = 66

    NODE_COLORS = [
        "#B05880", "#8B4060", "#A06880", "#7B3858",
        "#C07090", "#904870", "#D06090", "#7A4868",
        "#A03860", "#C85880", "#985070", "#B86888",
        "#884060", "#D07898", "#A04870",
    ]

    @staticmethod
    def _luminance(hex_color: str) -> float:
        r = int(hex_color[1:3], 16) / 255
        g = int(hex_color[3:5], 16) / 255
        b = int(hex_color[5:7], 16) / 255
        def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)

    @staticmethod
    def _fit_label(label: str, radius: float, fsize: float) -> list:
        max_w    = radius * 2 * 0.82
        char_w   = fsize * 0.52
        max_char = max(1, int(max_w / char_w))

        if len(label) <= max_char:
            return [label]

        spaces = [i for i, c in enumerate(label) if c == ' ']
        if spaces:
            mid = len(label) // 2
            best_sp = min(spaces, key=lambda p: abs(p - mid))
            line1 = label[:best_sp]
            line2 = label[best_sp + 1:]
            if len(line1) <= max_char and len(line2) <= max_char:
                return [line1, line2]
            for sp in sorted(spaces, key=lambda p: abs(p - mid)):
                l1, l2 = label[:sp], label[sp + 1:]
                if len(l1) <= max_char and len(l2) <= max_char:
                    return [l1, l2]

        truncated = label[:max_char - 1] + "…" if len(label) > max_char else label[:max_char]
        return [truncated]

    @staticmethod
    def _pmi_color(t: float) -> str:
        t = max(0.0, min(1.0, t))
        if t < 0.5:
            f = t * 2.0
            r = int(239 + f * (234 - 239))
            g = int(68 + f * (179 - 68))
            b = int(68 + f * (8 - 68))
        else:
            f = (t - 0.5) * 2.0
            r = int(234 + f * (34 - 234))
            g = int(179 + f * (197 - 179))
            b = int(8 + f * (94 - 8))
        return f"#{r:02x}{g:02x}{b:02x}"

    def __init__(self, animes: list, title: str, theme: dict = None, tooltip=None):
        super().__init__(expand=True)
        self._title   = title
        self._theme   = theme
        self._clicked_node = -1
        self._clicked_edge = -1
        self._w = self._h = 0
        self.animes = animes
        self.total_anime = len(animes)

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

        counts  = [genre_counter[g] for g in top_genres]
        max_cnt = max(counts) if counts else 1
        self._nodes = []
        for g, cnt in zip(top_genres, counts):
            r = self.NODE_MIN_R + (self.NODE_MAX_R - self.NODE_MIN_R) * (cnt / max_cnt)
            self._nodes.append({"label": g, "count": cnt, "r": r, "x": 0.0, "y": 0.0})

        raw_edges = []
        for (g1, g2), w in pair_counter.items():
            if g1 in top_genres and g2 in top_genres:
                count1 = genre_counter[g1]
                count2 = genre_counter[g2]
                if count1 > 0 and count2 > 0:
                    pmi = math.log2((w * self.total_anime) / (count1 * count2))
                    raw_edges.append({
                        "i": top_genres.index(g1),
                        "j": top_genres.index(g2),
                        "weight": w,
                        "pmi": pmi
                    })
        
        self._edges = []
        if raw_edges:
            min_pmi = min(e["pmi"] for e in raw_edges)
            max_pmi = max(e["pmi"] for e in raw_edges)
            rng_pmi = max(max_pmi - min_pmi, 0.0001)
            for e in raw_edges:
                e["pmi_norm"] = (e["pmi"] - min_pmi) / rng_pmi
                self._edges.append(e)

        self._canvas = cv.Canvas(shapes=[], expand=True, on_resize=self._on_resize)
        self._gd = ft.GestureDetector(
            content=ft.Container(expand=True),
            on_tap=self._on_tap,
        )

        c_title = theme["text_main"]  if theme else C_TEXT
        c_hint  = theme["text_muted"] if theme else C_TEXT3

        stack_controls = [self._canvas, self._gd]

        hint_text = (
            "Klik node/garis untuk detail  •  "
            "Warna garis = tingkat afinitas (merah: rendah, hijau: tinggi)  •  "
            "Lingkaran besar = genre populer"
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

        self._info_panel = ft.Column(
            controls=[
                ft.Text("Pilih elemen", size=14, weight=ft.FontWeight.BOLD, color=c_title),
                ft.Text("Klik pada genre (node) atau garis penghubung untuk melihat statistik detail.", size=12, color=c_hint)
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        panel_container = ft.Container(
            content=self._info_panel,
            width=320,
            padding=ft.padding.all(16),
            border=ft.border.only(left=ft.border.BorderSide(1, theme["border_color"] if theme else "#e0e0e0")),
            bgcolor=theme["bg"] if theme else ft.colors.TRANSPARENT,
        )

        graph_area = ft.Column(
            controls=[header, ft.Stack(controls=stack_controls, expand=True)],
            spacing=0,
            expand=True,
        )

        self.content = ft.Row(
            controls=[graph_area, panel_container],
            spacing=0,
            expand=True,
        )

    def _compute_layout(self):
        n = len(self._nodes)
        if n == 0 or self._w == 0 or self._h == 0:
            return
        graph_top = self.HEADER_H
        usable_h  = self._h - graph_top
        usable_w  = self._w
        PAD       = 44
        cx        = usable_w / 2
        cy        = graph_top + usable_h / 2
        r = max(10.0, min(usable_w / 2 - PAD, usable_h / 2 - PAD))
        for i, node in enumerate(self._nodes):
            a = 2 * math.pi * i / n - math.pi / 2
            node["x"] = cx + r * math.cos(a)
            node["y"] = cy + r * math.sin(a)
        
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
        self._redraw(self._clicked_node, self._clicked_edge)

    def _redraw(self, hov_node: int, hov_edge: int):
        if self._w == 0 or not self._nodes:
            return
        shapes = []

        c_text3   = self._theme["text_muted"] if self._theme else C_TEXT3
        c_primary = self._theme["primary"]    if self._theme else C_SAKURA
        c_hover   = self._theme["primary"]    if self._theme else C_HOVER
        node_colors = (
            self._theme.get("chart_colors", self.NODE_COLORS)
            if self._theme else self.NODE_COLORS
        )

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
                alpha = 0.40
            
            base_color = self._pmi_color(edge.get("pmi_norm", 0.5))
            color = c_hover if is_hov_e else base_color
            stroke_w = 4.0 if is_hov_e else (2.5 if is_adj else 1.5)

            shapes.append(cv.Path(
                [cv.Path.MoveTo(ni["x"], ni["y"]),
                 cv.Path.LineTo(nj["x"], nj["y"])],
                ft.Paint(style=ft.PaintingStyle.STROKE,
                         stroke_width=stroke_w, color=_rgba(color, alpha)),
            ))

        adj_nodes: set = set()
        if hov_node >= 0:
            for edge in self._edges:
                if edge["i"] == hov_node:
                    adj_nodes.add(edge["j"])
                elif edge["j"] == hov_node:
                    adj_nodes.add(edge["i"])

        for ni, node in enumerate(self._nodes):
            is_hov_n = (ni == hov_node)
            is_adj_n = (ni in adj_nodes)
            color    = node_colors[ni % len(node_colors)]
            alpha    = 1.0 if (hov_node == -1 or is_hov_n or is_adj_n) else 0.28
            r        = node["r"]
            x, y     = node["x"], node["y"]

            if is_hov_n:
                shapes.append(cv.Circle(x=x, y=y, radius=r + 7,
                    paint=ft.Paint(style=ft.PaintingStyle.FILL,
                                   color=_rgba(c_hover, 0.20))))
            elif is_adj_n and hov_node >= 0:
                shapes.append(cv.Circle(x=x, y=y, radius=r + 3,
                    paint=ft.Paint(style=ft.PaintingStyle.STROKE,
                                   stroke_width=1.5, color=_rgba(c_primary, 0.50))))

            shapes.append(cv.Circle(x=x, y=y, radius=r,
                paint=ft.Paint(style=ft.PaintingStyle.FILL, color=_rgba(color, alpha))))
            shapes.append(cv.Circle(x=x, y=y, radius=r,
                paint=ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=1.5,
                               color=_rgba(C_WHITE, min(alpha + 0.1, 1.0)))))

            fsize   = 7.5 if r < 22 else (9.0 if r < 28 else 10.0)
            lum     = self._luminance(color)
            txt_col = C_TEXT if lum > 0.25 else C_WHITE
            lines   = self._fit_label(node["label"], r, fsize)
            n_lines = len(lines)
            line_h  = _text_h(fsize)
            gap     = 1.5
            total_h = n_lines * line_h + (n_lines - 1) * gap
            y0      = y - total_h / 2
            for li, ln in enumerate(lines):
                ty = y0 + li * (line_h + gap) + line_h / 2
                tw = _text_w(ln, fsize)
                shapes.append(cv.Text(
                    x=x - tw / 2, y=ty - line_h / 2, value=ln,
                    style=ft.TextStyle(
                        size=fsize, color=txt_col,
                        weight=ft.FontWeight.BOLD if is_hov_n else ft.FontWeight.W_600,
                    ),
                ))

        self._canvas.shapes = shapes
        self._canvas.update()

    def _on_tap(self, e):
        mx, my = e.local_position.x, e.local_position.y
        if self._w == 0:
            return

        hit_node = -1
        for ni, node in enumerate(self._nodes):
            if math.hypot(mx - node["x"], my - node["y"]) <= node["r"] + 4:
                hit_node = ni
                break

        hit_edge = -1
        if hit_node == -1:
            best_dist = 12.0
            
            # Pass 1: Prioritas pada edge milik node yang sedang aktif
            if self._clicked_node >= 0:
                for ei, edge in enumerate(self._edges):
                    if self._clicked_node in (edge["i"], edge["j"]):
                        ni = self._nodes[edge["i"]]
                        nj = self._nodes[edge["j"]]
                        dist = self._pt_to_seg(mx, my, ni["x"], ni["y"], nj["x"], nj["y"])
                        if dist < best_dist:
                            best_dist = dist
                            hit_edge = ei
            
            # Pass 2: Jika tidak ada edge prioritas yang ditekan, periksa seluruh edge
            if hit_edge == -1:
                for ei, edge in enumerate(self._edges):
                    ni = self._nodes[edge["i"]]
                    nj = self._nodes[edge["j"]]
                    dist = self._pt_to_seg(mx, my, ni["x"], ni["y"], nj["x"], nj["y"])
                    if dist < best_dist:
                        best_dist = dist
                        hit_edge = ei

        if hit_node == -1 and hit_edge == -1:
            self._clicked_node = -1
            self._clicked_edge = -1
            self._redraw(-1, -1)
            self._update_panel(-1, -1)
            return

        if hit_node == self._clicked_node and hit_edge == self._clicked_edge:
            self._clicked_node = -1
            self._clicked_edge = -1
            self._redraw(-1, -1)
            self._update_panel(-1, -1)
            return

        self._clicked_node = hit_node
        self._clicked_edge = hit_edge
        self._redraw(hit_node, hit_edge)
        self._update_panel(hit_node, hit_edge)

    def _update_panel(self, node_idx: int, edge_idx: int):
        c_title = self._theme["text_main"] if self._theme else C_TEXT
        c_text  = self._theme["text_secondary"] if self._theme else C_TEXT
        c_hint  = self._theme["text_muted"] if self._theme else C_TEXT3
        
        if node_idx == -1 and edge_idx == -1:
            self._info_panel.controls = [
                ft.Text("Pilih elemen", size=14, weight=ft.FontWeight.BOLD, color=c_title),
                ft.Text("Klik pada genre (node) atau garis penghubung untuk melihat statistik detail.", size=12, color=c_hint)
            ]
            self._info_panel.update()
            return
            
        def build_dimension_ui(title, scores, is_synergy=False):
            labels = ["Plot", "Visual", "Audio", "Char.", "Direct."]
            rows = []
            for lbl, val in zip(labels, scores[:5]):
                rows.append(ft.Row([
                    ft.Text(lbl, size=11, color=c_text, expand=True),
                    ft.Text(f"{val:.2f}", size=11, color=c_title, weight=ft.FontWeight.BOLD)
                ], spacing=4))
            return ft.Container(
                content=ft.Column([
                    ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=c_title, italic=is_synergy),
                    ft.Row([
                        ft.Column(rows[:3], spacing=2, expand=True),
                        ft.Column(rows[3:], spacing=2, expand=True)
                    ], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(height=1, color=self._theme["border_color"] if self._theme else "#e0e0e0"),
                    ft.Row([
                        ft.Text("Overall Score", size=12, weight=ft.FontWeight.BOLD, color=c_title, expand=True),
                        ft.Text(f"{scores[5]:.2f}", size=12, weight=ft.FontWeight.BOLD, color=self._theme["primary"] if self._theme else C_SAKURA)
                    ])
                ], spacing=4),
                padding=8,
                border=ft.border.all(1, self._theme["border_color"] if self._theme else "#e0e0e0"),
                border_radius=8,
                bgcolor=self._theme["card"] if self._theme else ft.colors.TRANSPARENT
            )

        def calc_genre_stats(genre_name):
            matched = [a for a in self.animes if genre_name in a.get("genre", [])]
            if not matched:
                return [0,0,0,0,0,0], []
            
            dims = [0.0]*5
            overall = 0.0
            valid_count = 0
            for a in matched:
                sc = a.get("global_score_dimensions", [0,0,0,0,0])
                ov = a.get("global_score", 0.0)
                if ov > 0:
                    for i in range(5): dims[i] += sc[i]
                    overall += ov
                    valid_count += 1
            if valid_count > 0:
                dims = [d/valid_count for d in dims]
                overall /= valid_count
            
            top = sorted([a for a in matched if a.get("global_score",0) > 0], 
                         key=lambda x: x.get("global_score",0), reverse=True)[:3]
            return dims + [overall], top
            
        def calc_synergy_stats(g1, g2):
            matched = [a for a in self.animes if g1 in a.get("genre", []) and g2 in a.get("genre", [])]
            if not matched:
                return [0,0,0,0,0,0], []
            
            dims = [0.0]*5
            overall = 0.0
            valid_count = 0
            for a in matched:
                sc = a.get("global_score_dimensions", [0,0,0,0,0])
                ov = a.get("global_score", 0.0)
                if ov > 0:
                    for i in range(5): dims[i] += sc[i]
                    overall += ov
                    valid_count += 1
            if valid_count > 0:
                dims = [d/valid_count for d in dims]
                overall /= valid_count
            
            top = sorted([a for a in matched if a.get("global_score",0) > 0], 
                         key=lambda x: x.get("global_score",0), reverse=True)[:3]
            return dims + [overall], top

        def build_anime_list(title, anime_list):
            if not anime_list:
                return ft.Text("Belum ada anime.", size=11, color=c_hint)
            
            rows = [ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=c_title)]
            for i, a in enumerate(anime_list):
                rows.append(ft.Row([
                    ft.Text(f"{i+1}.", size=11, color=c_hint),
                    ft.Text(a.get("title", "Unknown"), size=11, color=c_text, expand=True, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"{a.get('global_score', 0):.2f}", size=11, weight=ft.FontWeight.BOLD, color=c_title)
                ], spacing=4))
            return ft.Column(rows, spacing=2)

        ctrls = []
        if node_idx >= 0:
            node = self._nodes[node_idx]
            g_name = node["label"]
            conn = sum(1 for e in self._edges if node_idx in (e["i"], e["j"]))
            
            stats, top3 = calc_genre_stats(g_name)
            
            ctrls.append(ft.Text(f"Genre: {g_name}", size=16, weight=ft.FontWeight.BOLD, color=c_title))
            ctrls.append(ft.Text(f"Jumlah Anime: {node['count']}  •  Koneksi: {conn}", size=12, color=c_hint))
            ctrls.append(ft.Divider(height=10, color="transparent"))
            
            ctrls.append(build_dimension_ui("Average Ratings", stats))
            ctrls.append(ft.Divider(height=10, color="transparent"))
            ctrls.append(build_anime_list(f"Top 3 Anime '{g_name}'", top3))

        elif edge_idx >= 0:
            edge = self._edges[edge_idx]
            n1 = self._nodes[edge["i"]]
            n2 = self._nodes[edge["j"]]
            g1, g2 = n1["label"], n2["label"]
            
            syn_stats, syn_top = calc_synergy_stats(g1, g2)
            g1_stats, _ = calc_genre_stats(g1)
            g2_stats, _ = calc_genre_stats(g2)
            
            pmi_val = edge.get("pmi", 0)
            if pmi_val > 2: aff = "Sangat Tinggi"
            elif pmi_val > 1: aff = "Tinggi"
            elif pmi_val > 0: aff = "Sedang"
            else: aff = "Rendah"
            
            p1_given_2 = edge["weight"] / n2["count"] if n2["count"] > 0 else 0
            p2_given_1 = edge["weight"] / n1["count"] if n1["count"] > 0 else 0
            
            ctrls.append(ft.Text(f"{g1} \u00d7 {g2}", size=16, weight=ft.FontWeight.BOLD, color=c_title))
            ctrls.append(ft.Text(f"Irisan: {edge['weight']} anime", size=12, weight=ft.FontWeight.BOLD, color=c_title))
            ctrls.append(ft.Text(f"Total anime {g1}: {n1['count']}  •  Total {g2}: {n2['count']}", size=11, color=c_hint))
            
            aff_color = self._pmi_color(edge.get("pmi_norm", 0.5))
            ctrls.append(ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("Kecocokan (Afinitas):", size=11, color=c_text),
                        ft.Text(aff, size=11, weight=ft.FontWeight.BOLD, color=aff_color)
                    ], spacing=4),
                    ft.Text("Kecenderungan:", size=11, weight=ft.FontWeight.BOLD, color=c_title),
                    ft.Text(f"Jika bergenre {g2}, probabilitas {p1_given_2:.1%} ia juga {g1}.", size=11, color=c_text),
                    ft.Text(f"Jika bergenre {g1}, probabilitas {p2_given_1:.1%} ia juga {g2}.", size=11, color=c_text)
                ], spacing=4),
                padding=8,
                bgcolor=ft.Colors.with_opacity(0.05, c_title),
                border_radius=4
            ))
            ctrls.append(ft.Divider(height=10, color="transparent"))
            
            ctrls.append(build_dimension_ui("Synergy Index", syn_stats, is_synergy=True))
            ctrls.append(ft.Divider(height=4, color="transparent"))
            ctrls.append(build_dimension_ui(f"Avg: {g1}", g1_stats))
            ctrls.append(ft.Divider(height=4, color="transparent"))
            ctrls.append(build_dimension_ui(f"Avg: {g2}", g2_stats))
            
            ctrls.append(ft.Divider(height=10, color="transparent"))
            ctrls.append(build_anime_list("Top 3 Synergy Anime", syn_top))

        self._info_panel.controls = ctrls
        self._info_panel.update()

    @staticmethod
    def _pt_to_seg(px, py, ax, ay, bx, by) -> float:
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            return math.hypot(px - ax, py - ay)
        t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
        return math.hypot(px - (ax + t * dx), py - (ay + t * dy))

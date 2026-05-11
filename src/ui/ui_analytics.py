import math
import flet as ft
import flet.canvas as cv
from collections import Counter

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

        self._main_content.controls.extend([
            stat_card,
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.TOUCH_APP, color=C_TEXT3, size=14),
                    ft.Text("Hover di atas bar / slice untuk detail",
                            size=11, color=C_TEXT3, italic=True),
                ],
                spacing=6,
            ),
            row1,
            row2,
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
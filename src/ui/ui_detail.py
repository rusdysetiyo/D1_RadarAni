import flet as ft
import flet.canvas as cv
import math
from src.ui.icons import _sakura_icon_svg
import random
import os
from src.config.theme import ThemeManager


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))


# ── Warna Tema ────────────────────────────────────────
C_BG = "#FCF8FA"
C_BG2 = "#F5EEF2"
C_SAKURA = "#C07090"
C_SAKURA_LT = "#F9F0F5"
C_BLUE_LT = "#D4EBF8"
C_TEXT = "#3D2535"
C_TEXT2 = "#8B6A7A"
C_TEXT3 = "#B0909A"
C_BORDER = "#EDE0E8"
C_GOLD = "#C08030"
C_PURPLE = "#9060A0"
C_WHITE = "#FFFFFF"
C_PBORDER = "#BFFF5593"
C_GBORDER = "#BF6958FF"
C_PRADAR = "#40FF81EA"
C_GRADAR = "#40709DFF"
# ═══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════
class AnimeCardSmall(ft.Container):
    def __init__(self, anime: dict, skor_global, skor_personal, is_favorite=False, on_click_callback=None):
        super().__init__()
        self.anime = anime
        self.is_favorite = is_favorite
        self._on_click_cb = on_click_callback

        # --- UKURAN BALIK KE ORI (Lebih jenjang/panjang) ---
        self.width = 120
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=["#FFFFFF", "#FDF5F8"]
        )
        self.border = ft.border.all(1, "#EDE0E8")
        self.border_radius = ft.border_radius.only(
            top_left=15, bottom_right=15, top_right=4, bottom_left=4
        )

        self.clip_behavior = ft.ClipBehavior.ANTI_ALIAS
        self.margin = ft.padding.only(left=6, right=6, top=10, bottom=20)

        self.on_click = lambda _: self._on_click_cb(anime.get("anime_id", "")) if on_click_callback else None
        self.on_hover = self._on_hover
        self.animate = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)
        self.rotate = ft.Rotate(angle=random.uniform(-0.015, 0.015))

        is_rated = skor_personal is not None

        if is_rated:
            pill_bg = "#EC407A"
            pill_txt = "★ rated"
            pill_color = "#FFFFFF"
        else:
            pill_bg = ft.Colors.with_opacity(0.9, "#F5EEF2")
            pill_txt = "not rated"
            pill_color = "#8B6A7A"

        self._status_pill = ft.Container(
            content=ft.Text(pill_txt, size=8, color=pill_color, weight=ft.FontWeight.BOLD),
            bgcolor=pill_bg,
            border_radius=ft.border_radius.only(top_left=10, bottom_right=10),
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            top=6, right=6,
            opacity=1.0,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )

        self._fav_icon = ft.Container(
            content=ft.Image(src=_sakura_icon_svg(), width=22, height=22),
            top=-30, right=6,
            opacity=0,
            animate_position=ft.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            animate_rotation=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            rotate=ft.Rotate(angle=-1)
        )

        # ── 3. DATA OVERLAY ──
        genres = anime.get("genre", [])[:3]
        sg_str = (f"★ {skor_global:.1f}  ·  {anime.get('episodes', '?')} eps"
                  if skor_global else f"{anime.get('episodes', '?')} eps")

        # ── 4. OVERLAY
        self._overlay = ft.Container(
            width=120, height=162,
            bgcolor=ft.Colors.with_opacity(0.85, "#000000"),
            border_radius=ft.border_radius.only(top_left=15, top_right=4),
            padding=8,
            content=ft.Column(
                controls=[
                    ft.Container(expand=True),
                    ft.Text(anime.get("title", ""), size=9, color="#FFFFFF",
                            weight=ft.FontWeight.BOLD, max_lines=2),
                    ft.Text(sg_str, size=8, color="#D4A8BC"),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(g, size=7, color="#F5D0E0"),
                                bgcolor="#C07090",
                                border_radius=ft.border_radius.only(top_left=6, bottom_right=6),
                                padding=ft.padding.symmetric(horizontal=4, vertical=1),
                                opacity=0.75,
                            )
                            for g in genres
                        ],
                        spacing=3, run_spacing=2, wrap=True,
                    ),
                ],
                spacing=3,
            ),
            visible=False,
        )

        thumb = anime.get("cover_path", "")
        if thumb:
            poster_path = os.path.abspath(os.path.join(ROOT_DIR, thumb))
        else:
            poster_path = ""

        poster = ft.Container(
            width=120, height=162,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            border_radius=ft.border_radius.only(top_left=15, top_right=4),
            content=ft.Image(
                src=poster_path if (poster_path and os.path.exists(poster_path)) else "",
                width=120, height=162,
                fit=ft.BoxFit.COVER,
            ) if poster_path else ft.Icon("photo", color="#B0909A")
        )

        sp_txt = f"you: {skor_personal:.1f}" if is_rated else "you: N/A"
        sp_col = "#9060A0" if is_rated else "#B0909A"

        info = ft.Container(
            padding=ft.padding.only(left=7, right=7, top=4, bottom=5),
            content=ft.Column(
                controls=[
                    ft.Text(
                        anime.get("title", "—"),
                        size=9,
                        color="#3D2535",
                        weight=ft.FontWeight.BOLD,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"★ {skor_global:.1f}" if skor_global else "★ —",
                                size=8,
                                color="#C08030",
                                weight=ft.FontWeight.BOLD
                            ),
                            ft.Text("·", size=8, color="#EDE0E8"),
                            ft.Text(
                                sp_txt,
                                size=8,
                                color=sp_col,
                                weight=ft.FontWeight.BOLD
                            ),
                        ],
                        spacing=3,
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                ],
                spacing=2,
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        # ── 7. GABUNGAN ──
        self.content = ft.Column(
            controls=[
                ft.Stack(
                    controls=[poster, self._overlay, self._status_pill, self._fav_icon],
                    width=120, height=162,
                ),
                info,
            ],
            spacing=0,
        )

    def _on_hover(self, e):
        is_hovered = str(e.data).lower() == "true"
        self._overlay.visible = is_hovered

        if is_hovered:
            self._status_pill.opacity = 0
            self._fav_icon.top = 6
            self._fav_icon.opacity = 1.0 if self.is_favorite else 0.4
            self._fav_icon.rotate.angle = 0
            self.rotate = ft.Rotate(angle=0.02)
        else:
            self._status_pill.opacity = 1.0
            self._fav_icon.top = -30
            self._fav_icon.opacity = 0
            self._fav_icon.rotate.angle = -1
            self.rotate = ft.Rotate(angle=0)

        self.border = ft.border.all(1.5 if is_hovered else 1, "#EC407A" if is_hovered else "#EDE0E8")
        self.scale = 1.03 if is_hovered else 1.0
        self.update()

def build_radar_chart(global_scores, personal_scores, labels, size=300):
    cx = cy = size / 2
    max_r = size / 2 - 40
    n = len(labels)
    grid_levels = 5
    shapes = []

    def petal_path(angle_deg, length, width_factor=0.46, notch_depth=0.11):
        """
        width_factor=0.72  ← naik dari 0.35, bikin kelopak jauh lebih lebar
        notch_depth=0.11   ← lekukan ke dalam di ujung
        """
        rad = math.radians(angle_deg)
        rad_perp = math.radians(angle_deg + 90)

        w = length * width_factor  # lebar samping kelopak

        # Dua notch di ujung kelopak (kiri & kanan)
        notch_dist = length * 0.92
        notch_lx = cx + notch_dist * math.cos(rad) + w * 0.22 * math.cos(rad_perp)
        notch_ly = cy + notch_dist * math.sin(rad) + w * 0.22 * math.sin(rad_perp)
        notch_rx = cx + notch_dist * math.cos(rad) - w * 0.22 * math.cos(rad_perp)
        notch_ry = cy + notch_dist * math.sin(rad) - w * 0.22 * math.sin(rad_perp)

        # Titik lekukan ke dalam (indent tengah)
        indent_x = cx + (length - length * notch_depth) * math.cos(rad)
        indent_y = cy + (length - length * notch_depth) * math.sin(rad)

        # Kontrol sisi kiri — menggelembung lebar
        c1x = cx + length * 0.50 * math.cos(rad) + w * 0.95 * math.cos(rad_perp)
        c1y = cy + length * 0.50 * math.sin(rad) + w * 0.95 * math.sin(rad_perp)
        c2x = notch_lx - length * 0.15 * math.cos(rad) + w * 0.45 * math.cos(rad_perp)
        c2y = notch_ly - length * 0.15 * math.sin(rad) + w * 0.45 * math.sin(rad_perp)

        # Kontrol sisi kanan — simetris
        c5x = cx + length * 0.50 * math.cos(rad) - w * 0.95 * math.cos(rad_perp)
        c5y = cy + length * 0.50 * math.sin(rad) - w * 0.95 * math.sin(rad_perp)
        c6x = notch_rx - length * 0.15 * math.cos(rad) - w * 0.45 * math.cos(rad_perp)
        c6y = notch_ry - length * 0.15 * math.sin(rad) - w * 0.45 * math.sin(rad_perp)

        # Kontrol lekukan indent
        ci1x = indent_x + w * 0.20 * math.cos(rad_perp)
        ci1y = indent_y + w * 0.20 * math.sin(rad_perp)
        ci2x = indent_x - w * 0.20 * math.cos(rad_perp)
        ci2y = indent_y - w * 0.20 * math.sin(rad_perp)

        return [
            cv.Path.MoveTo(cx, cy),
            cv.Path.CubicTo(c1x, c1y, c2x, c2y, notch_lx, notch_ly),   # sisi kiri
            cv.Path.CubicTo(ci1x, ci1y, ci2x, ci2y, notch_rx, notch_ry), # lekukan dalam
            cv.Path.CubicTo(c6x, c6y, c5x, c5y, cx, cy),                 # sisi kanan
            cv.Path.Close(),
        ]

    # def sub_petal_rings(angle_deg, length, color, num_rings=3):
    #     """Tambahkan 2 cincin sub-kelopak lebih kecil untuk efek berlapis."""
    #     ring_shapes = []
    #     for i in range(1, num_rings):
    #         fraction = i / num_rings
    #         cmds = petal_path(angle_deg, length * fraction, width_factor=0.3)
    #         ring_shapes.append(ft.canvas.Path(
    #             elements=cmds,
    #             paint=ft.Paint(
    #                 color=color.replace(")", f", {0.15})").replace("rgb", "rgba") if "rgb" in color else color + "25",
    #                 stroke_width=0.6,
    #                 style=ft.PaintingStyle.STROKE
    #             )
    #         ))
    #     return ring_shapes

    #Grid rings (poligon)
    for level in range(1, grid_levels + 1):
        r = max_r * level / grid_levels
        grid_pts = []
        for i in range(n):
            angle = math.radians(-90 + i * 360 / n)
            grid_pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        path_cmds = [ft.canvas.Path.MoveTo(grid_pts[0][0], grid_pts[0][1])]
        for p in grid_pts[1:]:
            path_cmds.append(ft.canvas.Path.LineTo(p[0], p[1]))
        path_cmds.append(ft.canvas.Path.Close())
        shapes.append(ft.canvas.Path(
            elements=path_cmds,
            paint=ft.Paint(color="#BFC5C0DE", stroke_width=0.8, style=ft.PaintingStyle.STROKE)
        ))

    #Grid Level (petal)
    # for level in range(1, grid_levels + 1):
    #     r = max_r * level / grid_levels
    #     # Gambar 1 "bunga" grid per level — pakai petal_path untuk setiap kelopak
    #     for i in range(n):
    #         angle_deg = -90 + i * 360 / n
    #         cmds = petal_path(angle_deg, r)
    #         shapes.append(ft.canvas.Path(
    #             elements=cmds,
    #             paint=ft.Paint(
    #                 color="#FF76504C",
    #                 stroke_width=0.6,
    #                 style=ft.PaintingStyle.STROKE
    #             )
    #         ))

    # Axis lines
    for i in range(n):
        angle = math.radians(-90 + i * 360 / n)
        shapes.append(ft.canvas.Path(
            elements=[
                ft.canvas.Path.MoveTo(cx, cy),
                ft.canvas.Path.LineTo(cx + max_r * math.cos(angle), cy + max_r * math.sin(angle)),
            ],
            paint=ft.Paint(color="#C5C0DE80", stroke_width=0.8)
        ))

    # Global petals (biru)
    for i, score in enumerate(global_scores):
        angle_deg = -90 + i * 360 / n
        length = (score / 10) * max_r
        cmds = petal_path(angle_deg, length)

        # Fill kelopak
        shapes.append(ft.canvas.Path(
            elements=cmds,
            paint=ft.Paint(color=C_GRADAR, style=ft.PaintingStyle.FILL)
        ))
        # Stroke luar
        shapes.append(ft.canvas.Path(
            elements=cmds,
            paint=ft.Paint(color=C_GBORDER, stroke_width=1.5, style=ft.PaintingStyle.STROKE)
        ))
        # Sub-kelopak berlapis
        for frac in [0.65, 0.4]:
            sub_cmds = petal_path(angle_deg, length * frac, width_factor=0.28)
            shapes.append(ft.canvas.Path(
                elements=sub_cmds,
                paint=ft.Paint(color=C_GRADAR, stroke_width=0.6, style=ft.PaintingStyle.STROKE)
            ))

    # Personal petals (pink)
    if any(s > 0 for s in personal_scores):
        for i, score in enumerate(personal_scores):
            angle_deg = -90 + i * 360 / n
            length = (score / 10) * max_r
            cmds = petal_path(angle_deg, length)

            shapes.append(ft.canvas.Path(
                elements=cmds,
                paint=ft.Paint(color=C_PRADAR, style=ft.PaintingStyle.FILL)
            ))
            shapes.append(ft.canvas.Path(
                elements=cmds,
                paint=ft.Paint(color=C_PBORDER, stroke_width=1.5, style=ft.PaintingStyle.STROKE)
            ))

    # Labels
    label_r = max_r + 22
    for i, label in enumerate(labels):
        angle = math.radians(-90 + i * 360 / n)
        lx = cx + label_r * math.cos(angle)
        ly = cy + label_r * math.sin(angle)
        shapes.append(ft.canvas.Text(
            x=lx, y=ly,
            value=label,
            alignment=ft.Alignment(0, 0),
            style=ft.TextStyle(size=11, color="#666666", weight=ft.FontWeight.W_500),
        ))

    # Center dot
    shapes.append(ft.canvas.Circle(cx, cy, 4, ft.Paint(color="#CCCCCC80", style=ft.PaintingStyle.FILL)))

    return ft.Container(
        width=size,
        height=size,
        content=ft.canvas.Canvas(shapes=shapes, width=size, height=size)
    )


def score_dropdown(label: str):
    return ft.Column(
        spacing=4,
        controls=[
            ft.Text(label, size=11, color=C_TEXT, weight=ft.FontWeight.W_500),
            ft.Dropdown(
                value="1",
                options=[ft.dropdown.Option(str(i)) for i in range(1, 11)],
                width=110,
                height=42,
                bgcolor=C_TEXT,
                border_color=C_BORDER,
                border_radius=8,
                text_size=13,
                content_padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
        ]
    )


def score_card(value, global_score=False):
    return ft.Container(
        width=150,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        bgcolor=C_WHITE,
        border_radius=12,
        border=ft.border.all(1, C_BORDER),
        content=ft.Column(
            spacing=2,
            controls=[
                ft.Text("USER SCORE" if not global_score else "GLOBAL SCORE", size=10, color=C_TEXT2, weight=ft.FontWeight.W_600),
                ft.Text(value, size=26, color=C_PURPLE if not global_score else C_GOLD, weight=ft.FontWeight.W_700),
                ft.Text("Your Rating" if not global_score else "Community Average Score", size=10, color=C_TEXT2)
            ]
        )
    )


def tag(text, meta=False):
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        bgcolor= C_WHITE if not meta else C_SAKURA,
        border_radius=20,
        border=ft.border.all(1.5, "#e8b4cb"),
        content=ft.Text(
            text, size=11,
            color= C_SAKURA if not meta else C_WHITE,
            weight=ft.FontWeight.W_600
        )
    )


def legend_dot(color):
    return ft.Container(width=12, height=12, bgcolor=color, border_radius=6)


# ═══════════════════════════════════════════════════════════════
#  LEFT PANEL — poster, judul, tag, synopsis
# ═══════════════════════════════════════════════════════════════

class LeftPanel(ft.Container):
    def __init__(self, detail_anime: dict, data_manager, screen_manager, anime_id):
        self.detail_anime = detail_anime
        self.data_manager = data_manager
        self.screen_manager = screen_manager
        self.anime_id = anime_id
        self.user_id = data_manager.baca_sesi()  # Ambil ID pengguna yang aktif
        cover = detail_anime.get("cover_path", "")
        gendres = detail_anime.get("genre", [])
        studio = detail_anime.get("studio", "N/A")
        type = detail_anime.get("type", "N/A")
        episode = detail_anime.get("episodes", "N/A")
        metaTags = [studio, type, episode]
        self.is_fav = self.data_manager.cek_is_favorit(self.user_id, self.anime_id)
        self.fav_button = self._build_fav_button()
        


        super().__init__(
            alignment=ft.Alignment(0, 0),                          # ← tambahkan ini
            width=268,
            content=ft.Column(
                spacing=16,
                controls=[
                    self._build_poster(cover),
                    ft.Text(self.detail_anime.get("title", "Anime Detail"), size=22,
                            weight=ft.FontWeight.W_800, color="#1E1B2E"),
                    self._build_genre_tags(gendres),
                    self._build_detail_info(),
                    ft.Container(height=24),
                ]
            )
        )

    def _build_poster(self, cover_path):
        return ft.Container(
            width=268,
            height=320,
            border_radius=16,
            border=ft.border.all(2, "#e8b4cb"),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Image(src=cover_path, fit="cover"),
            
        )

    def _build_meta_tags(self, metaTags):
        return ft.Row(
            wrap=True, spacing=6, run_spacing=6,
            controls=[tag(tag_text, meta=True) for tag_text in metaTags]
        )

    def _build_genre_tags(self, gendres):
        print("Genres:", gendres)  # Debug print untuk memastikan data genre diterima dengan benar
        return ft.Row(
            wrap=True, spacing=6, run_spacing=6,
            controls=[tag(genre) for genre in gendres]
        )
    
    def _build_fav_button(self):
        return ft.ElevatedButton(
            content=ft.Text("♥  Remove from Favorit" if self.is_fav else "♡  Add to Favorit"),
            on_click=self._toggle_favorit,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED_600 if self.is_fav else ft.Colors.BLUE_600,
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
            width=268,  # Menyesuaikan lebar container (300 - padding 16*2)
        )
    
    def _toggle_favorit(self, e):
        self.is_fav = self.data_manager.toggle_favorit(self.user_id, self.anime_id)
        self.fav_button.content.value = "♥  Remove from Favorit" if self.is_fav else "♡  Add to Favorit"
        self.fav_button.style = ft.ButtonStyle(
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_600 if self.is_fav else ft.Colors.BLUE_600,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
        )
        self.fav_button.update()

    def _section_card(self, title: str, content: ft.Control) -> ft.Container:
        return ft.Container(
            bgcolor="#FFFFFF",
            border=ft.border.all(1.5, "#e8b4cb"),
            border_radius=12,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column([
                ft.Container(
                    content=ft.Text(title, size=11, weight=ft.FontWeight.W_800,
                                    color="#EC407A",
                                    style=ft.TextStyle(letter_spacing=1.1)),
                    bgcolor="#FDF0F5",
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    border=ft.border.only(bottom=ft.BorderSide(1, "#e8b4cb")),
                    width=float("inf"),
                ),
                ft.Container(
                    content=content,
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                ),
            ], spacing=0, tight=True),
        )

    def _build_detail_info(self):
        en_title = self.detail_anime.get("en_title", "-")
        genre_list = self.detail_anime.get("genre", []) or ["-"]
        studio_name = self.detail_anime.get("studio", "No studio available.")
        type_anime = self.detail_anime.get("type", "Unknown")
        episodes = self.detail_anime.get("episodes", "-")

        label_color = "#505050"
        value_color = "#1A1A1A"
        font_size = 13

        genre_items = [
            ft.Text(f"   {g}", size=font_size, color=value_color)
            for g in genre_list
        ] or [ft.Text("   -", size=font_size, color=value_color)]

        def _info_row(label, value):
            return ft.Text(
                size=font_size,
                spans=[
                    ft.TextSpan(f"{label}: ", ft.TextStyle(color=label_color,
                                                            weight=ft.FontWeight.BOLD)),
                    ft.TextSpan(str(value), ft.TextStyle(color=value_color)),
                ]
            )

        return self._section_card(
            "ANIME DETAIL",
            ft.Column(
                spacing=8,
                controls=[
                    _info_row("English Title", en_title),
                    ft.Column(
                        spacing=4,
                        controls=[
                            ft.Text("Genre:", size=font_size,
                                    weight=ft.FontWeight.BOLD, color=label_color),
                            *genre_items,
                        ]
                    ),
                    _info_row("Studio", studio_name),
                    _info_row("Type", type_anime),
                    _info_row("Episodes", episodes),
                    ft.Divider(height=1, color="#e8b4cb"),
                    self.fav_button,
                ]
            )
        )


# ═══════════════════════════════════════════════════════════════
#  RIGHT PANEL — score, radar, dropdown, tombol
# ═══════════════════════════════════════════════════════════════

class RightPanel(ft.Container):
    def __init__(self, page: ft.Page, data_manager,screen_manager, anime_id):
        self.my_page = page
        self.data_manager = data_manager
        self.screen_manager = screen_manager
        self.anime_id = anime_id
        self.user_id = data_manager.baca_sesi()  # Ambil ID pengguna yang aktif
        # Pastikan jika None, diubah jadi list nol
        user_list_score = data_manager.get_rating_user_as_list(self.user_id, anime_id)
        global_list_score = data_manager.get_skor_global_dimensi_as_list(anime_id)
        self.detail_anime = self.data_manager.get_detail_anime(anime_id)
        self._unrated_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=14)


        if not user_list_score:
            user_list_score = [0, 0, 0, 0, 0]

        if not global_list_score:
            global_list_score = [0, 0, 0, 0, 0]


        global_avg_score = data_manager.hitung_skor_global(anime_id)
        user_avg_score = data_manager.hitung_skor_personal(self.user_id, anime_id)  # Menggunakan ID pengguna yang aktif
        # Mendapatkan list skor untuk radar chart
        # Di __init__, ubah baris radar_container:
        self.radar_container = ft.Container(
            content=self._build_radar(global_list_score, user_list_score, global_avg_score, user_avg_score)
)       
        
        self._global_btn_ref = ft.Ref[ft.ElevatedButton]()
        self._personal_btn_ref = ft.Ref[ft.ElevatedButton]()

        super().__init__(
            expand=True,
            bgcolor="#F4F3F8",        # ← ganti jadi abu muda supaya card putih kontras
            border_radius=20,
            padding=ft.padding.only(left=12, right=12, top=12, bottom=24),
            content=ft.Column(
                spacing=12,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                controls=[
                    self._build_synopsis(),
                    self.radar_container,          # sudah include legend
                    self._muat_top_unrated(self.user_id),
                    ft.Container(height=24),
                ]
            ),
        )

    def _section_card(self, title: str, content: ft.Control) -> ft.Container:
        return ft.Container(
            bgcolor="#FFFFFF",
            border=ft.border.all(1.5, "#e8b4cb"),
            border_radius=12,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Text(title, size=11, weight=ft.FontWeight.W_800,
                                    color="#EC407A",
                                    style=ft.TextStyle(letter_spacing=1.1)),
                    bgcolor="#FDF0F5",
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    border=ft.border.only(bottom=ft.BorderSide(1, "#e8b4cb")),
                    width=float("inf"),
                ),
                # Body
                ft.Container(
                    content=content,
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                ),
            ], spacing=0, tight=True),
        )

    def _build_score_cards(self, global_score, user_score):
        return ft.Row(
            spacing=12,
            controls=[
                score_card(str(global_score), global_score=True),
                score_card(str(user_score)),
            ]
        )

    def _build_radar(self, global_scores, personal_scores, global_avg_score, user_avg_score):
        self.score_cards_container = ft.Container(content=self._build_score_cards(global_avg_score, user_avg_score))
        labels = ["Plot", "Visual", "Audio", "Characterization", "Direction"]
        global_scores = global_scores if global_scores else [0, 0, 0, 0, 0]
        personal_scores = personal_scores if personal_scores else [0, 0, 0, 0, 0]
        return self._section_card(
            "RADAR CHART & RATING",
            ft.Column([
                self.score_cards_container,         # ← score cards di sini
                ft.Container(height=8),
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[build_radar_chart(global_scores, personal_scores, labels)]
                ),
                self._build_legend(),   # legend masuk ke dalam card yang sama
                ft.Container(height=8),
                self._build_dropdowns(),            # ← dropdowns di sini
                ft.Container(height=8),
                self._build_action_buttons(),       # ← tombol aksi di sini
            ], spacing=8, tight=True)
        )

    def _build_legend(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Row(spacing=6, controls=[
                    legend_dot("#4A90D9"),
                    ft.Text("Global", size=12, color="#555555")
                ]),
                ft.Row(spacing=6, controls=[
                    legend_dot("#FFB6C1"),
                    ft.Text("Personal", size=12, color="#555555")
                ]),
            ]
        )

    

    def _build_dropdowns(self):
        self.dropdown_controls = {}
        categories = ["Plot", "Visual", "Audio", "Characterization", "Direction"]
        dropdown_list = []

        for cat in categories:
            # Panggil fungsi UI kamu
            ui_component = score_dropdown(cat) 
            
            # ASUMSI: score_dropdown mengembalikan Column([Text, Dropdown])
            # Kita ambil Dropdown-nya (biasanya elemen terakhir/kedua)
            if isinstance(ui_component, ft.Column):
                # Mencari objek Dropdown di dalam controls milik Column
                dropdown_obj = next(c for c in ui_component.controls if isinstance(c, ft.Dropdown))
                self.dropdown_controls[cat] = dropdown_obj
            else:
                # Jika ternyata score_dropdown langsung mengembalikan Dropdown
                self.dropdown_controls[cat] = ui_component

            dropdown_list.append(ui_component)

        return ft.Row(wrap=True, spacing=8, run_spacing=8, controls=dropdown_list)

    def save_rating(self, e):
        try:
            user_scores = {}
            for category, dd in self.dropdown_controls.items():
                val = dd.value if dd.value is not None else 0
                user_scores[category.lower()] = int(val)

            user_id = self.data_manager.baca_sesi()
            self.data_manager.simpan_rating(user_id, self.anime_id, user_scores)

            new_avg_global = self.data_manager.hitung_skor_global(self.anime_id)
            new_avg_personal = self.data_manager.hitung_skor_personal(user_id, self.anime_id)
            new_list_score = list(user_scores.values())
            new_global_list_score = self.data_manager.get_skor_global_dimensi_as_list(self.anime_id)

            # Rebuild score_cards_container dulu sebelum radar di-rebuild
            self.radar_container.content = self._build_radar(new_global_list_score, new_list_score, new_avg_global, new_avg_personal)

            self.my_page.snack_bar = ft.SnackBar(ft.Text("Rating Berhasil Diperbarui!"), bgcolor="green")
            self.my_page.snack_bar.open = True
            self.my_page.update()

        except Exception as err:
            print(f"Error: {err}")

    def delete_rating(self, e):
        user_id = self.data_manager.baca_sesi()
        self.data_manager.hapus_rating(user_id, self.anime_id)

        new_avg_global = self.data_manager.hitung_skor_global(self.anime_id)
        new_global_list_score = self.data_manager.get_skor_global_dimensi_as_list(self.anime_id)
        new_avg_personal = self.data_manager.hitung_skor_personal(user_id, self.anime_id)

        self.radar_container.content = self._build_radar(new_global_list_score, [0, 0, 0, 0, 0], new_avg_global, new_avg_personal)

        self.my_page.snack_bar = ft.SnackBar(ft.Text("Rating Berhasil Dihapus!"), bgcolor="green")
        self.my_page.snack_bar.open = True
        self.my_page.update()







    def _build_action_buttons(self):
        return ft.Row(
            spacing=10,
            controls=[
                ft.ElevatedButton(
                    content="Save Rating",
                    expand=True,
                    bgcolor="#F472B6", color="#FFFFFF",
                    height=46,
                    on_click=lambda _: self.save_rating(None),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        elevation=0,
                    )
                ),
                ft.OutlinedButton(
                    content="Delete Rating",
                    expand=True,
                    height=46,
                    on_click=lambda _: self.delete_rating(None),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        side=ft.BorderSide(1, "#E0DDE8"),
                        color="#666666",
                    )
                ),
            ]
        )
    def _build_synopsis(self):
        return self._section_card(
            "SYNOPSIS",
            ft.Text(
                self.detail_anime.get("synopsis", "No synopsis available."),
                size=13, color="#303030",
            )
        )
    
    def _muat_top_unrated(self, user_id):
        user_id = self.data_manager.baca_sesi()
        if not user_id: return ft.Container()

        self._cached_semua_anime = self.data_manager.get_semua_anime()
        semua_rating = self.data_manager._read_json(self.data_manager.ratings_file) or {}
        rating_user_ini = semua_rating.get(user_id, {})

        self._cached_anime_rated = []
        self._cached_anime_unrated = []
        self._cached_skor_user = {}

        for anime in self._cached_semua_anime:
            aid = anime.get("anime_id", "")
            if aid == self.anime_id:
                continue
            if aid in rating_user_ini:
                skor_dict = rating_user_ini[aid]
                sp = round(sum(skor_dict.values()) / len(skor_dict), 2) if skor_dict else 0
                self._cached_anime_rated.append((anime, sp))
                self._cached_skor_user[aid] = sp
            else:
                self._cached_anime_unrated.append(anime)

        self._unrated_row.controls.clear()
        unrated_sorted = sorted(
            self._cached_anime_unrated,
            key=lambda a: a.get("global_score", 0) or 0,
            reverse=True
        )

        for anime in unrated_sorted[:10]:
            sg = anime.get("global_score", 0) or 0
            self._unrated_row.controls.append(
                AnimeCardSmall(anime, sg, None,
                            on_click_callback=self.screen_manager.tampilkan_detail)
            )

        if not self._cached_anime_unrated:
            self._unrated_row.controls.append(
                ft.Text("You've rated all available anime!", color="#AAAAAA", size=12)
            )

        return self._section_card(
            "RECOMMENDED UNRATED",
            self._unrated_row,
        )


# ═══════════════════════════════════════════════════════════════
#  UI DETAIL — ft.Row utama yang menyatukan LeftPanel + RightPanel
# ═══════════════════════════════════════════════════════════════

class UIDetail(ft.Column):
    def __init__(self, page, data_manager, screen_manager, anime_id):
        self.my_page = page
        self.data_manager = data_manager
        self.screen_manager = screen_manager
        self.anime_id = anime_id
        self.user_id = data_manager.baca_sesi()
        self.detail_anime = self.data_manager.get_detail_anime(anime_id)

        # ── TOPBAR ──────────────────────────────────────────────────────────
        top_bar = ft.Container(
            content=ft.Row([
                ft.Row([                          # ← grup tombol di kiri
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.HOME_OUTLINED, color="#EC407A", size=14),
                            ft.Text("Home", color="#EC407A", size=11,
                                    weight=ft.FontWeight.W_600),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                        on_click=lambda e: self.screen_manager.tampilkan_home(),
                        style=ft.ButtonStyle(
                            side=ft.BorderSide(1.5, "#e8b4cb"),
                            shape=ft.RoundedRectangleBorder(radius=20),
                            padding=ft.padding.symmetric(horizontal=14, vertical=6),
                        ),
                    ),
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHEVRON_LEFT, color="#EC407A", size=14),
                            ft.Text("Back", color="#EC407A", size=11,
                                    weight=ft.FontWeight.W_600),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                        on_click=lambda e: self.screen_manager.kembali_ke_asal(),
                        style=ft.ButtonStyle(
                            side=ft.BorderSide(1.5, "#e8b4cb"),
                            shape=ft.RoundedRectangleBorder(radius=20),
                            padding=ft.padding.symmetric(horizontal=14, vertical=6),
                        ),
                    ),
                ], spacing=8),
                ft.Text("RadarAni — アニメ詳細", size=13,
                        weight=ft.FontWeight.BOLD, color="#1E1B2E"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            border=ft.border.only(bottom=ft.BorderSide(1, "#EDE0E8")),
            bgcolor="#FFFFFF",
        )

        # ── SIDEBAR (LeftPanel) ──────────────────────────────────────────────
        sidebar = ft.Container(
            width=300,
            expand=False,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                controls=[
                    LeftPanel(self.detail_anime, self.data_manager, self.screen_manager, self.anime_id),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=0,
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,     # ← dan ini

            ),
            padding=ft.padding.only(left=12, right=12, top=12, bottom=24),
            border=ft.border.only(right=ft.BorderSide(1, "#EDE0E8")),
            bgcolor="#FAFAFA",
        )

        # ── MAIN AREA (RightPanel) ───────────────────────────────────────────
        main_area = ft.Container(
            expand=True,
            content=ft.Column(
                controls=[
                    RightPanel(self.my_page, self.data_manager, self.screen_manager, self.anime_id),
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                spacing=0,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=12),
            bgcolor="#F4F3F8",
        )

        # ── LAYOUT UTAMA ─────────────────────────────────────────────────────
        layout = ft.Container(
            content=ft.Column([
                top_bar,
                ft.Row([
                    sidebar,
                    main_area,
                ], spacing=0, expand=True,
                   vertical_alignment=ft.CrossAxisAlignment.START),
            ], spacing=0, expand=True),
            bgcolor="#FFFFFF",
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=28,
                color=ft.Colors.with_opacity(0.10, "#EC407A")
            ),
            expand=True,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        super().__init__(
            expand=True,
            controls=[layout],
        )



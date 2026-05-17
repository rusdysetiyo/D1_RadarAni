import flet as ft
import flet.canvas as cv
import math
from src.ui.icons import _sakura_icon_svg
import random
import os
from src.config.theme import ThemeManager


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

# ═══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════
class AnimeCardSmall(ft.Container):
    def __init__(self, anime: dict, skor_global, skor_personal, theme, is_favorite=False, on_click_callback=None):
        super().__init__()
        self.anime = anime
        self.is_favorite = is_favorite
        self._theme = theme
        self._on_click_cb = on_click_callback

        self.width = 120
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=[self._theme["card"], self._theme["bg"]]
        )
        self.border = ft.Border.all(1, self._theme["border_color"])
        self.border_radius = ft.border_radius.only(top_left=15, bottom_right=15, top_right=4, bottom_left=4)
        self.clip_behavior = ft.ClipBehavior.ANTI_ALIAS
        self.margin = ft.padding.only(left=6, right=6, top=10, bottom=20)

        self.base_shadow = ft.BoxShadow(
            blur_radius=8,
            color=ft.Colors.with_opacity(0.08, self._theme["text_main"]),
            offset=ft.Offset(0, 4)
        )
        self.shadow = [self.base_shadow]

        self.on_click = lambda _: self._on_click_cb(anime.get("anime_id", "")) if on_click_callback else None
        self.on_hover = self._on_hover
        self.animate = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)
        self.rotate = ft.Rotate(angle=random.uniform(-0.015, 0.015))

        is_rated = skor_personal is not None

        pill_bg = self._theme["pill_rated"] if is_rated else ft.Colors.with_opacity(0.85, self._theme["text_muted"])
        pill_txt = "★ rated" if is_rated else "not rated"
        pill_color = self._theme["card"]

        self._status_pill = ft.Container(
            content=ft.Text(pill_txt, size=8, color=pill_color, weight=ft.FontWeight.W_800),
            bgcolor=pill_bg,
            border_radius=ft.border_radius.only(top_left=10, bottom_right=10),
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            top=6, right=6, opacity=1.0,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )

        self._fav_icon = ft.Container(
            content=ft.Image(src=_sakura_icon_svg(), width=22, height=22),
            top=-30, right=6, opacity=0,
            shadow=ft.BoxShadow(blur_radius=8, spread_radius=1, color="#80000000", offset=ft.Offset(0, 2)),
            animate_position=ft.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            animate_rotation=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            rotate=ft.Rotate(angle=-1)
        )

        genres = anime.get("genre", [])[:3]
        sg_str = (
            f"★ {skor_global:.1f}  ·  {anime.get('episodes', '?')} eps" if skor_global else f"{anime.get('episodes', '?')} eps")

        self._overlay = ft.Container(
            width=120, height=162,
            bgcolor=self._theme["overlay_bg"],
            border_radius=ft.border_radius.only(top_left=15, top_right=4),
            padding=8,
            content=ft.Column(
                controls=[
                    ft.Container(expand=True),
                    ft.Text(anime.get("title", ""), size=9, color="#FFFFFF", weight=ft.FontWeight.BOLD, max_lines=2),
                    ft.Text(sg_str, size=8, color=self._theme["overlay_text"]),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(g, size=7, color=self._theme["pill_text"], weight=ft.FontWeight.W_800),
                                bgcolor=ft.Colors.with_opacity(0.85, self._theme["pill_genre_bg"]),
                                border_radius=ft.border_radius.only(top_left=6, bottom_right=6),
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            ) for g in genres
                        ], spacing=3, run_spacing=2, wrap=True,
                    ),
                ], spacing=3,
            ),
            visible=False,
        )

        thumb = anime.get("cover_path", "")
        poster_path = os.path.abspath(os.path.join(ROOT_DIR, thumb)) if thumb else ""

        poster = ft.Container(
            width=120, height=162,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            border_radius=ft.border_radius.only(top_left=15, top_right=4),
            content=ft.Image(
                src=poster_path if (poster_path and os.path.exists(poster_path)) else "",
                width=120, height=162, fit="cover",
            ) if poster_path else ft.Icon(ft.Icons.PHOTO, color=self._theme["text_muted"])
        )

        sp_txt = f"you: {skor_personal:.1f}" if is_rated else "you: N/A"
        sp_col = self._theme["primary"] if is_rated else self._theme["text_muted"]

        info = ft.Container(
            padding=ft.padding.only(left=7, right=7, top=4, bottom=5),
            content=ft.Column(
                controls=[
                    ft.Text(
                        anime.get("title", "—"), size=9, color=self._theme["text_main"],
                        weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(f"★ {skor_global:.1f}" if skor_global else "★ —", size=8,
                                    color=self._theme["accent_star"], weight=ft.FontWeight.BOLD),
                            ft.Text("·", size=8, color=self._theme["border_color"]),
                            ft.Text(sp_txt, size=8, color=sp_col, weight=ft.FontWeight.BOLD),
                        ], spacing=3, alignment=ft.MainAxisAlignment.CENTER
                    ),
                ], spacing=2, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        self.content = ft.Column(
            controls=[
                ft.Stack(controls=[poster, self._overlay, self._status_pill, self._fav_icon], width=120, height=162),
                info,
            ], spacing=0,
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

            glow_shadow = ft.BoxShadow(
                blur_radius=25,
                spread_radius=1,
                color=ft.Colors.with_opacity(0.5, self._theme["primary"])
            )
            self.shadow = [glow_shadow]
        else:
            self._status_pill.opacity = 1.0
            self._fav_icon.top = -30
            self._fav_icon.opacity = 0
            self._fav_icon.rotate.angle = -1
            self.rotate = ft.Rotate(angle=0)

            self.shadow = [self.base_shadow]

        self.border = ft.Border.all(1.5 if is_hovered else 1,
                                    self._theme["card_hover_border"] if is_hovered else self._theme["border_color"])
        self.scale = 1.03 if is_hovered else 1.0
        self.update()

def build_radar_chart(global_scores, personal_scores, labels, theme, size=300):
    cx = cy = size / 2
    max_r = size / 2 - 40
    n = len(labels)
    grid_levels = 5
    shapes = []

    def petal_path(angle_deg, length, width_factor=0.46, notch_depth=0.11):
        rad = math.radians(angle_deg)
        rad_perp = math.radians(angle_deg + 90)

        w = length * width_factor

        notch_dist = length * 0.92
        notch_lx = cx + notch_dist * math.cos(rad) + w * 0.22 * math.cos(rad_perp)
        notch_ly = cy + notch_dist * math.sin(rad) + w * 0.22 * math.sin(rad_perp)
        notch_rx = cx + notch_dist * math.cos(rad) - w * 0.22 * math.cos(rad_perp)
        notch_ry = cy + notch_dist * math.sin(rad) - w * 0.22 * math.sin(rad_perp)

        indent_x = cx + (length - length * notch_depth) * math.cos(rad)
        indent_y = cy + (length - length * notch_depth) * math.sin(rad)

        c1x = cx + length * 0.50 * math.cos(rad) + w * 0.95 * math.cos(rad_perp)
        c1y = cy + length * 0.50 * math.sin(rad) + w * 0.95 * math.sin(rad_perp)
        c2x = notch_lx - length * 0.15 * math.cos(rad) + w * 0.45 * math.cos(rad_perp)
        c2y = notch_ly - length * 0.15 * math.sin(rad) + w * 0.45 * math.sin(rad_perp)

        c5x = cx + length * 0.50 * math.cos(rad) - w * 0.95 * math.cos(rad_perp)
        c5y = cy + length * 0.50 * math.sin(rad) - w * 0.95 * math.sin(rad_perp)
        c6x = notch_rx - length * 0.15 * math.cos(rad) - w * 0.45 * math.cos(rad_perp)
        c6y = notch_ry - length * 0.15 * math.sin(rad) - w * 0.45 * math.sin(rad_perp)

        ci1x = indent_x + w * 0.20 * math.cos(rad_perp)
        ci1y = indent_y + w * 0.20 * math.sin(rad_perp)
        ci2x = indent_x - w * 0.20 * math.cos(rad_perp)
        ci2y = indent_y - w * 0.20 * math.sin(rad_perp)

        return [
            cv.Path.MoveTo(cx, cy),
            cv.Path.CubicTo(c1x, c1y, c2x, c2y, notch_lx, notch_ly),
            cv.Path.CubicTo(ci1x, ci1y, ci2x, ci2y, notch_rx, notch_ry),
            cv.Path.CubicTo(c6x, c6y, c5x, c5y, cx, cy),
            cv.Path.Close(),
        ]

    # Grid rings (poligon)
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
            paint=ft.Paint(color=theme["radar_grid"], stroke_width=0.8, style=ft.PaintingStyle.STROKE)
        ))

    # Axis lines
    for i in range(n):
        angle = math.radians(-90 + i * 360 / n)
        shapes.append(ft.canvas.Path(
            elements=[
                ft.canvas.Path.MoveTo(cx, cy),
                ft.canvas.Path.LineTo(cx + max_r * math.cos(angle), cy + max_r * math.sin(angle)),
            ],
            paint=ft.Paint(color=theme["radar_grid"], stroke_width=0.8)
        ))

    # Global petals
    for i, score in enumerate(global_scores):
        angle_deg = -90 + i * 360 / n
        length = (score / 10) * max_r
        cmds = petal_path(angle_deg, length)

        shapes.append(ft.canvas.Path(
            elements=cmds,
            paint=ft.Paint(color=theme["radar_g_area"], style=ft.PaintingStyle.FILL)
        ))
        shapes.append(ft.canvas.Path(
            elements=cmds,
            paint=ft.Paint(color=theme["radar_g_border"], stroke_width=1.5, style=ft.PaintingStyle.STROKE)
        ))
        for frac in [0.65, 0.4]:
            sub_cmds = petal_path(angle_deg, length * frac, width_factor=0.28)
            shapes.append(ft.canvas.Path(
                elements=sub_cmds,
                paint=ft.Paint(color=theme["radar_g_area"], stroke_width=0.6, style=ft.PaintingStyle.STROKE)
            ))

    # Personal petals
    if any(s > 0 for s in personal_scores):
        for i, score in enumerate(personal_scores):
            angle_deg = -90 + i * 360 / n
            length = (score / 10) * max_r
            cmds = petal_path(angle_deg, length)

            shapes.append(ft.canvas.Path(
                elements=cmds,
                paint=ft.Paint(color=theme["radar_p_area"], style=ft.PaintingStyle.FILL)
            ))
            shapes.append(ft.canvas.Path(
                elements=cmds,
                paint=ft.Paint(color=theme["radar_p_border"], stroke_width=1.5, style=ft.PaintingStyle.STROKE)
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
            style=ft.TextStyle(size=11, color=theme["radar_labels"], weight=ft.FontWeight.W_500),
        ))

    # Center dot
    shapes.append(ft.canvas.Circle(cx, cy, 4, ft.Paint(color=theme["radar_grid"], style=ft.PaintingStyle.FILL)))

    return ft.Container(
        width=size,
        height=size,
        content=ft.canvas.Canvas(shapes=shapes, width=size, height=size)
    )

def score_card(value, theme, global_score=False):
    return ft.Container(
        width=150,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        bgcolor=theme["card"],
        border_radius=12,
        border=ft.border.all(1, theme["border_color"]),
        content=ft.Column(
            spacing=2,
            controls=[
                ft.Text("USER SCORE" if not global_score else "GLOBAL SCORE", size=10, color=theme["text_secondary"],
                        weight=ft.FontWeight.W_600),
                ft.Text(value, size=26, color=theme["primary"] if not global_score else theme["stat_gold"],
                        weight=ft.FontWeight.W_700),
                ft.Text("Your Rating" if not global_score else "Community Average Score", size=10,
                        color=theme["text_secondary"])
            ]
        )
    )


def tag(text, theme, meta=False):
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        bgcolor=theme["card"] if not meta else theme["primary"],
        border=ft.border.all(1, theme["border_color"]) if not meta else None,
        border_radius=20,
        content=ft.Text(
            text, size=11,
            color=theme["text_main"] if not meta else theme["card"],
            weight=ft.FontWeight.W_600
        )
    )


def legend_dot(color):
    return ft.Container(width=12, height=12, bgcolor=color, border_radius=6)


# ═══════════════════════════════════════════════════════════════
#  LEFT PANEL — poster, judul, tag, synopsis
# ═══════════════════════════════════════════════════════════════

class LeftPanel(ft.Container):
    def __init__(self, detail_anime: dict, data_manager, screen_manager, theme, anime_id):
        self.detail_anime = detail_anime
        self.data_manager = data_manager
        self.screen_manager = screen_manager
        self._theme = theme
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
                    self._build_poster(cover, self._theme),
                    ft.Text(self.detail_anime.get("title", "Anime Detail"), size=22,
                            weight=ft.FontWeight.W_800, color=self._theme["text_main"]),
                    self._build_genre_tags(gendres),
                    self._build_detail_info(),
                    ft.Container(height=24),
                ]
            )
        )

    def _build_poster(self, cover_path, theme):
        return ft.Container(
            width=268,
            height=320,
            border_radius=16,
            border=ft.border.all(2, theme["border_color"]),
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            content=ft.Image(src=cover_path, fit="cover"),
            
        )

    def _build_meta_tags(self, metaTags):
        return ft.Row(
            wrap=True, spacing=6, run_spacing=6,
            controls=[tag(tag_text, self._theme, meta=True) for tag_text in metaTags]
        )

    def _build_genre_tags(self, gendres):
        return ft.Row(
            wrap=True, spacing=6, run_spacing=6,
            controls=[tag(genre, self._theme) for genre in gendres]
        )
    
    def _build_fav_button(self):
        return ft.ElevatedButton(
            content=ft.Text("♥  Remove from Favorit" if self.is_fav else "♡  Add to Favorit"),
            on_click=self._toggle_favorit,
            style=ft.ButtonStyle(
                color=self._theme["card"],
                bgcolor=ft.Colors.RED_600 if self.is_fav else self._theme["primary"],
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.padding.symmetric(horizontal=20, vertical=12),
            ),
            width=268,  # Menyesuaikan lebar container (300 - padding 16*2)
        )
    
    def _toggle_favorit(self, e):
        self.is_fav = self.data_manager.toggle_favorit(self.user_id, self.anime_id)
        self.fav_button.content.value = "♥  Remove from Favorit" if self.is_fav else "♡  Add to Favorit"
        self.fav_button.style = ft.ButtonStyle(
            color=self._theme["card"],
            bgcolor=ft.Colors.RED_600 if self.is_fav else self._theme["primary"],
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
        )
        self.fav_button.update()

    def _section_card(self, title: str, content: ft.Control) -> ft.Container:
        return ft.Container(
            bgcolor=self._theme["card"],
            border=ft.border.all(1.5, self._theme["border_color"]),
            border_radius=12,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column([
                ft.Container(
                    content=ft.Text(title, size=11, weight=ft.FontWeight.W_800,
                                    color=self._theme["text_main"],
                                    style=ft.TextStyle(letter_spacing=1.1)),
                    bgcolor=self._theme["bg_secondary"],
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    border=ft.border.only(bottom=ft.BorderSide(1, self._theme["border_color"])),
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

        label_color = self._theme["text_secondary"]
        value_color = self._theme["text_main"]
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
                    ft.Divider(height=1, color=self._theme["border_color"]),
                    self.fav_button,
                ]
            )
        )


# ═══════════════════════════════════════════════════════════════
#  RIGHT PANEL — score, radar, dropdown, tombol
# ═══════════════════════════════════════════════════════════════

class RightPanel(ft.Container):
    def __init__(self, page: ft.Page, data_manager,screen_manager, theme, anime_id):
        self.my_page = page
        self.data_manager = data_manager
        self.screen_manager = screen_manager
        self._theme = theme
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
            content=self._build_radar(global_list_score, user_list_score, global_avg_score, user_avg_score, self._theme)
)       
        
        self._global_btn_ref = ft.Ref[ft.ElevatedButton]()
        self._personal_btn_ref = ft.Ref[ft.ElevatedButton]()

        super().__init__(
            expand=True,
            bgcolor=self._theme["card"],        # ← ganti jadi abu muda supaya card putih kontras
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
            bgcolor=self._theme["card"],
            border=ft.border.all(1.5, self._theme["border_color"]),
            border_radius=12,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column([
                # Header
                ft.Container(
                    content=ft.Text(title, size=11, weight=ft.FontWeight.W_800,
                                    color=self._theme["text_main"],
                                    style=ft.TextStyle(letter_spacing=1.1)),
                    bgcolor=self._theme["bg_secondary"],
                    padding=ft.padding.symmetric(horizontal=16, vertical=10),
                    border=ft.border.only(bottom=ft.BorderSide(1, self._theme["border_color"])),
                    width=float("inf"),
                ),
                # Body
                ft.Container(
                    content=content,
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                ),
            ], spacing=0, tight=True),
        )

    def _build_score_cards(self, global_score, user_score, theme):
        return ft.Row(
            spacing=12,
            controls=[
                score_card(str(global_score), self._theme, global_score=True),
                score_card(str(user_score), self._theme),
            ]
        )

    def _build_radar(self, global_scores, personal_scores, global_avg_score, user_avg_score, theme):
        self.score_cards_container = ft.Container(content=self._build_score_cards(global_avg_score, user_avg_score, theme))
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
                    controls=[build_radar_chart(global_scores, personal_scores, labels, theme)]
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
                    legend_dot(self._theme["radar_g_border"]),
                    ft.Text("Global", size=12, color=self._theme["text_secondary"])
                ]),
                ft.Row(spacing=6, controls=[
                    legend_dot(self._theme["radar_p_border"]),
                    ft.Text("Personal", size=12, color= self._theme["text_secondary"])
                ]),
            ]
        )

    def _build_popup_dropdown(self, label: str, prefill_val: str = "1"):
        # Simpan nilai terpilih
        selected = ft.Text(prefill_val, size=13, color=self._theme["text_main"])
        
        def on_selected(e):
            selected.value = e.control.data
            selected.update()
            # Simpan ke dropdown_controls via data attribute
            self.dropdown_controls[label] = e.control.data

        return ft.Column(
            expand=True,
            spacing=4,
            controls=[
                ft.Text(label, size=11, color=self._theme["text_main"],
                        weight=ft.FontWeight.W_500),
                ft.Container(
                    expand=True,
                    height=42,
                    bgcolor=self._theme["bg_secondary"],
                    border=ft.border.all(1, self._theme["border_color"]),
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                    alignment=ft.Alignment(0, 0),
                    content=ft.PopupMenuButton(
                        expand=True,
                        content=ft.Row([
                            selected,
                            ft.Icon(ft.Icons.ARROW_DROP_DOWN,
                                    color=self._theme["text_main"], size=18),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        items=[
                            ft.PopupMenuItem(
                                content=ft.Text(str(i), color=self._theme["text_main"], size=13),
                                data=str(i),
                                on_click=on_selected,
                            ) for i in range(1, 11)
                        ],
                        bgcolor=self._theme["bg_secondary"],   # ← warna popup menu
                    )
                )
            ]
        )

    def _build_dropdowns(self):
        self.dropdown_controls = {}
        categories = ["Plot", "Visual", "Audio", "Characterization", "Direction"]
        dropdown_list = []

        existing_scores = {}
        user_id = self.data_manager.baca_sesi()
        if user_id:
            raw = self.data_manager.get_rating_user_as_list(user_id, self.anime_id)
            if raw:
                keys = ["plot", "visual", "audio", "characterization", "direction"]
                existing_scores = {k: str(v) for k, v in zip(keys, raw)}

        for cat in categories:
            prefill_val = existing_scores.get(cat.lower(), "1")
            self.dropdown_controls[cat] = prefill_val   # ← nilai awal
            dropdown_list.append(self._build_popup_dropdown(cat, prefill_val))

        return ft.Row(expand=True, spacing=8, controls=dropdown_list)

    def save_rating(self, e):
        try:
            user_scores = {}
            for category, val in self.dropdown_controls.items():
                user_scores[category.lower()] = int(val)

            user_id = self.data_manager.baca_sesi()
            self.data_manager.simpan_rating(user_id, self.anime_id, user_scores)

            new_avg_global = self.data_manager.hitung_skor_global(self.anime_id)
            new_avg_personal = self.data_manager.hitung_skor_personal(user_id, self.anime_id)
            new_list_score = list(user_scores.values())
            new_global_list_score = self.data_manager.get_skor_global_dimensi_as_list(self.anime_id)

            # Rebuild score_cards_container dulu sebelum radar di-rebuild
            self.radar_container.content = self._build_radar(new_global_list_score, new_list_score, new_avg_global, new_avg_personal, self._theme)

            self.my_page.update()
            self._show_snackbar("Rating Berhasil Diperbarui!", self._theme["success"])

        except Exception as ex:
            self._show_snackbar(f"Error saving rating: {str(ex)}", self._theme["error"])
            
    def delete_rating(self, e):
        user_id = self.data_manager.baca_sesi()
        self.data_manager.hapus_rating(user_id, self.anime_id)

        new_avg_global = self.data_manager.hitung_skor_global(self.anime_id)
        new_global_list_score = self.data_manager.get_skor_global_dimensi_as_list(self.anime_id)
        new_avg_personal = self.data_manager.hitung_skor_personal(user_id, self.anime_id)

        self.radar_container.content = self._build_radar(new_global_list_score, [0, 0, 0, 0, 0], new_avg_global, new_avg_personal, self._theme)

        self.my_page.update()
        self._show_snackbar("Rating Berhasil Diperbarui!", self._theme["success"])

    def _build_action_buttons(self):
        return ft.Row(
            spacing=10,
            controls=[
                ft.ElevatedButton(
                    content=ft.Text("Save Rating", color=self._theme["card"]),
                    expand=True,
                    bgcolor=self._theme["primary"],
                    height=46,
                    on_click=lambda _: self.save_rating(None),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        elevation=0,
                    )
                ),
                ft.OutlinedButton(
                    content=ft.Text("Delete Rating", color=self._theme["text_secondary"]),
                    expand=True,
                    height=46,
                    on_click=lambda _: self.delete_rating(None),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        side=ft.BorderSide(1, self._theme["border_color"]),
                    )
                ),
            ]
        )
    def _build_synopsis(self):
        return self._section_card(
            "SYNOPSIS",
            ft.Text(
                self.detail_anime.get("synopsis", "No synopsis available."),
                size=16, color=self._theme["text_secondary"],
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
                AnimeCardSmall(anime, sg, None,self._theme,
                            on_click_callback=self.screen_manager.tampilkan_detail)
            )

        if not self._cached_anime_unrated:
            self._unrated_row.controls.append(
                ft.Text("You've rated all available anime!", color=self._theme["text_muted"], size=12)
            )

        return self._section_card(
            "RECOMMENDED UNRATED",
            self._unrated_row,
        )
    
    def _show_snackbar(self, pesan: str, warna: str):
        snack = ft.SnackBar(content=ft.Text(pesan), bgcolor=warna)
        self.my_page.overlay.append(snack)
        snack.open = True
        self.my_page.update()


# ═══════════════════════════════════════════════════════════════
#  UI DETAIL — ft.Row utama yang menyatukan LeftPanel + RightPanel
# ═══════════════════════════════════════════════════════════════

class UIDetail(ft.Column):
    def __init__(self, page, data_manager, auth_manager, screen_manager, theme, anime_id):
        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager
        self._theme = theme
        self.anime_id = anime_id
        self.user_id = data_manager.baca_sesi()
        self.detail_anime = self.data_manager.get_detail_anime(anime_id)

        self.Right_panel = RightPanel(self.my_page, self.data_manager, self.screen_manager, self._theme, self.anime_id)

        # ── TOPBAR ──────────────────────────────────────────────────────────
        top_bar = ft.Container(
            content=ft.Row([
                ft.Row([                          # ← grup tombol di kiri
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.HOME_OUTLINED, color=self._theme["primary"], size=14),
                            ft.Text("Home", color=self._theme["primary"], size=11,
                                    weight=ft.FontWeight.W_600),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                        on_click=lambda e: self.screen_manager.tampilkan_home(),
                        style=ft.ButtonStyle(
                            side=ft.BorderSide(1.5,self._theme["primary_light"]),
                            shape=ft.RoundedRectangleBorder(radius=20),
                            padding=ft.padding.symmetric(horizontal=14, vertical=6),
                        ),
                    ),
                    ft.OutlinedButton(
                        content=ft.Row([
                            ft.Icon(ft.Icons.CHEVRON_LEFT, self._theme["primary"], size=14),
                            ft.Text("Back", color=self._theme["primary"], size=11,
                                    weight=ft.FontWeight.W_600),
                        ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                        on_click=lambda e: self.screen_manager.kembali_ke_asal(),
                        style=ft.ButtonStyle(
                            side=ft.BorderSide(1.5, self._theme["primary_light"]),
                            shape=ft.RoundedRectangleBorder(radius=20),
                            padding=ft.padding.symmetric(horizontal=14, vertical=6),
                        ),
                    ),
                ], spacing=8),
                ft.Text("RadarAni — アニメ詳細", size=13,
                        weight=ft.FontWeight.BOLD, color=self._theme["primary"]),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            border=ft.border.only(bottom=ft.BorderSide(1, self._theme["border_color"])),
            bgcolor=self._theme["card"],
        )

        # ── SIDEBAR (LeftPanel) ──────────────────────────────────────────────
        sidebar = ft.Container(
            width=300,
            expand=False,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                controls=[
                    LeftPanel(self.detail_anime, self.data_manager, self.screen_manager, self._theme, self.anime_id),
                ],
                scroll=ft.ScrollMode.AUTO,
                spacing=0,
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,     # ← dan ini

            ),
            padding=ft.padding.only(left=12, right=12, top=12, bottom=24),
            border=ft.border.only(right=ft.BorderSide(1, self._theme["border_color"])),
            bgcolor=self._theme["bg"],
        )

        # ── MAIN AREA (RightPanel) ───────────────────────────────────────────
        main_area = ft.Container(
            expand=True,
            content=ft.Column(
                controls=[
                    self.Right_panel,
                ],
                scroll=ft.ScrollMode.AUTO,
                expand=True,
                spacing=0,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=12),
            bgcolor=self._theme["bg"],
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
            bgcolor=self._theme["card"],
            border_radius=16,
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=28,
                color=ft.Colors.with_opacity(0.10, self._theme["primary"])
            ),
            expand=True,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )



        super().__init__(
            expand=True,
            controls=[layout],
        )
    
    def save_rating(self, e):
        self.Right_panel.save_rating(e)

    def delete_rating(self, e):
        self.Right_panel.delete_rating(e)
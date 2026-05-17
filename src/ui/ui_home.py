import flet as ft
import random
import asyncio
import os
from src.ui.icons import _sakura_icon_svg

# IMPORT TEMA
from src.config.theme import ThemeManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

class HujanSakura:
    def __init__(self, target_container, theme):
        self.target = target_container
        self.petals = []
        self.is_running = True

        for _ in range(15):
            petal = ft.Container(
                width=10, height=14,
                bgcolor=random.choice(theme["petal_colors"]),
                border_radius=ft.border_radius.only(top_left=15, bottom_right=15, top_right=2, bottom_left=2),
                opacity=0.6,
                left=random.randint(0, 1000),
                top=-50,
                rotate=ft.Rotate(angle=0),
            )
            self.petals.append(petal)
            self.target.controls.append(petal)

    async def turun(self):
        await asyncio.sleep(1.5)
        while self.is_running:
            try:
                if not self.target.page:
                    self.is_running = False
                    break
                for petal in self.petals:
                    petal.animate_position = ft.Animation(0)
                    petal.animate_rotation = ft.Animation(0)
                    petal.top = -50
                    petal.left = random.randint(0, 1000)
                    petal.rotate.angle = random.uniform(0, 3.14)
                self.target.update()
                await asyncio.sleep(0.1)
                if not self.target.page:
                    self.is_running = False
                    break
                for petal in self.petals:
                    durasi = random.randint(6000, 9000)
                    petal.animate_position = ft.Animation(durasi, ft.AnimationCurve.LINEAR)
                    petal.animate_rotation = ft.Animation(durasi, ft.AnimationCurve.LINEAR)
                    petal.top = 1000
                    petal.left += random.randint(-200, 200)
                    petal.rotate.angle += random.uniform(3, 7)
                self.target.update()
                await asyncio.sleep(7)
            except Exception as e:
                if "Control must be added" in str(e):
                    self.is_running = False
                    break
                await asyncio.sleep(2)

def _stat_pill(kanji, label, warna) -> ft.Container:
    return ft.Container(
        content=ft.Row([
            ft.Text(kanji, size=14, font_family="Mofuji04", color=warna),
            ft.Text(label, size=8, font_family="Hitchcut", color=warna, weight=ft.FontWeight.BOLD),
            ft.Text("—", size=10, font_family="Hitchcut", color=warna, weight=ft.FontWeight.BOLD),
        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[ft.Colors.with_opacity(0.2, warna), ft.Colors.with_opacity(0.05, warna)],
        ),
        border=ft.Border.all(1, ft.Colors.with_opacity(0.4, warna)),
        border_radius=ft.border_radius.only(top_left=12, bottom_right=12, top_right=3, bottom_left=3),
        padding=ft.padding.symmetric(horizontal=12, vertical=5),
    )

def _section_header(title: str, theme, on_lihat_semua=None) -> ft.Container:
    return ft.Container(
        padding=ft.padding.only(left=20, right=20, top=20, bottom=8),
        content=ft.Row(
            controls=[
                ft.Container(width=4, height=16, bgcolor=theme["primary"], border_radius=4),
                ft.Text(title, font_family="Soopafresh", size=18, color=theme["text_main"]),
                ft.Container(expand=True),
                ft.TextButton(
                    "View All →",
                    style=ft.ButtonStyle(
                        color={ft.ControlState.DEFAULT: theme["primary"]},
                        padding=ft.padding.all(0),
                    ),
                    on_click=on_lihat_semua,
                ) if on_lihat_semua else ft.Container(),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )


class AnimeCardSmall(ft.Container):
    def __init__(self, anime: dict, skor_global, skor_personal, theme, is_favorite=False, on_click_callback=None):
        super().__init__()
        self.anime = anime
        self.is_favorite = is_favorite
        self.theme = theme
        self._on_click_cb = on_click_callback

        self.width = 120
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=[self.theme["card"], self.theme["bg"]]
        )
        self.border = ft.Border.all(1, self.theme["border_color"])
        self.border_radius = ft.border_radius.only(top_left=15, bottom_right=15, top_right=4, bottom_left=4)
        self.clip_behavior = ft.ClipBehavior.ANTI_ALIAS
        self.margin = ft.padding.only(left=6, right=6, top=10, bottom=20)

        self.base_shadow = ft.BoxShadow(
            blur_radius=8,
            color=ft.Colors.with_opacity(0.08, self.theme["text_main"]),
            offset=ft.Offset(0, 4)
        )
        self.shadow = [self.base_shadow]

        self.on_click = lambda _: self._on_click_cb(anime.get("anime_id", "")) if on_click_callback else None
        self.on_hover = self._on_hover
        self.animate = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)
        self.rotate = ft.Rotate(angle=random.uniform(-0.015, 0.015))

        is_rated = skor_personal is not None

        pill_bg = self.theme["pill_rated"] if is_rated else ft.Colors.with_opacity(0.85, self.theme["text_muted"])
        pill_txt = "★ rated" if is_rated else "not rated"
        pill_color = self.theme["card"]

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
            bgcolor=self.theme["overlay_bg"],
            border_radius=ft.border_radius.only(top_left=15, top_right=4),
            padding=8,
            content=ft.Column(
                controls=[
                    ft.Container(expand=True),
                    ft.Text(anime.get("title", ""), size=9, color="#FFFFFF", weight=ft.FontWeight.BOLD, max_lines=2),
                    ft.Text(sg_str, size=8, color=self.theme["overlay_text"]),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(g, size=7, color=self.theme["pill_text"], weight=ft.FontWeight.W_800),
                                bgcolor=ft.Colors.with_opacity(0.85, self.theme["pill_genre_bg"]),
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
            ) if poster_path else ft.Icon(ft.Icons.PHOTO, color=self.theme["text_muted"])
        )

        sp_txt = f"you: {skor_personal:.1f}" if is_rated else "you: N/A"
        sp_col = self.theme["primary"] if is_rated else self.theme["text_muted"]

        info = ft.Container(
            padding=ft.padding.only(left=7, right=7, top=4, bottom=5),
            content=ft.Column(
                controls=[
                    ft.Text(
                        anime.get("title", "—"), size=9, color=self.theme["text_main"],
                        weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(f"★ {skor_global:.1f}" if skor_global else "★ —", size=8,
                                    color=self.theme["accent_star"], weight=ft.FontWeight.BOLD),
                            ft.Text("·", size=8, color=self.theme["border_color"]),
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
                color=ft.Colors.with_opacity(0.5, self.theme["primary"])
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
                                    self.theme["card_hover_border"] if is_hovered else self.theme["border_color"])
        self.scale = 1.03 if is_hovered else 1.0
        self.update()

def _nav_item(kanji, label, style, on_click):
    return ft.TextButton(
        content=ft.Row(
            controls=[
                ft.Text(kanji, font_family="DotGothic16", size=16, weight=ft.FontWeight.BOLD, width=28, text_align=ft.TextAlign.CENTER),
                ft.Text(label, size=13, weight=ft.FontWeight.W_500),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ), style=style, width=216, on_click=on_click,
    )

def _sidebar(screen_manager, auth_manager, toggle_fn, theme, halaman_aktif="home"):
    nav_s = ft.ButtonStyle(
        color={ft.ControlState.DEFAULT: theme["text_main"]},
        bgcolor={ft.ControlState.HOVERED: theme["bg_secondary"], ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
        shape=ft.RoundedRectangleBorder(radius=10), padding=ft.padding.symmetric(horizontal=16, vertical=10), alignment=ft.Alignment(-1, 0),
    )
    active_nav_s = ft.ButtonStyle(
        color={ft.ControlState.DEFAULT: theme["primary"]},
        bgcolor={ft.ControlState.DEFAULT: theme["primary_light"]},
        shape=ft.RoundedRectangleBorder(radius=10), padding=ft.padding.symmetric(horizontal=16, vertical=10), alignment=ft.Alignment(-1, 0),
    )
    danger_s = ft.ButtonStyle(
        color={ft.ControlState.DEFAULT: theme["text_secondary"]},
        bgcolor={ft.ControlState.HOVERED: theme["bg_secondary"], ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
        shape=ft.RoundedRectangleBorder(radius=8), padding=ft.padding.symmetric(horizontal=14, vertical=8), alignment=ft.Alignment(-1, 0),
    )

    return ft.Container(
        width=0, bgcolor=None,
        content=ft.Container(
            width=240, expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=[theme["bg_secondary"], theme["bg"]],
            ),
            border=ft.Border(right=ft.BorderSide(1, theme["border_color"])),
            padding=ft.padding.only(left=12, right=12, top=24, bottom=24),
            content=ft.Column(
                controls=[
                    ft.Row(
                        [ft.IconButton(ft.Icons.CHEVRON_LEFT, icon_color=theme["primary"], icon_size=20, on_click=toggle_fn)],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    ft.Container(height=8),
                    _nav_item("ホ", "Home", active_nav_s if halaman_aktif == "home" else nav_s, lambda _: screen_manager.tampilkan_home()),
                    _nav_item("覧", "Anime List", active_nav_s if halaman_aktif == "katalog" else nav_s, lambda _: screen_manager.tampilkan_katalog()),
                    _nav_item("追", "Add Anime", active_nav_s if halaman_aktif == "scraping" else nav_s, lambda _: screen_manager.tampilkan_scraping()),
                    _nav_item("析", "Analytics", active_nav_s if halaman_aktif == "analytics" else nav_s, lambda _: screen_manager.tampilkan_analytics()),
                    _nav_item("人", "Profile", active_nav_s if halaman_aktif == "profil" else nav_s, lambda _: screen_manager.tampilkan_profil()),
                    ft.Container(expand=True),
                    ft.Divider(color=theme["border_color"], height=1, thickness=1),
                    ft.Container(height=4),
                    ft.TextButton(
                        content=ft.Row(
                            controls=[
                                ft.Text("出", font_family="DotGothic16", size=16, weight=ft.FontWeight.BOLD, width=28, text_align=ft.TextAlign.CENTER),
                                ft.Text("Log Out", size=13),
                            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ), style=danger_s, width=216,
                        on_click=lambda _: (auth_manager.logout(), screen_manager.tampilkan_login()),
                    ),
                ], spacing=2, expand=True,
            ),
        ),
        animate_size=ft.Animation(duration=280, curve=ft.AnimationCurve.EASE_OUT),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )

class UIHome(ft.Row):
    def __init__(self, page, data_manager, auth_manager, screen_manager, theme):
        super().__init__()
        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager
        self._sidebar_open = False
        self.current_theme = ThemeManager.get_theme(self.screen_manager.tema_aktif)
        self.theme = theme

        self.expand = True
        self.spacing = 0

        self._sidebar_widget = _sidebar(
            screen_manager, auth_manager,
            self._toggle_sidebar, self.current_theme, halaman_aktif="home"
        )

        # FITUR UJI COBA THEME SEMENTARA (Akan dipindah ke profile nanti)
        def on_theme_selected(e):
            pilihan = e.control.data
            theme_dialog.open = False
            self.my_page.update()
            self.screen_manager.tampilkan_home(pilihan_tema=pilihan)

        def _bikin_buletan(key_tema, warna_hex):
            return ft.Container(
                width=40, height=40,
                bgcolor=warna_hex,
                shape=ft.BoxShape.CIRCLE,
                data=key_tema,
                on_click=on_theme_selected
            )

        swatches_row = ft.Row(
            controls=[
                _bikin_buletan("1", "#E8CEDB"),
                _bikin_buletan("2", "#C3D3B4"),
                _bikin_buletan("3", "#121212"),
                _bikin_buletan("4", "#3B82F6"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15
        )

        theme_dialog = ft.AlertDialog(
            title=ft.Text("Select Theme", size=16, weight=ft.FontWeight.BOLD, color=self.current_theme["text_main"], text_align=ft.TextAlign.CENTER),
            content=ft.Container(content=swatches_row, padding=ft.padding.symmetric(vertical=10)),
            bgcolor=self.current_theme["card"],
            shape=ft.RoundedRectangleBorder(radius=16),
        )

        def buka_dialog_tema(e):
            if theme_dialog not in self.my_page.overlay:
                self.my_page.overlay.append(theme_dialog)
            theme_dialog.open = True
            self.my_page.update()

        btn_theme_picker = ft.IconButton(
            icon=ft.Icons.PALETTE_OUTLINED,
            icon_color=self.current_theme["text_main"],
            tooltip="Change Theme",
            on_click=buka_dialog_tema
        )

        topbar = ft.Container(
            padding=ft.padding.symmetric(horizontal=16), height=55,
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            bgcolor=ft.Colors.with_opacity(0.8, self.current_theme["bg"]),
            shadow=ft.BoxShadow(blur_radius=15, color="#15000000", offset=ft.Offset(0, 4)),
            content=ft.Row(
                controls=[
                    ft.IconButton(ft.Icons.MENU, icon_color=self.current_theme["primary"], on_click=self._toggle_sidebar, tooltip="Menu"),
                    ft.Column(
                        [
                            ft.Row(
                                spacing=0,
                                controls=[
                                    ft.Text("R", font_family="Hitchcut", size=24, color=self.current_theme["logo_1"]),
                                    ft.Text("a", font_family="Hitchcut", size=24, color=self.current_theme["logo_2"]),
                                    ft.Text("d", font_family="Hitchcut", size=24, color=self.current_theme["logo_1"]),
                                    ft.Text("a", font_family="Hitchcut", size=24, color=self.current_theme["logo_2"]),
                                    ft.Text("r", font_family="Hitchcut", size=24, color=self.current_theme["logo_1"]),
                                    ft.Text("A", font_family="Hitchcut", size=24, color=self.current_theme["logo_2"]),
                                    ft.Text("n", font_family="Hitchcut", size=24, color=self.current_theme["logo_1"]),
                                    ft.Text("i", font_family="Hitchcut", size=24, color=self.current_theme["logo_2"]),
                                ]
                            ),
                            ft.Text("レーダアニ", font_family="Mofuji04", size=10, color=self.current_theme["text_muted"]),
                        ], spacing=0, tight=True,
                    ),
                    ft.Container(expand=True),
                    btn_theme_picker,
                    ft.IconButton(ft.Icons.ACCOUNT_CIRCLE, icon_color=self.current_theme["text_muted"], tooltip="Profile", on_click=lambda _: self.screen_manager.tampilkan_profil())
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        user_id = self.auth_manager.get_user_aktif()
        user_data = self.data_manager.get_user_by_id(user_id)
        username = user_data.get("username", "User") if user_data else "User"

        self._stat_rated = _stat_pill("評", "RATED", self.current_theme["pill_rated"])
        self._stat_unrated = _stat_pill("未", "UNRATED", self.current_theme["pill_unrated"])
        self._stat_avg = _stat_pill("均", "AVG", self.current_theme["pill_avg"])
        self._stat_dim = _stat_pill("極", "TOP", self.current_theme["pill_top"])

        self._rec_title = ft.Text(
            "—", size=28,
            color="#FFFFFF",
            weight=ft.FontWeight.BOLD,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        self._rec_reason = ft.Text(
            "Based on your top dimension",
            size=12, color="#CCFFFFFF",
        )

        self._rec_synopsis = ft.Text(
            "", size=12, color="#CCCCCC", max_lines=3, overflow=ft.TextOverflow.ELLIPSIS
        )
        self._rec_anime_id = None

        self._rec_image = ft.Image(src="", width=36, height=50, fit="cover", visible=False)

        self._rec_image_container = ft.Image(
            src="",
            width=float("inf"),
            height=340,
            fit=ft.BoxFit.COVER,
            expand=True,
        )

        def banner_hover(e):
            is_hover = str(e.data).lower() == "true"
            e.control.scale = 1.01 if is_hover else 1.0
            e.control.update()

        rec_banner = ft.Container(
            height=340,
            border_radius=16,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            on_hover=banner_hover,
            animate=ft.Animation(duration=250, curve=ft.AnimationCurve.EASE_OUT),
            scale=1.0,
            shadow=ft.BoxShadow(
                spread_radius=0, blur_radius=24,
                color="#22000000", offset=ft.Offset(0, 6),
            ),
            content=ft.Stack(
                expand=True,
                controls=[
                    # Layer 1: Gambar ditarik Full (Burek gapapa, ntar ditutup gradien)
                    self._rec_image_container,

                    # Layer 2: Overlay Gelap tipis di seluruh gambar biar bureknya tersamarkan
                    ft.Container(
                        expand=True,
                        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                    ),

                    # Layer 3: Gradient HITAM PEKAT dari Kiri ke Kanan (Anti-Kamuflase)
                    ft.Container(
                        expand=True,
                        gradient=ft.LinearGradient(
                            begin=ft.Alignment(-1.0, 0),  # Kiri mentok
                            end=ft.Alignment(1.0, 0),  # Kanan mentok
                            colors=[
                                "#F2000000",  # Hitam 95% nutupin kiri banget buat teks
                                "#B3000000",  # Hitam 70%
                                "#4D000000",  # Hitam 30%
                                ft.Colors.TRANSPARENT,  # Kanan bolong buat liat gambar
                            ],
                            stops=[0.0, 0.45, 0.8, 1.0],
                        ),
                    ),

                    # Layer 4: Konten Teks di Kiri
                    ft.Container(
                        expand=True,
                        padding=ft.padding.only(left=50, right=50, top=0, bottom=0),
                        alignment=ft.Alignment.CENTER_LEFT,
                        content=ft.Column(
                            width=600,
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.START,
                            controls=[
                                # Label kecil
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Container(width=3, height=14, bgcolor=self.current_theme["primary"],
                                                         border_radius=2),
                                            ft.Text("RECOMMENDED FOR YOU", size=10, color=self.current_theme["primary"],
                                                    weight=ft.FontWeight.W_800),
                                        ], spacing=6,
                                    ),
                                ),
                                ft.Container(height=8),

                                # Judul (Pasti putih)
                                self._rec_title,
                                ft.Container(height=4),

                                # Alasan (Pasti putih pudar)
                                self._rec_reason,
                                ft.Container(height=12),

                                # Sinopsis
                                self._rec_synopsis,
                                ft.Container(height=24),

                                # Tombol
                                ft.ElevatedButton(
                                    content=ft.Row(
                                        controls=[
                                            ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=20,
                                                    color=self.current_theme["bg"]),
                                            ft.Text("View Details", size=14, weight=ft.FontWeight.W_700,
                                                    color=self.current_theme["bg"]),
                                        ], spacing=6, tight=True,
                                    ),
                                    style=ft.ButtonStyle(
                                        bgcolor={
                                            ft.ControlState.DEFAULT: self.current_theme["primary"],
                                            ft.ControlState.HOVERED: ft.Colors.WHITE
                                        },
                                        shape=ft.RoundedRectangleBorder(radius=6),
                                        padding=ft.padding.symmetric(horizontal=24, vertical=14),
                                        elevation=0,
                                    ),
                                    on_click=lambda _: self._klik_rekomendasi(),
                                ),
                            ],
                            spacing=0,
                        ),
                    ),
                ],
            ),
        )

        header = ft.Container(
            padding=ft.padding.only(left=20, right=20, top=14, bottom=12),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Image(src=_sakura_icon_svg(), width=24, height=24, fit="contain"),
                            ft.Text(f"Konnichiwa, {username}!", size=18, color=self.current_theme["text_main"], weight=ft.FontWeight.BOLD),
                        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8
                    ),
                    ft.Row(controls=[self._stat_rated, self._stat_unrated, self._stat_avg, self._stat_dim], spacing=6),
                    rec_banner,
                ], spacing=10,
            ),
        )

        self.daftar_baris_animasi = []

        def animasikan_baris(e, baris_terpilih):
            is_hover = str(e.data).lower() == "true"
            for b in self.daftar_baris_animasi:
                if is_hover:
                    if b == baris_terpilih:
                        b.opacity = 1.0; b.scale = 1.02
                    else:
                        b.opacity = 0.4; b.scale = 0.95
                else:
                    b.opacity = 1.0; b.scale = 1.0
                b.update()

        self._trending_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=14)
        trending_section = ft.Container(
            padding=ft.padding.only(top=10),
            content=ft.Column(
                controls=[
                    _section_header("What Everyone's Watching", self.current_theme, on_lihat_semua=lambda _: self.screen_manager.tampilkan_katalog(filter_kategori="trending")),
                    ft.Container(content=self._trending_row, padding=ft.padding.only(left=24, right=24, top=5, bottom=15)),
                ], spacing=0,
            ), opacity=1.0, animate_opacity=300, scale=1.0, animate_scale=300,
        )
        trending_section.on_hover = lambda e: animasikan_baris(e, trending_section)
        self.daftar_baris_animasi.append(trending_section)

        self._recent_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=14)
        recent_section = ft.Container(
            padding=ft.padding.only(top=10),
            content=ft.Column(
                controls=[
                    _section_header("Your Latest Picks", self.current_theme, on_lihat_semua=lambda _: self.screen_manager.tampilkan_katalog(filter_kategori="rated")),
                    ft.Container(content=self._recent_row, padding=ft.padding.only(left=24, right=24, top=5, bottom=15)),
                ], spacing=0,
            ), opacity=1.0, animate_opacity=300, scale=1.0, animate_scale=300,
        )
        recent_section.on_hover = lambda e: animasikan_baris(e, recent_section)
        self.daftar_baris_animasi.append(recent_section)

        self._unrated_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=14)
        unrated_section = ft.Container(
            padding=ft.padding.only(top=10),
            content=ft.Column(
                controls=[
                    _section_header("Ready for Your Review", self.current_theme, on_lihat_semua=lambda _: self.screen_manager.tampilkan_katalog(filter_kategori="unrated")),
                    ft.Container(content=self._unrated_row, padding=ft.padding.only(left=24, right=24, top=5, bottom=15)),
                ], spacing=0,
            ), opacity=1.0, animate_opacity=300, scale=1.0, animate_scale=300, margin=ft.margin.only(bottom=30),
        )
        unrated_section.on_hover = lambda e: animasikan_baris(e, unrated_section)
        self.daftar_baris_animasi.append(unrated_section)

        self.main_scroll = ft.Column(
            controls=[header, trending_section, recent_section, unrated_section],
            scroll=ft.ScrollMode.AUTO, expand=True, spacing=0,
        )

        self._main_col = ft.Column(
            controls=[
                topbar,
                self.main_scroll,
            ], spacing=0, expand=True,
        )

        _hujan_stack = ft.Stack(expand=True)
        wadah_sakura = ft.TransparentPointer(_hujan_stack, expand=True)

        area_utama = ft.Stack(
            controls=[
                ft.Container(
                    content=self._main_col, left=0, right=0, top=0, bottom=0,
                    bgcolor=self.current_theme["bg"] # Pake warna BG tema
                ),
                wadah_sakura,
            ], expand=True,
        )

        self.controls = [self._sidebar_widget, area_utama]

        self.efek_sakura = HujanSakura(_hujan_stack, self.current_theme)
        self.my_page.run_task(self.efek_sakura.turun)

    # ... Sisa Method (_muat_sections, _perbarui_stats, _muat_rekomendasi, _muat_recent, dll)
    # BIARKAN SAMA PERSIS KAYA KODE ASLI LU, HANYA GANTI PARAMETER PAS MANGGIL AnimeCardSmall

    async def _muat_sections(self):
        user_id = self.data_manager.baca_sesi()
        if not user_id: return

        self._cached_semua_anime = self.data_manager.get_semua_anime()
        semua_rating = self.data_manager._read_json(self.data_manager.ratings_file) or {}
        rating_user_ini = semua_rating.get(user_id, {})

        self._cached_anime_rated = []
        self._cached_anime_unrated = []
        self._cached_skor_user = {}

        for i, anime in enumerate(self._cached_semua_anime):
            aid = anime.get("anime_id", "")

            if aid in rating_user_ini:
                skor_dict = rating_user_ini[aid]
                sp = round(sum(skor_dict.values()) / len(skor_dict), 2) if skor_dict else 0
                self._cached_anime_rated.append((anime, sp))
                self._cached_skor_user[aid] = sp
            else:
                self._cached_anime_unrated.append(anime)

            if i % 50 == 0:
                await asyncio.sleep(0)

        await asyncio.sleep(0.01)
        self._perbarui_stats(user_id)

        await asyncio.sleep(0.01)
        self._muat_rekomendasi(user_id)

        await asyncio.sleep(0.01)
        self._muat_trending(user_id)

        await asyncio.sleep(0.01)
        self._muat_recent(user_id)

        await asyncio.sleep(0.01)
        self._muat_top_unrated(user_id)

        try:
            if hasattr(self, '_trending_row'): self._trending_row.update()
            if hasattr(self, '_recent_row'): self._recent_row.update()
            if hasattr(self, '_unrated_row'): self._unrated_row.update()
            self.update()
        except Exception as err:
            print(f"Error pas update Home: {err}")

    def _perbarui_stats(self, user_id):
        if not user_id: return
        rated = len(self._cached_anime_rated)
        unrated = len(self._cached_anime_unrated)
        user_data = self.data_manager.get_user_by_id(user_id) or {}
        avg_list = user_data.get("average_dimensions", [0.0, 0.0, 0.0, 0.0, 0.0])
        urutan_dimensi = ["plot", "visual", "audio", "characterization", "direction"]
        avg_dim = {urutan_dimensi[i]: avg_list[i] for i in range(5) if avg_list[i] > 0}
        top_dim = max(avg_dim, key=avg_dim.get).capitalize() if avg_dim else "—"
        scores = [sp for _, sp in self._cached_anime_rated]
        avg_val = f"{sum(scores) / len(scores):.1f}" if scores else "—"

        self._stat_rated.content.controls[2].value = str(rated)
        self._stat_unrated.content.controls[2].value = str(unrated)
        self._stat_avg.content.controls[2].value = str(avg_val)
        self._stat_dim.content.controls[2].value = str(top_dim)
        self.update()

    def _muat_rekomendasi(self, user_id):
        if not user_id: return
        MIN_RATING = 3
        jumlah_rated = len(self._cached_anime_rated) if hasattr(self, '_cached_anime_rated') else 0

        if jumlah_rated == 0:
            self._rec_title.value = "Start rating to unlock recommendations."
            self._rec_reason.value = "Rate your first anime to begin."
            self._rec_image.visible = False
            self.update(); return

        if jumlah_rated < MIN_RATING:
            sisa = MIN_RATING - jumlah_rated
            progress = "●" * jumlah_rated + "○" * sisa
            self._rec_title.value = f"Rate {sisa} more anime to unlock recommendations."
            self._rec_reason.value = f"{progress}  {jumlah_rated} / {MIN_RATING}"
            self._rec_image.visible = False
            self.update(); return

        user_data = self.data_manager.get_user_by_id(user_id) or {}
        avg_list = user_data.get("average_dimensions", [0.0, 0.0, 0.0, 0.0, 0.0])
        urutan_dimensi = ["plot", "visual", "audio", "characterization", "direction"]
        avg_dim = {urutan_dimensi[i]: avg_list[i] for i in range(5) if avg_list[i] > 0}

        if not avg_dim:
            self._rec_title.value = "Keep rating to improve your recommendations."
            self._rec_reason.value = "Not enough dimension data yet."
            self._rec_image.visible = False
            self.update(); return

        skor_tertinggi = max(avg_dim.values())
        dimensi_seri = [dim for dim, skor in avg_dim.items() if skor == skor_tertinggi]
        sudah_ditonton = [a.get("anime_id") for a, _ in self._cached_anime_rated]

        best_anime_id = None
        alasan = ""

        if hasattr(self.data_manager, "get_rekomendasi_multidimensi"):
            best_anime_id = self.data_manager.get_rekomendasi_multidimensi(dimensi_seri, sudah_ditonton)
        elif hasattr(self.data_manager, "get_rekomendasi_by_dimensi"):
            best_anime_id = self.data_manager.get_rekomendasi_by_dimensi(dimensi_seri[0], sudah_ditonton)

        best_anime = None
        if best_anime_id:
            best_anime = self.data_manager.get_detail_anime(best_anime_id)
            nama_dimensi = " & ".join([d.capitalize() for d in dimensi_seri])
            alasan = f"Highest rated in your favorite aspects: {nama_dimensi}"
        else:
            kandidat = [a for a in self._cached_semua_anime if a.get("anime_id") not in sudah_ditonton and a.get("global_score")]
            if kandidat:
                kandidat.sort(key=lambda x: x.get("global_score", 0), reverse=True)
                best_anime = kandidat[0]
                alasan = "Highly rated by the community"

        if not best_anime:
            self._rec_title.value = "You've conquered our catalog!"
            self._rec_reason.value = "No more anime left to recommend."
            self._rec_image.visible = False
            self.update(); return

        self._rec_anime_id = best_anime.get("anime_id")
        self._rec_title.value = best_anime.get("title", "—")
        self._rec_reason.value = alasan

        self._rec_synopsis.value = best_anime.get("synopsis", "No synopsis available.")

        path_banner = best_anime.get("banner_path", "")

        # Prioritas 2: Poster HD (Hasil download jikan kemarin)
        path_hd = best_anime.get("cover_path_hd", "")

        # Prioritas 3: Poster Lokal (Bawaan burik)
        path_lokal = best_anime.get("cover_path", "") or best_anime.get("thumbnail_path", "")

        # Pemilihan Kasta
        cover_terpilih = path_banner if path_banner else (path_hd if path_hd else path_lokal)

        if cover_terpilih:
            full_path = os.path.join(ROOT_DIR, cover_terpilih)
            if os.path.exists(full_path):
                self._rec_image_container.src = full_path
                self._rec_image_container.update()

        self._rec_synopsis.update()

        self._rec_synopsis.update()

    def _muat_recent(self, user_id):
        self._recent_row.controls.clear()
        if not user_id:
            self._recent_row.controls.append(ft.Text("No ratings yet.", color=self.current_theme["text_muted"], size=12))
            return
        for anime, sp in self._cached_anime_rated[:10]:
            sg = anime.get("global_score", 0) or 0
            # PASS THEME KESINI
            self._recent_row.controls.append(AnimeCardSmall(anime, sg, sp, self.current_theme, on_click_callback=self.screen_manager.tampilkan_detail))

        if not self._cached_anime_rated:
            self._recent_row.controls.append(
                ft.Container(
                    width=320, height=180,
                    gradient=ft.LinearGradient(begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=[self.current_theme["card"], self.current_theme["bg"]]),
                    border=ft.Border.all(1, self.current_theme["border_color"]), border_radius=16, padding=20, margin=ft.padding.only(left=4, right=4, top=10, bottom=10),
                    content=ft.Column(
                        controls=[
                            ft.Text("( ╥ω╥ )", size=32, color=self.current_theme["primary"], weight=ft.FontWeight.BOLD),
                            ft.Text("Oops, you haven't rated any anime yet!", color=self.current_theme["text_main"], size=13, weight=ft.FontWeight.BOLD),
                            ft.Text("Rate your favorite anime to get personalized recommendations.", color=self.current_theme["text_secondary"], size=11, text_align=ft.TextAlign.CENTER),
                            ft.Container(height=5),
                            ft.ElevatedButton("Explore Catalog", icon=ft.Icons.EXPLORE, color=self.current_theme["card"], bgcolor=self.current_theme["primary"], style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10), padding=ft.padding.symmetric(horizontal=20, vertical=12), elevation=0), on_click=lambda _: self.screen_manager.tampilkan_katalog()),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4,
                    ), alignment=ft.Alignment(0, 0),
                )
            )

    def _muat_trending(self, user_id):
         self._trending_row.controls.clear()
         semua_sorted = sorted(self._cached_semua_anime, key=lambda a: (a.get("rating_count", 0) or 0, a.get("global_score", 0) or 0), reverse=True)
         for anime in semua_sorted[:7]:
            aid = anime.get("anime_id", "")
            sg = anime.get("global_score", 0) or 0
            sp = self._cached_skor_user.get(aid, None) if user_id else None
            # PASS THEME KESINI
            self._trending_row.controls.append(AnimeCardSmall(anime, sg, sp, self.current_theme, on_click_callback=self.screen_manager.tampilkan_detail))

    def _muat_top_unrated(self, user_id):
        self._unrated_row.controls.clear()
        unrated_sorted = sorted(self._cached_anime_unrated, key=lambda a: a.get("global_score", 0) or 0, reverse=True)
        for anime in unrated_sorted[:10]:
            sg = anime.get("global_score", 0) or 0
            # PASS THEME KESINI
            self._unrated_row.controls.append(AnimeCardSmall(anime, sg, None, self.current_theme, on_click_callback=self.screen_manager.tampilkan_detail))
        if not self._cached_anime_unrated:
            self._unrated_row.controls.append(ft.Text("You've rated all available anime!", color=self.current_theme["text_muted"], size=12))

    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._sidebar_widget.update()

    def _klik_rekomendasi(self):
        if self._rec_anime_id: self.screen_manager.tampilkan_detail(self._rec_anime_id)
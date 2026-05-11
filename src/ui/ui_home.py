import flet as ft
import random
import asyncio
import os
from src.ui.icons import _sakura_icon_svg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

C_BG = "#FCF8FA"
C_BG2 = "#F5EEF2"
C_SAKURA = "#C07090"
C_SAKURA_LT = "#F9F0F5"
C_TEXT = "#3D2535"
C_TEXT2 = "#8B6A7A"
C_TEXT3 = "#B0909A"
C_BORDER = "#EDE0E8"
C_GOLD = "#C08030"
C_WHITE = "#FFFFFF"


class HujanSakura:
    def __init__(self, target_container):
        self.target = target_container
        self.petals = []
        self.is_running = True

        for _ in range(15):
            petal = ft.Container(
                width=10, height=14,
                bgcolor=random.choice(["#FFB7C5", "#FFD1DC", "#F8A1B9"]),
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
            ft.Text(label, size=8, font_family="Hitchcut", color=warna, weight="bold"),
            ft.Text("—", size=10, font_family="Hitchcut", color=warna, weight="bold"),
        ], spacing=8, alignment=ft.MainAxisAlignment.CENTER),
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[
                ft.Colors.with_opacity(0.2, warna),
                ft.Colors.with_opacity(0.05, warna)
            ],
        ),
        border=ft.border.all(1, ft.Colors.with_opacity(0.4, warna)),
        border_radius=ft.border_radius.only(top_left=12, bottom_right=12, top_right=3, bottom_left=3),
        padding=ft.padding.symmetric(horizontal=12, vertical=5),
    )


def _section_header(title: str, on_lihat_semua=None) -> ft.Container:
    return ft.Container(
        padding=ft.padding.only(left=20, right=20, top=20, bottom=8),
        content=ft.Row(
            controls=[
                ft.Container(
                    width=4,
                    height=16,
                    bgcolor=C_SAKURA,
                    border_radius=4
                ),
                ft.Text(
                    title,
                    font_family="Soopafresh",
                    size=18,
                    color="#6A4A5A",
                ),
                ft.Container(expand=True),
                ft.TextButton(
                    "View All →",
                    style=ft.ButtonStyle(
                        color={ft.ControlState.DEFAULT: C_SAKURA},
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

def _nav_item(kanji, label, style, on_click):
    return ft.TextButton(
        content=ft.Row(
            controls=[
                ft.Text(
                    kanji,
                    font_family="DotGothic16",
                    size=16,
                    weight=ft.FontWeight.BOLD,
                    width=28,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(label, size=13, weight=ft.FontWeight.W_500),
            ],
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        style=style,
        width=216,
        on_click=on_click,
    )


def _sidebar(screen_manager, auth_manager, toggle_fn, halaman_aktif="home"):
    nav_s = ft.ButtonStyle(
        color={ft.ControlState.DEFAULT: C_TEXT},
        bgcolor={ft.ControlState.HOVERED: C_BG2,
                 ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
        shape=ft.RoundedRectangleBorder(radius=10),
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        alignment=ft.Alignment(-1, 0),
    )
    active_nav_s = ft.ButtonStyle(
        color={ft.ControlState.DEFAULT: C_SAKURA},
        bgcolor={ft.ControlState.DEFAULT: C_SAKURA_LT},
        shape=ft.RoundedRectangleBorder(radius=10),
        padding=ft.padding.symmetric(horizontal=16, vertical=10),
        alignment=ft.Alignment(-1, 0),
    )
    danger_s = ft.ButtonStyle(
        color={ft.ControlState.DEFAULT: C_TEXT2},
        bgcolor={ft.ControlState.HOVERED: C_BG2,
                 ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
        shape=ft.RoundedRectangleBorder(radius=8),
        padding=ft.padding.symmetric(horizontal=14, vertical=8),
        alignment=ft.Alignment(-1, 0),
    )

    return ft.Container(
        width=0,
        bgcolor=None,
        content=ft.Container(
            width=240, expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#FDEEF4", "#EAF3FC"],
            ),
            border=ft.border.only(right=ft.BorderSide(1, C_BORDER)),
            padding=ft.padding.only(left=12, right=12, top=24, bottom=24),
            content=ft.Column(
                controls=[
                    ft.Row(
                        [ft.IconButton(
                            ft.Icons.CHEVRON_LEFT,
                            icon_color=C_SAKURA, icon_size=20,
                            on_click=toggle_fn,
                        )],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    ft.Container(height=8),
                    _nav_item("ホ", "Home",
                              active_nav_s if halaman_aktif == "home" else nav_s,
                              lambda _: screen_manager.tampilkan_home()),

                    _nav_item("覧", "Anime List",
                              active_nav_s if halaman_aktif == "katalog" else nav_s,
                              lambda _: screen_manager.tampilkan_katalog()),

                    _nav_item("追", "Add Anime",
                              active_nav_s if halaman_aktif == "scraping" else nav_s,
                              lambda _: screen_manager.tampilkan_scraping()),

                    _nav_item("析", "Analytics",
                              active_nav_s if halaman_aktif == "analytics" else nav_s,
                              lambda _: screen_manager.tampilkan_analytics()),

                    _nav_item("人", "Profile",
                              active_nav_s if halaman_aktif == "profil" else nav_s,
                              lambda _: screen_manager.tampilkan_profil()),
                    ft.Container(expand=True),
                    ft.Divider(color=C_BORDER, height=1, thickness=1),
                    ft.Container(height=4),
                    ft.TextButton(
                        content=ft.Row(
                            controls=[
                                ft.Text("出", font_family="DotGothic16",
                                        size=16, weight=ft.FontWeight.BOLD,
                                        width=28, text_align=ft.TextAlign.CENTER),
                                ft.Text("Log Out", size=13),
                            ],
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        style=danger_s, width=216,
                        on_click=lambda _: (auth_manager.logout(),
                                            screen_manager.tampilkan_login()),
                    ),
                ],
                spacing=2, expand=True,
            ),
        ),
        animate_size=ft.Animation(duration=280, curve=ft.AnimationCurve.EASE_OUT),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
    )


class UIHome(ft.Row):
    def __init__(self, page, data_manager, auth_manager, screen_manager):
        super().__init__()
        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager
        self._sidebar_open = False

        self.expand = True
        self.spacing = 0

        self._sidebar_widget = _sidebar(
            screen_manager, auth_manager,
            self._toggle_sidebar, halaman_aktif="home"
        )

        topbar = ft.Container(
            padding=ft.padding.symmetric(horizontal=16),
            height=55,
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#E6FFFFFF", "#CCFCF8FA"],
            ),
            shadow=ft.BoxShadow(
                blur_radius=15,
                color="#15000000",
                offset=ft.Offset(0, 4)
            ),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        ft.Icons.MENU, icon_color=C_SAKURA,
                        on_click=self._toggle_sidebar, tooltip="Menu",
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                spacing=0,
                                controls=[
                                    ft.Text("R", font_family="Hitchcut", size=24, color="#C07090"),
                                    ft.Text("a", font_family="Hitchcut", size=24, color="#D48CA8"),
                                    ft.Text("d", font_family="Hitchcut", size=24, color="#C07090"),
                                    ft.Text("a", font_family="Hitchcut", size=24, color="#D48CA8"),
                                    ft.Text("r", font_family="Hitchcut", size=24, color="#C07090"),
                                    ft.Text("A", font_family="Hitchcut", size=24, color="#D48CA8"),
                                    ft.Text("n", font_family="Hitchcut", size=24, color="#C07090"),
                                    ft.Text("i", font_family="Hitchcut", size=24, color="#D48CA8"),
                                ]
                            ),
                            ft.Text(
                                "レーダアニ",
                                font_family="Mofuji04",
                                size=10,
                                color=C_TEXT3,
                            ),
                        ],
                        spacing=0,
                        tight=True,
                    ),
                    ft.Container(expand=True),
                    ft.IconButton(
                        ft.Icons.ACCOUNT_CIRCLE,
                        icon_color=C_TEXT3,
                        tooltip="Profile",
                        on_click=lambda _: self.screen_manager.tampilkan_profil()
                    )
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        user_id = self.auth_manager.get_user_aktif()
        user_data = self.data_manager.get_user_by_id(user_id)
        username = user_data.get("username", "User") if user_data else "User"

        self._stat_rated = _stat_pill("評", "RATED", "#DE7C88")
        self._stat_unrated = _stat_pill("未", "UNRATED", "#52B7FF")
        self._stat_avg = _stat_pill("均", "AVG", "#7AB9E6")
        self._stat_dim = _stat_pill("極", "TOP", "#C0616D")

        self._rec_title = ft.Text("—", size=14, color=C_TEXT, weight=ft.FontWeight.BOLD, max_lines=1,
                                  overflow=ft.TextOverflow.ELLIPSIS, expand=True)
        self._rec_reason = ft.Text("Based on your top dimension", size=10, color="#A07888")
        self._rec_anime_id = None

        self._rec_image = ft.Image(
            src="", width=36, height=50, fit=ft.BoxFit.COVER, visible=False
        )
        self._rec_image_container = ft.Container(
            width=36, height=50, bgcolor="#D4A8C0", border_radius=6,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=self._rec_image
        )

        def banner_hover(e):
            is_hover = str(e.data).lower() == "true"
            if is_hover:
                e.control.shadow = ft.BoxShadow(spread_radius=0, blur_radius=20, color="#66C07090",
                                                offset=ft.Offset(0, 6))
            else:
                e.control.shadow = ft.BoxShadow(spread_radius=0, blur_radius=15, color="#1A000000",
                                                offset=ft.Offset(0, 4))
            e.control.update()

        rec_banner = ft.Container(
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, 0),
                end=ft.Alignment(1, 0),
                colors=["#F2E3EB", C_WHITE, C_WHITE, "#F2E3EB"],
                stops=[0.0, 0.15, 0.85, 1.0]
            ),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=15,
                color="#1A000000",
                offset=ft.Offset(0, 4)
            ),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            on_hover=banner_hover,
            animate=ft.Animation(duration=250, curve=ft.AnimationCurve.EASE_OUT),
            content=ft.Row(
                controls=[
                    self._rec_image_container,
                    ft.Column(
                        controls=[
                            ft.Text("✦  RECOMMENDED FOR YOU", size=9, color=C_TEXT3, weight=ft.FontWeight.W_900),
                            self._rec_title,
                            self._rec_reason,
                        ],
                        spacing=2, tight=True, expand=True,
                    ),
                    ft.ElevatedButton(
                        "View",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.padding.symmetric(horizontal=14, vertical=6),
                            elevation=0,
                            color={
                                ft.ControlState.HOVERED: C_SAKURA,
                                ft.ControlState.DEFAULT: C_WHITE
                            },
                            bgcolor={
                                ft.ControlState.HOVERED: C_WHITE,
                                ft.ControlState.DEFAULT: C_SAKURA
                            },
                            side={
                                ft.ControlState.HOVERED: ft.BorderSide(1, C_SAKURA),
                                ft.ControlState.DEFAULT: ft.BorderSide(0, ft.Colors.TRANSPARENT)
                            }
                        ),
                        on_click=lambda _: self._klik_rekomendasi(),
                    ),
                ],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        header = ft.Container(
            padding=ft.padding.only(left=20, right=20, top=14, bottom=12),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Image(src=_sakura_icon_svg(), width=24, height=24, fit="contain"),
                            ft.Text(f"Konnichiwa, {username}!", size=18, color="#5C3D52", weight=ft.FontWeight.BOLD),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=8
                    ),
                    ft.Row(
                        controls=[
                            self._stat_rated, self._stat_unrated,
                            self._stat_avg, self._stat_dim,
                        ],
                        spacing=6
                    ),
                    rec_banner,
                ],
                spacing=10,
            ),
        )

        self.daftar_baris_animasi = []

        def animasikan_baris(e, baris_terpilih):
            is_hover = str(e.data).lower() == "true"
            for b in self.daftar_baris_animasi:
                if is_hover:
                    if b == baris_terpilih:
                        b.opacity = 1.0
                        b.scale = 1.02
                    else:
                        b.opacity = 0.4
                        b.scale = 0.95
                else:
                    b.opacity = 1.0
                    b.scale = 1.0
                b.update()

        self._trending_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=14)
        trending_section = ft.Container(
            padding=ft.padding.only(top=10),
            content=ft.Column(
                controls=[
                    _section_header("What Everyone's Watching",
                                    on_lihat_semua=lambda _: self.screen_manager.tampilkan_katalog(
                                        filter_kategori="trending")),
                    ft.Container(
                        content=self._trending_row,
                        padding=ft.padding.only(left=24, right=24, top=5, bottom=15)
                    ),
                ],
                spacing=0,
            ),
            opacity=1.0,
            animate_opacity=300,
            scale=1.0,
            animate_scale=300,
        )
        trending_section.on_hover = lambda e: animasikan_baris(e, trending_section)
        self.daftar_baris_animasi.append(trending_section)

        self._recent_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=14)
        recent_section = ft.Container(
            padding=ft.padding.only(top=10),
            content=ft.Column(
                controls=[
                    _section_header("Your Latest Picks",
                                    on_lihat_semua=lambda _: self.screen_manager.tampilkan_katalog(
                                        filter_kategori="rated")),
                    ft.Container(
                        content=self._recent_row,
                        padding=ft.padding.only(left=24, right=24, top=5, bottom=15)
                    ),
                ],
                spacing=0,
            ),
            opacity=1.0,
            animate_opacity=300,
            scale=1.0,
            animate_scale=300,
        )
        recent_section.on_hover = lambda e: animasikan_baris(e, recent_section)
        self.daftar_baris_animasi.append(recent_section)

        self._unrated_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=14)
        unrated_section = ft.Container(
            padding=ft.padding.only(top=10),
            content=ft.Column(
                controls=[
                    _section_header("Ready for Your Review",
                                    on_lihat_semua=lambda _: self.screen_manager.tampilkan_katalog(
                                        filter_kategori="unrated")),
                    ft.Container(
                        content=self._unrated_row,
                        padding=ft.padding.only(left=24, right=24, top=5, bottom=15)
                    ),
                ],
                spacing=0,
            ),
            opacity=1.0,
            animate_opacity=300,
            scale=1.0,
            animate_scale=300,
            margin=ft.margin.only(bottom=30),
        )
        unrated_section.on_hover = lambda e: animasikan_baris(e, unrated_section)
        self.daftar_baris_animasi.append(unrated_section)

        self._main_col = ft.Column(
            controls=[
                topbar,
                ft.Column(
                    controls=[header, trending_section, recent_section, unrated_section],
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                    spacing=0,
                ),
            ],
            spacing=0, expand=True,
        )

        _hujan_stack = ft.Stack(expand=True)
        wadah_sakura = ft.TransparentPointer(_hujan_stack, expand=True)

        area_utama = ft.Stack(
            controls=[
                ft.Container(
                    content=self._main_col,
                    left=0, right=0, top=0, bottom=0,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(0, -1),
                        end=ft.Alignment(0, 1),
                        colors=["#FFFFFF", "#F0F2F5"],
                        stops=[0.4, 1.0],
                    )
                ),
                wadah_sakura,
            ],
            expand=True,
        )

        self.controls = [self._sidebar_widget, area_utama]


        self.efek_sakura = HujanSakura(_hujan_stack)
        self.my_page.run_task(self.efek_sakura.turun)

    # ── Muat Sections ──
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

    # ── Perbarui Stats ──
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

    # ── Muat Rekomendasi ──
    def _muat_rekomendasi(self, user_id):
        if not user_id:
            return

        MIN_RATING = 3
        jumlah_rated = len(self._cached_anime_rated) if hasattr(self, '_cached_anime_rated') else 0

        if jumlah_rated == 0:
            self._rec_title.value = "Start rating to unlock recommendations."
            self._rec_reason.value = "Rate your first anime to begin."
            self._rec_image.visible = False
            try:
                self.update()
            except RuntimeError:
                pass
            return

        if jumlah_rated < MIN_RATING:
            sisa = MIN_RATING - jumlah_rated
            progress = "●" * jumlah_rated + "○" * sisa
            self._rec_title.value = f"Rate {sisa} more anime to unlock recommendations."
            self._rec_reason.value = f"{progress}  {jumlah_rated} / {MIN_RATING}"
            self._rec_image.visible = False
            try:
                self.update()
            except RuntimeError:
                pass
            return

        user_data = self.data_manager.get_user_by_id(user_id) or {}
        avg_list = user_data.get("average_dimensions", [0.0, 0.0, 0.0, 0.0, 0.0])
        urutan_dimensi = ["plot", "visual", "audio", "characterization", "direction"]
        avg_dim = {urutan_dimensi[i]: avg_list[i] for i in range(5) if avg_list[i] > 0}

        if not avg_dim:
            self._rec_title.value = "Keep rating to improve your recommendations."
            self._rec_reason.value = "Not enough dimension data yet."
            self._rec_image.visible = False
            try:
                self.update()
            except RuntimeError:
                pass
            return

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
            kandidat = [a for a in self._cached_semua_anime if
                        a.get("anime_id") not in sudah_ditonton and a.get("global_score")]
            if kandidat:
                kandidat.sort(key=lambda x: x.get("global_score", 0), reverse=True)
                best_anime = kandidat[0]
                alasan = "Highly rated by the community"

        if not best_anime:
            self._rec_title.value = "You've conquered our catalog!"
            self._rec_reason.value = "No more anime left to recommend."
            self._rec_image.visible = False
            try:
                self.update()
            except RuntimeError:
                pass
            return

        self._rec_anime_id = best_anime.get("anime_id")
        self._rec_title.value = best_anime.get("title", "—")
        self._rec_reason.value = alasan

        thumb_path = best_anime.get("thumbnail_path", "")
        if thumb_path:
            full_path = os.path.join(ROOT_DIR, thumb_path)
            if os.path.exists(full_path):
                self._rec_image.src = full_path
                self._rec_image.visible = True
            else:
                self._rec_image.visible = False
        else:
            self._rec_image.visible = False

        try:
            self.update()
        except RuntimeError:
            pass

    # ── Muat Recent ──
    def _muat_recent(self, user_id):
        self._recent_row.controls.clear()

        if not user_id:
            self._recent_row.controls.append(ft.Text("No ratings yet.", color=C_TEXT3, size=12))
            return

        for anime, sp in self._cached_anime_rated[:10]:
            sg = anime.get("global_score", 0) or 0
            self._recent_row.controls.append(
                AnimeCardSmall(anime, sg, sp, on_click_callback=self.screen_manager.tampilkan_detail)
            )

        if not self._cached_anime_rated:
            self._recent_row.controls.append(
                ft.Container(
                    width=320,
                    height=180,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(0, -1),
                        end=ft.Alignment(0, 1),
                        colors=["#FFFFFF", "#FDF5F8"]
                    ),
                    border=ft.border.all(1, "#F4E6EC"),
                    border_radius=16,
                    padding=20,
                    margin=ft.padding.only(left=4, right=4, top=10, bottom=10),
                    content=ft.Column(
                        controls=[
                            ft.Text("( ╥ω╥ )", size=32, color="#D4A8C0", weight=ft.FontWeight.BOLD),
                            ft.Text("Oops, you haven't rated any anime yet!", color=C_TEXT2, size=13,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text("Rate your favorite anime to get personalized recommendations.", color=C_TEXT3,
                                    size=11, text_align=ft.TextAlign.CENTER),
                            ft.Container(height=5),
                            ft.ElevatedButton(
                                "Explore Catalog",
                                icon=ft.Icons.EXPLORE,
                                color=C_WHITE,
                                bgcolor=C_SAKURA,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                    elevation=0,
                                ),
                                on_click=lambda _: self.screen_manager.tampilkan_katalog(),
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    alignment=ft.Alignment(0, 0),
                )
            )

     # ── Muat Trending ──
    def _muat_trending(self, user_id):
         self._trending_row.controls.clear()

         semua_sorted = sorted(
             self._cached_semua_anime,
            key=lambda a: (a.get("rating_count", 0) or 0, a.get("global_score", 0) or 0),
            reverse=True
         )

         for anime in semua_sorted[:7]:
            aid = anime.get("anime_id", "")
            sg = anime.get("global_score", 0) or 0
            sp = self._cached_skor_user.get(aid, None) if user_id else None
            self._trending_row.controls.append(
                AnimeCardSmall(anime, sg, sp, on_click_callback=self.screen_manager.tampilkan_detail)
             )

    # ── Muat Top Unrated ──
    def _muat_top_unrated(self, user_id):
        self._unrated_row.controls.clear()
        unrated_sorted = sorted(self._cached_anime_unrated, key=lambda a: a.get("global_score", 0) or 0,
                                reverse=True)

        for anime in unrated_sorted[:10]:
            sg = anime.get("global_score", 0) or 0
            self._unrated_row.controls.append(
                AnimeCardSmall(anime, sg, None, on_click_callback=self.screen_manager.tampilkan_detail)
            )

        if not self._cached_anime_unrated:
            self._unrated_row.controls.append(
                ft.Text("You've rated all available anime!", color=C_TEXT3, size=12))

    # ── Sidebar & Klik Actions ──
    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._sidebar_widget.update()

    def _klik_rekomendasi(self):
        if self._rec_anime_id:
            self.screen_manager.tampilkan_detail(self._rec_anime_id)
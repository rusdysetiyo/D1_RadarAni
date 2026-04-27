import flet as ft
import random
import asyncio
import os
from src.ui.icons import _sakura_icon_svg

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
                    await asyncio.sleep(0.5)
                    continue

                for petal in self.petals:
                    petal.animate_position = ft.Animation(0)
                    petal.animate_rotation = ft.Animation(0)
                    petal.top = -50
                    petal.left = random.randint(0, 1000)
                    petal.rotate.angle = random.uniform(0, 3.14)

                self.target.update()
                await asyncio.sleep(0.1)

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
                print(f"Error Hujan Sakura: {e}")
                await asyncio.sleep(2)

def _pill(text: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(text, size=11, color=C_TEXT2),
        bgcolor=C_BG2,
        border=ft.border.all(1, C_BORDER),
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=12, vertical=4),
    )

def _section_header(title: str, on_lihat_semua=None) -> ft.Container:
    return ft.Container(
        padding=ft.padding.only(left=20, right=20, top=20, bottom=8),
        content=ft.Row(
            controls=[
                ft.Text(title, size=14, color=C_TEXT, weight=ft.FontWeight.BOLD),
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
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

class AnimeCardSmall(ft.Container):
    def __init__(self, anime: dict, skor_global, skor_personal, on_click_callback):
        super().__init__()
        self.anime = anime
        self._on_click_cb = on_click_callback

        self.width = 120
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment(0, -1),
            end=ft.Alignment(0, 1),
            colors=["#FFFFFF", "#FDF5F8"]
        )
        self.border = ft.border.all(1, C_BORDER)
        self.border_radius = 10
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE
        self.margin = ft.padding.only(left=6, right=6, top=10, bottom=20)

        self.shadow = ft.BoxShadow(
            blur_radius=12,
            color=ft.Colors.with_opacity(0.06, ft.Colors.BLACK),
            offset=ft.Offset(0, 4)
        )

        self.on_click = lambda _: self._on_click_cb(anime.get("anime_id", ""))
        self.on_hover = self._on_hover
        self.animate = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)

        thumb = anime.get("thumbnail_path", "")
        if thumb:
            thumb = os.path.join(BASE_DIR, thumb)

        if thumb and os.path.exists(thumb):
            poster = ft.Image(
                src=thumb, width=120, height=140,
                fit=ft.BoxFit.COVER,
                border_radius=ft.border_radius.only(top_left=9, top_right=9),
            )
        else:
            poster = ft.Container(
                width=120, height=140,
                bgcolor=C_BG2,
                border_radius=ft.border_radius.only(top_left=9, top_right=9),
                content=ft.Icon(
                    name=ft.icons.IMAGE_OUTLINED,
                    color=C_TEXT3,
                    size=32
                ),
                alignment=ft.alignment.center,
            )

        genres = anime.get("genre", [])[:3]
        sg_str = (f"★ {skor_global:.1f}  ·  {anime.get('episodes', '?')} eps"
                  if skor_global else f"{anime.get('episodes', '?')} eps")

        self._overlay = ft.Container(
            width=120, height=140,
            bgcolor=ft.Colors.with_opacity(0.85, "#000000"),
            border_radius=ft.border_radius.only(top_left=9, top_right=9),
            padding=6,
            content=ft.Column(
                controls=[
                    ft.Container(expand=True),
                    ft.Text(anime.get("title", ""), size=9, color=C_WHITE,
                            weight=ft.FontWeight.BOLD, max_lines=2),
                    ft.Text(sg_str, size=8, color="#D4A8BC"),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(g, size=7, color="#F5D0E0"),
                                bgcolor="#C07090", border_radius=8,
                                padding=ft.padding.symmetric(horizontal=4, vertical=1),
                                opacity=0.75,
                            )
                            for g in genres
                        ],
                        spacing=2,
                        run_spacing=2,
                        wrap=True,
                    ),
                ],
                spacing=3,
            ),
            visible=False,
        )

        is_rated = skor_personal is not None
        score_txt = f"★ {skor_global:.1f}" if skor_global else "★ —"
        you_txt = f"you: {skor_personal:.1f}" if is_rated else "you: N/A"

        info = ft.Container(
            padding=ft.padding.only(left=6, right=6, top=4, bottom=5),
            content=ft.Column(
                controls=[
                    ft.Text(anime.get("title", "—"), size=9, color=C_TEXT,
                            weight=ft.FontWeight.BOLD, max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(f"{score_txt}  {you_txt}", size=8, color=C_TEXT3),
                ],
                spacing=2, tight=True,
            ),
        )

        self.content = ft.Column(
            controls=[
                ft.Stack(controls=[poster, self._overlay], width=120, height=140),
                info
            ],
            spacing=0, tight=True,
        )

    def _on_hover(self, e):
        is_hovered = str(e.data).lower() == "true"
        self._overlay.visible = is_hovered
        self.border = ft.border.all(1.5 if is_hovered else 1, C_SAKURA if is_hovered else C_BORDER)
        self.scale = 1.03 if is_hovered else 1.0

        self.shadow = ft.BoxShadow(
            blur_radius=16 if is_hovered else 12,
            color=ft.Colors.with_opacity(0.12 if is_hovered else 0.06, ft.Colors.BLACK),
            offset=ft.Offset(0, 6 if is_hovered else 4)
        )

        if self.page:
            self.update()

def _sidebar(screen_manager, auth_manager, toggle_fn, halaman_aktif="home"):
    nav_s = ft.ButtonStyle(
        color={ft.ControlState.DEFAULT: C_TEXT},
        bgcolor={ft.ControlState.HOVERED: C_BG2, ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
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
        bgcolor={ft.ControlState.HOVERED: C_BG2, ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
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
                    ft.TextButton(
                        "   Home",
                        style=active_nav_s if halaman_aktif == "home" else nav_s,
                        width=216,
                        on_click=lambda _: screen_manager.tampilkan_home(),
                    ),
                    ft.TextButton(
                        "   Anime List",
                        style=active_nav_s if halaman_aktif == "katalog" else nav_s,
                        width=216,
                        on_click=lambda _: screen_manager.tampilkan_katalog(),
                    ),
                    ft.TextButton(
                        "   Profile",
                        style=active_nav_s if halaman_aktif == "profil" else nav_s,
                        width=216,
                        on_click=lambda _: screen_manager.tampilkan_profil(),
                    ),
                    ft.Container(expand=True),
                    ft.Divider(color=C_BORDER, height=1, thickness=1),
                    ft.Container(height=4),
                    ft.TextButton(
                        "↪   Log Out", style=danger_s, width=216,
                        on_click=lambda _: (auth_manager.logout(), screen_manager.tampilkan_login()),
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
                    ft.Column([
                        ft.Text("RadarAni", size=13, color=C_SAKURA, weight=ft.FontWeight.BOLD),
                        ft.Text("レーダアニ", size=8, color=C_TEXT3),
                    ], spacing=0, tight=True),
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

        # ── Data Fetching ──
        user_id = self.auth_manager.get_user_aktif()
        user_data = self.data_manager.get_user_by_id(user_id)
        username = user_data.get("username", "User") if user_data else "User"

        self._stat_rated = _pill("— rated")
        self._stat_unrated = _pill("— unrated")
        self._stat_avg = _pill("avg —")
        self._stat_dim = _pill("top: —")

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

        rec_banner = ft.Container(
            bgcolor=C_SAKURA_LT,
            border=ft.border.all(1, "#E8D0DE"),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=14, vertical=10),
            content=ft.Row(
                controls=[
                    self._rec_image_container,
                    ft.Column(
                        controls=[
                            ft.Text("✦  RECOMMENDED FOR YOU", size=9, color="#9B6080", weight=ft.FontWeight.BOLD),
                            self._rec_title,
                            self._rec_reason,
                        ],
                        spacing=2, tight=True, expand=True,
                    ),
                    ft.ElevatedButton(
                        "View", bgcolor=C_SAKURA, color=C_WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.padding.symmetric(horizontal=14, vertical=6),
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

        self._muat_sections()

        self.efek_sakura = HujanSakura(_hujan_stack)
        self.my_page.run_task(self.efek_sakura.turun)

    def _muat_sections(self):
        user_id = self.auth_manager.get_user_aktif()
        self._perbarui_stats(user_id)
        self._muat_rekomendasi(user_id)
        self._muat_trending(user_id)
        self._muat_recent(user_id)
        self._muat_top_unrated(user_id)

    def _muat_rekomendasi(self, user_id):
        if not user_id: return

        avg_dim = {}
        if hasattr(self.data_manager, "get_avg_dimensi_user"):
            avg_dim = self.data_manager.get_avg_dimensi_user(user_id) or {}

        # Skenario 1: User belum pernah rating sama sekali
        if not avg_dim:
            self._rec_title.value = "Rate more anime to get recommendations!"
            self._rec_reason.value = "Not enough data to calculate top dimension."
            return

        # Cari dimensi terfavorit user
        top_dim = max(avg_dim, key=avg_dim.get)

        # Collect semua anime yg sudah ditonton
        semua_anime = self.data_manager.get_semua_anime()
        sudah_ditonton = []
        for anime in semua_anime:
            if self.data_manager.hitung_skor_personal(user_id, anime.get("anime_id", "")) is not None:
                sudah_ditonton.append(anime.get("anime_id", ""))

        # cek DataManager nyari anime menonjol di dimensi favorit
        best_anime_id = None
        if hasattr(self.data_manager, "get_rekomendasi_by_dimensi"):
            best_anime_id = self.data_manager.get_rekomendasi_by_dimensi(top_dim, sudah_ditonton)

        best_anime = None
        alasan = ""

        # Skenario 2: Ketemu anime yang menonjol di dimensi tersebut
        if best_anime_id:
            best_anime = self.data_manager.get_detail_anime(best_anime_id)
            alasan = f"Highest rated in your favorite aspect: {top_dim.capitalize()}"
        else:
            # Skenario 3 : Anime lain belum ada rating dimensi dari komunitas.
            # Jadi kita ambil anime belum ditonton dengan global_score tertinggi.
            kandidat = []
            for anime in semua_anime:
                aid = anime.get("anime_id", "")
                if aid not in sudah_ditonton:
                    sg = anime.get("global_score", 0) or 0
                    if sg:
                        kandidat.append((anime, sg))

            if kandidat:
                kandidat.sort(key=lambda x: x[1], reverse=True)
                best_anime = kandidat[0][0]
                alasan = "Highly rated by the community"

        # Skenario 4: semua anime di database sudah ditonton
        if not best_anime:
            self._rec_title.value = "You've conquered our catalog!"
            self._rec_reason.value = "No more anime left to recommend."
            return

        self._rec_anime_id = best_anime.get("anime_id")
        self._rec_title.value = best_anime.get("title", "—")
        self._rec_reason.value = alasan

        thumb_path = best_anime.get("thumbnail_path", "")
        if thumb_path:
            full_path = os.path.join(BASE_DIR, thumb_path)
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

    def _muat_recent(self, user_id):
        self._recent_row.controls.clear()

        if not user_id:
            self._recent_row.controls.append(ft.Text("No ratings yet.", color=C_TEXT3, size=12))
            return

        semua = self.data_manager.get_semua_anime()

        dinilai = []
        for a in semua:
            sp = self.data_manager.hitung_skor_personal(user_id, a["anime_id"])
            if sp is not None:
                dinilai.append((a, sp))
                if len(dinilai) >= 10:
                    break

        for anime, sp in dinilai:
            sg = anime.get("global_score", 0) or 0
            self._recent_row.controls.append(
                AnimeCardSmall(anime, sg, sp, on_click_callback=self.screen_manager.tampilkan_detail)
            )

        if not dinilai:
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

    def _muat_trending(self, user_id):
        self._trending_row.controls.clear()
        semua = self.data_manager.get_semua_anime()
        semua_sorted = sorted(semua, key=lambda a: a.get("global_score", 0) or 0, reverse=True)

        for anime in semua_sorted[:7]:
            aid = anime.get("anime_id", "")
            sg = anime.get("global_score", 0) or 0
            sp = self.data_manager.hitung_skor_personal(user_id, aid) if user_id else None
            self._trending_row.controls.append(
                AnimeCardSmall(anime, sg, sp, on_click_callback=self.screen_manager.tampilkan_detail)
            )

    def _muat_top_unrated(self, user_id):
        self._unrated_row.controls.clear()
        semua = self.data_manager.get_semua_anime()

        unrated = []
        for a in semua:
            if self.data_manager.hitung_skor_personal(user_id, a["anime_id"]) is None:
                unrated.append(a)

        unrated.sort(key=lambda a: a.get("global_score", 0) or 0, reverse=True)

        for anime in unrated[:10]:
            aid = anime.get("anime_id", "")
            sg = anime.get("global_score", 0) or 0
            self._unrated_row.controls.append(
                AnimeCardSmall(anime, sg, None, on_click_callback=self.screen_manager.tampilkan_detail)
            )

        if not unrated:
            self._unrated_row.controls.append(ft.Text("You've rated all available anime! 🎉", color=C_TEXT3, size=12))

    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._sidebar_widget.update()

    def _klik_rekomendasi(self):
        if self._rec_anime_id:
            self.screen_manager.tampilkan_detail(self._rec_anime_id)

    def _perbarui_stats(self, user_id):
        if not user_id: return
        semua = self.data_manager.get_semua_anime()

        rated = 0
        scores = []
        for a in semua:
            sp = self.data_manager.hitung_skor_personal(user_id, a["anime_id"])
            if sp is not None:
                rated += 1
                scores.append(sp)

        unrated = len(semua) - rated

        avg_dim = {}
        if hasattr(self.data_manager, "get_avg_dimensi_user"):
            avg_dim = self.data_manager.get_avg_dimensi_user(user_id) or {}
        top_dim = max(avg_dim, key=avg_dim.get).capitalize() if avg_dim else "—"

        avg_val = f"{sum(scores) / len(scores):.1f}" if scores else "—"

        self._stat_rated.content = ft.Text(f"  {rated} rated", size=11, color=C_TEXT2)
        self._stat_unrated.content = ft.Text(f"  {unrated} unrated", size=11, color=C_TEXT2)
        self._stat_avg.content = ft.Text(f"  avg {avg_val}", size=11, color=C_TEXT2)
        self._stat_dim.content = ft.Text(f"  top: {top_dim}", size=11, color=C_TEXT2)
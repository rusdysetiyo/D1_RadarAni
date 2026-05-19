import flet as ft
import asyncio
import os
from ui.components.icons import _sakura_icon_svg
from src.ui.components.hujan_sakura import HujanSakura
from src.ui.components.anime_cards import AnimeCardHome
from src.ui.components.theme_picker import ThemePicker
from src.ui.components.hero_banner import HeroBanner
from src.ui.components.anime_section_row import AnimeSectionRow

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

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
                        [
                            ft.IconButton(
                                icon=ft.Icons.CHEVRON_LEFT,
                                icon_size=20,
                                on_click=toggle_fn,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.Colors.TRANSPARENT,
                                    icon_color={
                                        ft.ControlState.HOVERED: ft.Colors.with_opacity(0.8, theme["primary"]),
                                        ft.ControlState.DEFAULT: theme["primary"],
                                    }
                                )
                            )
                        ],
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
        self.theme = theme
        self._sidebar_open = False

        self.theme_picker = ThemePicker(page, self.screen_manager, self.theme)

        self.expand = True
        self.spacing = 0

        self._sidebar_widget = _sidebar(
            screen_manager, auth_manager,
            self._toggle_sidebar, self.theme, halaman_aktif="home"
        )

        topbar = self._build_topbar()

        user_id = self.auth_manager.get_user_aktif()
        user_data = self.data_manager.get_user_by_id(user_id)
        username = user_data.get("username", "User") if user_data else "User"

        self._stat_rated   = _stat_pill("評", "RATED",   self.theme["pill_rated"])
        self._stat_unrated = _stat_pill("未", "UNRATED", self.theme["pill_unrated"])
        self._stat_avg     = _stat_pill("均", "AVG",     self.theme["pill_avg"])
        self._stat_dim     = _stat_pill("極", "TOP",     self.theme["pill_top"])

        # ── Injeksi Komponen Hero Banner Baru ──
        self.hero_banner = HeroBanner(self.theme, self._klik_rekomendasi)

        header = ft.Container(
            padding=ft.padding.only(left=20, right=20, top=14, bottom=12),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Image(src=_sakura_icon_svg(), width=24, height=24, fit="contain"),
                            ft.Text(f"Konnichiwa, {username}!", size=18, color=self.theme["text_main"], weight=ft.FontWeight.BOLD),
                        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8
                    ),
                    ft.Row(controls=[self._stat_rated, self._stat_unrated, self._stat_avg, self._stat_dim], spacing=6),
                    self.hero_banner,
                ], spacing=10,
            ),
        )

        # ── Injeksi Komponen Horizontal Sections Baru ──
        self.daftar_baris_animasi = []
        self.trending_section = AnimeSectionRow("What Everyone's Watching", "trending", self.theme, self.screen_manager, self._animasikan_baris)
        self.recent_section = AnimeSectionRow("Your Latest Picks", "rated", self.theme, self.screen_manager, self._animasikan_baris)
        self.unrated_section = AnimeSectionRow("Ready for Your Review", "unrated", self.theme, self.screen_manager, self._animasikan_baris)
        self.unrated_section.margin = ft.margin.only(bottom=30)

        self.daftar_baris_animasi.extend([self.trending_section, self.recent_section, self.unrated_section])

        self.main_scroll = ft.Column(
            controls=[header, self.trending_section, self.recent_section, self.unrated_section],
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
                    bgcolor=self.theme["bg"]
                ),
                wadah_sakura,
            ], expand=True,
        )

        self.controls = [self._sidebar_widget, area_utama]

        self.efek_sakura = HujanSakura(_hujan_stack, self.theme)
        self.my_page.run_task(self.efek_sakura.turun)

    def will_unmount(self):
        if hasattr(self, "efek_sakura") and self.efek_sakura:
            self.efek_sakura.stop()

    def _animasikan_baris(self, e, baris_terpilih):
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
            self._safe_update(b)

    def _isi_katalog_row(self, target_row, list_anime, skor_user_dict, pakai_skor_personal=False):
        target_row.controls.clear()
        for anime in list_anime:
            aid = anime.get("anime_id", "")
            sg = anime.get("global_score", 0) or 0
            sp = skor_user_dict.get(aid, None) if pakai_skor_personal else None

            target_row.controls.append(
                AnimeCardHome(
                    anime=anime,
                    skor_global=sg,
                    skor_personal=sp,
                    theme=self.theme,
                    on_click_callback=self.screen_manager.tampilkan_detail
                )
            )

    async def _muat_sections(self):
        user_id = self.data_manager.baca_sesi()
        if not user_id: return

        cache = self.data_manager.get_home_cache_data(user_id)
        self._cached_semua_anime, self._cached_anime_rated, self._cached_anime_unrated, self._cached_skor_user = cache

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

        self._safe_update(self.trending_section.inner_row)
        self._safe_update(self.recent_section.inner_row)
        self._safe_update(self.unrated_section.inner_row)
        self._safe_update(self)

    def _perbarui_stats(self, user_id):
        if not user_id: return
        rated_count = len(self._cached_anime_rated)
        unrated_count = len(self._cached_anime_unrated)
        scores = [sp for _, sp in self._cached_anime_rated]

        r, u, a, d = self.data_manager.get_user_stats_summary(user_id, rated_count, unrated_count, scores)

        self._stat_rated.content.controls[2].value = r
        self._stat_unrated.content.controls[2].value = u
        self._stat_avg.content.controls[2].value = a
        self._stat_dim.content.controls[2].value = d
        self._safe_update(self)

    def _muat_rekomendasi(self, user_id):
        if not user_id: return

        MIN_RATING = 3
        jumlah_rated = len(self._cached_anime_rated) if hasattr(self, '_cached_anime_rated') else 0

        if jumlah_rated == 0:
            self.hero_banner._rec_title.value = "Start rating to unlock recommendations."
            self.hero_banner._rec_reason.value = "Rate your first anime to begin."
            self.hero_banner._hide_rec_empty_state()
            self._safe_update(self)
            return

        if jumlah_rated < MIN_RATING:
            sisa = MIN_RATING - jumlah_rated
            progress = "●" * jumlah_rated + "○" * sisa
            self.hero_banner._rec_title.value = f"Rate {sisa} more anime to unlock recommendations."
            self.hero_banner._rec_reason.value = f"{progress}  {jumlah_rated} / {MIN_RATING}"
            self.hero_banner._hide_rec_empty_state()
            self._safe_update(self)
            return

        sudah_ditonton = [a.get("anime_id") for a, _ in self._cached_anime_rated]
        hasil_rec = self.data_manager.get_rekomendasi_banner_home(
            user_id=user_id,
            sudah_ditonton=sudah_ditonton,
            semua_anime_cache=self._cached_semua_anime
        )

        if hasil_rec["status"] == "no_dimension_data":
            self.hero_banner._rec_title.value = "Keep rating to improve your recommendations."
            self.hero_banner._rec_reason.value = "Not enough dimension data yet."
            self.hero_banner._hide_rec_empty_state()
            self._safe_update(self)
            return

        if hasil_rec["status"] == "empty_catalog":
            self.hero_banner._rec_title.value = "You've conquered our catalog!"
            self.hero_banner._rec_reason.value = "No more anime left to recommend."
            self.hero_banner._hide_rec_empty_state()
            self._safe_update(self)
            return

        best_anime = hasil_rec["anime"]

        self.hero_banner.anime_id = best_anime.get("anime_id")
        self.hero_banner._rec_title.value = best_anime.get("title", "—")
        self.hero_banner._rec_reason.value = hasil_rec["alasan"]
        self.hero_banner._rec_synopsis.value = best_anime.get("synopsis", "No synopsis available.")

        path_banner = best_anime.get("banner_path", "")
        path_hd = best_anime.get("cover_path_hd", "")
        path_lokal = best_anime.get("cover_path") or best_anime.get("thumbnail_path", "")
        cover_terpilih = path_banner if path_banner else (path_hd if path_hd else path_lokal)

        if cover_terpilih:
            full_path = os.path.join(ROOT_DIR, cover_terpilih)
            if os.path.exists(full_path):
                self.hero_banner._rec_image_container.src = full_path
                self.hero_banner._show_rec_content()
                self._safe_update(self.hero_banner._rec_image_container)

        self._safe_update(self.hero_banner._rec_synopsis)
        self._safe_update(self)

    def _muat_recent(self, user_id):
        self.recent_section.inner_row.controls.clear()
        if not user_id or not self._cached_anime_rated:
            self.recent_section.inner_row.controls.append(
                ft.Container(
                    width=320, height=180,
                    gradient=ft.LinearGradient(begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                                               colors=[self.theme["card"], self.theme["bg"]]),
                    border=ft.Border.all(1, self.theme["border_color"]), border_radius=16, padding=20,
                    margin=ft.padding.only(left=4, right=4, top=10, bottom=10),
                    content=ft.Column(
                        controls=[
                            ft.Text("( ╥ω╥ )", size=32, color=self.theme["primary"], weight=ft.FontWeight.BOLD),
                            ft.Text("Oops, you haven't rated any anime yet!", color=self.theme["text_main"], size=13,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text("Rate your favorite anime to get personalized recommendations.",
                                    color=self.theme["text_secondary"], size=11, text_align=ft.TextAlign.CENTER),
                            ft.Container(height=5),
                            ft.ElevatedButton(
                                "Explore Catalog",
                                icon=ft.Icons.EXPLORE,
                                on_click=lambda _: self.screen_manager.tampilkan_katalog(),
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=10),
                                    padding=ft.padding.symmetric(horizontal=20, vertical=12),
                                    elevation=0,
                                    overlay_color=ft.Colors.TRANSPARENT,
                                    color=self.theme["card"],
                                    bgcolor={
                                        ft.ControlState.HOVERED: ft.Colors.with_opacity(0.8, self.theme["primary"]),
                                        ft.ControlState.DEFAULT: self.theme["primary"],
                                    }
                                )
                            ),
                        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4,
                    ), alignment=ft.Alignment(0, 0),
                )
            )
            return

        recent_animes = [a for a, _ in self._cached_anime_rated[:10]]
        self._isi_katalog_row(self.recent_section.inner_row, recent_animes, self._cached_skor_user, pakai_skor_personal=True)

    def _muat_trending(self, user_id):
        trending_sorted = self.data_manager.get_trending_anime(self._cached_semua_anime, limit=7)
        self._isi_katalog_row(self.trending_section.inner_row, trending_sorted, self._cached_skor_user,
                              pakai_skor_personal=True if user_id else False)

    def _muat_top_unrated(self, user_id):
        unrated_sorted = self.data_manager.get_top_unrated(self._cached_anime_unrated, limit=10)
        self._isi_katalog_row(self.unrated_section.inner_row, unrated_sorted, {}, pakai_skor_personal=False)

        if not self._cached_anime_unrated:
            self.unrated_section.inner_row.controls.append(
                ft.Text("You've rated all available anime!", color=self.theme["text_muted"], size=12))

    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._safe_update(self._sidebar_widget)

    def _safe_update(self, control):
        try:
            if control and control.page:
                control.update()
        except Exception:
            pass

    def _build_topbar(self):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=16), height=55,
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            bgcolor=ft.Colors.with_opacity(0.8, self.theme["bg"]),
            shadow=ft.BoxShadow(blur_radius=15, color="#15000000", offset=ft.Offset(0, 4)),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.MENU,
                        tooltip="Menu",
                        on_click=self._toggle_sidebar,
                        style=ft.ButtonStyle(
                            overlay_color=ft.Colors.TRANSPARENT,
                            icon_color={
                                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.8, self.theme["primary"]),
                                ft.ControlState.DEFAULT: self.theme["primary"],
                            }
                        )
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                spacing=0,
                                controls=[
                                    ft.Text(huruf, font_family="Hitchcut", size=24, color=self.theme["logo_1" if i % 2 == 0 else "logo_2"])
                                    for i, huruf in enumerate("RadarAni")
                                ]
                            ),
                            ft.Text("レーダアニ", font_family="Mofuji04", size=10, color=self.theme["text_muted"]),
                        ], spacing=0, tight=True,
                    ),
                    ft.Container(expand=True),

                    self.theme_picker.get_button(),

                    ft.IconButton(
                        icon=ft.Icons.ACCOUNT_CIRCLE,
                        tooltip="Profile",
                        on_click=lambda _: self.screen_manager.tampilkan_profil(),
                        style=ft.ButtonStyle(
                            overlay_color=ft.Colors.TRANSPARENT,
                            icon_color={
                                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.8, self.theme["primary"]),
                                ft.ControlState.DEFAULT: self.theme["text_muted"]
                            }
                        )
                    )
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

    def _klik_rekomendasi(self):
        if self.hero_banner.anime_id:
            self.screen_manager.tampilkan_detail(self.hero_banner.anime_id)
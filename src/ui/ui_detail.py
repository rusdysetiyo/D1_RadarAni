import flet as ft
import flet.canvas as cv
import math
from src.ui.icons import _sakura_icon_svg
from src.ui.ui_home import AnimeCardSmall
from src.ui.radar_chart import detail_radar_chart
import random
import os
from src.config.theme import ThemeManager



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))

# ═══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════
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
                    controls=[detail_radar_chart(global_scores, personal_scores, labels, theme)]
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
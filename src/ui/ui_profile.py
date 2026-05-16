# -*- coding: utf-8 -*-
import flet as ft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64

class UIProfile(ft.Container):
    def __init__(self, page: ft.Page, data_manager, auth_manager, screen_manager):
        super().__init__(expand=True)
        self._page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager
        
        self.content = self.bangun_ui()

    # Warna tema
    _PINK_DARK = "#b5476e"
    _PINK_MID = "#e07aaa"
    _PINK_LIGHT = "#fce8f0"
    _PINK_BORDER = "#f3d8e8"
    _TEXT_DARK = "#3D2535"
    _TEXT_MUTED = "#b08090"
    _BG = "#fdf6f9"
    _WHITE = "#ffffff"

    # Chart
    def gambar_bar_chart(self, rata_rata: dict) -> str:
        dimensi = list(rata_rata.keys())
        nilai = list(rata_rata.values())

        fig, ax = plt.subplots(figsize=(8.0, 3.0))
        fig.patch.set_facecolor(self._BG)
        ax.set_facecolor(self._BG)

        bar_color  = "#d84b8a"
        track_color = "#f3d8e8"
        line_color  = "#ffffff"
        max_nilai  = 10
        bar_height = 0.22   # tipis
        line_width = 1.4    # garis tengah pada batang

        for i, (dim, val) in enumerate(zip(dimensi, nilai)):
            # Track (background bar)
            ax.barh(i, max_nilai, color=track_color, height=bar_height, zorder=1)
            # Bar isi
            ax.barh(i, val, color=bar_color, height=bar_height, zorder=2)
            # Garis tengah horizontal di atas batang (seperti outline/stroke)
            ax.plot([0, val], [i, i], color=line_color,
                    linewidth=line_width, zorder=3, solid_capstyle="round")
            # Label nilai
            ax.text(max_nilai + 0.15, i, str(val),
                    va="center", ha="left", fontsize=10,
                    fontweight="bold", color="#2d1a2e")

        ax.set_yticks(range(len(dimensi)))
        ax.set_yticklabels(dimensi, fontsize=10, color="#6b4460", fontweight="600")
        ax.set_xlim(0, max_nilai + 0.9)
        ax.set_ylim(-0.6, len(dimensi) - 0.4)
        ax.invert_yaxis()
        ax.xaxis.set_visible(False)
        ax.spines[:].set_visible(False)
        ax.tick_params(left=False)
        plt.tight_layout(pad=0.6)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, facecolor=fig.get_facecolor())
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")


    def gambar_pie_chart(self, proporsi_genre: dict) -> str:
        labels = list(proporsi_genre.keys())
        sizes = list(proporsi_genre.values())
        colors = ["#c06080", "#e07aaa", "#f5b8d0", "#f8d0e4", "#b08090"]

        fig, ax = plt.subplots(figsize=(2.2, 2.2))
        fig.patch.set_facecolor(self._WHITE)
        ax.set_facecolor(self._WHITE)

        wedge_props = {"linewidth": 1.5, "edgecolor": "white"}
        ax.pie(
            sizes,
            colors=colors[:len(sizes)],
            startangle=90,
            wedgeprops=wedge_props,
            radius=1.0,
        )
        plt.tight_layout(pad=0.2)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")


    # Tombol Aksi
    def aksi_tombol_kembali(self, e):
        self.screen_manager.tampilkan_home()

    def aksi_tombol_hapus_akun(self, e):
        self.auth_manager.hapus_akun_aktif()
        self.screen_manager.tampilkan_login()


    # Muat Data
    def muat_data_profil(self) -> dict:
        _FALLBACK = {
            "user": {"username": "-", "user_id": "-", "created_at": "-"},
            "statistik": {},
            "anime": [],
            "genre": {},
        }
        user_id = self.auth_manager.get_user_aktif()
        if user_id is None:
            self.screen_manager.tampilkan_login()
            return _FALLBACK
        user = self.data_manager.get_user_by_id(user_id)
        if user is None:
            self.auth_manager.logout()
            self.screen_manager.tampilkan_login()
            return _FALLBACK
        statistik = self.data_manager.get_avg_dimensi_user(user_id)
        anime     = self.data_manager.get_anime_favorit(user_id)
        genre     = self.data_manager.get_top_genre_user(user_id)
        return {
            "user": user,
            "statistik": statistik,
            "anime": anime,
            "genre": genre,
        }


    # Widget

    def _info_row(self, label: str, value: str, is_last: bool = False) -> ft.Container:
        # Baris Tabel Info Akun
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(label, size=12, color=self._TEXT_MUTED, weight=ft.FontWeight.W_600),
                    ft.Text(value, size=12, color=self._TEXT_DARK, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=12, vertical=9),
            border=ft.border.only(
                bottom=ft.BorderSide(1, self._PINK_BORDER) if not is_last else None
            ),
        )


    def _anime_item(self, rank: int, judul: str, genre: str) -> ft.Container:
        # Satu Baris Item Anime Favorit
        return ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(f"#{rank}", size=11, color=self._PINK_MID,
                            weight=ft.FontWeight.W_800, width=22),
                    ft.Text(judul, size=12, color=self._TEXT_DARK,
                            weight=ft.FontWeight.BOLD, expand=True),
                    ft.Container(
                        content=ft.Text(genre, size=10, color=self._PINK_DARK,
                                        weight=ft.FontWeight.W_600),
                        bgcolor=self._PINK_BORDER,
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                    ),
                ],
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor="#fdf0f5",
            border=ft.border.all(1, self._PINK_BORDER),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=10, vertical=8),
        )

    # Ketika data tidak tersedia
    def _empty_state(self, pesan: str) -> ft.Container:
            return ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(ft.Icons.INBOX_OUTLINED, color=self._PINK_BORDER, size=28),
                        ft.Text(pesan, size=11, color=self._TEXT_MUTED,
                                text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                bgcolor="#fdf0f5",
                border=ft.border.all(1, self._PINK_BORDER),
                border_radius=10,
                padding=ft.padding.symmetric(horizontal=10, vertical=14),
                alignment=ft.Alignment(0, 0),
                width=float("inf"),
            )


    def _section_title(self, teks: str) -> ft.Text:
        return ft.Text(
            teks.upper(),
            size=10,
            color=self._TEXT_MUTED,
            weight=ft.FontWeight.W_800,
            style=ft.TextStyle(letter_spacing=1.2),
        )


    def _chart_card(
        self,
        judul_label: str,
        chart_widget: ft.Control,
        footer_label: str,
        body_height: int = None,
    ) -> ft.Container:
        # Card Pembungkus Chart (bar / pie)
        body = ft.Container(
            content=chart_widget,
            padding=14,
            height=body_height,
        )
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Header
                    ft.Container(
                        content=ft.Text(
                            judul_label.upper(), size=10,
                            color=self._TEXT_MUTED, weight=ft.FontWeight.W_800,
                            style=ft.TextStyle(letter_spacing=1.1),
                        ),
                        bgcolor=self._BG,
                        padding=ft.padding.symmetric(horizontal=14, vertical=10),
                        border=ft.border.only(bottom=ft.BorderSide(1, self._PINK_BORDER)),
                        expand=True,
                    ),
                    # Body
                    body,
                    # Footer
                    ft.Container(
                        content=ft.Text(
                            footer_label.upper(), size=10,
                            color=self._TEXT_MUTED, weight=ft.FontWeight.W_800,
                            style=ft.TextStyle(letter_spacing=1.1),
                        ),
                        bgcolor=self._BG,
                        padding=ft.padding.symmetric(horizontal=14, vertical=10),
                        border=ft.border.only(top=ft.BorderSide(1, self._PINK_BORDER)),
                        expand=True,
                    ),
                ],
                spacing=0,
            ),
            border=ft.border.all(1, self._PINK_BORDER),
            border_radius=12,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            expand=True,
        )


    def _legend_item(self, warna: str, label: str, persen: str) -> ft.Row:
        return ft.Row(
            controls=[
                ft.Container(width=10, height=10, bgcolor=warna,
                            border_radius=10),
                ft.Text(label, size=11, color=self._TEXT_DARK,
                        weight=ft.FontWeight.W_600, expand=True),
                ft.Text(persen, size=11, color=self._TEXT_MUTED,
                        weight=ft.FontWeight.BOLD),
            ],
            spacing=7,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )


    def _no_rating_placeholder(self) -> ft.Container:
        """Panel kanan ketika user belum pernah memberi rating sama sekali."""
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(ft.Icons.STAR_BORDER_ROUNDED, color=self._PINK_BORDER, size=52),
                    ft.Text("Belum Ada Rating", size=16, weight=ft.FontWeight.W_800,
                            color=self._TEXT_DARK, text_align=ft.TextAlign.CENTER),
                    ft.Text(
                        "Kamu belum pernah memberi rating anime apapun.\n"
                        "Mulai eksplorasi katalog dan beri penilaianmu!",
                        size=12, color=self._TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(
                        content=ft.Text(">> Buka Katalog", size=12, color=self._PINK_DARK,
                                        weight=ft.FontWeight.W_700),
                        bgcolor=self._PINK_LIGHT,
                        border=ft.border.all(1.5, "#e8b4cb"),
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=18, vertical=8),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=12,
            ),
            expand=True,
            alignment=ft.Alignment(0, 0),
        )

    def _partial_rating_placeholder(self, statistik: dict, genre_proporsi: dict) -> ft.Container:
        """
        Panel kanan ketika user sudah rating tapi data tidak lengkap:
        - ada statistik tapi tidak ada genre, atau sebaliknya.
        Tetap tampilkan chart yang ada + pesan untuk bagian yang kosong.
        """
        ada_statistik = bool(statistik)
        ada_genre     = bool(genre_proporsi)

        # Bar chart (jika ada)
        if ada_statistik:
            bar_b64   = self.gambar_bar_chart(statistik)
            bar_image = ft.Image(
                src=f"data:image/png;base64,{bar_b64}",
                fit="contain",
                expand=True,
            )
            bar_card  = self._chart_card(
                judul_label="Bar Chart - Rata-Rata Dimensi",
                chart_widget=bar_image,
                footer_label="Rata-rata dari semua rating yang diberikan",
                body_height=180,
            )
        else:
            bar_card = self._empty_state("Data statistik belum tersedia.\nBeri rating pada beberapa anime.")

        # Pie chart (jika ada)
        if ada_genre:
            pie_b64   = self.gambar_pie_chart(genre_proporsi)
            genre_colors = ["#c06080", "#e07aaa", "#f5b8d0", "#f8d0e4", "#b08090"]
            legend_items = [
                self._legend_item(genre_colors[i % len(genre_colors)], label, f"{pct}%")
                for i, (label, pct) in enumerate(genre_proporsi.items())
            ]
            pie_body = ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Image(
                            src=f"data:image/png;base64,{pie_b64}",
                            fit="contain",
                        ),
                        expand=1,
                        alignment=ft.Alignment(0, 0),
                    ),
                    ft.Container(
                        content=ft.Column(legend_items, spacing=8),
                        expand=1,
                        alignment=ft.Alignment(-1, 0),
                    ),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
            pie_card = self._chart_card(
                judul_label="Pie Chart - Proporsi Genre Favorit",
                chart_widget=pie_body,
                footer_label="Top 5 genre dari semua anime yang dirating",
                body_height=160,
            )
        else:
            pie_card = self._empty_state("Data genre belum tersedia.\nBeri rating pada lebih banyak anime.")

        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Statistik Penilaian", size=17,
                            weight=ft.FontWeight.W_800, color=self._TEXT_DARK),
                    ft.Text("Berdasarkan semua rating yang telah kamu berikan",
                            size=11, color=self._TEXT_MUTED),
                    bar_card,
                    pie_card,
                    ft.Container(height=8),
                ],
                spacing=18,
                scroll=ft.ScrollMode.AUTO,
            ),
            expand=True,
            padding=ft.padding.symmetric(horizontal=20, vertical=22),
        )

    # Bangun UI
    def bangun_ui(self) -> ft.Control:

        # 1. Ambil data
        data          = self.muat_data_profil()
        user          = data["user"]
        statistik     = data["statistik"]      # dict dimensi → nilai rata-rata
        anime_list    = data["anime"]          # list of dict
        genre_proporsi = data["genre"]         # dict genre → persen

        ada_statistik = bool(statistik)
        ada_genre     = bool(genre_proporsi)

        # ── Topbar ──────────────────────────────────────────────────────────
        tombol_kembali = ft.OutlinedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.CHEVRON_LEFT, color=self._PINK_DARK, size=16),
                    ft.Text("Back to Dashboard", color=self._PINK_DARK, size=12,
                            weight=ft.FontWeight.W_600),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=4,
            ),
            on_click=lambda e: self.aksi_tombol_kembali(e),
            style=ft.ButtonStyle(
                side=ft.BorderSide(1.5, "#e8b4cb"),
                shape=ft.RoundedRectangleBorder(radius=20),
                padding=ft.padding.symmetric(horizontal=14, vertical=5),
            ),
        )
        top_bar = ft.Container(
            content=ft.Row(
                controls=[
                    tombol_kembali,
                    ft.Text("RadarAni — プロフィール", size=13,
                            weight=ft.FontWeight.BOLD, color=self._PINK_DARK),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.symmetric(horizontal=20, vertical=12),
            border=ft.border.only(bottom=ft.BorderSide(1, self._PINK_BORDER)),
        )

        # ── Panel Kiri (expand=3, ~28% dari lebar window) ───────────────────
        # Avatar
        avatar = ft.Container(
            content=ft.Text("桜", size=36, color=self._PINK_DARK,
                            text_align=ft.TextAlign.CENTER,
                            style=ft.TextStyle(font_family="serif")),
            width=88, height=88, border_radius=44,
            border=ft.border.all(2.5, "#e8b4cb"),
            bgcolor=self._PINK_LIGHT,
            alignment=ft.Alignment(0, 0),
        )

        # Stat strip: Rated | Avg | Genres
        total_rated  = user.get("rating_count", 0)  # dari users.json, akurat
        avg_overall  = round(sum(statistik.values()) / len(statistik), 1) if statistik else 0.0
        total_genres = len(genre_proporsi)
        stat_strip = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Column([
                            ft.Text(str(total_rated), size=16, weight=ft.FontWeight.W_800,
                                    color=self._PINK_DARK, text_align=ft.TextAlign.CENTER),
                            ft.Text("Rated", size=9, color=self._TEXT_MUTED,
                                    text_align=ft.TextAlign.CENTER),
                        ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=1, padding=ft.padding.symmetric(vertical=8),
                    ),
                    ft.VerticalDivider(width=1, color=self._PINK_BORDER),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(str(avg_overall), size=16, weight=ft.FontWeight.W_800,
                                    color=self._PINK_DARK, text_align=ft.TextAlign.CENTER),
                            ft.Text("Avg", size=9, color=self._TEXT_MUTED,
                                    text_align=ft.TextAlign.CENTER),
                        ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=1, padding=ft.padding.symmetric(vertical=8),
                    ),
                    ft.VerticalDivider(width=1, color=self._PINK_BORDER),
                    ft.Container(
                        content=ft.Column([
                            ft.Text(str(total_genres), size=16, weight=ft.FontWeight.W_800,
                                    color=self._PINK_DARK, text_align=ft.TextAlign.CENTER),
                            ft.Text("Genres", size=9, color=self._TEXT_MUTED,
                                    text_align=ft.TextAlign.CENTER),
                        ], spacing=1, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        expand=1, padding=ft.padding.symmetric(vertical=8),
                    ),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            border=ft.border.all(1, self._PINK_BORDER),
            border_radius=10,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            bgcolor=self._PINK_LIGHT,
        )

        # Tabel Info Akun (5 baris)
        info_rows = [
            self._info_row("Username",     user.get("username", "-")),
            self._info_row("User ID",      user.get("user_id", "-")),
            self._info_row("Created At",   str(user.get("created_at", "-"))[:10]),
            self._info_row("Last Login",   str(user.get("last_login", "-"))[:10]),
            self._info_row("Total Ratings", str(total_rated) + " anime", is_last=True),
        ]
        account_info_card = ft.Container(
            content=ft.Column(info_rows, spacing=0),
            border=ft.border.all(1, self._PINK_BORDER),
            border_radius=10,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        # Daftar Anime Favorit
        if anime_list:
            anime_section_content = ft.Column(
                controls=[
                    self._anime_item(
                        rank=i + 1,
                        judul=a.get("title", "Unknown"),
                        genre=", ".join(a.get("genre", [])[:1]) or "-",
                    )
                    for i, a in enumerate(anime_list)
                ],
                spacing=7,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            )
        else:
            anime_section_content = self._empty_state(
                "Belum ada anime favorit.\nBeri rating agar muncul di sini."
            )

        # Tombol Hapus Akun
        tombol_hapus = ft.ElevatedButton(
            content=ft.Row(
                controls=[
                    ft.Icon(ft.Icons.DELETE_OUTLINE_ROUNDED, color=self._WHITE, size=16),
                    ft.Text("Hapus Akun", color=self._WHITE, size=13,
                            weight=ft.FontWeight.W_800,
                            style=ft.TextStyle(letter_spacing=0.3)),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=6,
            ),
            on_click=lambda e: self.aksi_tombol_hapus_akun(e),
            style=ft.ButtonStyle(
                bgcolor=self._PINK_DARK,
                overlay_color=ft.Colors.with_opacity(0.12, self._WHITE),
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=0, vertical=11),
            ),
            width=float("inf"),
        )

        panel_kiri = ft.Container(
            content=ft.Column(
                controls=[
                    avatar,
                    ft.Text(user.get("username", "-"),
                            size=16, weight=ft.FontWeight.W_800,
                            color=self._TEXT_DARK, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"Member since {str(user.get('created_at', ''))[:10]}",
                            size=10, color=self._TEXT_MUTED,
                            text_align=ft.TextAlign.CENTER),
                    stat_strip,
                    self._section_title("Account Info"),
                    account_info_card,
                    self._section_title("Anime Favorit"),
                    anime_section_content,
                    tombol_hapus,
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                scroll=ft.ScrollMode.AUTO,
                expand=True,
            ),
            expand=3,                   # ~28% dari Row
            padding=ft.padding.symmetric(horizontal=18, vertical=20),
            border=ft.border.only(right=ft.BorderSide(1, self._PINK_BORDER)),
            bgcolor=self._BG,
        )

        # ── Panel Kanan (expand=7, ~72% dari lebar window) ──────────────────
        if not ada_statistik and not ada_genre:
            panel_kanan = ft.Container(
                content=self._no_rating_placeholder(),
                expand=7,
            )
        else:
            # Dimension summary cards (baris atas, 6 card = 5 dimensi + 1 overall)
            all_dims = list(statistik.items()) if ada_statistik else []
            overall_val = round(sum(v for _, v in all_dims) / len(all_dims), 1) if all_dims else 0.0

            def _dim_card(label, val, highlight=False):
                pct = val / 10
                return ft.Container(
                    content=ft.Column([
                        ft.Text(label, size=9, color=self._PINK_DARK if highlight else self._TEXT_MUTED,
                                weight=ft.FontWeight.W_700),
                        ft.Text(str(val), size=22, weight=ft.FontWeight.W_800,
                                color=self._PINK_DARK, height=26),
                        ft.Text("/ 10", size=9, color=self._TEXT_MUTED),
                        ft.Container(
                            content=ft.Container(
                                bgcolor=self._PINK_DARK,
                                border_radius=99,
                                width=pct,      # akan di-scale via expand
                            ),
                            bgcolor=self._PINK_BORDER,
                            border_radius=99,
                            height=4,
                            expand=True,
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        ),
                    ], spacing=3),
                    bgcolor="#fce8f0" if highlight else self._PINK_LIGHT,
                    border=ft.border.all(1, "#f9a8c9" if highlight else self._PINK_BORDER),
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    expand=1,
                )

            dim_cards_controls = [
                _dim_card(label, val) for label, val in all_dims
            ] + [_dim_card("Overall Avg", overall_val, highlight=True)]

            dim_row = ft.Row(
                controls=dim_cards_controls,
                spacing=10,
            )

            # Charts bawah: bar chart kiri + pie chart kanan
            if ada_statistik:
                bar_b64   = self.gambar_bar_chart(statistik)
                bar_image = ft.Image(
                    src=f"data:image/png;base64,{bar_b64}",
                    fit="contain",
                    expand=True,
                )
                bar_card = self._chart_card(
                    judul_label="Bar Chart - Rata-Rata Dimensi",
                    chart_widget=bar_image,
                    footer_label="Rata-rata dari semua rating yang diberikan",
                    body_height=None,
                )
            else:
                bar_card = self._empty_state("Data statistik belum tersedia.")

            if ada_genre:
                pie_b64      = self.gambar_pie_chart(genre_proporsi)
                genre_colors = ["#c06080", "#e07aaa", "#f5b8d0", "#f8d0e4", "#b08090"]
                legend_items = [
                    self._legend_item(genre_colors[i % len(genre_colors)], label, f"{pct}%")
                    for i, (label, pct) in enumerate(genre_proporsi.items())
                ]
                pie_body = ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Image(
                                src=f"data:image/png;base64,{pie_b64}",
                                fit="contain",
                            ),
                            expand=1,
                            alignment=ft.Alignment(0, 0),
                        ),
                        ft.Container(
                            content=ft.Column(legend_items, spacing=8),
                            expand=1,
                            alignment=ft.Alignment(-1, 0),
                        ),
                    ],
                    spacing=0,
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
                pie_card = self._chart_card(
                    judul_label="Pie Chart - Proporsi Genre Favorit",
                    chart_widget=pie_body,
                    footer_label="Top 5 genre dari semua anime yang dirating",
                    body_height=None,
                )
            else:
                pie_card = self._empty_state("Data genre belum tersedia.")

            charts_row = ft.Row(
                controls=[bar_card, pie_card],
                spacing=14,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
            )

            panel_kanan = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Statistik Penilaian", size=16,
                                weight=ft.FontWeight.W_800, color=self._TEXT_DARK),
                        ft.Text("Berdasarkan semua rating yang telah kamu berikan",
                                size=11, color=self._TEXT_MUTED),
                        dim_row,
                        charts_row,
                    ],
                    spacing=14,
                    expand=True,
                ),
                expand=7,               # ~72% dari Row
                padding=ft.padding.symmetric(horizontal=22, vertical=20),
            )

        # ── Layout Utama ────────────────────────────────────────────────────
        layout = ft.Container(
            content=ft.Column(
                controls=[
                    top_bar,
                    ft.Row(
                        controls=[panel_kiri, panel_kanan],
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                        expand=True,
                    ),
                ],
                spacing=0,
                expand=True,
            ),
            bgcolor=self._WHITE,
            border_radius=18,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=32,
                color=ft.Colors.with_opacity(0.10, "#dc6496"),
            ),
            expand=True,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        return layout
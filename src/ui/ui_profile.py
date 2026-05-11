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

        fig, ax = plt.subplots(figsize=(5.2, 2.6))
        fig.patch.set_facecolor(self._BG)
        ax.set_facecolor(self._BG)

        bar_color = "#d84b8a"
        track_color = "#f3d8e8"
        max_nilai = 10

        for i, (dim, val) in enumerate(zip(dimensi, nilai)):
            # Background
            ax.barh(i, max_nilai, color=track_color, height=0.5, zorder=1)
            # Bar isi
            ax.barh(i, val, color=bar_color, height=0.5, zorder=2)
            # Label Nilai
            ax.text(max_nilai + 0.1, i, str(val),
                    va="center", ha="left", fontsize=9,
                    fontweight="bold", color="#2d1a2e")

        ax.set_yticks(range(len(dimensi)))
        ax.set_yticklabels(dimensi, fontsize=9, color="#6b4460", fontweight="600")
        ax.set_xlim(0, max_nilai + 0.8)
        ax.set_ylim(-0.6, len(dimensi) - 0.4)
        ax.invert_yaxis()
        ax.xaxis.set_visible(False)
        ax.spines[:].set_visible(False)
        ax.tick_params(left=False)
        plt.tight_layout(pad=0.4)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=120, facecolor=fig.get_facecolor())
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
    def aksi_tombol_hapus_akun(self, e):
        if self.auth_manager.hapus_akun_aktif():
            self.screen_manager.tampilkan_login()


    # Muat Data
    def muat_data_profil(self) -> dict:
        user_id = self.auth_manager.get_user_aktif()
        user = self.data_manager.get_user_by_id(user_id)
        statistik = self.data_manager.get_avg_dimensi_user(user_id)
        anime = self.data_manager.get_anime_favorit(user_id)
        genre = self.data_manager.get_top_genre_user(user_id)

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
        fn_label: str,
        chart_widget: ft.Control,
        footer_text: str,
    ) -> ft.Container:
        # Card Pembungkus Chart (bar / pie)
        return ft.Container(
            content=ft.Column(
                controls=[
                    # Header
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(judul_label.upper(), size=10,
                                        color=self._TEXT_MUTED, weight=ft.FontWeight.W_800,
                                        style=ft.TextStyle(letter_spacing=1.1)),
                                ft.Container(
                                    content=ft.Text(fn_label, size=10,
                                                    color=self._PINK_DARK,
                                                    weight=ft.FontWeight.BOLD,
                                                    style=ft.TextStyle(font_family="monospace")),
                                    bgcolor=self._PINK_BORDER,
                                    border_radius=6,
                                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        bgcolor=self._BG,
                        padding=ft.padding.symmetric(horizontal=14, vertical=10),
                        border=ft.border.only(bottom=ft.BorderSide(1, self._PINK_BORDER)),
                    ),
                    # Body
                    ft.Container(chart_widget, padding=14),
                    # Footer
                    ft.Container(
                        content=ft.Text(footer_text, size=10, color=self._TEXT_MUTED,
                                        style=ft.TextStyle(italic=True)),
                        bgcolor=self._BG,
                        padding=ft.padding.symmetric(horizontal=14, vertical=8),
                        border=ft.border.only(top=ft.BorderSide(1, self._PINK_BORDER)),
                    ),
                ],
                spacing=0,
            ),
            border=ft.border.all(1, self._PINK_BORDER),
            border_radius=12,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
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


    # Bangun UI
    def bangun_ui(self) -> ft.Control:

        # 1. Ambil data
        data = self.muat_data_profil()
        user = data["user"]
        statistik = data["statistik"]          # dict dimensi → nilai
        anime_list = data["anime"]             # list of dict {rank, judul, genre}
        genre_proporsi = data["genre"]         # dict genre → persen

        ada_statistik = bool(statistik)
        ada_genre     = bool(genre_proporsi)


        # 2. Panel Kiri
        # Avatar
        avatar = ft.Container(
            content=ft.Text("桜", size=36, color=self._PINK_DARK,
                            text_align=ft.TextAlign.CENTER,
                            style=ft.TextStyle(font_family="serif")),
            width=88, height=88,
            border_radius=44,
            border=ft.border.all(2.5, "#e8b4cb"),
            bgcolor=self._PINK_LIGHT,
            alignment=ft.Alignment(0, 0),
        )

        # Tabel Info Akun
        info_rows = [
            self._info_row("Username", user.get("username", "-")),
            self._info_row("User ID", user.get("user_id", "-")),
            self._info_row("Created At", user.get("created_at", "-"), is_last=True),
        ]
        account_info_card = ft.Container(
            content=ft.Column(info_rows, spacing=0),
            border=ft.border.all(1, self._PINK_BORDER),
            border_radius=10,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        # list Anime Favorit
        if anime_list:
            anime_section_content = ft.Column(
                controls=[
                    self._anime_item(a["rank"], a["judul"], a["genre"])
                    for a in anime_list
                ],
                spacing=7,
            )
        else:
            anime_section_content = self._empty_state("Belum ada anime favorit.\nBeri rating untuk anime agar muncul di sini.")


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
                    ft.Text(user.get("username", "sakura_user"),
                            size=17, weight=ft.FontWeight.W_800,
                            color=self._TEXT_DARK, text_align=ft.TextAlign.CENTER),
                    ft.Text(f"Member since {user.get('created_at', '')}",
                            size=11, color=self._TEXT_MUTED,
                            text_align=ft.TextAlign.CENTER),
                    ft.Container(height=2),
                    self._section_title("Account Info"),
                    account_info_card,
                    ft.Container(height=2),
                    self._section_title("Anime Favorit"),
                    ft.Column(anime_section_content, spacing=7),
                    ft.Container(height=2),
                    tombol_hapus,
                ],
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            width=265,
            padding=ft.padding.symmetric(horizontal=20, vertical=24),
            border=ft.border.only(right=ft.BorderSide(1, self._PINK_BORDER)),
        )


        # 3. Panel Kanan
        if not ada_statistik and not ada_genre:
            panel_kanan = self._no_rating_placeholder()
        else:
            # Bar Chart
            if ada_statistik:
                bar_b64   = self.gambar_bar_chart(statistik)
                bar_image = ft.Image(src=f"data:image/png;base64,{bar_b64}", width=440, fit="contain")
                bar_card  = self._chart_card(
                    judul_label="Bar Chart — Rata-Rata Dimensi",
                    fn_label="gambar_bar_chart()",
                    chart_widget=bar_image,
                    footer_text=" ",
                )
            else:
                bar_card = self._empty_state("Data statistik belum tersedia.")


            # Pie Chart + Legend
            if ada_genre:
                pie_b64   = self.gambar_pie_chart(genre_proporsi)
                pie_image = ft.Image(src=f"data:image/png;base64,{pie_b64}", width=110, height=110,
                                     fit="contain")
                genre_colors = ["#c06080", "#e07aaa", "#f5b8d0", "#f8d0e4", "#b08090"]
                legend_items = [
                    self._legend_item(genre_colors[i % len(genre_colors)], label, f"{pct}%")
                    for i, (label, pct) in enumerate(genre_proporsi.items())
                ]
                pie_body = ft.Row(
                    controls=[
                        pie_image,
                        ft.Column(legend_items, spacing=6, expand=True),
                    ],
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
                pie_card = self._chart_card(
                    judul_label="Pie Chart — Proporsi Genre Favorit",
                    chart_widget=pie_body,
                    footer_text=" ",
                )
            else:
                pie_card = self._empty_state("Data genre belum tersedia.")
 
            panel_kanan = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text("Statistik Penilaian", size=17,
                                weight=ft.FontWeight.W_800, color=self._TEXT_DARK),
                        ft.Text("Berdasarkan semua rating yang telah kamu berikan",
                                size=11, color=self._TEXT_MUTED),
                        bar_card,
                        pie_card,
                    ],
                    spacing=18,
                ),
                expand=True,
                padding=ft.padding.symmetric(horizontal=20, vertical=22),
            )


        # 4. Tombol Back
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
            content=tombol_kembali,
            padding=ft.padding.symmetric(horizontal=18, vertical=12),
            border=ft.border.only(bottom=ft.BorderSide(1, self._PINK_BORDER)),
        )

        
        # 5. Layout utama
        layout = ft.Container(
            content=ft.Column(
                controls=[
                    top_bar,
                    ft.Row(
                        controls=[panel_kiri, panel_kanan],
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.START,
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
        )

        return layout

import flet as ft
from src.ui.radar_chart import CustomRadarChart


class UIDetail(ft.Container):
    def __init__(self, page, data_manager, auth_manager, screen_manager, anime_id):
        super().__init__()
        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager
        self.anime_id = anime_id

        self.expand = True
        self.padding = 20
        self.bgcolor = "#FAFAFC"

        # ── Data Fetching ──
        self.user_id = self.auth_manager.get_user_aktif()
        self.anime_data = self.data_manager.get_detail_anime(self.anime_id) or {}

        user_score = self.data_manager.get_rating_user(self.user_id, self.anime_id)
        if user_score:
            self.personal_data = [
                user_score.get("plot", 0),
                user_score.get("visual", 0),
                user_score.get("audio", 0),
                user_score.get("characterization", 0),
                user_score.get("direction", 0)
            ]
        else:
            self.personal_data = [0, 0, 0, 0, 0]

        avg_personal = self.data_manager.hitung_skor_personal(self.user_id, self.anime_id)
        avg_global = self.data_manager.hitung_skor_global(self.anime_id)

        str_personal = f"{avg_personal:.1f}" if avg_personal is not None else "N/A"
        str_global = f"{avg_global:.1f}" if avg_global is not None else "N/A"

        self.global_data = self.data_manager.hitung_skor_global_radar(self.anime_id)

        # ── Setup Dynamic Score Text References ──
        self.global_score_text = ft.Text(str_global, size=28, color="#2196F3", weight=ft.FontWeight.BOLD)
        self.user_score_text = ft.Text(str_personal, size=28, color="#A0A0A0", weight=ft.FontWeight.BOLD)

        # ── Radar Chart Initialization ──
        self.radar = CustomRadarChart(
            global_scores=self.global_data,
            personal_scores=self.personal_data,
            size=350
        )

        # ── Dropdowns Setup ──
        self.dropdowns = []
        labels = ["plot", "visual", "audio", "characterization", "direction"]

        for i, label in enumerate(labels):
            dd = ft.Dropdown(
                label=label.capitalize(),
                width=135,
                options=[ft.dropdown.Option(str(n)) for n in range(1, 11)],
            )
            if self.personal_data[i] > 0:
                dd.value = str(self.personal_data[i])

            self.dropdowns.append(dd)

        # ── Anime Additional Details Setup ──
        genres = self.anime_data.get("genres", ["Action", "Adventure"])
        if isinstance(genres, str):
            genres = [genres]

        info_row = ft.Row(
            spacing=20,
            controls=[
                ft.Container(
                    content=ft.Text(self.anime_data.get("broadcast", "TV"), size=11, color="#888888"),
                    padding=ft.padding.symmetric(horizontal=10, vertical=3),
                    border=ft.border.all(1, "#C07090"),
                    border_radius=10
                ),
                ft.Text(f"Eps: {self.anime_data.get('episodes', '?')}", size=11, color="#888888"),
                ft.Text(f"Studio: {self.anime_data.get('studio', '?')}", size=11, color="#888888"),
                ft.Text(f"Year: {self.anime_data.get('year', '?')}", size=11, color="#888888"),
            ]
        )

        genre_row = ft.Row(
            spacing=10,
            wrap=True,
            controls=[
                ft.Container(
                    content=ft.Text(g, size=11, color="#555555"),
                    padding=ft.padding.symmetric(horizontal=15, vertical=5),
                    bgcolor="#EAEAEA",
                    border=ft.border.all(1, "#D890A8"),
                    border_radius=15
                ) for g in genres
            ]
        )

        # ── Left Column: Anime Info ──
        left_column = ft.Column(
            expand=1,
            controls=[
                ft.TextButton(
                    "← Back to Dashboard",
                    icon_color="#555555",
                    on_click=lambda e: self.screen_manager.tampilkan_home()
                ),
                ft.Container(
                    width=300, height=400, bgcolor="#EAEAEA", border_radius=15,
                    content=ft.Image(
                        src=self.anime_data.get("cover_path", ""),
                        fit=ft.BoxFit.COVER
                    ) if self.anime_data.get("cover_path") else ft.Icon(ft.icons.IMAGE, size=50, color="#CCCCCC")
                ),
                ft.Text(self.anime_data.get("title", "Anime Title"), size=24, weight=ft.FontWeight.BOLD),
                info_row,
                genre_row,
                ft.Container(
                    bgcolor="#EAEAEA", padding=15, border_radius=10, margin=ft.margin.only(top=10),
                    content=ft.Text(self.anime_data.get("synopsis", "Synopsis not available."))
                )
            ]
        )

        # ── Right Column: Scores & Radar Chart ──
        right_column = ft.Container(
            expand=2,
            bgcolor=ft.Colors.WHITE,
            border_radius=15,
            padding=30,
            shadow=ft.BoxShadow(blur_radius=15, color="#08000000"),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            self._score_card("GLOBAL SCORE", self.global_score_text, "Community Average"),
                            self._score_card("USER SCORE", self.user_score_text, "Your Rating"),
                        ]
                    ),
                    ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                    self.radar,
                    ft.Divider(height=30, color=ft.Colors.TRANSPARENT),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                        wrap=True,
                        controls=self.dropdowns
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.ElevatedButton("Save Rating", bgcolor="#FFB7C5", color=ft.Colors.WHITE, width=200,
                                              on_click=self.save_rating),
                            ft.OutlinedButton("Delete Rating", width=200, on_click=self.delete_rating),
                        ]
                    )
                ]
            )
        )

        # ── Main Wrapper ──
        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[left_column, right_column]
                )
            ]
        )

    # ── Score Card Component ──
    def _score_card(self, title, score_text_widget, subtitle):
        return ft.Container(
            padding=15, bgcolor="#F5F5F5", border_radius=10, width=180,
            content=ft.Column(
                spacing=2,
                controls=[
                    ft.Text(title, size=10, color="#888888", weight=ft.FontWeight.BOLD),
                    score_text_widget,
                    ft.Text(subtitle, size=10, color="#AAAAAA"),
                ]
            )
        )

    # ── Rating CRUD Logic ──
    def save_rating(self, e):
        new_score = {
            "plot": int(self.dropdowns[0].value) if self.dropdowns[0].value else 0,
            "visual": int(self.dropdowns[1].value) if self.dropdowns[1].value else 0,
            "audio": int(self.dropdowns[2].value) if self.dropdowns[2].value else 0,
            "characterization": int(self.dropdowns[3].value) if self.dropdowns[3].value else 0,
            "direction": int(self.dropdowns[4].value) if self.dropdowns[4].value else 0,
        }

        if 0 in new_score.values():
            print("Please fill out all dimensions before saving!")
            return

        self.data_manager.simpan_rating(self.user_id, self.anime_id, new_score)
        print("Rating saved successfully!")

        self.personal_data = [
            new_score["plot"], new_score["visual"], new_score["audio"],
            new_score["characterization"], new_score["direction"]
        ]

        self.radar.update_personal_scores(self.personal_data, self.my_page)

        self.global_data = self.data_manager.hitung_skor_global_radar(self.anime_id)
        self.radar.global_scores = self.global_data
        self.radar._draw_static_background()
        self.radar.static_canvas.update()

        avg_personal = self.data_manager.hitung_skor_personal(self.user_id, self.anime_id)
        self.user_score_text.value = f"{avg_personal:.1f}" if avg_personal is not None else "N/A"
        self.user_score_text.update()

        avg_global = self.data_manager.hitung_skor_global(self.anime_id)
        self.global_score_text.value = f"{avg_global:.1f}" if avg_global is not None else "N/A"
        self.global_score_text.update()

    def delete_rating(self, e):
        self.data_manager.hapus_rating(self.user_id, self.anime_id)
        print("Rating deleted successfully!")

        self.personal_data = [0, 0, 0, 0, 0]
        self.radar.update_personal_scores(self.personal_data, self.my_page)

        self.global_data = self.data_manager.hitung_skor_global_radar(self.anime_id)
        self.radar.global_scores = self.global_data
        self.radar._draw_static_background()
        self.radar.static_canvas.update()

        for dd in self.dropdowns:
            dd.value = None
            dd.update()

        self.user_score_text.value = "N/A"
        self.user_score_text.update()

        avg_global = self.data_manager.hitung_skor_global(self.anime_id)
        self.global_score_text.value = f"{avg_global:.1f}" if avg_global is not None else "N/A"
        self.global_score_text.update()
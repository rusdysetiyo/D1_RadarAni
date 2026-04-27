import flet as ft


class UIProfile(ft.Container):
    def __init__(self, page, data_manager, auth_manager, screen_manager):
        super().__init__()
        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager

        self.expand = True
        self.padding = 30
        self.bgcolor = "#FAFAFC"

        # ── Data Fetching & Aggregation ──
        self.user_id = self.auth_manager.get_user_aktif()

        users = self.data_manager._read_json(self.data_manager.users_file) or []
        user_data = next((u for u in users if u.get("user_id") == self.user_id), {})
        self.username = user_data.get("username", "Guest")

        all_ratings = self.data_manager._read_json(self.data_manager.ratings_file) or {}
        my_ratings = all_ratings.get(self.user_id, {})

        self.total_anime_rated = len(my_ratings)

        self.avg_scores = {"plot": 0, "visual": 0, "audio": 0, "characterization": 0, "direction": 0}

        if self.total_anime_rated > 0:
            for anime_id, scores in my_ratings.items():
                self.avg_scores["plot"] += scores.get("plot", 0)
                self.avg_scores["visual"] += scores.get("visual", 0)
                self.avg_scores["audio"] += scores.get("audio", 0)
                self.avg_scores["characterization"] += scores.get("characterization", 0)
                self.avg_scores["direction"] += scores.get("direction", 0)

            for key in self.avg_scores:
                self.avg_scores[key] = round(self.avg_scores[key] / self.total_anime_rated, 1)

        if self.total_anime_rated > 0:
            self.dominant_trait = max(self.avg_scores, key=self.avg_scores.get)
            self.overall_avg = round(sum(self.avg_scores.values()) / 5, 1)
        else:
            self.dominant_trait = "None"
            self.overall_avg = 0.0

        self.content = self._build_ui()

    def _build_ui(self):
        # ── Header & Back Button ──
        header = ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_IOS_NEW,
                    icon_color="#555555",
                    on_click=lambda e: self.screen_manager.tampilkan_home()
                ),
                ft.Text("User Profile", size=24, weight=ft.FontWeight.BOLD, color="#333333")
            ],
            alignment=ft.MainAxisAlignment.START
        )

        # ── Profile Details Card ──
        inisial = self.username[0].upper() if self.username != "Guest" else "?"

        def stat_box(icon_name, title, value, val_color="#333333"):
            return ft.Container(
                padding=15,
                border=ft.border.all(1, "#F0F0F0"),
                border_radius=10,
                bgcolor=ft.Colors.WHITE,
                width=160,
                content=ft.Row(
                    spacing=15,
                    controls=[
                        ft.Icon(icon_name, color="#D890A8", size=24),
                        ft.Column(
                            spacing=2,
                            controls=[
                                ft.Text(title, size=12, color="#888888"),
                                ft.Text(value, size=16, weight=ft.FontWeight.BOLD, color=val_color)
                            ]
                        )
                    ]
                )
            )

        profile_card = ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=25,
            border_radius=15,
            border=ft.border.all(1, "#F5E6EA"),
            shadow=ft.BoxShadow(blur_radius=10, color="#05000000"),
            content=ft.Column(
                spacing=20,
                controls=[
                    ft.Row(
                        spacing=20,
                        controls=[
                            ft.CircleAvatar(
                                content=ft.Text(inisial, size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                radius=35,
                                bgcolor="#C07090"
                            ),
                            ft.Column(
                                spacing=4,
                                controls=[
                                    ft.Text(self.username, size=22, weight=ft.FontWeight.BOLD, color="#333333"),
                                    ft.Text("Anime Enthusiast", size=14, color="#888888"),
                                ]
                            )
                        ]
                    ),
                    ft.Row(
                        spacing=15,
                        controls=[
                            stat_box(ft.Icons.MOVIE_CREATION_OUTLINED, "Rated Anime", str(self.total_anime_rated)),
                            stat_box(ft.Icons.SHOW_CHART, "Average Score", f"{self.overall_avg}"),
                            stat_box(ft.Icons.MENU_BOOK_ROUNDED, "Signature", self.dominant_trait.capitalize(), "#C07090"),
                        ]
                    )
                ]
            )
        )

        # ── Taste Insights & Distribution Card ──
        chart_content = [
            ft.Text("Taste Insights & Distribution", size=18, weight=ft.FontWeight.BOLD, color="#333333"),
            ft.Text(
                f"Signature Dimension: {self.dominant_trait.upper()} is your most dominant anime taste dimension.",
                size=14, color="#666666"
            ),
            ft.Divider(height=20, color=ft.Colors.TRANSPARENT)
        ]

        labels = ["plot", "visual", "audio", "characterization", "direction"]
        for label in labels:
            score = self.avg_scores.get(label, 0)
            bar_width = (score / 10) * 400 if score > 0 else 0

            is_dominant = label == self.dominant_trait
            bar_color = "#C07090" if is_dominant else "#F5E6EA"
            text_color = "#C07090" if is_dominant else "#555555"

            row = ft.Row(
                spacing=15,
                controls=[
                    ft.Container(
                        width=120,
                        alignment=ft.Alignment(1, 0),
                        content=ft.Text(label.capitalize(), size=14, color=text_color,
                                        weight=ft.FontWeight.BOLD if is_dominant else ft.FontWeight.NORMAL)
                    ),
                    ft.Container(
                        width=400,
                        height=20,
                        bgcolor="#F9F9F9",
                        border_radius=10,
                        content=ft.Row(
                            controls=[
                                ft.Container(
                                    width=bar_width,
                                    height=20,
                                    bgcolor=bar_color,
                                    border_radius=10,
                                    animate=ft.Animation(800, ft.AnimationCurve.EASE_OUT)
                                )
                            ]
                        )
                    ),
                    ft.Text(f"{score:.1f}", size=14, color="#333333", weight=ft.FontWeight.BOLD)
                ]
            )
            chart_content.append(row)

        taste_card = ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=25,
            border_radius=15,
            border=ft.border.all(1, "#F5E6EA"),
            margin=ft.margin.only(top=10),
            shadow=ft.BoxShadow(blur_radius=10, color="#05000000"),
            content=ft.Column(spacing=15, controls=chart_content)
        )

        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=15,
            controls=[
                header,
                profile_card,
                taste_card
            ]
        )
import flet as ft
from collections import Counter
from src.ui.charts import (
    VerticalBarChart, HorizontalBarChart, DonutChart,
    GenreNetworkGraph, CategoricalBubbleChart, KDEChart
)
from src.config.theme import ThemeManager


# ─────────────────────────────────────────────────────────────────────────────
# Chart card wrapper
# ─────────────────────────────────────────────────────────────────────────────
def _chart_card(chart, theme) -> ft.Container:
    return ft.Container(
        content=chart,
        expand=True,
        height=350,
        bgcolor=theme["card"],
        border_radius=12,
        border=ft.border.all(1, theme["border_color"]),
        padding=ft.padding.all(0),
        shadow=ft.BoxShadow(blur_radius=8, color="#0A000000",
                            offset=ft.Offset(0, 2)),
    )


def _network_card(chart, theme) -> ft.Container:
    """Card khusus untuk network graph — lebih tinggi agar node tidak berhimpit."""
    return ft.Container(
        content=chart,
        expand=True,
        height=480,
        bgcolor=theme["card"],
        border_radius=12,
        border=ft.border.all(1, theme["border_color"]),
        padding=ft.padding.all(0),
        shadow=ft.BoxShadow(blur_radius=8, color="#0A000000",
                            offset=ft.Offset(0, 2)),
    )


def _bubble_card(chart, theme) -> ft.Container:
    """Card untuk Categorical Bubble Chart — lebih tinggi agar sel tidak sempit."""
    return ft.Container(
        content=chart,
        expand=True,
        height=560,
        bgcolor=theme["card"],
        border_radius=12,
        border=ft.border.all(1, theme["border_color"]),
        padding=ft.padding.all(0),
        shadow=ft.BoxShadow(blur_radius=8, color="#0A000000",
                            offset=ft.Offset(0, 2)),
    )


# ─────────────────────────────────────────────────────────────────────────────
# Main UI
# ─────────────────────────────────────────────────────────────────────────────
class UIAnalytics(ft.Row):
    def __init__(self, page, data_manager, auth_manager, screen_manager):
        super().__init__()
        self.my_page        = page
        self.data_manager   = data_manager
        self.auth_manager   = auth_manager
        self.screen_manager = screen_manager
        self.expand  = True
        self.spacing = 0
        self._sidebar_open = False

        self.current_theme = ThemeManager.get_theme(self.screen_manager.tema_aktif)

        from src.ui.ui_home import _sidebar
        self._sidebar_widget = _sidebar(
            screen_manager, auth_manager,
            self._toggle_sidebar, self.current_theme, halaman_aktif="analytics",
        )

        topbar = ft.Container(
            padding=ft.padding.symmetric(horizontal=16),
            height=55,
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            bgcolor=ft.Colors.with_opacity(0.8, self.current_theme["bg"]),
            shadow=ft.BoxShadow(blur_radius=15, color="#15000000",
                                offset=ft.Offset(0, 4)),
            content=ft.Row(
                controls=[
                    ft.IconButton(ft.Icons.MENU, icon_color=self.current_theme["primary"],
                                  on_click=self._toggle_sidebar,
                                  tooltip="Menu"),
                    ft.Text("Analytics Dashboard", size=18,
                            color=self.current_theme["text_main"], weight=ft.FontWeight.BOLD),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self._main_content = ft.Column(
            scroll=ft.ScrollMode.AUTO, expand=True, spacing=16,
        )
        self._load_analytics()

        area_utama = ft.Container(
            content=ft.Column(
                controls=[
                    topbar,
                    ft.Container(
                        content=self._main_content,
                        padding=ft.padding.symmetric(
                            horizontal=20, vertical=16),
                        expand=True,
                    ),
                ],
                spacing=0, expand=True,
            ),
            bgcolor=self.current_theme["bg"],
            expand=True,
        )
        self.controls = [self._sidebar_widget, area_utama]

    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._sidebar_widget.update()

    def _load_analytics(self):
        animes = self.data_manager.get_semua_anime()
        users  = self.data_manager._read_json(self.data_manager.users_file) or []

        total_anime   = len(animes)
        total_users   = len(users)
        total_ratings = sum(u.get("rating_count", 0) for u in users)

        stat_card = ft.Container(
            bgcolor=self.current_theme["primary_light"],
            border=ft.border.all(1, self.current_theme["border_color"]),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            content=ft.Row(
                controls=[
                    self._build_stat("Total Anime",   total_anime,   ft.Icons.MOVIE),
                    ft.VerticalDivider(width=1, color=self.current_theme["border_color"]),
                    self._build_stat("Total Users",   total_users,   ft.Icons.PEOPLE),
                    ft.VerticalDivider(width=1, color=self.current_theme["border_color"]),
                    self._build_stat("Total Ratings", total_ratings, ft.Icons.STAR),
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            ),
        )

        # Chart 1 — Genre
        genres_counter = Counter()
        for a in animes:
            for g in a.get("genre", []):
                genres_counter[g] += 1
        genre_data = [{"label": g, "value": cnt, "extra": None}
                      for g, cnt in genres_counter.most_common(10)]
        chart1 = VerticalBarChart(genre_data, "Most Common Genres", y_label="Jumlah Anime", theme=self.current_theme)

        # Chart 2 — Episodes
        bin_labels = ["1–12", "13–24", "25–36", "37–48", "49–100", "100+"]
        bin_counts = [0] * 6
        for a in animes:
            try:
                ep = int(a.get("episodes") or 0)
            except (TypeError, ValueError):
                continue
            if   ep <= 12:  bin_counts[0] += 1
            elif ep <= 24:  bin_counts[1] += 1
            elif ep <= 36:  bin_counts[2] += 1
            elif ep <= 48:  bin_counts[3] += 1
            elif ep <= 100: bin_counts[4] += 1
            else:           bin_counts[5] += 1
        ep_data = [{"label": lbl, "value": cnt, "extra": f"{cnt} anime"}
                   for lbl, cnt in zip(bin_labels, bin_counts)]
        chart2 = VerticalBarChart(ep_data, "Episode Count Distribution",
                                  y_label="Jumlah Anime", theme=self.current_theme)

        # Chart 3 — Type donut
        types_counter = Counter(a.get("type", "Unknown") for a in animes)
        t_sorted = types_counter.most_common()
        t_total  = sum(v for _, v in t_sorted)
        donut_data = [{"label": lbl, "value": cnt, "pct": cnt / t_total * 100}
                      for lbl, cnt in t_sorted]
        chart3 = DonutChart(donut_data, "Show Types Proportion", theme=self.current_theme)

        # Chart 4 — Studios
        studio_scores: dict = {}
        for a in animes:
            studio = a.get("studio") or "Unknown"
            score  = a.get("global_score")
            if isinstance(score, (int, float)):
                studio_scores.setdefault(studio, []).append(score)
        top10 = sorted(studio_scores.items(),
                       key=lambda kv: len(kv[1]), reverse=True)[:10]
        top10 = sorted(top10, key=lambda kv: sum(kv[1]) / len(kv[1]))
        studio_data = [
            {"label": kv[0],
             "value": round(sum(kv[1]) / len(kv[1]), 2),
             "extra": f"{len(kv[1])}"}
            for kv in top10
        ]
        chart4 = HorizontalBarChart(studio_data, "Average Scores of the Top 10 Most Active Studios", theme=self.current_theme)

        row1 = ft.Row(
            controls=[_chart_card(chart1, self.current_theme), _chart_card(chart2, self.current_theme)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )
        row2 = ft.Row(
            controls=[_chart_card(chart3, self.current_theme), _chart_card(chart4, self.current_theme)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )

        # Chart 5 — Genre Co-occurrence Network Graph
        chart5 = GenreNetworkGraph(animes, "Genre Co-occurrence Network", theme=self.current_theme)

        row3 = ft.Row(
            controls=[_network_card(chart5, self.current_theme)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )

        # Chart 6 — KDE Plot
        chart6 = KDEChart(animes, theme=self.current_theme)
        row4 = ft.Row(
            controls=[_chart_card(chart6, self.current_theme)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )

        # Chart 7 — Studio × Genre Categorical Bubble Chart
        chart7 = CategoricalBubbleChart(
            animes, "Studio × Genre Bubble Chart", theme=self.current_theme
        )
        row5 = ft.Row(
            controls=[_bubble_card(chart7, self.current_theme)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )

        self._main_content.controls.extend([
            stat_card,
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.TOUCH_APP, color=self.current_theme["text_muted"], size=14),
                    ft.Text(
                        "Hover di atas bar / slice / node / gelembung untuk detail",
                        size=11, color=self.current_theme["text_muted"], italic=True,
                    ),
                ],
                spacing=6,
            ),
            row1,
            row2,
            row3,
            row4,
            row5,
            ft.Container(height=24),
        ])

    def _build_stat(self, label, value, icon):
        return ft.Column(
            controls=[
                ft.Icon(icon, color=self.current_theme["primary"], size=28),
                ft.Text(str(value), size=22, color=self.current_theme["text_main"],
                        weight=ft.FontWeight.BOLD),
                ft.Text(label, size=11, color=self.current_theme["text_secondary"]),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        )
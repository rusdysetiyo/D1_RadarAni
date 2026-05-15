import flet as ft
from collections import Counter
from src.ui.charts import (
    C_SAKURA, C_SAKURA_LT, C_TEXT, C_TEXT2, C_TEXT3, C_BORDER, C_WHITE,
    VerticalBarChart, HorizontalBarChart, DonutChart,
    GenreNetworkGraph, CategoricalBubbleChart, KDEChart
)

# ─────────────────────────────────────────────────────────────────────────────
# Chart card wrapper
# ─────────────────────────────────────────────────────────────────────────────
def _chart_card(chart) -> ft.Container:
    return ft.Container(
        content=chart,
        expand=True,
        height=350,
        bgcolor=C_WHITE,
        border_radius=12,
        border=ft.border.all(1, C_BORDER),
        padding=ft.padding.all(0),
        shadow=ft.BoxShadow(blur_radius=8, color="#0A000000",
                            offset=ft.Offset(0, 2)),
    )


def _network_card(chart) -> ft.Container:
    """Card khusus untuk network graph — lebih tinggi agar node tidak berhimpit."""
    return ft.Container(
        content=chart,
        expand=True,
        height=480,
        bgcolor=C_WHITE,
        border_radius=12,
        border=ft.border.all(1, C_BORDER),
        padding=ft.padding.all(0),
        shadow=ft.BoxShadow(blur_radius=8, color="#0A000000",
                            offset=ft.Offset(0, 2)),
    )


def _bubble_card(chart) -> ft.Container:
    """Card untuk Categorical Bubble Chart — lebih tinggi agar sel tidak sempit."""
    return ft.Container(
        content=chart,
        expand=True,
        height=560,
        bgcolor=C_WHITE,
        border_radius=12,
        border=ft.border.all(1, C_BORDER),
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

        from src.ui.ui_home import _sidebar
        self._sidebar_widget = _sidebar(
            screen_manager, auth_manager,
            self._toggle_sidebar, halaman_aktif="analytics",
        )

        topbar = ft.Container(
            padding=ft.padding.symmetric(horizontal=16),
            height=55,
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=["#E6FFFFFF", "#CCFCF8FA"],
            ),
            shadow=ft.BoxShadow(blur_radius=15, color="#15000000",
                                offset=ft.Offset(0, 4)),
            content=ft.Row(
                controls=[
                    ft.IconButton(ft.Icons.MENU, icon_color=C_SAKURA,
                                  on_click=self._toggle_sidebar,
                                  tooltip="Menu"),
                    ft.Text("Analytics Dashboard", size=18,
                            color=C_SAKURA, weight=ft.FontWeight.BOLD),
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
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=["#FFFFFF", "#F0F2F5"], stops=[0.4, 1.0],
            ),
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
            bgcolor=C_SAKURA_LT,
            border=ft.border.all(1, "#E8D0DE"),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            content=ft.Row(
                controls=[
                    self._build_stat("Total Anime",   total_anime,   ft.Icons.MOVIE),
                    ft.VerticalDivider(width=1, color=C_BORDER),
                    self._build_stat("Total Users",   total_users,   ft.Icons.PEOPLE),
                    ft.VerticalDivider(width=1, color=C_BORDER),
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
        chart1 = VerticalBarChart(genre_data, "Most Common Genres", y_label="Jumlah Anime")

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
                                  y_label="Jumlah Anime")

        # Chart 3 — Type donut
        types_counter = Counter(a.get("type", "Unknown") for a in animes)
        t_sorted = types_counter.most_common()
        t_total  = sum(v for _, v in t_sorted)
        donut_data = [{"label": lbl, "value": cnt, "pct": cnt / t_total * 100}
                      for lbl, cnt in t_sorted]
        chart3 = DonutChart(donut_data, "Show Types Proportion")

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
        chart4 = HorizontalBarChart(studio_data, "Average Scores of the Top 10 Most Active Studios")

        row1 = ft.Row(
            controls=[_chart_card(chart1), _chart_card(chart2)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )
        row2 = ft.Row(
            controls=[_chart_card(chart3), _chart_card(chart4)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )

        # Chart 5 — Genre Co-occurrence Network Graph
        chart5 = GenreNetworkGraph(animes, "Genre Co-occurrence Network")

        row3 = ft.Row(
            controls=[_network_card(chart5)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )

        # Chart 6 — KDE Plot
        chart6 = KDEChart(animes)
        row4 = ft.Row(
            controls=[_chart_card(chart6)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )

        # Chart 7 — Studio × Genre Categorical Bubble Chart
        chart7 = CategoricalBubbleChart(
            animes, "Studio × Genre Bubble Chart"
        )
        row5 = ft.Row(
            controls=[_bubble_card(chart7)],
            alignment=ft.MainAxisAlignment.CENTER, spacing=16, expand=True,
        )

        self._main_content.controls.extend([
            stat_card,
            ft.Row(
                controls=[
                    ft.Icon(ft.Icons.TOUCH_APP, color=C_TEXT3, size=14),
                    ft.Text(
                        "Hover di atas bar / slice / node / gelembung untuk detail",
                        size=11, color=C_TEXT3, italic=True,
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
                ft.Icon(icon, color=C_SAKURA, size=28),
                ft.Text(str(value), size=22, color=C_TEXT,
                        weight=ft.FontWeight.BOLD),
                ft.Text(label, size=11, color=C_TEXT2),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        )
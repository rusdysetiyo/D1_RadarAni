import flet as ft
import io
import base64
from collections import Counter
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

# Ukuran figure yang seragam untuk semua chart (lebar x tinggi dalam inch)
_FIG_W, _FIG_H = 6.5, 4.2


def _fig_to_src(fig) -> str:
    """Simpan figure ke data URI base64 (kompatibel Flet >= 0.21)."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight',
                transparent=True, dpi=110)
    plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64}"


# ── Main UI ───────────────────────────────────────────────────────────────────
class UIAnalytics(ft.Row):
    def __init__(self, page, data_manager, auth_manager, screen_manager, theme):
        super().__init__()
        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager
        self.theme = theme
        self.expand = True
        self.spacing = 0
        self._sidebar_open = False

        from src.ui.ui_home import _sidebar
        self._sidebar_widget = _sidebar(
            screen_manager,
            auth_manager,
            toggle_fn=self._toggle_sidebar,
            theme=self.theme,
            halaman_aktif="analytics"
        )

        self._main_content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=16,
        )

        self._area_utama = ft.Container(
            expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=[self.theme["card"], self.theme["bg"]],
                stops=[0.4, 1.0],
            ),
        )

        self.controls = [self._sidebar_widget, self._area_utama]
        self._bangun_ui()

    def perbarui_tema(self):
        """Fungsi sakti buat dipanggil KeyboardManager saat ganti tema in-place"""
        self._bangun_ui()
        self.update()

    def _bangun_ui(self):
        """Bangun ulang seluruh UI ketika inisialisasi atau ganti tema"""
        self._main_content.controls.clear()

        topbar = ft.Container(
            padding=ft.padding.symmetric(horizontal=16),
            height=55,
            bgcolor=ft.Colors.with_opacity(0.8, self.theme["card"]),
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            shadow=ft.BoxShadow(
                blur_radius=15,
                color=ft.Colors.with_opacity(0.08, self.theme["text_main"]),
                offset=ft.Offset(0, 4),
            ),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        ft.Icons.MENU, icon_color=self.theme["primary"],
                        on_click=self._toggle_sidebar, tooltip="Menu",
                    ),
                    ft.Text(
                        "Analytics Dashboard", size=18,
                        color=self.theme["primary"], weight=ft.FontWeight.BOLD,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self._load_analytics()

        self._area_utama.gradient = ft.LinearGradient(
            begin=ft.Alignment(0, -1),
            end=ft.Alignment(0, 1),
            colors=[self.theme["card"], self.theme["bg"]],
            stops=[0.4, 1.0],
        )

        self._area_utama.content = ft.Column(
            controls=[
                topbar,
                ft.Container(
                    content=self._main_content,
                    padding=ft.padding.symmetric(horizontal=20, vertical=16),
                    expand=True,
                ),
            ],
            spacing=0,
            expand=True,
        )

    # ── Sidebar toggle ─────────────────────────────────────────────────────
    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._sidebar_widget.update()

    # ── Helpers Style ──────────────────────────────────────────────────────
    def _apply_chart_style(self, ax, fig):
        """Terapkan gaya tema aktif ke semua axes."""
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        ax.tick_params(colors=self.theme["text_secondary"])
        ax.xaxis.label.set_color(self.theme["text_secondary"])
        ax.yaxis.label.set_color(self.theme["text_secondary"])
        ax.title.set_color(self.theme["text_main"])
        ax.title.set_fontsize(12)
        ax.title.set_fontweight('bold')
        for spine in ax.spines.values():
            spine.set_edgecolor(self.theme["border_color"])

    def _chart_container(self, img_widget) -> ft.Container:
        """Bungkus chart dalam container berukuran seragam."""
        return ft.Container(
            content=img_widget,
            expand=True,
            height=260,
            bgcolor=self.theme["card"],
            border_radius=12,
            border=ft.border.all(1, self.theme["border_color"]),
            padding=ft.padding.all(12),
            shadow=ft.BoxShadow(
                blur_radius=8,
                color=ft.Colors.with_opacity(0.05, self.theme["text_main"]),
                offset=ft.Offset(0, 2),
            ),
        )

    def _get_dynamic_colors(self, count):
        """Ambil warna dari list secara berulang jika item lebih dari jumlah warna."""
        base_colors = self.theme["chart_colors"]
        return [base_colors[i % len(base_colors)] for i in range(count)]

    # ── Analytics loader ───────────────────────────────────────────────────
    def _load_analytics(self):
        animes = self.data_manager.get_semua_anime()
        users = self.data_manager._read_json(self.data_manager.users_file) or []

        total_anime = len(animes)
        total_users = len(users)
        total_ratings = sum(u.get("rating_count", 0) for u in users)

        # ── Overview Stats ─────────────────────────────────────────────────
        stat_card = ft.Container(
            bgcolor=self.theme["bg_secondary"],
            border=ft.border.all(1, self.theme["border_color"]),
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=24, vertical=16),
            content=ft.Row(
                controls=[
                    self._build_stat("Total Anime", total_anime, ft.Icons.MOVIE),
                    ft.VerticalDivider(width=1, color=self.theme["border_color"]),
                    self._build_stat("Total Users", total_users, ft.Icons.PEOPLE),
                    ft.VerticalDivider(width=1, color=self.theme["border_color"]),
                    self._build_stat("Total Ratings", total_ratings, ft.Icons.STAR),
                ],
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            ),
        )

        # ── Chart 1: Genre Distribution (bar) ─────────────────────────────
        genres_counter = Counter()
        for a in animes:
            for g in a.get("genre", []):
                genres_counter[g] += 1
        top_genres = genres_counter.most_common(10)
        g_labels = [g[0] for g in top_genres]
        g_vals = [g[1] for g in top_genres]

        fig1, ax1 = plt.subplots(figsize=(_FIG_W, _FIG_H))
        bars = ax1.bar(g_labels, g_vals, color=self._get_dynamic_colors(len(g_labels)),
                       edgecolor=self.theme["card"], linewidth=0.8, zorder=3)
        ax1.set_title('Top 10 Genres')
        ax1.tick_params(axis='x', rotation=40)
        ax1.yaxis.grid(True, color=self.theme["border_color"], linewidth=0.6, zorder=0)
        ax1.set_axisbelow(True)
        self._apply_chart_style(ax1, fig1)
        fig1.tight_layout()
        img1 = ft.Image(src=_fig_to_src(fig1), fit=ft.BoxFit.CONTAIN,
                        width=None, height=None, expand=True)

        # ── Chart 2: Episode Count Histogram ─────────────────────────────
        episodes = []
        for a in animes:
            raw = a.get("episodes")
            try:
                episodes.append(int(raw))
            except (TypeError, ValueError):
                pass

        bin_edges = [1, 13, 25, 37, 49, 100]
        bin_labels = ["1–12", "13–24", "25–36", "37–48", "49–100", "100+"]
        bin_counts = [0, 0, 0, 0, 0, 0]
        for ep in episodes:
            if ep <= 12:
                bin_counts[0] += 1
            elif ep <= 24:
                bin_counts[1] += 1
            elif ep <= 36:
                bin_counts[2] += 1
            elif ep <= 48:
                bin_counts[3] += 1
            elif ep <= 100:
                bin_counts[4] += 1
            else:
                bin_counts[5] += 1

        fig2, ax2 = plt.subplots(figsize=(_FIG_W, _FIG_H))
        x_pos = range(len(bin_labels))
        bars2 = ax2.bar(x_pos, bin_counts,
                        color=self._get_dynamic_colors(len(bin_labels)),
                        edgecolor=self.theme["card"], linewidth=0.8, zorder=3)

        for bar, cnt in zip(bars2, bin_counts):
            if cnt > 0:
                ax2.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.3,
                    str(cnt), ha='center', va='bottom',
                    fontsize=9, color=self.theme["text_secondary"],
                )

        ax2.set_xticks(list(x_pos))
        ax2.set_xticklabels(bin_labels)
        ax2.set_title('Episode Count Distribution')
        ax2.set_xlabel('Episode Range')
        ax2.set_ylabel('Jumlah Anime')
        ax2.yaxis.grid(True, color=self.theme["border_color"], linewidth=0.6, zorder=0)
        ax2.set_axisbelow(True)
        self._apply_chart_style(ax2, fig2)
        fig2.tight_layout()
        img2 = ft.Image(src=_fig_to_src(fig2), fit=ft.BoxFit.CONTAIN,
                        width=None, height=None, expand=True)

        # ── Chart 3: Show Type Donut ───────────────────────────────────────
        types_counter = Counter(a.get("type", "Unknown") for a in animes)
        t_sorted = types_counter.most_common()
        t_labels = [x[0] for x in t_sorted]
        t_vals = [x[1] for x in t_sorted]
        t_total = sum(t_vals) if sum(t_vals) > 0 else 1  # Cegah devide by zero

        fig3, ax3 = plt.subplots(figsize=(_FIG_W, _FIG_H))
        wedges, _ = ax3.pie(
            t_vals,
            startangle=90,
            colors=self._get_dynamic_colors(len(t_labels)),
            wedgeprops=dict(width=0.45, edgecolor=self.theme["card"], linewidth=1.2),
        )
        legend_labels = [
            f"{lbl}  {cnt} ({cnt / t_total * 100:.1f}%)"
            for lbl, cnt in zip(t_labels, t_vals)
        ]
        ax3.legend(
            wedges, legend_labels,
            loc="center left",
            bbox_to_anchor=(0.88, 0.5),
            fontsize=8,
            frameon=False,
            labelcolor=self.theme["text_secondary"],
        )
        ax3.set_title('Show Types Proportion')
        self._apply_chart_style(ax3, fig3)
        fig3.tight_layout()
        img3 = ft.Image(src=_fig_to_src(fig3), fit=ft.BoxFit.CONTAIN,
                        width=None, height=None, expand=True)

        # ── Chart 4: Top 10 Studios – Avg Global Score ────────────────────
        studio_scores: dict[str, list] = {}
        for a in animes:
            studio = a.get("studio") or "Unknown"
            score = a.get("global_score")
            if isinstance(score, (int, float)):
                studio_scores.setdefault(studio, []).append(score)

        top10_studios = sorted(
            studio_scores.items(), key=lambda kv: len(kv[1]), reverse=True
        )[:10]
        top10_studios = sorted(
            top10_studios, key=lambda kv: sum(kv[1]) / len(kv[1])
        )

        st_labels = [kv[0] for kv in top10_studios]
        st_avgs = [sum(kv[1]) / len(kv[1]) for kv in top10_studios]
        st_counts = [len(kv[1]) for kv in top10_studios]

        fig4, ax4 = plt.subplots(figsize=(_FIG_W, _FIG_H))
        y_pos = range(len(st_labels))
        bars4 = ax4.barh(
            list(y_pos), st_avgs,
            color=self._get_dynamic_colors(len(st_labels)),
            edgecolor=self.theme["card"], linewidth=0.8, zorder=3,
        )

        x_min = min(st_avgs) * 0.97 if st_avgs else 0
        ax4.set_xlim(left=x_min)
        for bar, avg, cnt in zip(bars4, st_avgs, st_counts):
            ax4.text(
                bar.get_width() + 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{avg:.2f}  (n={cnt})",
                va='center', ha='left', fontsize=8, color=self.theme["text_secondary"],
            )

        ax4.set_yticks(list(y_pos))
        ax4.set_yticklabels(st_labels, fontsize=9)
        ax4.set_title('Top 10 Studios – Avg Score')
        ax4.set_xlabel('Avg Global Score')
        ax4.xaxis.grid(True, color=self.theme["border_color"], linewidth=0.6, zorder=0)
        ax4.set_axisbelow(True)
        self._apply_chart_style(ax4, fig4)
        fig4.tight_layout()
        img4 = ft.Image(src=_fig_to_src(fig4), fit=ft.BoxFit.CONTAIN,
                        width=None, height=None, expand=True)

        # ── Layout: 2×2 grid ──────────────────────────────────────────────
        row1 = ft.Row(
            controls=[
                self._chart_container(img1),
                self._chart_container(img2),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
            expand=True,
        )

        row2 = ft.Row(
            controls=[
                self._chart_container(img3),
                self._chart_container(img4),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
            expand=True,
        )

        self._main_content.controls.extend([
            stat_card,
            row1,
            row2,
            ft.Container(height=24),
        ])

    # ── Stat builder ───────────────────────────────────────────────────────
    def _build_stat(self, label: str, value, icon) -> ft.Column:
        return ft.Column(
            controls=[
                ft.Icon(icon, color=self.theme["primary"], size=28),
                ft.Text(str(value), size=22, color=self.theme["text_main"],
                        weight=ft.FontWeight.BOLD),
                ft.Text(label, size=11, color=self.theme["text_secondary"]),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=4,
        )
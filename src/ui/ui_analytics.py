import flet as ft
import io
import base64
from collections import Counter
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

# ── Palette ───────────────────────────────────────────────────────────────────
C_SAKURA    = "#C07090"
C_SAKURA_LT = "#F9F0F5"
C_TEXT      = "#3D2535"
C_TEXT2     = "#8B6A7A"
C_TEXT3     = "#B0909A"
C_BORDER    = "#EDE0E8"
C_WHITE     = "#FFFFFF"
C_BG        = "#FCF8FA"
C_BG2       = "#F5EEF2"

# Palet warna chart yang konsisten
CHART_COLORS = ["#C07090", "#D4A8C0", "#E8D0DE", "#A0506A", "#F0E4EB",
                "#B08090", "#E0B0C8", "#906070", "#F4D8E8", "#C890A8"]

# Ukuran figure yang seragam untuk semua chart (lebar x tinggi dalam inch)
_FIG_W, _FIG_H = 6.5, 4.2

# ── Helper ────────────────────────────────────────────────────────────────────
def _apply_chart_style(ax, fig):
    """Terapkan gaya sakura yang konsisten ke semua axes."""
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    ax.tick_params(colors=C_TEXT2)
    ax.xaxis.label.set_color(C_TEXT2)
    ax.yaxis.label.set_color(C_TEXT2)
    ax.title.set_color(C_TEXT)
    ax.title.set_fontsize(12)
    ax.title.set_fontweight('bold')
    for spine in ax.spines.values():
        spine.set_edgecolor(C_BORDER)


def _fig_to_src(fig) -> str:
    """Simpan figure ke data URI base64 (kompatibel Flet >= 0.21)."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight',
                transparent=True, dpi=110)
    plt.close(fig)
    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64}"


def _chart_container(img_widget) -> ft.Container:
    """Bungkus chart dalam container berukuran seragam."""
    return ft.Container(
        content=img_widget,
        expand=True,
        height=260,
        bgcolor=C_WHITE,
        border_radius=12,
        border=ft.border.all(1, C_BORDER),
        padding=ft.padding.all(12),
        shadow=ft.BoxShadow(
            blur_radius=8,
            color="#0A000000",
            offset=ft.Offset(0, 2),
        ),
    )


# ── Main UI ───────────────────────────────────────────────────────────────────
class UIAnalytics(ft.Row):
    def __init__(self, page, data_manager, auth_manager, screen_manager):
        super().__init__()
        self.my_page         = page
        self.data_manager    = data_manager
        self.auth_manager    = auth_manager
        self.screen_manager  = screen_manager

        self.expand  = True
        self.spacing = 0
        self._sidebar_open = False

        from src.ui.ui_home import _sidebar
        self._sidebar_widget = _sidebar(
            screen_manager, auth_manager,
            self._toggle_sidebar, halaman_aktif="analytics"
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
                offset=ft.Offset(0, 4),
            ),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        ft.Icons.MENU, icon_color=C_SAKURA,
                        on_click=self._toggle_sidebar, tooltip="Menu",
                    ),
                    ft.Text(
                        "Analytics Dashboard", size=18,
                        color=C_SAKURA, weight=ft.FontWeight.BOLD,
                    ),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self._main_content = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=16,
        )
        self._load_analytics()

        area_utama = ft.Container(
            content=ft.Column(
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
            ),
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#FFFFFF", "#F0F2F5"],
                stops=[0.4, 1.0],
            ),
            expand=True,
        )

        self.controls = [self._sidebar_widget, area_utama]

    # ── Sidebar toggle ─────────────────────────────────────────────────────
    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._sidebar_widget.update()

    # ── Analytics loader ───────────────────────────────────────────────────
    def _load_analytics(self):
        animes = self.data_manager.get_semua_anime()
        users  = self.data_manager._read_json(self.data_manager.users_file) or []

        total_anime   = len(animes)
        total_users   = len(users)
        total_ratings = sum(u.get("rating_count", 0) for u in users)

        # ── Overview Stats ─────────────────────────────────────────────────
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

        # ── Chart 1: Genre Distribution (bar) ─────────────────────────────
        genres_counter = Counter()
        for a in animes:
            for g in a.get("genre", []):
                genres_counter[g] += 1
        top_genres = genres_counter.most_common(10)
        g_labels = [g[0] for g in top_genres]
        g_vals   = [g[1] for g in top_genres]

        fig1, ax1 = plt.subplots(figsize=(_FIG_W, _FIG_H))
        bars = ax1.bar(g_labels, g_vals, color=CHART_COLORS[:len(g_labels)],
                       edgecolor='white', linewidth=0.8, zorder=3)
        ax1.set_title('Top 10 Genres')
        ax1.tick_params(axis='x', rotation=40)
        ax1.yaxis.grid(True, color=C_BORDER, linewidth=0.6, zorder=0)
        ax1.set_axisbelow(True)
        _apply_chart_style(ax1, fig1)
        fig1.tight_layout()
        img1 = ft.Image(src=_fig_to_src(fig1), fit=ft.BoxFit.CONTAIN,
                        width=None, height=None, expand=True)

        # ── Chart 2: Episode Count Histogram (Custom Bins + Catch-All) ────
        episodes = []
        for a in animes:
            raw = a.get("episodes")
            try:
                episodes.append(int(raw))
            except (TypeError, ValueError):
                pass  # skip "Unknown", None, atau nilai tak valid

        # Custom bins: rentang wajar + catch-all "100+" untuk outlier
        bin_edges   = [1, 13, 25, 37, 49, 100]   # batas kiri tiap bin normal
        bin_labels  = ["1–12", "13–24", "25–36", "37–48", "49–100", "100+"]
        bin_counts  = [0, 0, 0, 0, 0, 0]
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
                bin_counts[5] += 1  # catch-all: 100+

        fig2, ax2 = plt.subplots(figsize=(_FIG_W, _FIG_H))
        x_pos = range(len(bin_labels))
        bars2 = ax2.bar(x_pos, bin_counts,
                        color=CHART_COLORS[:len(bin_labels)],
                        edgecolor='white', linewidth=0.8, zorder=3)

        # Teks jumlah di atas tiap bar
        for bar, cnt in zip(bars2, bin_counts):
            if cnt > 0:
                ax2.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.3,
                    str(cnt), ha='center', va='bottom',
                    fontsize=9, color=C_TEXT2,
                )

        ax2.set_xticks(list(x_pos))
        ax2.set_xticklabels(bin_labels)
        ax2.set_title('Episode Count Distribution')
        ax2.set_xlabel('Episode Range')
        ax2.set_ylabel('Jumlah Anime')
        ax2.yaxis.grid(True, color=C_BORDER, linewidth=0.6, zorder=0)
        ax2.set_axisbelow(True)
        _apply_chart_style(ax2, fig2)
        fig2.tight_layout()
        img2 = ft.Image(src=_fig_to_src(fig2), fit=ft.BoxFit.CONTAIN,
                        width=None, height=None, expand=True)

        # ── Chart 3: Show Type Donut ───────────────────────────────────────
        types_counter = Counter(a.get("type", "Unknown") for a in animes)
        # Urutkan dari terbesar agar legend rapi
        t_sorted = types_counter.most_common()
        t_labels = [x[0] for x in t_sorted]
        t_vals   = [x[1] for x in t_sorted]
        t_total  = sum(t_vals)

        fig3, ax3 = plt.subplots(figsize=(_FIG_W, _FIG_H))
        # Tidak ada labels/autopct langsung di slice — cegah tumpang tindih
        wedges, _ = ax3.pie(
            t_vals,
            startangle=90,
            colors=CHART_COLORS[:len(t_labels)],
            wedgeprops=dict(width=0.45, edgecolor='white', linewidth=1.2),
        )
        # Legend di luar donut — label berisi nama + persentase
        legend_labels = [
            f"{lbl}  {cnt} ({cnt/t_total*100:.1f}%)"
            for lbl, cnt in zip(t_labels, t_vals)
        ]
        ax3.legend(
            wedges, legend_labels,
            loc="center left",
            bbox_to_anchor=(0.88, 0.5),
            fontsize=8,
            frameon=False,
            labelcolor=C_TEXT2,
        )
        ax3.set_title('Show Types Proportion')
        _apply_chart_style(ax3, fig3)
        fig3.tight_layout()
        img3 = ft.Image(src=_fig_to_src(fig3), fit=ft.BoxFit.CONTAIN,
                        width=None, height=None, expand=True)

        # ── Chart 4: Top 10 Studios – Avg Global Score ────────────────────
        # Kumpulkan score per studio
        studio_scores: dict[str, list] = {}
        for a in animes:
            studio = a.get("studio") or "Unknown"
            score  = a.get("global_score")
            if isinstance(score, (int, float)):
                studio_scores.setdefault(studio, []).append(score)

        # Pilih 10 studio dengan jumlah anime terbanyak
        top10_studios = sorted(
            studio_scores.items(), key=lambda kv: len(kv[1]), reverse=True
        )[:10]
        # Urutkan berdasarkan avg score (terbesar di atas)
        top10_studios = sorted(
            top10_studios, key=lambda kv: sum(kv[1]) / len(kv[1])
        )

        st_labels   = [kv[0] for kv in top10_studios]
        st_avgs     = [sum(kv[1]) / len(kv[1]) for kv in top10_studios]
        st_counts   = [len(kv[1]) for kv in top10_studios]

        fig4, ax4 = plt.subplots(figsize=(_FIG_W, _FIG_H))
        y_pos  = range(len(st_labels))
        bars4  = ax4.barh(
            list(y_pos), st_avgs,
            color=CHART_COLORS[:len(st_labels)],
            edgecolor='white', linewidth=0.8, zorder=3,
        )

        # Anotasi: tampilkan avg score + jumlah anime di ujung bar
        x_min = min(st_avgs) * 0.97 if st_avgs else 0
        ax4.set_xlim(left=x_min)
        for bar, avg, cnt in zip(bars4, st_avgs, st_counts):
            ax4.text(
                bar.get_width() + 0.02,
                bar.get_y() + bar.get_height() / 2,
                f"{avg:.2f}  (n={cnt})",
                va='center', ha='left', fontsize=8, color=C_TEXT2,
            )

        ax4.set_yticks(list(y_pos))
        ax4.set_yticklabels(st_labels, fontsize=9)
        ax4.set_title('Top 10 Studios – Avg Score')
        ax4.set_xlabel('Avg Global Score')
        ax4.xaxis.grid(True, color=C_BORDER, linewidth=0.6, zorder=0)
        ax4.set_axisbelow(True)
        _apply_chart_style(ax4, fig4)
        fig4.tight_layout()
        img4 = ft.Image(src=_fig_to_src(fig4), fit=ft.BoxFit.CONTAIN,
                        width=None, height=None, expand=True)

        # ── Layout: 2×2 grid ──────────────────────────────────────────────
        row1 = ft.Row(
            controls=[
                _chart_container(img1),   # genre bar
                _chart_container(img2),   # episode histogram
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
            expand=True,
        )

        row2 = ft.Row(
            controls=[
                _chart_container(img3),   # type donut
                _chart_container(img4),   # status bar (BARU)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
            expand=True,
        )

        self._main_content.controls.extend([
            stat_card,
            row1,
            row2,
            ft.Container(height=24),  # padding bawah
        ])

    # ── Stat builder ───────────────────────────────────────────────────────
    def _build_stat(self, label: str, value, icon) -> ft.Column:
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
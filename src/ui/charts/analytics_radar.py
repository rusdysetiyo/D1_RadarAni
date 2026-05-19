import flet as ft
from collections import Counter
from src.ui.radar_chart import detail_radar_chart


class AnalyticsRadarChart(ft.Container):
    """
    Radar Chart komponen individual untuk satu kategori (Anime, Genre, atau Studio).
    - Mode Tunggal: tampilkan satu item.
    - Mode Komparasi: tampilkan dua item berdampingan pada radar.
    - Anime: setiap slot memiliki TextField pencarian mandiri untuk memfilter
      dropdown di bawahnya secara independen.
    """

    def __init__(self, animes: list, category: str, theme: dict = None):
        super().__init__(expand=True)
        self.animes   = animes
        self.category = category
        self._theme   = theme
        self._labels  = ["Plot", "Visual", "Audio", "Characterization", "Direction"]
        self.is_compare = False

        # ── Siapkan data ──────────────────────────────────────────────────────
        self.data_dict   = {}
        self.all_options = []

        if self.category == "Anime":
            for a in animes:
                title = a.get("title", "Unknown")
                dims  = a.get("global_score_dimensions", [0, 0, 0, 0, 0])
                if title not in self.data_dict:
                    self.data_dict[title] = dims
            self.all_options = sorted(self.data_dict.keys())

        elif self.category == "Genre":
            genre_count  = Counter()
            genre_scores = {}
            for a in animes:
                dims = a.get("global_score_dimensions", [0, 0, 0, 0, 0])
                for g in a.get("genre", []):
                    genre_count[g] += 1
                    genre_scores.setdefault(g, []).append(dims)
            self.all_options = [g for g, _ in genre_count.most_common(15)]
            self.data_dict   = {
                g: [sum(col) / len(col) for col in zip(*genre_scores[g])]
                for g in self.all_options
            }

        elif self.category == "Studio":
            studio_count  = Counter()
            studio_scores = {}
            for a in animes:
                s = (a.get("studio") or "Unknown").strip()
                if not s:
                    continue
                dims = a.get("global_score_dimensions", [0, 0, 0, 0, 0])
                studio_count[s] += 1
                studio_scores.setdefault(s, []).append(dims)
            self.all_options = [s for s, _ in studio_count.most_common(10)]
            self.data_dict   = {
                s: [sum(col) / len(col) for col in zip(*studio_scores[s])]
                for s in self.all_options
            }

        self.item1 = self.all_options[0] if len(self.all_options) > 0 else None
        self.item2 = self.all_options[1] if len(self.all_options) > 1 else self.item1

        self._build_ui()

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _try_update(ctrl):
        try:
            if ctrl.page:
                ctrl.update()
        except Exception:
            pass

    def _dd_opts(self, query: str = "") -> list:
        """Kembalikan daftar ft.dropdown.Option difilter query."""
        opts = self.all_options if not query else [
            o for o in self.all_options if query.lower() in o.lower()
        ]
        return [ft.dropdown.Option(o) for o in opts]

    # ── Event Handlers ────────────────────────────────────────────────────────

    def _on_switch_change(self, e):
        self.is_compare = e.control.value
        self.block2.visible      = self.is_compare
        self.legend2_row.visible = self.is_compare
        self._try_update(self.block2)
        self._try_update(self.legend2_row)
        self._refresh_chart()

    # --- Slot 1 ---
    def _on_search1_change(self, e):
        """Filter dropdown item1 secara mandiri."""
        query = e.control.value or ""
        self.dd_item1.options = self._dd_opts(query)
        self._try_update(self.dd_item1)

    def _on_item1_change(self, e):
        val = e.data if e.data else e.control.value
        if val and val in self.all_options:
            self.item1 = val
            # Reset filter setelah pilihan valid
            if self.category == "Anime":
                self.tf_search1.value = ""
                self.dd_item1.options = self._dd_opts()
                self._try_update(self.tf_search1)
            self._try_update(self.dd_item1)
            self._refresh_chart()

    # --- Slot 2 ---
    def _on_search2_change(self, e):
        """Filter dropdown item2 secara mandiri."""
        query = e.control.value or ""
        self.dd_item2.options = self._dd_opts(query)
        self._try_update(self.dd_item2)

    def _on_item2_change(self, e):
        val = e.data if e.data else e.control.value
        if val and val in self.all_options:
            self.item2 = val
            if self.category == "Anime":
                self.tf_search2.value = ""
                self.dd_item2.options = self._dd_opts()
                self._try_update(self.tf_search2)
            self._try_update(self.dd_item2)
            self._refresh_chart()

    # ── Render ────────────────────────────────────────────────────────────────

    def _refresh_chart(self):
        s1 = self.data_dict.get(self.item1, [0] * 5) if self.item1 else [0] * 5
        s2 = self.data_dict.get(self.item2, [0] * 5) if (self.item2 and self.is_compare) else [0] * 5

        self.chart_container.content = detail_radar_chart(
            global_scores=s1,
            personal_scores=s2,
            labels=self._labels,
            theme=self._theme,
            size=220,
        )
        self.legend1_text.value = self.item1 or "None"
        self.legend2_text.value = self.item2 or "None"

        self._try_update(self.chart_container)
        self._try_update(self.legend1_text)
        self._try_update(self.legend2_text)

    # ── Build UI ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        theme    = self._theme or {}
        c_text   = theme.get("text_main",      "#1A1A1A")
        c_text2  = theme.get("text_secondary", "#555555")
        c_border = theme.get("border_color",   "#E0D0D8")
        c_g      = theme.get("radar_g_border", "#C07090")
        c_p      = theme.get("radar_p_border", "#7090C0")
        is_anime = self.category == "Anime"

        # ── Header + switch ──
        header_row = ft.Row(
            controls=[
                ft.Text(f"{self.category} Radar", size=14,
                        weight=ft.FontWeight.BOLD, color=c_text),
                ft.Row([
                    ft.Text("Bandingkan", size=10, color=c_text2),
                    ft.Switch(value=self.is_compare,
                              on_change=self._on_switch_change, scale=0.7),
                ], spacing=2, alignment=ft.MainAxisAlignment.END),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # ── Helper: buat dropdown ──
        def _mk_dd(on_change):
            dd = ft.Dropdown(
                on_text_change=on_change,
                height=36, text_size=11,
                content_padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_color=c_border, border_radius=8, color=c_text,
                options=self._dd_opts(),
            )
            return dd

        # ── Helper: buat search TextField ──
        def _mk_search(on_change, placeholder):
            return ft.TextField(
                hint_text=placeholder,
                on_change=on_change,
                height=34,
                text_size=11,
                content_padding=ft.padding.symmetric(horizontal=10, vertical=2),
                border_color=c_border,
                border_radius=8,
                color=c_text,
                prefix_icon=ft.Icons.SEARCH,
            )

        # ── Slot 1 ──
        self.dd_item1 = _mk_dd(self._on_item1_change)
        self.dd_item1.value = self.item1

        if is_anime:
            self.tf_search1 = _mk_search(self._on_search1_change, "Cari Anime 1...")
            slot1_controls = [
                ft.Text("Anime 1", size=10, color=c_text2, weight=ft.FontWeight.BOLD),
                self.tf_search1,
                self.dd_item1,
            ]
        else:
            slot1_controls = [
                ft.Text("Item 1", size=10, color=c_text2, weight=ft.FontWeight.BOLD),
                self.dd_item1,
            ]

        block1 = ft.Column(controls=slot1_controls, spacing=4)

        # ── Slot 2 ──
        self.dd_item2 = _mk_dd(self._on_item2_change)
        self.dd_item2.value = self.item2

        if is_anime:
            self.tf_search2 = _mk_search(self._on_search2_change, "Cari Anime 2...")
            slot2_controls = [
                ft.Text("Anime 2", size=10, color=c_text2, weight=ft.FontWeight.BOLD),
                self.tf_search2,
                self.dd_item2,
            ]
        else:
            slot2_controls = [
                ft.Text("Item 2", size=10, color=c_text2, weight=ft.FontWeight.BOLD),
                self.dd_item2,
            ]

        self.block2 = ft.Column(controls=slot2_controls, spacing=4, visible=self.is_compare)

        controls_col = ft.Column(controls=[block1, self.block2], spacing=8)

        # ── Chart container ──
        self.chart_container = ft.Container(
            alignment=ft.Alignment.CENTER,
        )

        # ── Legend ──
        self.legend1_text = ft.Text(
            self.item1 or "None", size=11, color=c_text2,
            weight=ft.FontWeight.W_500, max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS, width=120,
        )
        self.legend2_text = ft.Text(
            self.item2 or "None", size=11, color=c_text2,
            weight=ft.FontWeight.W_500, max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS, width=120,
        )

        def _dot(color):
            return ft.Container(width=10, height=10, bgcolor=color, border_radius=5)

        self.legend1_row = ft.Row(
            spacing=6, alignment=ft.MainAxisAlignment.CENTER,
            controls=[_dot(c_g), self.legend1_text],
        )
        self.legend2_row = ft.Row(
            spacing=6, alignment=ft.MainAxisAlignment.CENTER,
            controls=[_dot(c_p), self.legend2_text],
            visible=self.is_compare,
        )

        legends_col = ft.Column(
            controls=[self.legend1_row, self.legend2_row],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.content = ft.Column(
            controls=[
                ft.Container(content=header_row, padding=ft.padding.only(top=4, bottom=8)),
                controls_col,
                ft.Container(height=8),
                ft.Row([self.chart_container], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=8),
                legends_col,
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        )

        self._refresh_chart()

import flet as ft
import flet.canvas as cv
import math


# ═══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def build_radar_chart(global_scores, personal_scores, labels, theme, size=300):
    cx = cy = size / 2
    max_r = size / 2 - 40
    n = len(labels)
    grid_levels = 5
    shapes = []

    def petal_path(angle_deg, length, width_factor=0.46, notch_depth=0.11):
        rad = math.radians(angle_deg)
        rad_perp = math.radians(angle_deg + 90)

        w = length * width_factor

        notch_dist = length * 0.92
        notch_lx = cx + notch_dist * math.cos(rad) + w * 0.22 * math.cos(rad_perp)
        notch_ly = cy + notch_dist * math.sin(rad) + w * 0.22 * math.sin(rad_perp)
        notch_rx = cx + notch_dist * math.cos(rad) - w * 0.22 * math.cos(rad_perp)
        notch_ry = cy + notch_dist * math.sin(rad) - w * 0.22 * math.sin(rad_perp)

        indent_x = cx + (length - length * notch_depth) * math.cos(rad)
        indent_y = cy + (length - length * notch_depth) * math.sin(rad)

        c1x = cx + length * 0.50 * math.cos(rad) + w * 0.95 * math.cos(rad_perp)
        c1y = cy + length * 0.50 * math.sin(rad) + w * 0.95 * math.sin(rad_perp)
        c2x = notch_lx - length * 0.15 * math.cos(rad) + w * 0.45 * math.cos(rad_perp)
        c2y = notch_ly - length * 0.15 * math.sin(rad) + w * 0.45 * math.sin(rad_perp)

        c5x = cx + length * 0.50 * math.cos(rad) - w * 0.95 * math.cos(rad_perp)
        c5y = cy + length * 0.50 * math.sin(rad) - w * 0.95 * math.sin(rad_perp)
        c6x = notch_rx - length * 0.15 * math.cos(rad) - w * 0.45 * math.cos(rad_perp)
        c6y = notch_ry - length * 0.15 * math.sin(rad) - w * 0.45 * math.sin(rad_perp)

        ci1x = indent_x + w * 0.20 * math.cos(rad_perp)
        ci1y = indent_y + w * 0.20 * math.sin(rad_perp)
        ci2x = indent_x - w * 0.20 * math.cos(rad_perp)
        ci2y = indent_y - w * 0.20 * math.sin(rad_perp)

        return [
            cv.Path.MoveTo(cx, cy),
            cv.Path.CubicTo(c1x, c1y, c2x, c2y, notch_lx, notch_ly),
            cv.Path.CubicTo(ci1x, ci1y, ci2x, ci2y, notch_rx, notch_ry),
            cv.Path.CubicTo(c6x, c6y, c5x, c5y, cx, cy),
            cv.Path.Close(),
        ]

    # Grid rings (poligon)
    for level in range(1, grid_levels + 1):
        r = max_r * level / grid_levels
        grid_pts = []
        for i in range(n):
            angle = math.radians(-90 + i * 360 / n)
            grid_pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        path_cmds = [ft.canvas.Path.MoveTo(grid_pts[0][0], grid_pts[0][1])]
        for p in grid_pts[1:]:
            path_cmds.append(ft.canvas.Path.LineTo(p[0], p[1]))
        path_cmds.append(ft.canvas.Path.Close())
        shapes.append(ft.canvas.Path(
            elements=path_cmds,
            paint=ft.Paint(color=theme["radar_grid"], stroke_width=0.8, style=ft.PaintingStyle.STROKE)
        ))

    # Axis lines
    for i in range(n):
        angle = math.radians(-90 + i * 360 / n)
        shapes.append(ft.canvas.Path(
            elements=[
                ft.canvas.Path.MoveTo(cx, cy),
                ft.canvas.Path.LineTo(cx + max_r * math.cos(angle), cy + max_r * math.sin(angle)),
            ],
            paint=ft.Paint(color=theme["radar_grid"], stroke_width=0.8)
        ))

    # Global petals
    for i, score in enumerate(global_scores):
        angle_deg = -90 + i * 360 / n
        length = (score / 10) * max_r
        cmds = petal_path(angle_deg, length)

        shapes.append(ft.canvas.Path(
            elements=cmds,
            paint=ft.Paint(color=theme["radar_g_area"], style=ft.PaintingStyle.FILL)
        ))
        shapes.append(ft.canvas.Path(
            elements=cmds,
            paint=ft.Paint(color=theme["radar_g_border"], stroke_width=1.5, style=ft.PaintingStyle.STROKE)
        ))
        for frac in [0.65, 0.4]:
            sub_cmds = petal_path(angle_deg, length * frac, width_factor=0.28)
            shapes.append(ft.canvas.Path(
                elements=sub_cmds,
                paint=ft.Paint(color=theme["radar_g_area"], stroke_width=0.6, style=ft.PaintingStyle.STROKE)
            ))

    # Personal petals
    if any(s > 0 for s in personal_scores):
        for i, score in enumerate(personal_scores):
            angle_deg = -90 + i * 360 / n
            length = (score / 10) * max_r
            cmds = petal_path(angle_deg, length)

            shapes.append(ft.canvas.Path(
                elements=cmds,
                paint=ft.Paint(color=theme["radar_p_area"], style=ft.PaintingStyle.FILL)
            ))
            shapes.append(ft.canvas.Path(
                elements=cmds,
                paint=ft.Paint(color=theme["radar_p_border"], stroke_width=1.5, style=ft.PaintingStyle.STROKE)
            ))

    # Labels
    label_r = max_r + 22
    for i, label in enumerate(labels):
        angle = math.radians(-90 + i * 360 / n)
        lx = cx + label_r * math.cos(angle)
        ly = cy + label_r * math.sin(angle)
        shapes.append(ft.canvas.Text(
            x=lx, y=ly,
            value=label,
            alignment=ft.Alignment(0, 0),
            style=ft.TextStyle(size=11, color=theme["radar_labels"], weight=ft.FontWeight.W_500),
        ))

    # Center dot
    shapes.append(ft.canvas.Circle(cx, cy, 4, ft.Paint(color=theme["radar_grid"], style=ft.PaintingStyle.FILL)))

    return ft.Container(
        width=size,
        height=size,
        content=ft.canvas.Canvas(shapes=shapes, width=size, height=size)
    )


def score_dropdown(label: str, theme):
    return ft.Column(
        spacing=4,
        controls=[
            ft.Text(label, size=11, color=theme["text_main"], weight=ft.FontWeight.W_500),
            ft.Dropdown(
                value="1",
                options=[ft.dropdown.Option(str(i)) for i in range(1, 11)],
                width=110,
                height=42,
                bgcolor=theme["card"],
                border_color=theme["border_color"],
                color=theme["text_main"],
                border_radius=8,
                text_size=13,
                content_padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
        ]
    )


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
#  LEFT PANEL
# ═══════════════════════════════════════════════════════════════

class LeftPanel(ft.Container):
    def __init__(self, detail_anime: dict, theme):
        self.detail_anime = detail_anime
        self._theme = theme
        cover = detail_anime.get("cover_path", "")
        gendres = detail_anime.get("genre", [])
        studio = detail_anime.get("studio", "N/A")
        type = detail_anime.get("type", "N/A")
        episode = detail_anime.get("episodes", "N/A")
        metaTags = [studio, type, str(episode)]

        super().__init__(
            width=300,
            content=ft.Column(
                spacing=16,
                controls=[
                    self._build_poster(cover),
                    ft.Text(self.detail_anime.get("title", "Anime Detail"), size=22,
                            weight=ft.FontWeight.W_800, color=self._theme["text_main"]),
                    self._build_genre_tags(gendres),
                    self._build_meta_tags(metaTags),
                    self._build_synopsis(),
                ]
            )
        )

    def _build_poster(self, cover_path):
        return ft.Container(
            width=300,
            height=360,
            border_radius=16,
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

    def _build_synopsis(self):
        return ft.Container(
            bgcolor=self._theme["bg_secondary"],
            border_radius=12,
            padding=ft.padding.all(16),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text("Synopsis", size=13, weight=ft.FontWeight.W_700, color=self._theme["text_main"]),
                    ft.Text(
                        self.detail_anime.get("synopsis", "No synopsis available."),
                        size=12, color=self._theme["text_secondary"]
                    )
                ]
            )
        )


# ═══════════════════════════════════════════════════════════════
#  RIGHT PANEL
# ═══════════════════════════════════════════════════════════════

class RightPanel(ft.Container):
    def __init__(self, page: ft.Page, data_manager, anime_id, theme):
        self.my_page = page
        self.data_manager = data_manager
        self.anime_id = anime_id
        self._theme = theme
        self.user_id = data_manager.baca_sesi()

        user_list_score = data_manager.get_rating_user_as_list(self.user_id, anime_id)
        global_list_score = data_manager.get_skor_global_dimensi_as_list(anime_id)

        if not user_list_score:
            user_list_score = [0, 0, 0, 0, 0]
        if not global_list_score:
            global_list_score = [0, 0, 0, 0, 0]

        global_avg_score = data_manager.hitung_skor_global(anime_id)
        user_avg_score = data_manager.hitung_skor_personal(self.user_id, anime_id)

        self.radar_container = ft.Container(content=self._build_radar(global_list_score, user_list_score))
        self.score_cards_container = ft.Container(content=self._build_score_cards(global_avg_score, user_avg_score))
        self._global_btn_ref = ft.Ref[ft.ElevatedButton]()
        self._personal_btn_ref = ft.Ref[ft.ElevatedButton]()

        super().__init__(
            expand=True,
            bgcolor=self._theme["card"],
            border_radius=20,
            padding=ft.padding.all(28),
            content=ft.Column(
                spacing=20,
                controls=[
                    self.score_cards_container,
                    ft.Text("RADAR CHART", size=11, color=self._theme["text_muted"], weight=ft.FontWeight.W_700),
                    self.radar_container,
                    self._build_legend(),
                    self._build_dropdowns(),
                    self._build_action_buttons(),
                ]
            )
        )

    def _build_score_cards(self, global_score, user_score):
        return ft.Row(
            spacing=12,
            controls=[
                score_card(str(global_score), self._theme, global_score=True),
                score_card(str(user_score), self._theme),
            ]
        )

    def _build_radar(self, global_scores, personal_scores):
        labels = ["Plot", "Visual", "Audio", "Characterization", "Direction"]
        global_scores = global_scores if global_scores else [0, 0, 0, 0, 0]
        personal_scores = personal_scores if personal_scores else [0, 0, 0, 0, 0]
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[build_radar_chart(global_scores, personal_scores, labels, self._theme)]
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

    def _build_dropdowns(self):
        self.dropdown_controls = {}
        categories = ["Plot", "Visual", "Audio", "Characterization", "Direction"]
        dropdown_list = []

        for cat in categories:
            ui_component = score_dropdown(cat,  self._theme)
            if isinstance(ui_component, ft.Column):
                dropdown_obj = next(c for c in ui_component.controls if isinstance(c, ft.Dropdown))
                self.dropdown_controls[cat] = dropdown_obj
            else:
                self.dropdown_controls[cat] = ui_component
            dropdown_list.append(ui_component)

        return ft.Row(wrap=True, spacing=8, run_spacing=8, controls=dropdown_list)

    def save_rating(self, e):
        try:
            user_scores = {}
            for category, dd in self.dropdown_controls.items():
                val = dd.value if dd.value is not None else 0
                user_scores[category.lower()] = int(val)

            user_id = self.data_manager.baca_sesi()
            self.data_manager.simpan_rating(user_id, self.anime_id, user_scores)

            new_avg_global = self.data_manager.hitung_skor_global(self.anime_id)
            new_avg_personal = self.data_manager.hitung_skor_personal(user_id, self.anime_id)
            new_list_score = list(user_scores.values())
            new_global_list_score = self.data_manager.get_skor_global_dimensi_as_list(self.anime_id)

            self.score_cards_container.content = self._build_score_cards(new_avg_global, new_avg_personal)
            self.radar_container.content = self._build_radar(new_global_list_score, new_list_score)

            self.my_page.update()
            self.my_page.snack_bar = ft.SnackBar(ft.Text("Rating Berhasil Diperbarui!"),
                                                 bgcolor= self._theme("success", "green"))
            self.my_page.snack_bar.open = True
            self.my_page.update()

        except Exception as err:
            print(f"Error: {err}")

    def delete_rating(self, e):
        user_id = self.data_manager.baca_sesi()
        self.data_manager.hapus_rating(user_id, self.anime_id)

        new_avg_global = self.data_manager.hitung_skor_global(self.anime_id)
        new_global_list_score = self.data_manager.get_skor_global_dimensi_as_list(self.anime_id)
        new_avg_personal = self.data_manager.hitung_skor_personal(user_id, self.anime_id)
        new_list_score = [0, 0, 0, 0, 0]

        self.score_cards_container.content = self._build_score_cards(new_avg_global, new_avg_personal)
        self.radar_container.content = self._build_radar(new_global_list_score, new_list_score)

        self.my_page.update()
        self.my_page.snack_bar = ft.SnackBar(ft.Text("Rating Berhasil Dihapus!"),
                                             bgcolor=self._theme.get("success", "green"))
        self.my_page.snack_bar.open = True
        self.my_page.update()

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


# ═══════════════════════════════════════════════════════════════
#  UI DETAIL
# ═══════════════════════════════════════════════════════════════

class UIDetail(ft.Column):
    def __init__(self, page, data_manager, auth_manager, screen_manager, theme, anime_id):
        self.my_page = page
        self.data_manager = data_manager
        self.screen_manager = screen_manager
        self.anime_id = anime_id
        self._theme = theme
        self.main_scroll = self  # <--- Ini doang tambahannya bang

        self.detail_anime = self.data_manager.get_detail_anime(anime_id)

        # 1. Komponen Tombol Back
        self.back_btn = ft.TextButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=self._theme["primary"],
            content=ft.Text("Back", color=self._theme["primary"]),
            on_click=lambda _: self.screen_manager.kembali_ke_asal()
        )

        # 2. Konten Utama
        self.main_content = ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
            controls=[
                LeftPanel(self.detail_anime, self._theme),
                RightPanel(self.my_page, self.data_manager, anime_id, self._theme),
            ]
        )

        # 3. Setting Layout dimasukkan ke dalam Container pembungkus
        self.container_wrapper = ft.Container(
            bgcolor=self._theme["bg"],
            padding=ft.padding.all(24),
            border_radius=10,
            content=ft.Column(
                controls=[
                    self.back_btn,
                    self.main_content,
                ],
                spacing=10,
            )
        )

        # 4. Jalankan init Column dengan pembungkus tadi
        super().__init__(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[self.container_wrapper]
        )
import flet as ft
import flet.canvas as cv
import math

# ── Warna Tema ────────────────────────────────────────
C_BG = "#FCF8FA"
C_BG2 = "#F5EEF2"
C_SAKURA = "#C07090"
C_SAKURA_LT = "#F9F0F5"
C_BLUE_LT = "#D4EBF8"
C_TEXT = "#3D2535"
C_TEXT2 = "#8B6A7A"
C_TEXT3 = "#B0909A"
C_BORDER = "#EDE0E8"
C_GOLD = "#C08030"
C_PURPLE = "#9060A0"
C_WHITE = "#FFFFFF"
# ═══════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def build_radar_chart(global_scores, personal_scores, labels, size=260):
    cx = cy = size / 2
    max_r = size / 2 - 30
    n = len(labels)
    grid_levels = 5
    shapes = []

    def polygon_points(scores):
        pts = []
        for i, s in enumerate(scores):
            angle = math.radians(-90 + i * 360 / n)
            r = (s / 10) * max_r
            pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
        return pts

    # Grid rings
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
            paint=ft.Paint(color="#E0DDE8", stroke_width=1, style=ft.PaintingStyle.STROKE)
        ))

    # Axis lines
    for i in range(n):
        angle = math.radians(-90 + i * 360 / n)
        shapes.append(ft.canvas.Path(
            elements=[
                ft.canvas.Path.MoveTo(cx, cy),
                ft.canvas.Path.LineTo(
                    cx + max_r * math.cos(angle),
                    cy + max_r * math.sin(angle)
                ),
            ],
            paint=ft.Paint(color="#E0DDE8", stroke_width=1)
        ))

    # Global filled polygon
    g_pts = polygon_points(global_scores)
    g_cmds = [cv.Path.MoveTo(g_pts[0][0], g_pts[0][1])]
    for p in g_pts[1:]:
        g_cmds.append(cv.Path.LineTo(p[0], p[1]))
    g_cmds.append(cv.Path.Close())
    shapes.append(cv.Path(
        elements=g_cmds,
        paint=ft.Paint(color="#4A90D940", style=ft.PaintingStyle.FILL)
    ))
    shapes.append(cv.Path(
        elements=g_cmds,
        paint=ft.Paint(color="#4A90D9", stroke_width=2, style=ft.PaintingStyle.STROKE)
    ))

    # Personal filled polygon
    if any(s > 0 for s in personal_scores):
        p_pts = polygon_points(personal_scores)
        p_cmds = [cv.Path.MoveTo(p_pts[0][0], p_pts[0][1])]
        for p in p_pts[1:]:
            p_cmds.append(cv.Path.LineTo(p[0], p[1]))
        p_cmds.append(cv.Path.Close())
        shapes.append(cv.Path(
            elements=p_cmds,
            paint=ft.Paint(color="#FFB6C140", style=ft.PaintingStyle.FILL)
        ))
        shapes.append(cv.Path(
            elements=p_cmds,
            paint=ft.Paint(color="#FF8FA3", stroke_width=2, style=ft.PaintingStyle.STROKE)
        ))

    # Labels
    label_r = max_r + 18
    for i, label in enumerate(labels):
        angle = math.radians(-90 + i * 360 / n)
        lx = cx + label_r * math.cos(angle)
        ly = cy + label_r * math.sin(angle)
        shapes.append(ft.canvas.Text(
            x=lx, y=ly,
            value=label,
            alignment=ft.Alignment(0, 0),
            style=ft.TextStyle(size=10, color="#555555", weight=ft.FontWeight.W_500),
        ))

    return ft.Container(
        width=size,
        height=size,
        content=ft.canvas.Canvas(shapes=shapes, width=size, height=size)
    )


def score_dropdown(label: str):
    return ft.Column(
        spacing=4,
        controls=[
            ft.Text(label, size=11, color=C_TEXT, weight=ft.FontWeight.W_500),
            ft.Dropdown(
                value="1",
                options=[ft.dropdown.Option(str(i)) for i in range(1, 11)],
                width=110,
                height=42,
                bgcolor=C_SAKURA_LT,
                border_color=C_BORDER,
                border_radius=8,
                text_size=13,
                content_padding=ft.padding.symmetric(horizontal=10, vertical=4),
            )
        ]
    )


def score_card(value, global_score=False):
    return ft.Container(
        width=150,
        padding=ft.padding.symmetric(horizontal=16, vertical=12),
        bgcolor=C_WHITE,
        border_radius=12,
        border=ft.border.all(1, C_BORDER),
        content=ft.Column(
            spacing=2,
            controls=[
                ft.Text("USER SCORE" if not global_score else "GLOBAL SCORE", size=10, color=C_TEXT2, weight=ft.FontWeight.W_600),
                ft.Text(value, size=26, color=C_PURPLE if not global_score else C_GOLD, weight=ft.FontWeight.W_700),
                ft.Text("Your Rating" if not global_score else "Community Average Score", size=10, color=C_TEXT2)
            ]
        )
    )


def tag(text, meta=False):
    return ft.Container(
        padding=ft.padding.symmetric(horizontal=10, vertical=4),
        bgcolor= C_WHITE if not meta else C_SAKURA,
        border_radius=20,
        content=ft.Text(
            text, size=11,
            color= C_SAKURA if not meta else C_WHITE,
            weight=ft.FontWeight.W_600
        )
    )


def legend_dot(color):
    return ft.Container(width=12, height=12, bgcolor=color, border_radius=6)


# ═══════════════════════════════════════════════════════════════
#  LEFT PANEL — poster, judul, tag, synopsis
# ═══════════════════════════════════════════════════════════════

class LeftPanel(ft.Container):
    def __init__(self, detail_anime: dict):
        self.detail_anime = detail_anime
        cover = detail_anime.get("cover_path", "")
        gendres = detail_anime.get("genre", [])
        studio = detail_anime.get("studio", "N/A")
        type = detail_anime.get("type", "N/A")
        episode = detail_anime.get("episodes", "N/A")
        metaTags=[studio, type, episode]

        super().__init__(
            width=300,
            content=ft.Column(
                spacing=16,
                controls=[
                    self._build_poster(cover),
                    ft.Text(self.detail_anime.get("title", "Anime Detail"), size=22,
                            weight=ft.FontWeight.W_800, color="#1E1B2E"),
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
            controls=[tag(tag_text, meta=True) for tag_text in metaTags]
        )

    def _build_genre_tags(self, gendres):
        print("Genres:", gendres)  # Debug print untuk memastikan data genre diterima dengan benar
        return ft.Row(
            wrap=True, spacing=6, run_spacing=6,
            controls=[tag(genre) for genre in gendres]
        )

    def _build_synopsis(self):
        return ft.Container(
            bgcolor="#F8F6FF",
            border_radius=12,
            padding=ft.padding.all(16),
            content=ft.Column(
                spacing=8,
                controls=[
                    ft.Text("Synopsis", size=13,
                            weight=ft.FontWeight.W_700, color="#1E1B2E"),
                    ft.Text(
                        self.detail_anime.get("synopsis", "No synopsis available."),
                        size=12, color="#666666",
                    )
                ]
            )
        )


# ═══════════════════════════════════════════════════════════════
#  RIGHT PANEL — score, radar, dropdown, tombol
# ═══════════════════════════════════════════════════════════════

class RightPanel(ft.Container):
    def __init__(self, page: ft.Page, data_manager, anime_id):
        self.my_page = page
        self.data_manager = data_manager
        self.anime_id = anime_id
        global_avg_score = data_manager.hitung_skor_global(anime_id)
        user_avg_score = data_manager.hitung_skor_personal(data_manager.baca_sesi(), anime_id)  # Menggunakan ID pengguna yang aktif
        user_list_score = data_manager.get_list_rating_user(data_manager.baca_sesi(), anime_id)  # Mendapatkan list skor untuk radar chart
        self.radar_container = ft.Container(content=self._build_radar(user_list_score))
        self.score_cards_container = ft.Container(content=self._build_score_cards(global_avg_score, user_avg_score))
        self._global_btn_ref = ft.Ref[ft.ElevatedButton]()
        self._personal_btn_ref = ft.Ref[ft.ElevatedButton]()

        super().__init__(
            expand=True,
            bgcolor="#FFFFFF",
            border_radius=20,
            padding=ft.padding.all(28),
            content=ft.Column(
                spacing=20,
                controls=[
                    self.score_cards_container,
                    ft.Text("RADAR CHART", size=11, color="#AAAAAA",
                            weight=ft.FontWeight.W_700),
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
                score_card(str(global_score), global_score=True),
                score_card(str(user_score)),
            ]
        )

    def _build_radar(self, user_score):
        labels = ["Plot", "Visual", "Audio", "Characterization", "Direction"]
        global_scores = [7.5, 8.0, 7.0, 8.5, 8.0]
        personal_scores = user_score if user_score is not None else [0, 0, 0, 0, 0] # Pastikan personal_scores selalu berupa list dengan 5 elemen
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[build_radar_chart(global_scores, personal_scores, labels)]
        )

    def _build_legend(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
            controls=[
                ft.Row(spacing=6, controls=[
                    legend_dot("#4A90D9"),
                    ft.Text("Global", size=12, color="#555555")
                ]),
                ft.Row(spacing=6, controls=[
                    legend_dot("#FFB6C1"),
                    ft.Text("Personal", size=12, color="#555555")
                ]),
            ]
        )

    

    def _build_dropdowns(self):
        self.dropdown_controls = {}
        categories = ["Plot", "Visual", "Audio", "Characterization", "Direction"]
        dropdown_list = []

        for cat in categories:
            # Panggil fungsi UI kamu
            ui_component = score_dropdown(cat) 
            
            # ASUMSI: score_dropdown mengembalikan Column([Text, Dropdown])
            # Kita ambil Dropdown-nya (biasanya elemen terakhir/kedua)
            if isinstance(ui_component, ft.Column):
                # Mencari objek Dropdown di dalam controls milik Column
                dropdown_obj = next(c for c in ui_component.controls if isinstance(c, ft.Dropdown))
                self.dropdown_controls[cat] = dropdown_obj
            else:
                # Jika ternyata score_dropdown langsung mengembalikan Dropdown
                self.dropdown_controls[cat] = ui_component

            dropdown_list.append(ui_component)

        return ft.Row(wrap=True, spacing=8, run_spacing=8, controls=dropdown_list)

    def save_rating(self, e):
        try:
            user_scores = {}
            for category, dd in self.dropdown_controls.items():
                val = dd.value if dd.value is not None else 0
                user_scores[category.lower()] = int(val)
            
            # 1. Simpan ke JSON
            user_id = self.data_manager.baca_sesi()
            self.data_manager.simpan_rating(user_id, self.anime_id, user_scores)

            # 2. UPDATE RADAR CHART (Bagian Penting)
            # Ambil nilai dari dict ke dalam list: [5, 8, 7, 7, 7]
            new_avg_global = self.data_manager.hitung_skor_global(self.anime_id)
            new_avg_personal = self.data_manager.hitung_skor_personal(user_id, self.anime_id)
            new_list_score = list(user_scores.values())
            
            # 4. UPDATE UI TANPA REFRESH HALAMAN
            # Update bagian angka/cards
            self.score_cards_container.content = self._build_score_cards(new_avg_global, new_avg_personal)
        
            # Update bagian radar
            self.radar_container.content = self._build_radar(new_list_score)
        
            # 5. Eksekusi perubahan ke layar
            self.my_page.update()

            self.my_page.snack_bar = ft.SnackBar(ft.Text("Rating Berhasil Diperbarui!"), bgcolor="green")
            self.my_page.snack_bar.open = True
            self.my_page.update()
            
            print("Grafik berhasil diperbarui!")

        except Exception as err:
            print(f"Error: {err}")

    def _build_action_buttons(self):
        return ft.Row(
            spacing=10,
            controls=[
                ft.ElevatedButton(
                    content="Save Rating",
                    expand=True,
                    bgcolor="#F472B6", color="#FFFFFF",
                    height=46,
                    on_click=lambda _: self.save_rating(None),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        elevation=0,
                    )
                ),
                ft.OutlinedButton(
                    content="Delete Rating",
                    expand=True,
                    height=46,
                    on_click=lambda _: print("Delete rating clicked! (fungsi penghapusan belum diimplementasikan)"),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                        side=ft.BorderSide(1, "#E0DDE8"),
                        color="#666666",
                    )
                ),
            ]
        )


# ═══════════════════════════════════════════════════════════════
#  UI DETAIL — ft.Row utama yang menyatukan LeftPanel + RightPanel
# ═══════════════════════════════════════════════════════════════

class UIDetail(ft.Column):
    def __init__(self, page, data_manager, screen_manager, anime_id):
            self.my_page = page
            self.data_manager = data_manager
            self.screen_manager = screen_manager
            self.anime_id = anime_id
            
            self.detail_anime= self.data_manager.get_detail_anime(anime_id)

            self.back_btn = ft.TextButton(
                icon=ft.Icons.ARROW_BACK,
                content=ft.Text("Back to Dashboard"), # Gunakan ft.Text untuk Flet terbaru
                style=ft.ButtonStyle(color="#7C4DFF"),
                on_click=lambda _: self.screen_manager.tampilkan_dashboard() # Sesuaikan fungsi navigasimu
            )

            self.main_content = ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.START,
            spacing=20,
            controls=[
                LeftPanel(self.detail_anime),
                RightPanel(self.my_page,self.data_manager, anime_id),
            ]
            )
            super().__init__(
                spacing=10,
                controls=[
                self.back_btn,
                self.main_content,   # <-- inilah yang hilang sebelumnya!
            ]
        )
    

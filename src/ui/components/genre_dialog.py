import flet as ft

class GenreDialog(ft.AlertDialog):
    def __init__(self, page, theme, list_genre, on_genre_selected):
        self.my_page = page
        self.theme = theme
        self.list_genre = list_genre
        self.on_genre_selected = on_genre_selected
        self.selected_genre = "All Genres"
        self._chip_refs = {}

        # Buat chips list
        genre_chips = []
        chip_all = self._buat_chip("All Genres", "All Genres", aktif=True)
        self._chip_refs["All Genres"] = chip_all
        genre_chips.append(chip_all)

        for g in self.list_genre:
            chip = self._buat_chip(g, g, aktif=False)
            self._chip_refs[g] = chip
            genre_chips.append(chip)

        super().__init__(
            title=ft.Row(
                controls=[
                    ft.Row([
                         ft.Icon(ft.Icons.STYLE, color=self.theme["primary"], size=24),
                         ft.Text("Select Genre", size=20, weight=ft.FontWeight.BOLD, color=self.theme["text_main"]),
                    ], spacing=8),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.IconButton(
                            icon=ft.Icons.CLOSE, icon_size=18,
                            on_click=lambda _: self.tutup(),
                            style=ft.ButtonStyle(
                                overlay_color=ft.Colors.TRANSPARENT,
                                icon_color={
                                    ft.ControlState.HOVERED: f"{self.theme['primary']},0.8",
                                    ft.ControlState.DEFAULT: self.theme["text_muted"],
                                }
                            )
                        ),
                        bgcolor=self.theme["bg_secondary"], border_radius=20,
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            title_padding=ft.padding.only(left=24, right=16, top=16, bottom=8),
            content=ft.Container(
                width=550, height=400, padding=ft.padding.all(8),
                content=ft.Column(
                    controls=[ft.Row(controls=genre_chips, wrap=True, spacing=10, run_spacing=10, alignment=ft.MainAxisAlignment.CENTER)],
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            content_padding=ft.padding.only(left=16, right=16, bottom=24, top=8),
            bgcolor=self.theme["card"], shape=ft.RoundedRectangleBorder(radius=20), elevation=10,
        )

    def _buat_chip(self, label, data, aktif=False):
        def _on_hover(e):
            e.control.scale = 1.05 if str(e.data).lower() == "true" else 1.0
            try: e.control.update()
            except: pass

        return ft.Container(
            content=ft.Text(
                label, size=12, color=ft.Colors.WHITE if aktif else self.theme["text_main"],
                weight=ft.FontWeight.W_600 if aktif else ft.FontWeight.W_500,
            ),
            data=data,
            bgcolor=self.theme["primary"] if aktif else self.theme["primary_light"],
            border=ft.border.all(1.5 if aktif else 1, self.theme["primary"] if aktif else self.theme["border_color"]),
            border_radius=25, padding=ft.padding.symmetric(horizontal=16, vertical=8),
            on_click=self._pilih_genre, on_hover=_on_hover, scale=1.0,
            animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
        )

    def _pilih_genre(self, e):
        self.selected_genre = e.control.data
        for key, chip in self._chip_refs.items():
            aktif = (key == self.selected_genre)
            chip.bgcolor = self.theme["primary"] if aktif else self.theme["card"]
            chip.border = ft.border.all(1.5 if aktif else 1, self.theme["primary"] if aktif else self.theme["border_color"])
            chip.content.color = ft.Colors.WHITE if aktif else self.theme["text_secondary"]
            chip.content.weight = ft.FontWeight.W_600 if aktif else ft.FontWeight.W_400
            try: chip.update()
            except: pass

        self.tutup()
        if self.on_genre_selected:
            self.on_genre_selected(self.selected_genre)

    def buka(self):
        if self not in self.my_page.overlay:
            self.my_page.overlay.append(self)
        self.open = True
        try: self.my_page.update()
        except: pass

    def tutup(self):
        self.open = False
        try: self.my_page.update()
        except: pass
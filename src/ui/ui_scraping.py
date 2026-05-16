import flet as ft
import urllib.parse
from scripts.scrapjudul import DynamicAnimeScraper

class UIScraping(ft.Row):
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
            self.screen_manager,
            self.auth_manager,
            self._toggle_sidebar,
            self.theme,
            halaman_aktif="scraping"
        )

        self.scraper = DynamicAnimeScraper()
        self.scraper.data_manager = self.data_manager

        # --- UI Elements (Warna Mengikuti Theme) ---
        self._tf_query = ft.TextField(
            label="Anime Title or MAL URL",
            hint_text="e.g. 'Naruto' or 'https://myanimelist.net/anime/20'",
            expand=True,
            border_color=self.theme["border_color"],
            focused_border_color=self.theme["primary"],
            color=self.theme["text_main"],
            on_submit=self._on_search_click
        )

        self._btn_search = ft.ElevatedButton(
            "Search",
            icon=ft.Icons.SEARCH,
            bgcolor=self.theme["primary"],
            color=self.theme.get("pill_text", "#FFFFFF"), # Default to white if not set
            on_click=self._on_search_click
        )

        self._loading_indicator = ft.ProgressRing(visible=False, color=self.theme["primary"])
        self._status_text = ft.Text("", color=self.theme["text_secondary"], size=14)
        self._results_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        # Top Bar (Gradasi disesuaikan dengan tema)
        topbar = ft.Container(
            padding=ft.padding.symmetric(horizontal=16),
            height=55,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=[self.theme["bg_secondary"], self.theme["bg"]],
            ),
            shadow=ft.BoxShadow(
                blur_radius=15,
                color="#15000000",
                offset=ft.Offset(0, 4)
            ),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        ft.Icons.MENU, icon_color=self.theme["primary"],
                        on_click=self._toggle_sidebar, tooltip="Menu",
                    ),
                    ft.Column([
                        ft.Text("RadarAni", size=13, color=self.theme["primary"], weight=ft.FontWeight.BOLD),
                        ft.Text("レーダアニ", size=8, color=self.theme["text_muted"]),
                    ], spacing=0, tight=True),
                    ft.Container(expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        main_content = ft.Container(
            padding=30,
            expand=True,
            bgcolor=self.theme["bg"],
            content=ft.Column(
                controls=[
                    ft.Text("Live Anime Scraper", size=24, weight=ft.FontWeight.BOLD, color=self.theme["text_main"]),
                    ft.Text("Add anime directly from MyAnimeList by title or URL.", size=14, color=self.theme["text_secondary"]),
                    ft.Container(height=10),
                    ft.Row([self._tf_query, self._btn_search], alignment=ft.MainAxisAlignment.START),
                    ft.Row([self._loading_indicator, self._status_text], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(color=self.theme["border_color"]),
                    ft.Text("Results:", size=16, weight=ft.FontWeight.BOLD, color=self.theme["text_main"]),
                    self._results_container,
                ],
                expand=True
            )
        )

        self._main_col = ft.Column(
            controls=[topbar, main_content],
            spacing=0, expand=True,
        )

        self.controls = [self._sidebar_widget, self._main_col]

    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._sidebar_widget.update()

    def submit_field(self, e=None):
        self._on_search_click(e)

    def _on_search_click(self, e):
        query = self._tf_query.value.strip()
        if not query:
            return

        danger_color = self.theme.get("danger", ft.Colors.RED_400)

        if "myanimelist.net/anime/" not in query and len(query) < 3:
            self._status_text.value = "Input minimal 3 karakter. Jika judul memang sangat pendek, harap gunakan URL MyAnimeList."
            self._status_text.color = danger_color
            self._loading_indicator.visible = False
            self._results_container.controls.clear()
            self.update()
            return

        self._status_text.color = self.theme["text_secondary"]
        self._status_text.value = "Searching..."
        self._loading_indicator.visible = True
        self._results_container.controls.clear()
        self.update()

        try:
            if "myanimelist.net/anime/" in query:
                try:
                    mal_id = int(query.split('/')[4])
                    is_duplicate, judul_terdaftar = self.scraper._cek_duplikasi(mal_id)

                    # Fetch judul dan thumbnail dari halaman MAL
                    judul, thumb_url = self.scraper.dapatkan_info_dari_url(query)
                    label_text = f"{judul} (Already in database)" if is_duplicate else judul

                    teks_judul = ft.Text(
                        value=label_text,
                        color=danger_color if is_duplicate else self.theme["text_main"],
                        size=14,
                        expand=True,
                    )

                    btn_add = ft.ElevatedButton(
                        "Added" if is_duplicate else "Add Anime",
                        icon=ft.Icons.CHECK if is_duplicate else ft.Icons.ADD,
                        bgcolor=self.theme["bg_secondary"] if is_duplicate else self.theme["primary"],
                        color=self.theme["text_muted"] if is_duplicate else self.theme.get("pill_text", "#FFFFFF"),
                        disabled=is_duplicate,
                        data=(judul, query, thumb_url),
                        on_click=self._on_add_click,
                    )

                    row = ft.Row(
                        controls=[
                            ft.Image(src=thumb_url, width=40, height=55, fit=ft.BoxFit.COVER)
                            if thumb_url else ft.Container(width=40, height=55, bgcolor=self.theme["bg_secondary"]),
                            teks_judul,
                            btn_add,
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    )
                    self._results_container.controls.append(row)
                    self._status_text.value = "Anime already in database." if is_duplicate else "1 result found."

                except (IndexError, ValueError):
                    self._results_container.controls.append(
                        ft.Text("Invalid MyAnimeList URL format.", color=danger_color)
                    )
            else:
                # --- Jalur pencarian judul ---
                kandidat_list = self.scraper.dapatkan_kandidat_judul(query)
                if not kandidat_list:
                    self._status_text.value = "No results found."
                else:
                    self._status_text.value = f"Found {len(kandidat_list)} results."
                    for kandidat in kandidat_list:
                        judul, url, thumb = kandidat

                        try:
                            mal_id = int(url.split('/')[4])
                            is_duplicate, judul_terdaftar = self.scraper._cek_duplikasi(mal_id)
                        except:
                            is_duplicate = False

                        label_text = f"{judul} (Already in database)" if is_duplicate else judul

                        teks_judul = ft.Text(
                            value=label_text,
                            color=danger_color if is_duplicate else self.theme["text_main"],
                            size=14,
                            expand=True,
                        )

                        btn_add = ft.ElevatedButton(
                            "Added" if is_duplicate else "Add Anime",
                            icon=ft.Icons.CHECK if is_duplicate else ft.Icons.ADD,
                            bgcolor=self.theme["bg_secondary"] if is_duplicate else self.theme["primary"],
                            color=self.theme["text_muted"] if is_duplicate else self.theme.get("pill_text", "#FFFFFF"),
                            disabled=is_duplicate,
                            data=kandidat,
                            on_click=self._on_add_click,
                        )

                        row = ft.Row(
                            controls=[
                                ft.Image(src=thumb, width=40, height=55, fit=ft.BoxFit.COVER)
                                if thumb else ft.Container(width=40, height=55, bgcolor=self.theme["bg_secondary"]),
                                teks_judul,
                                btn_add,
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                        self._results_container.controls.append(row)

        except Exception as ex:
            self._status_text.value = f"Error: {ex}"
            self._status_text.color = danger_color

        self._loading_indicator.visible = False
        self.update()

    def _on_add_click(self, e):
        judul, url, thumb = e.control.data

        e.control.disabled = True
        e.control.text = "Adding..."
        e.control.icon = ft.Icons.HOURGLASS_EMPTY
        self._status_text.color = self.theme["text_secondary"]
        self._status_text.value = f"Adding '{judul}'... Please wait."
        self._loading_indicator.visible = True
        e.control.update()
        self.update()

        try:
            self.scraper.eksekusi_tambah_anime(url, thumb)
            e.control.text = "Added"
            e.control.icon = ft.Icons.CHECK
            e.control.bgcolor = self.theme["bg_secondary"]
            e.control.color = self.theme["text_muted"]
            self._status_text.color = self.theme.get("success", "#10B981") # Warna success
            self._status_text.value = f"'{judul}' added successfully!"
        except Exception as ex:
            e.control.disabled = False
            e.control.text = "Add Anime"
            e.control.icon = ft.Icons.ADD
            self._status_text.color = self.theme.get("danger", ft.Colors.RED_400)
            self._status_text.value = f"Error adding anime: {ex}"

        self._loading_indicator.visible = False
        e.control.update()
        self.update()
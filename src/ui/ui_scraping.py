import flet as ft
import threading
import urllib.parse
from scripts.scrapjudul import DynamicAnimeScraper

C_SAKURA = "#C07090"
C_SAKURA_LT = "#F9F0F5"
C_TEXT = "#3D2535"
C_TEXT2 = "#8B6A7A"
C_TEXT3 = "#B0909A"
C_BORDER = "#EDE0E8"
C_WHITE = "#FFFFFF"
C_BG = "#FCF8FA"
C_BG2 = "#F5EEF2"


class UIScraping(ft.Row):
    def __init__(self, page, data_manager, auth_manager, screen_manager):
        super().__init__()
        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager

        self.expand = True
        self.spacing = 0
        self._sidebar_open = False

        from src.ui.ui_home import _sidebar
        self._sidebar_widget = _sidebar(
            screen_manager, auth_manager,
            self._toggle_sidebar, halaman_aktif="scraping"
        )

        self.scraper = DynamicAnimeScraper()
        self.scraper.data_manager = self.data_manager

        # --- UI Elements ---
        self._tf_query = ft.TextField(
            label="Anime Title or MAL URL",
            hint_text="e.g. 'Naruto' or 'https://myanimelist.net/anime/20'",
            expand=True,
            border_color=C_BORDER,
            focused_border_color=C_SAKURA,
            color=C_TEXT,
        )

        self._btn_search = ft.ElevatedButton(
            "Search",
            icon=ft.Icons.SEARCH,
            bgcolor=C_SAKURA,
            color=C_WHITE,
            on_click=self._on_search_click,
        )

        self._loading_indicator = ft.ProgressRing(visible=False, color=C_SAKURA)
        self._status_text = ft.Text("", color=C_TEXT2, size=14)
        self._results_container = ft.Column(
            spacing=10, scroll=ft.ScrollMode.AUTO, expand=True
        )

        # Top Bar
        topbar = ft.Container(
            padding=ft.padding.symmetric(horizontal=16),
            height=55,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1),
                end=ft.Alignment(0, 1),
                colors=["#A1C4FD", "#E0F2FE"],
            ),
            shadow=ft.BoxShadow(
                blur_radius=15,
                color="#15000000",
                offset=ft.Offset(0, 4),
            ),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        ft.Icons.MENU,
                        icon_color=C_SAKURA,
                        on_click=self._toggle_sidebar,
                        tooltip="Menu",
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "RadarAni",
                                size=13,
                                color=C_SAKURA,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text("レーダアニ", size=8, color=C_TEXT3),
                        ],
                        spacing=0,
                        tight=True,
                    ),
                    ft.Container(expand=True),
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        main_content = ft.Container(
            padding=30,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Live Anime Scraper",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=C_TEXT,
                    ),
                    ft.Text(
                        "Add anime directly from MyAnimeList by title or URL.",
                        size=14,
                        color=C_TEXT2,
                    ),
                    ft.Container(height=10),
                    ft.Row(
                        [self._tf_query, self._btn_search],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Row(
                        [self._loading_indicator, self._status_text],
                        alignment=ft.MainAxisAlignment.START,
                    ),
                    ft.Divider(color=C_BORDER),
                    ft.Text(
                        "Results:",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=C_TEXT,
                    ),
                    self._results_container,
                ],
                expand=True,
            ),
        )

        self._main_col = ft.Column(
            controls=[topbar, main_content],
            spacing=0,
            expand=True,
        )

        self.controls = [self._sidebar_widget, self._main_col]

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._sidebar_widget.update()

    def _set_searching(self, is_searching: bool):
        """Lock/unlock the search button and show/hide the spinner."""
        self._btn_search.disabled = is_searching
        self._btn_search.text = "Searching…" if is_searching else "Search"
        self._btn_search.icon = (
            ft.Icons.HOURGLASS_EMPTY if is_searching else ft.Icons.SEARCH
        )
        self._loading_indicator.visible = is_searching
        self._btn_search.update()
        self._loading_indicator.update()

    # ------------------------------------------------------------------ #
    #  Search                                                              #
    # ------------------------------------------------------------------ #

    def _on_search_click(self, e):
        query = self._tf_query.value.strip()
        if not query:
            return

        if "myanimelist.net/anime/" not in query and len(query) < 3:
            self._status_text.value = (
                "Input minimal 3 karakter. "
                "Jika judul memang sangat pendek, harap gunakan URL MyAnimeList."
            )
            self._status_text.color = ft.Colors.RED_400
            self._status_text.update()
            return

        self._status_text.color = C_TEXT2
        self._status_text.value = "Searching…"
        self._results_container.controls.clear()
        self._set_searching(True)
        self._status_text.update()
        self._results_container.update()

        # Run the blocking scrape on a background thread so the UI stays live
        threading.Thread(
            target=self._do_search, args=(query,), daemon=True
        ).start()

    def _do_search(self, query: str):
        """Runs on a background thread — never call .update() on page here,
        only mutate controls then call self.update() at the end."""
        new_rows: list[ft.Control] = []
        status_msg = ""
        status_color = C_TEXT2

        try:
            if "myanimelist.net/anime/" in query:
                try:
                    mal_id = int(query.split("/")[4])
                    is_duplicate, _ = self.scraper._cek_duplikasi(mal_id)
                    judul, thumb_url = self.scraper.dapatkan_info_dari_url(query)

                    label_text = (
                        f"{judul} (Already in database)" if is_duplicate else judul
                    )
                    row = self._build_result_row(
                        judul=judul,
                        url=query,
                        thumb=thumb_url,
                        label_text=label_text,
                        is_duplicate=is_duplicate,
                        data=(judul, query, thumb_url),
                    )
                    new_rows.append(row)
                    status_msg = (
                        "Anime already in database." if is_duplicate else "1 result found."
                    )

                except (IndexError, ValueError):
                    new_rows.append(
                        ft.Text("Invalid MyAnimeList URL format.", color=ft.Colors.RED_400)
                    )
                    status_msg = "Invalid URL."
                    status_color = ft.Colors.RED_400

            else:
                kandidat_list = self.scraper.dapatkan_kandidat_judul(query)
                if not kandidat_list:
                    status_msg = "No results found."
                else:
                    status_msg = f"Found {len(kandidat_list)} results."
                    for kandidat in kandidat_list:
                        judul, url, thumb = kandidat
                        try:
                            mal_id = int(url.split("/")[4])
                            is_duplicate, _ = self.scraper._cek_duplikasi(mal_id)
                        except Exception:
                            is_duplicate = False

                        label_text = (
                            f"{judul} (Already in database)" if is_duplicate else judul
                        )
                        row = self._build_result_row(
                            judul=judul,
                            url=url,
                            thumb=thumb,
                            label_text=label_text,
                            is_duplicate=is_duplicate,
                            data=kandidat,
                        )
                        new_rows.append(row)

        except Exception as ex:
            status_msg = f"Error: {ex}"
            status_color = ft.Colors.RED_400

        self._results_container.controls.clear()
        self._results_container.controls.extend(new_rows)
        self._status_text.value = status_msg
        self._status_text.color = status_color
        self._set_searching(False)
        self._status_text.update()
        self._results_container.update()

    def _build_result_row(
        self,
        judul: str,
        url: str,
        thumb: str | None,
        label_text: str,
        is_duplicate: bool,
        data: tuple,
    ) -> ft.Row:
        teks_judul = ft.Text(
            value=label_text,
            color=ft.Colors.RED_400 if is_duplicate else C_TEXT,
            size=14,
            expand=True,
        )
        btn_add = ft.ElevatedButton(
            "Added" if is_duplicate else "Add Anime",
            icon=ft.Icons.CHECK if is_duplicate else ft.Icons.ADD,
            bgcolor=C_BG2 if is_duplicate else C_SAKURA,
            color=C_TEXT3 if is_duplicate else C_WHITE,
            disabled=is_duplicate,
            data=data,
            on_click=self._on_add_click,
        )
        return ft.Row(
            controls=[
                ft.Image(src=thumb, width=40, height=55, fit=ft.BoxFit.COVER)
                if thumb
                else ft.Container(width=40, height=55, bgcolor=C_BG2),
                teks_judul,
                btn_add,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # ------------------------------------------------------------------ #
    #  Add Anime                                                           #
    # ------------------------------------------------------------------ #

    def _on_add_click(self, e):
        judul, url, thumb = e.control.data
        btn: ft.ElevatedButton = e.control

        # --- Immediate visual feedback on the button itself ---
        btn.disabled = True
        btn.text = "Adding…"
        btn.icon = ft.Icons.HOURGLASS_EMPTY
        btn.bgcolor = C_BG2
        btn.color = C_TEXT3
        self._status_text.value = f"Adding '{judul}'… Please wait."
        self._loading_indicator.visible = True
        btn.update()
        self._status_text.update()
        self._loading_indicator.update()

        # Heavy work on background thread
        threading.Thread(
            target=self._do_add,
            args=(btn, judul, url, thumb),
            daemon=True,
        ).start()

    def _do_add(
        self,
        btn: ft.ElevatedButton,
        judul: str,
        url: str,
        thumb: str | None,
    ):
        try:
            self.scraper.eksekusi_tambah_anime(url, thumb)

            btn.text = "Added"
            btn.icon = ft.Icons.CHECK
            btn.bgcolor = C_BG2
            btn.color = C_TEXT3
            btn.disabled = True
            self._status_text.value = f"'{judul}' added successfully!"
            self._status_text.color = C_TEXT2

        except Exception as ex:
            btn.disabled = False
            btn.text = "Add Anime"
            btn.icon = ft.Icons.ADD
            btn.bgcolor = C_SAKURA
            btn.color = C_WHITE
            self._status_text.value = f"Error adding anime: {ex}"
            self._status_text.color = ft.Colors.RED_400

        self._loading_indicator.visible = False
        btn.update()
        self._status_text.update()
        self._loading_indicator.update()
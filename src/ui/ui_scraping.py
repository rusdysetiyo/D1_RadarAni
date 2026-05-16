import flet as ft
from scripts.scrapjudul import DynamicAnimeScraper
from src.config.theme import ThemeManager




class UIScraping(ft.Row):
    def __init__(self, page, data_manager, auth_manager, screen_manager, theme=None):
        super().__init__()
        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager

        self.expand = True
        self.spacing = 0
        self._sidebar_open = False

        # Terima theme dari screen_manager; fallback ke ThemeManager jika tidak ada
        self.current_theme = theme if theme is not None else ThemeManager.get_theme(self.screen_manager.tema_aktif)

        from src.ui.ui_home import _sidebar
        self._sidebar_widget = _sidebar(
            screen_manager, auth_manager,
            self._toggle_sidebar, self.current_theme, halaman_aktif="scraping"
        )

        self.scraper = DynamicAnimeScraper()
        self.scraper.data_manager = self.data_manager

        self._tf_query = ft.TextField(
            label="Anime Title or MAL URL",
            hint_text="e.g. 'Naruto' or 'https://myanimelist.net/anime/20'",
            expand=True,
            border_color=self.current_theme["border_color"],
            focused_border_color=self.current_theme["primary"],
            color=self.current_theme["text_main"],
        )

        self._btn_search = ft.ElevatedButton(
            "Search",
            icon=ft.Icons.SEARCH,
            bgcolor=self.current_theme["primary"],
            color=self.current_theme["card"],
            on_click=self._on_search_click,
        )

        self._loading_indicator = ft.ProgressRing(visible=False, color=self.current_theme["primary"])
        self._status_text = ft.Text("", color=self.current_theme["text_secondary"], size=14)
        self._results_container = ft.Column(
            spacing=10, scroll=ft.ScrollMode.AUTO, expand=True
        )

        topbar = ft.Container(
            padding=ft.padding.symmetric(horizontal=16),
            height=55,
            blur=ft.Blur(10, 10, ft.BlurTileMode.MIRROR),
            bgcolor=ft.Colors.with_opacity(0.8, self.current_theme["bg"]),
            shadow=ft.BoxShadow(
                blur_radius=15,
                color="#15000000",
                offset=ft.Offset(0, 4),
            ),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        ft.Icons.MENU,
                        icon_color=self.current_theme["primary"],
                        on_click=self._toggle_sidebar,
                        tooltip="Menu",
                    ),
                    ft.Column(
                        [
                            ft.Text(
                                "RadarAni",
                                size=13,
                                color=self.current_theme["primary"],
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Text("レーダアニ", size=8, color=self.current_theme["text_muted"]),
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
            bgcolor=self.current_theme["bg"],
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Live Anime Scraper",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=self.current_theme["text_main"],
                    ),
                    ft.Text(
                        "Add anime directly from MyAnimeList by title or URL.",
                        size=14,
                        color=self.current_theme["text_secondary"],
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
                    ft.Divider(color=self.current_theme["border_color"]),
                    ft.Text(
                        "Results:",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=self.current_theme["text_main"],
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

        self.controls = [self._sidebar_widget, ft.Container(content=self._main_col, bgcolor=self.current_theme["bg"], expand=True)]

    # ------------------------------------------------------------------ #
    #  Helpers                                                             #
    # ------------------------------------------------------------------ #

    def _make_button(
            self,
            text: str,
            icon: str,
            bgcolor: str,
            color: str,
            disabled: bool,
            on_click=None,
            data=None,
    ) -> ft.Container:
        """Custom button berbasis Container"""
        return ft.Container(
            data=data,
            bgcolor=bgcolor,
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            opacity=0.5 if disabled else 1.0,
            on_click=None if disabled else on_click,
            content=ft.Row(
                controls=[
                    ft.Icon(icon, color=color, size=16),
                    ft.Text(text, color=color, size=13, weight=ft.FontWeight.W_500),
                ],
                spacing=6,
                tight=True,
            ),
            animate_opacity=200,
        )

    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._sidebar_widget.update()

    def _set_searching(self, is_searching: bool):
        self._btn_search.disabled = is_searching
        self._btn_search.text = "Searching…" if is_searching else "Search"
        self._btn_search.icon = (
            ft.Icons.HOURGLASS_EMPTY if is_searching else ft.Icons.SEARCH
        )
        self._loading_indicator.visible = is_searching
        # ✅ Update masing-masing secara eksplisit
        self._btn_search.update()
        self._loading_indicator.update()

    # ------------------------------------------------------------------ #
    #  Search                                                              #
    # ------------------------------------------------------------------ #

    def _on_search_click(self, e):
        query = self._tf_query.value.strip()
        if not query:
            return

        try:
            self.scraper.validasi_input(query)
        except ValueError as ex:
            self._show_input_error(str(ex))
            return

        self._status_text.color = self.current_theme["text_secondary"]
        self._status_text.value = "Searching…"
        self._results_container.controls.clear()
        self._set_searching(True)
        self._status_text.update()
        self._results_container.update()

        # ✅ Gunakan page.run_thread() — aman untuk Flet 0.84
        self.my_page.run_thread(self._do_search, query)

    def _show_input_error(self, message: str):
        self._status_text.value = message
        self._status_text.color = ft.Colors.RED_400
        self._status_text.update()

    def _do_search(self, query: str):
        new_rows: list[ft.Control] = []
        status_msg = ""
        status_color = self.current_theme["text_secondary"]
        tip_msg = ""

        try:
            if self.scraper.is_mal_anime_url(query):
                judul, thumb_url, is_duplicate, normalized_url = self.scraper.cari_dari_url(query)

                label_text = f"{judul} (Already in database)" if is_duplicate else judul
                new_rows.append(
                    self._build_result_row(
                        judul=judul,
                        url=normalized_url,
                        thumb=thumb_url,
                        label_text=label_text,
                        is_duplicate=is_duplicate,
                        data=(judul, normalized_url, thumb_url),
                    )
                )
                status_msg = "Anime sudah ada di database." if is_duplicate else "1 hasil ditemukan."

            else:
                kandidat_list = self.scraper.dapatkan_kandidat_judul(query)

                if not kandidat_list:
                    status_msg = "Tidak ada hasil ditemukan untuk judul tersebut."
                else:
                    status_msg = f"Ditemukan {len(kandidat_list)} hasil."
                    for judul, url, thumb in kandidat_list:
                        try:
                            is_duplicate, _ = self.scraper._cek_duplikasi(
                                int(url.split("/")[4])
                            )
                        except Exception:
                            is_duplicate = False

                        label_text = f"{judul} (Already in database)" if is_duplicate else judul
                        new_rows.append(
                            self._build_result_row(
                                judul=judul,
                                url=url,
                                thumb=thumb,
                                label_text=label_text,
                                is_duplicate=is_duplicate,
                                data=(judul, url, thumb),
                            )
                        )

        except (ValueError, ConnectionError) as ex:
            status_msg = str(ex)
            status_color = ft.Colors.RED_400
            tip_msg = "💡 Tips: Pastikan koneksi internet aktif dan coba lagi."
        except Exception as ex:
            status_msg = f"Terjadi kesalahan tak terduga: {ex}"
            status_color = ft.Colors.RED_400
            tip_msg = "💡 Tips: Coba lagi atau gunakan URL MAL secara langsung."

        if tip_msg:
            new_rows.append(
                ft.Text(tip_msg, color=self.current_theme["text_secondary"], size=12, italic=True)
            )

        self._results_container.controls.clear()
        self._results_container.controls.extend(new_rows)
        self._status_text.value = status_msg
        self._status_text.color = status_color
        self._set_searching(False)
        self._status_text.update()
        self._results_container.update()

    # ------------------------------------------------------------------ #
    #  Result Row Builder                                                  #
    # ------------------------------------------------------------------ #

    def _build_result_row(self, judul, url, thumb, label_text, is_duplicate, data):
        teks_judul = ft.Text(
            value=label_text,
            color=self.current_theme["error"] if is_duplicate else self.current_theme["text_main"],
            size=14,
            expand=True,
        )

        # ✅ Pakai custom container, bukan ElevatedButton
        btn_add = self._make_button(
            text="Added" if is_duplicate else "Add Anime",
            icon=ft.Icons.CHECK if is_duplicate else ft.Icons.ADD,
            bgcolor=self.current_theme["bg_secondary"] if is_duplicate else self.current_theme["primary"],
            color=self.current_theme["text_muted"] if is_duplicate else self.current_theme["card"],
            disabled=is_duplicate,
            on_click=self._on_add_click,
            data=data,
        )

        return ft.Row(
            controls=[
                ft.Image(src=thumb, width=40, height=55, fit=ft.BoxFit.COVER)
                if thumb
                else ft.Container(width=40, height=55, bgcolor=self.current_theme["bg_secondary"]),
                teks_judul,
                btn_add,
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # ------------------------------------------------------------------ #
    #  Add Anime                                                           #
    # ------------------------------------------------------------------ #

    def _make_btn_content(self, icon, text, color):
        """Helper: buat Row isi tombol — dipanggil setiap state change."""
        return ft.Row(
            controls=[
                ft.Icon(icon, color=color, size=16),
                ft.Text(text, color=color, size=13, weight=ft.FontWeight.W_500),
            ],
            spacing=6,
            tight=True,
        )

    def _on_add_click(self, e):
        judul, url, thumb = e.control.data
        btn: ft.Container = e.control

        btn.on_click = None
        btn.opacity = 0.5
        btn.bgcolor = self.current_theme["bg_secondary"]
        # ✅ Ganti seluruh content sekaligus — bukan mutasi child
        btn.content = self._make_btn_content(ft.Icons.HOURGLASS_EMPTY, "Adding…", self.current_theme["text_muted"])
        btn.update()

        self._status_text.value = f"Menambahkan '{judul}'… Mohon tunggu."
        self._status_text.update()
        self._loading_indicator.visible = True
        self._loading_indicator.update()

        self.my_page.run_thread(self._do_add, btn, judul, url, thumb)

    def _do_add(self, btn: ft.Container, judul: str, url: str, thumb: str | None):
        try:
            self.scraper.eksekusi_tambah_anime(url, thumb)

            btn.bgcolor = self.current_theme["bg_secondary"]
            btn.opacity = 0.5
            btn.on_click = None
            btn.content = self._make_btn_content(ft.Icons.CHECK, "Added", self.current_theme["text_muted"])
            self._status_text.value = f"'{judul}' berhasil ditambahkan!"
            self._status_text.color = self.current_theme["text_secondary"]

        except Exception as ex:
            btn.bgcolor = self.current_theme["primary"]
            btn.opacity = 1.0
            btn.on_click = self._on_add_click
            btn.content = self._make_btn_content(ft.Icons.ADD, "Add Anime", self.current_theme["card"])
            self._status_text.value = f"Gagal menambahkan '{judul}': {ex}"
            self._status_text.color = self.current_theme["error"]

        self._loading_indicator.visible = False
        btn.update()
        self._status_text.update()
        self._loading_indicator.update()
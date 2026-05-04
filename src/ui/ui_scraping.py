import flet as ft
import requests
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
            on_click=self._on_search_click
        )

        self._loading_indicator = ft.ProgressRing(visible=False, color=C_SAKURA)
        self._status_text = ft.Text("", color=C_TEXT2, size=14)
        self._results_container = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

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
                offset=ft.Offset(0, 4)
            ),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        ft.Icons.MENU, icon_color=C_SAKURA,
                        on_click=self._toggle_sidebar, tooltip="Menu",
                    ),
                    ft.Column([
                        ft.Text("RadarAni", size=13, color=C_SAKURA, weight=ft.FontWeight.BOLD),
                        ft.Text("レーダアニ", size=8, color=C_TEXT3),
                    ], spacing=0, tight=True),
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
                    ft.Text("Live Anime Scraper", size=24, weight=ft.FontWeight.BOLD, color=C_TEXT),
                    ft.Text("Add anime directly from MyAnimeList by title or URL.", size=14, color=C_TEXT2),
                    ft.Container(height=10),
                    ft.Row([self._tf_query, self._btn_search], alignment=ft.MainAxisAlignment.START),
                    ft.Row([self._loading_indicator, self._status_text], alignment=ft.MainAxisAlignment.START),
                    ft.Divider(color=C_BORDER),
                    ft.Text("Results:", size=16, weight=ft.FontWeight.BOLD, color=C_TEXT),
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

    def _set_error(self, message):
        """Tampilkan pesan error di status bar."""
        self._status_text.value = message
        self._status_text.color = ft.Colors.RED_400
        self._loading_indicator.visible = False
        self.update()

    def _set_status(self, message):
        """Tampilkan pesan status biasa di status bar."""
        self._status_text.value = message
        self._status_text.color = C_TEXT2
        self.update()

    def _on_search_click(self, e):
        query = self._tf_query.value.strip()
        if not query:
            return

        is_url = "http" in query

        # --- Validasi: URL tapi bukan MAL anime ---
        if is_url and "myanimelist.net/anime/" not in query:
            self._set_error(
                "URL tidak valid. Pastikan URL berasal dari halaman anime MyAnimeList.\n"
                "Contoh: https://myanimelist.net/anime/20/Naruto"
            )
            self._results_container.controls.clear()
            self.update()
            return

        # --- Validasi: judul terlalu pendek ---
        if not is_url and len(query) < 3:
            self._set_error(
                "Input minimal 3 karakter. "
                "Jika judul sangat pendek, gunakan URL MyAnimeList."
            )
            self._results_container.controls.clear()
            self.update()
            return

        self._status_text.color = C_TEXT2
        self._status_text.value = "Searching..."
        self._loading_indicator.visible = True
        self._results_container.controls.clear()
        self.update()

        try:
            if is_url:
                # --- Normalisasi URL: buang sub-tab MAL ---
                normalized = DynamicAnimeScraper.normalize_mal_url(query)

                # Ekstrak MAL ID dari URL
                parts = normalized.split('/')
                try:
                    mal_id = int(parts[4])
                except (IndexError, ValueError):
                    self._set_error(
                        "Format URL tidak dikenali. Tidak dapat membaca MAL ID.\n"
                        "Contoh URL yang benar: https://myanimelist.net/anime/20/Naruto"
                    )
                    return

                is_duplicate, judul_terdaftar = self.scraper._cek_duplikasi(mal_id)

                # Fetch judul dan thumbnail dari halaman MAL
                judul, thumb_url = self.scraper.dapatkan_info_dari_url(normalized)

                if judul == "N/A":
                    self._set_error(
                        "Gagal mengambil data dari MyAnimeList. "
                        "Halaman tidak ditemukan atau koneksi bermasalah."
                    )
                    return

                label_text = f"{judul} (Already in database)" if is_duplicate else judul

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
                    data=(judul, normalized, thumb_url),
                    on_click=self._on_add_click,
                )

                row = ft.Row(
                    controls=[
                        ft.Image(src=thumb_url, width=40, height=55, fit=ft.BoxFit.COVER)
                        if thumb_url else ft.Container(width=40, height=55, bgcolor=C_BG2),
                        teks_judul,
                        btn_add,
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                )
                self._results_container.controls.append(row)
                self._set_status(
                    "Anime sudah ada di database." if is_duplicate else "1 hasil ditemukan."
                )

            else:
                # --- Jalur pencarian judul ---
                kandidat_list = self.scraper.dapatkan_kandidat_judul(query)
                if not kandidat_list:
                    self._set_status("Tidak ada hasil yang ditemukan.")
                else:
                    self._set_status(f"Ditemukan {len(kandidat_list)} hasil.")
                    for kandidat in kandidat_list:
                        judul, url, thumb = kandidat

                        try:
                            mal_id = int(url.split('/')[4])
                            is_duplicate, _ = self.scraper._cek_duplikasi(mal_id)
                        except (IndexError, ValueError):
                            is_duplicate = False

                        label_text = f"{judul} (Already in database)" if is_duplicate else judul

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
                            data=kandidat,
                            on_click=self._on_add_click,
                        )

                        row = ft.Row(
                            controls=[
                                ft.Image(src=thumb, width=40, height=55, fit=ft.BoxFit.COVER)
                                if thumb else ft.Container(width=40, height=55, bgcolor=C_BG2),
                                teks_judul,
                                btn_add,
                            ],
                            alignment=ft.MainAxisAlignment.START,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                        self._results_container.controls.append(row)

        except requests.exceptions.ConnectionError:
            self._set_error(
                "Gagal terhubung ke MyAnimeList. Periksa koneksi internet Anda."
            )
        except requests.exceptions.Timeout:
            self._set_error(
                "Koneksi ke MyAnimeList habis waktu (timeout). Coba lagi beberapa saat."
            )
        except requests.exceptions.TooManyRedirects:
            self._set_error(
                "Terlalu banyak redirect — URL mungkin tidak valid."
            )
        except requests.exceptions.RequestException as ex:
            self._set_error(f"Kesalahan jaringan: {ex}")
        except Exception as ex:
            self._set_error(f"Terjadi kesalahan tak terduga: {ex}")

        self._loading_indicator.visible = False
        self.update()

    def _on_add_click(self, e):
        judul, url, thumb = e.control.data

        e.control.disabled = True
        e.control.text = "Adding..."
        e.control.icon = ft.Icons.HOURGLASS_EMPTY
        self._status_text.value = f"Adding '{judul}'... Please wait."
        self._loading_indicator.visible = True
        e.control.update()  # pastikan tombol ter-refresh sebelum proses berat
        self.update()

        try:
            self.scraper.eksekusi_tambah_anime(url, thumb)
            e.control.text = "Added"
            e.control.icon = ft.Icons.CHECK
            e.control.bgcolor = C_BG2
            e.control.color = C_TEXT3
            self._status_text.value = f"'{judul}' berhasil ditambahkan!"
            self._status_text.color = ft.Colors.GREEN_600

        except requests.exceptions.ConnectionError:
            e.control.disabled = False
            e.control.text = "Add Anime"
            e.control.icon = ft.Icons.ADD
            self._set_error("Gagal terhubung ke MyAnimeList saat mengunduh data. Periksa koneksi internet Anda.")

        except requests.exceptions.Timeout:
            e.control.disabled = False
            e.control.text = "Add Anime"
            e.control.icon = ft.Icons.ADD
            self._set_error("Koneksi timeout saat mengunduh data anime. Coba lagi beberapa saat.")

        except requests.exceptions.RequestException as ex:
            e.control.disabled = False
            e.control.text = "Add Anime"
            e.control.icon = ft.Icons.ADD
            self._set_error(f"Kesalahan jaringan saat menambahkan anime: {ex}")

        except ValueError as ex:
            e.control.disabled = False
            e.control.text = "Add Anime"
            e.control.icon = ft.Icons.ADD
            self._set_error(f"Data dari MAL tidak valid atau tidak dapat diproses: {ex}")

        except Exception as ex:
            e.control.disabled = False
            e.control.text = "Add Anime"
            e.control.icon = ft.Icons.ADD
            self._set_error(f"Terjadi kesalahan tak terduga: {ex}")

        self._loading_indicator.visible = False
        e.control.update()  # pastikan perubahan akhir tombol ter-render
        self.update()
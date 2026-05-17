import flet as ft


class KeyboardManager:
    def __init__(self, page, screen_manager):
        self.page = page
        self.sm = screen_manager
        self.page.on_keyboard_event = self.handle_event

    def handle_event(self, e: ft.KeyboardEvent):
        key_pressed = e.key.upper() if e.key else ""
        view = getattr(self.sm, "current_view_instance", None)
        halaman_sekarang = getattr(self.sm, "halaman_terakhir", "")

        # -----Global Search Popup (Ctrl + F)-----
        if e.ctrl and key_pressed == "F":
            if hasattr(self.sm, "buka_pencarian_global"):
                self.sm.buka_pencarian_global()
            return

        # -----Focus Search Bar Lokal Katalog (Ctrl + /) -----
        if e.ctrl and key_pressed == "/":
            if halaman_sekarang == "katalog" and view and hasattr(view, "search_input"):
                self.page.run_task(view.search_input.focus)
            return

        # -----Navigasi Menu (Alt + 1/2/3/4/5)-----
        if e.alt:
            if key_pressed == "1":
                self.sm.tampilkan_home()
                return
            elif key_pressed == "2":
                self.sm.tampilkan_katalog(filter_kategori=getattr(self.sm, "filter_terakhir", "all"))
                return
            elif key_pressed == "3":
                if hasattr(self.sm, "tampilkan_analytics"): self.sm.tampilkan_analytics()
                return
            elif key_pressed == "4":
                if hasattr(self.sm, "tampilkan_scraping"): self.sm.tampilkan_scraping()
                return
            elif key_pressed == "5":
                if hasattr(self.sm, "tampilkan_profil"): self.sm.tampilkan_profil()
                return

        # -----Escape (Close Dialog / Search / Sidebar / Back to Home)-----
        if key_pressed == "ESCAPE":
            # 1. Tutup Popup Guide kalau lagi kebuka (Fungsi sakti kita tadi)
            if hasattr(self.sm, "guide_manager") and self.sm.guide_manager:
                if hasattr(self.sm.guide_manager, "guide_dialog") and self.sm.guide_manager.guide_dialog.open:
                    self.sm.guide_manager.force_close()
                    return

            # 2. Tutup Dialog bawaan Page (Pake pengecekan aman)
            current_dialog = getattr(self.page, "dialog", None)
            if current_dialog and getattr(current_dialog, "open", False):
                current_dialog.open = False
                self.page.update()
                return

            # 3. Tutup Global Search
            if hasattr(self.sm, "tutup_pencarian_global"):
                self.sm.tutup_pencarian_global()
                return

            # 4. Tutup Search Manager Internal
            if hasattr(self.sm, "search_manager") and getattr(self.sm.search_manager, "is_open", False):
                self.sm.search_manager.tutup_pencarian()
                return

            # 5. Logic Khusus Halaman Katalog (Clear Search / Tutup Sidebar)
            if halaman_sekarang == "katalog" and view:
                if hasattr(view, "search_input") and view.search_input.value != "":
                    view.search_input.value = ""
                    if hasattr(view, "_on_search"): view._on_search(None)
                    view.search_input.update()
                    return
                if hasattr(view, "_sidebar_open") and getattr(view, "_sidebar_open", False):
                    if hasattr(view, "_toggle_sidebar"):
                        view._toggle_sidebar(None)
                    return

            # 6. Fallback: Balik ke Home
            if halaman_sekarang != "home":
                self.sm.tampilkan_home()
            return

        # -----Switch Theme Langsung (Ctrl + 1/2/3/4)-----
        if e.ctrl and key_pressed in ["1", "2", "3", "4"]:
            self.sm.update_theme(key_pressed)
            if halaman_sekarang == "home":
                self.sm.tampilkan_home()
            elif halaman_sekarang == "katalog":
                self.sm.tampilkan_katalog(filter_kategori=getattr(self.sm, "filter_terakhir", "all"))
            elif halaman_sekarang == "profil":
                if hasattr(self.sm, "tampilkan_profil"): self.sm.tampilkan_profil()
            elif halaman_sekarang == "analytics":
                if hasattr(self.sm, "tampilkan_analytics"): self.sm.tampilkan_analytics()
            elif halaman_sekarang == "scraping":
                if hasattr(self.sm, "tampilkan_scraping"): self.sm.tampilkan_scraping()
            elif halaman_sekarang == "detail" and view:
                if hasattr(view, "perbarui_tema"): view.perbarui_tema()
            return

        # -----Ganti Tema Berurutan (Ctrl + T)-----
        if e.ctrl and key_pressed == "T":
            tema_sekarang = getattr(self.sm, "tema_aktif", "1")
            try:
                tema_angka = int(tema_sekarang)
            except ValueError:
                tema_angka = 1
            tema_berikutnya = (tema_angka % 4) + 1
            self.sm.update_theme(str(tema_berikutnya))

            if halaman_sekarang == "home":
                self.sm.tampilkan_home()
            elif halaman_sekarang == "katalog":
                self.sm.tampilkan_katalog(filter_kategori=getattr(self.sm, "filter_terakhir", "all"))
            elif halaman_sekarang == "profil":
                if hasattr(self.sm, "tampilkan_profil"): self.sm.tampilkan_profil()
            elif halaman_sekarang == "analytics":
                if hasattr(self.sm, "tampilkan_analytics"): self.sm.tampilkan_analytics()
            elif halaman_sekarang == "scraping":
                if hasattr(self.sm, "tampilkan_scraping"): self.sm.tampilkan_scraping()
            elif halaman_sekarang == "detail" and view:
                if hasattr(view, "perbarui_tema"): view.perbarui_tema()
            return

        # -----Toggle Grid/List di Katalog (Ctrl + G)-----
        if e.ctrl and key_pressed == "G":
            if halaman_sekarang == "katalog" and view:
                if hasattr(view, "_view_mode") and hasattr(view, "_set_view"):
                    mode_baru = "list" if view._view_mode == "grid" else "grid"
                    view._set_view(mode_baru)
            return

        # -----Refresh Home (Ctrl + R)-----
        if e.ctrl and key_pressed == "R" and halaman_sekarang == "home":
            self.sm.tampilkan_home()
            return

        # -----Aksi Profile (Logout = Ctrl+L, Hapus Akun = Ctrl+Delete) -----
        if e.ctrl and halaman_sekarang == "profile" and view:
            if key_pressed == "L" and hasattr(view, "logout"):
                view.logout(None)  # Pastikan di ui_profile.py ada fungsi logout()
            elif key_pressed == "DELETE" and hasattr(view, "hapus_akun"):
                view.hapus_akun(None)  # Pastikan di ui_profile.py ada fungsi hapus_akun()

        # -----Shortcut Filter & Sort di Katalog (Pakai SHIFT) -----
        if e.shift and not e.ctrl and not e.alt:
            if halaman_sekarang == "katalog" and view:
                # Tab Filter (All, Rated, Unrated)
                if key_pressed == "A" and hasattr(view, "_set_filter"):
                    view._set_filter("all")
                elif key_pressed == "R" and hasattr(view, "_set_filter"):
                    view._set_filter("rated")
                elif key_pressed == "U" and hasattr(view, "_set_filter"):
                    view._set_filter("unrated")

                # Buka Dialog Genre Filter
                elif key_pressed == "F" and hasattr(view, "_buka_dialog_genre"):
                    view._buka_dialog_genre(None)

                # Looping Toggle Sortir (Title -> Global -> Personal)
                elif key_pressed == "O" and hasattr(view, "_sort") and hasattr(view, "muat_tabel_anime"):
                    # Map urutan rotasi sortir
                    rotasi = {"title": "global", "global": "personal", "personal": "title"}
                    label_map = {"title": "Title", "global": "Global Score", "personal": "Your Score"}

                    sort_baru = rotasi.get(view._sort, "title")
                    view._sort = sort_baru

                    # Update label di tombol sort
                    if hasattr(view, "_sort_label"):
                        view._sort_label.value = f"Sort: {label_map[sort_baru]}"

                    view.muat_tabel_anime()

        # -----Aksi Halaman Detail (S = Save, D = Delete, Enter) -----
        if not e.ctrl and not e.alt and not e.shift:
            if halaman_sekarang == "detail" and view:
                if key_pressed == "S" and hasattr(view, "simpan_rating"):
                    view.simpan_rating(None)
                elif key_pressed == "D" and hasattr(view, "hapus_rating"):
                    view.hapus_rating(None)

            if key_pressed == "ENTER" and view and hasattr(view, "submit_field"):
                view.submit_field(None)

        # -----Scroll & Pagination Halaman (Arrows, Home, End)-----
        if hasattr(view, "main_scroll") and view.main_scroll:
            # CTRL + UP / HOME
            if e.ctrl and key_pressed in ["HOME", "ARROW UP"]:
                self.page.run_task(view.main_scroll.scroll_to, offset=0, duration=200)

            # CTRL + DOWN / END
            elif e.ctrl and key_pressed in ["END", "ARROW DOWN"]:
                self.page.run_task(view.main_scroll.scroll_to, offset=99999, duration=200)

            # PAGE UP / DOWN (Loncat lebih jauh)
            elif key_pressed == "PAGE UP":
                self.page.run_task(view.main_scroll.scroll_to, delta=-600, duration=200)
            elif key_pressed == "PAGE DOWN":
                self.page.run_task(view.main_scroll.scroll_to, delta=600, duration=200)

            # ARROW UP / DOWN (Scroll halus)
            elif not e.ctrl and key_pressed == "ARROW UP":
                self.page.run_task(view.main_scroll.scroll_to, delta=-150, duration=150)
            elif not e.ctrl and key_pressed == "ARROW DOWN":
                self.page.run_task(view.main_scroll.scroll_to, delta=150, duration=150)
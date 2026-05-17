import flet as ft


class KeyboardManager:
    def __init__(self, page, screen_manager, auth_manager):
        self.page = page
        self.sm = screen_manager
        self.auth = auth_manager
        self.page.on_keyboard_event = self.handle_event

    def _close_active_dialog(self):
        """Forcefully closes any active dialogs, popups, or bottom sheets safely."""
        closed_something = False
        current_dialog = getattr(self.page, "dialog", None)
        if current_dialog and getattr(current_dialog, "open", False):
            current_dialog.open = False
            closed_something = True

        if hasattr(self.page, "overlay"):
            for item in self.page.overlay:
                if hasattr(item, "open") and item.open:
                    try:
                        self.page.close(item)
                    except AttributeError:
                        item.open = False
                    closed_something = True
        if closed_something:
            self.page.update()

        return closed_something

    def _refresh_current_view(self, halaman_sekarang, view):
        """Reloads the current view gracefully (useful after theme change)."""
        if halaman_sekarang == "home":
            self.sm.tampilkan_home()
        elif halaman_sekarang == "login":
                if hasattr(self.sm, "tampilkan_login"): self.sm.tampilkan_login()
        elif halaman_sekarang == "katalog":
            self.sm.tampilkan_katalog(filter_kategori=getattr(self.sm, "filter_terakhir", "all"))
        elif halaman_sekarang == "profil":
            if hasattr(self.sm, "tampilkan_profil"): self.sm.tampilkan_profil()
        elif halaman_sekarang == "analytics":
            if hasattr(self.sm, "tampilkan_analytics"): self.sm.tampilkan_analytics()
        elif halaman_sekarang == "scraping":
            if hasattr(self.sm, "tampilkan_scraping"): self.sm.tampilkan_scraping()
        elif halaman_sekarang == "detail" and view:
            if hasattr(self.sm,"tampilkan_detail"): self.sm.tampilkan_detail(anime_id=getattr(view, "anime_id", None))

    # ---------------------------------------------------------
    # MAIN EVENT HANDLER
    # ---------------------------------------------------------
    def handle_event(self, e: ft.KeyboardEvent):
        key_pressed = e.key.upper() if e.key else ""
        view = getattr(self.sm, "current_view_instance", None)
        halaman_sekarang = getattr(self.sm, "halaman_terakhir", "")

        # [Ctrl + F] Open Global Search
        if e.ctrl and key_pressed == "F":
            if hasattr(self.sm, "buka_pencarian_global"):
                self.sm.buka_pencarian_global()
            return

        # [Ctrl + /] Focus Local Search Bar (Catalog)
        if e.ctrl and key_pressed == "/":
            if halaman_sekarang == "katalog" and view and hasattr(view, "search_input"):
                self.page.run_task(view.search_input.focus)
            elif halaman_sekarang == "scraping" and view and hasattr(view, "_tf_query"):
                self.page.run_task(view._tf_query.focus)
            return

        # [Alt + 1/2/3/4/5] Quick Menu Navigation
        if e.alt:
            self._close_active_dialog()
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

        # [Escape] Universal Close / Back Action
        if key_pressed == "ESCAPE":
            if hasattr(self.sm, "guide_manager") and self.sm.guide_manager:
                if hasattr(self.sm.guide_manager, "guide_dialog") and getattr(self.sm.guide_manager.guide_dialog,
                                                                              "open", False):
                    self.sm.guide_manager.force_close()
                    return
            if self._close_active_dialog():
                return

            # 3. Close Global Search
            if hasattr(self.sm, "tutup_pencarian_global"):
                self.sm.tutup_pencarian_global()
                return

            # 4. Close Local Search Manager
            if hasattr(self.sm, "search_manager") and getattr(self.sm.search_manager, "is_open", False):
                self.sm.search_manager.tutup_pencarian()
                return

            # 5. Clear Search or Close Sidebar in Catalog
            if halaman_sekarang == "katalog" and view:
                if hasattr(view, "search_input") and view.search_input.value != "":
                    view.search_input.value = ""
                    if hasattr(view, "_on_search"): view._on_search(None)
                    view.search_input.update()
                    return
                if hasattr(view, "_sidebar_open") and getattr(view, "_sidebar_open", False):
                    if hasattr(view, "_toggle_sidebar"): view._toggle_sidebar(None)
                    return

            # 6. Fallback: Return to Home Screen
            if halaman_sekarang != "home":
                self.sm.tampilkan_home()
            return

        # [Ctrl + 1-8] Direct Theme Switch
        if e.ctrl and key_pressed in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            self._close_active_dialog()
            self.sm.update_theme(key_pressed)
            self._refresh_current_view(halaman_sekarang, view)
            return

        # [Ctrl + T] Cycle Theme
        if e.ctrl and key_pressed == "T":
            self._close_active_dialog()
            tema_sekarang = getattr(self.sm, "tema_aktif", "1")
            try:
                tema_angka = int(tema_sekarang)
            except ValueError:
                tema_angka = 1
            tema_berikutnya = (tema_angka % 8) + 1  # 8 is total themes
            self.sm.update_theme(str(tema_berikutnya))
            self._refresh_current_view(halaman_sekarang, view)
            return

        # [Ctrl + G] Toggle Grid/List in Catalog
        if e.ctrl and key_pressed == "G":
            if halaman_sekarang == "katalog" and view:
                if hasattr(view, "_view_mode") and hasattr(view, "_set_view"):
                    mode_baru = "list" if view._view_mode == "grid" else "grid"
                    view._set_view(mode_baru)
            return

        # [Ctrl + R] Refresh Home / Current Data
        if e.ctrl and key_pressed == "R":  # <- INI YANG TADI LUPA LU TULIS BANG!
            self._close_active_dialog()
            if halaman_sekarang == "home":
                self.sm.tampilkan_home()
            return

        # [Ctrl + L / Ctrl + Delete]
        if e.ctrl and key_pressed == "L":
            if halaman_sekarang == "profil" and hasattr(view, "aksi_tombol_logout"):
                view.aksi_tombol_logout(None)
            else:
                theme = getattr(self.sm, "theme", {})
                PRIMARY = theme.get("primary", "#6c5ce7")
                CARD = theme.get("card", "#ffffff")
                TEXT_MUTED = theme.get("text_muted", "#999999")
                BORDER = theme.get("border_color", "#e0e0e0")

                def aksi_ya(ev):
                    dialog_logout.open = False
                    self.page.update()
                    self.auth.logout()
                    self.sm.tampilkan_login()

                def aksi_batal(ev):
                    dialog_logout.open = False
                    self.page.update()

                dialog_logout = ft.AlertDialog(
                    modal=True,
                    title=ft.Row([
                        ft.Icon(ft.Icons.LOGOUT_ROUNDED, color=PRIMARY, size=20),
                        ft.Text("Confirm Logout", weight=ft.FontWeight.W_800, color=PRIMARY, size=14),
                    ], spacing=8),
                    content=ft.Text(
                        "Are you sure you want to log out of your account?",
                        size=12, color=TEXT_MUTED,
                    ),
                    actions=[
                        ft.OutlinedButton(
                            "Cancel", on_click=aksi_batal,
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1.5, BORDER),
                                shape=ft.RoundedRectangleBorder(radius=8),
                                color=TEXT_MUTED,
                            ),
                        ),
                        ft.ElevatedButton(
                            "Log Out", on_click=aksi_ya,
                            style=ft.ButtonStyle(
                                bgcolor=PRIMARY, color=CARD,
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                    bgcolor=CARD,
                )

                self.page.overlay.append(dialog_logout)
                dialog_logout.open = True
                self.page.update()
            return

        if e.ctrl and halaman_sekarang == "profil" and view:
            if key_pressed == "DELETE" and hasattr(view, "aksi_tombol_hapus_akun"):
                view.aksi_tombol_hapus_akun(None)
                return

        # [Shift + Keys] Quick Filters & Sorting in Catalog
        if e.shift and not e.ctrl and not e.alt:
            if halaman_sekarang == "katalog" and view:
                if key_pressed == "A" and hasattr(view, "_set_filter"):
                    view._set_filter("all")
                elif key_pressed == "R" and hasattr(view, "_set_filter"):
                    view._set_filter("rated")
                elif key_pressed == "U" and hasattr(view, "_set_filter"):
                    view._set_filter("unrated")
                elif key_pressed == "F" and hasattr(view, "_buka_dialog_genre"):
                    view._buka_dialog_genre(None)
                elif key_pressed == "O" and hasattr(view, "_sort") and hasattr(view, "muat_tabel_anime"):
                    rotasi = {"title": "global", "global": "personal", "personal": "title"}
                    label_map = {"title": "Title", "global": "Global Score", "personal": "Your Score"}
                    sort_baru = rotasi.get(view._sort, "title")
                    view._sort = sort_baru
                    if hasattr(view, "_sort_label"):
                        view._sort_label.value = f"Sort: {label_map[sort_baru]}"
                    view.muat_tabel_anime()
            return

        # [S, D, Enter] Single Key Actions
        if not e.ctrl and not e.alt and not e.shift:
            if halaman_sekarang == "detail" and view:
                if key_pressed == "S" and hasattr(view, "save_rating"):
                    view.save_rating(None)
                elif key_pressed == "D" and hasattr(view, "delete_rating"):
                    view.delete_rating(None)

            if key_pressed == "ENTER" and view and hasattr(view, "submit_field"):
                view.submit_field(None)

        # [Navigation Keys] Page Scrolling
        if hasattr(view, "main_scroll") and view.main_scroll:
            if e.ctrl and key_pressed in ["HOME", "ARROW UP"]:
                self.page.run_task(view.main_scroll.scroll_to, offset=0, duration=200)
            elif e.ctrl and key_pressed in ["END", "ARROW DOWN"]:
                self.page.run_task(view.main_scroll.scroll_to, offset=99999, duration=200)
            elif key_pressed == "PAGE UP":
                self.page.run_task(view.main_scroll.scroll_to, delta=-600, duration=200)
            elif key_pressed == "PAGE DOWN":
                self.page.run_task(view.main_scroll.scroll_to, delta=600, duration=200)
            elif not e.ctrl and key_pressed == "ARROW UP":
                self.page.run_task(view.main_scroll.scroll_to, delta=-150, duration=150)
            elif not e.ctrl and key_pressed == "ARROW DOWN":
                self.page.run_task(view.main_scroll.scroll_to, delta=150, duration=150)
            if halaman_sekarang == "katalog" and view:
                if key_pressed == "ARROW LEFT" and hasattr(view, "_ganti_halaman"):
                    if view._halaman > 1:
                        view._ganti_halaman(view._halaman - 1)
                elif key_pressed == "ARROW RIGHT" and hasattr(view, "_ganti_halaman"):
                    if view._halaman < view._total_pg:
                        view._ganti_halaman(view._halaman + 1)
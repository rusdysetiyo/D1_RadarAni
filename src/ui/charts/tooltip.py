import flet as ft
from .palette import C_WHITE, C_SAKURA_DK, C_TEXT, C_TEXT3


class Tooltip(ft.Container):
    """
    Tooltip overlay tunggal yang diletakkan di page.overlay agar tidak
    ter-clip oleh batas card/chart mana pun.

    Koordinat (x, y) yang diterima show_at() adalah global page coordinates
    (dari e.global_position), bukan lokal chart.

    Update UI hanya dipanggil apabila konten ATAU posisi berubah melewati
    _SNAP piksel, sehingga tidak menimbulkan lag saat kursor bergerak cepat.
    """

    _SNAP        = 4    # threshold piksel — posisi baru diabaikan jika < snap px
    _OFFSET_X    = 16   # jarak horizontal tooltip dari kursor (ke kanan)
    _OFFSET_Y    = -10  # jarak vertikal tooltip dari kursor (ke atas)
    _TOOLTIP_W   = 220  # perkiraan lebar tooltip untuk flip logic

    def __init__(self):
        super().__init__(
            visible=False,
            bgcolor=C_WHITE,
            border=ft.border.all(1, "#E0C8D4"),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            shadow=ft.BoxShadow(blur_radius=14, color="#25C07090",
                                offset=ft.Offset(0, 3)),
            left=0, top=0,
            # Lebar tetap agar posisi flip bisa dihitung konsisten
            width=self._TOOLTIP_W,
            content=ft.Column(spacing=3, tight=True),
        )
        self._current_title = None
        self._current_rows  = None
        self._page_w        = 9999  # diupdate via set_page_size()

    def set_page_size(self, width: float, height: float):
        """Dipanggil sekali setelah tooltip dipasang di overlay."""
        self._page_w  = width
        self._page_h  = height

    def show_at(self, gx: float, gy: float, title: str, rows: list):
        """
        Tampilkan tooltip di dekat titik (gx, gy) dalam koordinat halaman global.
        Tooltip otomatis flip ke kiri jika mendekati tepi kanan halaman.
        """
        changed_content = False
        if title != self._current_title or rows != self._current_rows:
            self._current_title = title
            self._current_rows  = rows
            self.content.controls = [
                ft.Text(title, size=12, weight=ft.FontWeight.BOLD,
                        color=C_SAKURA_DK),
                *[
                    ft.Row([
                        ft.Text(lbl, size=11, color=C_TEXT3, expand=True),
                        ft.Text(val, size=11, color=C_TEXT,
                                weight=ft.FontWeight.W_600),
                    ], spacing=8)
                    for lbl, val in rows
                ],
            ]
            changed_content = True

        # Flip ke kiri jika terlalu dekat tepi kanan halaman
        if gx + self._OFFSET_X + self._TOOLTIP_W > self._page_w - 8:
            new_left = gx - self._TOOLTIP_W - self._OFFSET_X
        else:
            new_left = gx + self._OFFSET_X

        new_top = max(4, gy + self._OFFSET_Y)

        # Hanya render ulang jika melewati threshold snap
        changed_pos = (
            abs(self.left - new_left) > self._SNAP or
            abs(self.top  - new_top)  > self._SNAP
        )

        if changed_content or changed_pos or not self.visible:
            self.left    = new_left
            self.top     = new_top
            self.visible = True
            self.update()

    def hide(self):
        if self.visible:
            self.visible = False
            self.update()

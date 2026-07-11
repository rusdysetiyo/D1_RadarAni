import flet as ft
import flet.canvas as cv
from .palette import (
    C_TEXT, C_TEXT2, C_TEXT3, C_SAKURA_DK, C_BORDER, CHART_COLORS,
    _rgba, _cv_text_right, _cv_text_left, _cv_text_top_center, _text_w, _text_h
)


class StackedBarChart(ft.Container):
    """Vertical stacked-bar chart — setiap bar berisi segment dari berbagai kategori."""

    PAD_L = 46
    PAD_R = 12
    PAD_T = 30
    PAD_B = 90          # lebih besar agar label miring tidak terpotong
    LEGEND_H = 28       # tinggi area legenda

    # Hardcoded mapping: TV & Movie mendapat dua warna utama tema (index 0 & 1)
    _PRIORITY_TYPES = {"TV": 0, "Movie": 1}

    def __init__(
        self,
        stacked_data: list[dict],
        title: str,
        y_label: str = "",
        theme: dict = None,
        tooltip=None,
    ):
        """
        Parameters
        ----------
        stacked_data : list[dict]
            Setiap elemen = {
                "label": str,              # label sumbu-x  (mis. "1–12")
                "segments": dict[str,int],  # {type_name: count, …}
                "total": int,              # sum of segments
            }
        title : str
        """
        super().__init__(expand=True)
        self._data   = stacked_data
        self._title  = title
        self._theme  = theme
        self._tooltip = tooltip
        self._w = self._h = 0
        self._bar_rects: list[tuple[float, float, float, float]] = []  # (bx, by, bw, bh)

        # Kumpulkan semua type names yang muncul (urutan konsisten)
        seen: dict[str, None] = {}
        for d in stacked_data:
            for key in d["segments"]:
                if key not in seen:
                    seen[key] = None
        self._type_keys: list[str] = list(seen.keys())

        # ── Assign warna per type dari tema aktif ─────────────────────────────
        chart_colors = theme.get("chart_colors", CHART_COLORS) if theme else CHART_COLORS
        self._type_colors: dict[str, str] = {}

        # TV → chart_colors[0], Movie → chart_colors[1]  (hardcoded)
        used_indices: set[int] = set()
        for type_name, color_idx in self._PRIORITY_TYPES.items():
            if type_name in seen and color_idx < len(chart_colors):
                self._type_colors[type_name] = chart_colors[color_idx]
                used_indices.add(color_idx)

        # Sisa tipe — ambil warna berikutnya dari chart_colors, skip yang sudah dipakai
        remaining_pool = [c for i, c in enumerate(chart_colors) if i not in used_indices]
        pool_idx = 0
        for key in self._type_keys:
            if key not in self._type_colors:
                self._type_colors[key] = remaining_pool[pool_idx % len(remaining_pool)]
                pool_idx += 1

        c_title = theme["text_main"] if theme else C_TEXT

        self._canvas = cv.Canvas(
            shapes=[], expand=True,
            on_resize=self._on_resize,
        )

        # Gesture detector untuk menangkap klik pada bar
        self._gd = ft.GestureDetector(
            content=self._canvas,
            on_tap_up=self._on_tap,
            expand=True,
        )

        title_bar = ft.Container(
            content=ft.Text(
                title, size=14, weight=ft.FontWeight.BOLD,
                color=c_title, text_align=ft.TextAlign.CENTER,
            ),
            padding=ft.padding.only(top=8, bottom=0),
            alignment=ft.alignment.Alignment.TOP_CENTER,
        )

        # Legend chips — ft controls di atas canvas, diratakan tengah
        legend_controls: list[ft.Control] = []
        for key in self._type_keys:
            legend_controls.append(
                ft.Row(
                    controls=[
                        ft.Container(
                            width=10, height=10, border_radius=3,
                            bgcolor=self._type_colors[key],
                        ),
                        ft.Text(key, size=10, color=theme["text_secondary"] if theme else C_TEXT2),
                    ],
                    spacing=4,
                    tight=True,
                )
            )

        legend_row = ft.Container(
            content=ft.Row(
                controls=legend_controls,
                spacing=12,
                alignment=ft.MainAxisAlignment.CENTER,
                wrap=True,
            ),
            padding=ft.padding.only(top=2, bottom=4),
            alignment=ft.alignment.Alignment.CENTER,
        )

        self.content = ft.Column(
            controls=[title_bar, legend_row, ft.Stack(controls=[self._gd], expand=True)],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # ── resize & redraw ───────────────────────────────────────────────────────

    def _on_resize(self, e):
        self._w, self._h = e.width, e.height
        self._redraw()

    # ── click handler ─────────────────────────────────────────────────────────

    def _on_tap(self, e: ft.TapEvent):
        """Saat bar diklik, tampilkan tooltip berisi detail per-type."""
        if not self._tooltip or not self._bar_rects:
            return

        lx, ly = e.local_position.x, e.local_position.y
        for i, (bx, by, bw, bh) in enumerate(self._bar_rects):
            if bx <= lx <= bx + bw and by <= ly <= by + bh:
                d = self._data[i]
                title = f"Episode {d['label']}"
                rows = []
                for key in self._type_keys:
                    cnt = d["segments"].get(key, 0)
                    if cnt > 0:
                        rows.append((f"● {key}", str(cnt)))
                rows.append(("Total", str(d["total"])))

                self._tooltip.show_at(
                    e.global_position.x, e.global_position.y,
                    title, rows,
                )
                return

        # Klik di luar bar → sembunyikan tooltip
        self._tooltip.hide()

    # ── redraw ────────────────────────────────────────────────────────────────

    def _redraw(self):
        if self._w == 0:
            return
        w, h    = self._w, self._h
        max_v   = max((d["total"] for d in self._data), default=1) or 1
        area_w  = w - self.PAD_L - self.PAD_R
        area_h  = h - self.PAD_T - self.PAD_B
        n       = len(self._data)
        shapes: list = []
        self._bar_rects = []

        c_text2   = self._theme["text_secondary"]   if self._theme else C_TEXT2
        c_text3   = self._theme["text_secondary"]   if self._theme else C_TEXT3
        c_border  = self._theme["border_color"]      if self._theme else C_BORDER
        c_primary = self._theme["primary"]           if self._theme else C_SAKURA_DK

        # ── horizontal grid lines ─────────────────────────────────────────────
        grid_p = ft.Paint(
            style=ft.PaintingStyle.STROKE, stroke_width=0.7,
            color=self._theme["border_color"] if self._theme else "#22000000",
        )
        for frac in [0.25, 0.5, 0.75, 1.0]:
            gy    = self.PAD_T + area_h * (1 - frac)
            label = str(int(max_v * frac))
            shapes.append(cv.Path(
                [cv.Path.MoveTo(self.PAD_L, gy),
                 cv.Path.LineTo(w - self.PAD_R, gy)],
                grid_p,
            ))
            shapes.append(_cv_text_right(self.PAD_L - 4, gy, label, 11, c_text3))

        # ── bars ──────────────────────────────────────────────────────────────
        slot_w = area_w / n
        bar_w  = max(4.0, slot_w * 0.62)

        for i, d in enumerate(self._data):
            bx = self.PAD_L + i * slot_w + (slot_w - bar_w) / 2
            total_bar_h = area_h * (d["total"] / max_v)
            bar_top_y   = self.PAD_T + area_h - total_bar_h

            # Simpan hit-rect untuk click detection
            self._bar_rects.append((bx, bar_top_y, bar_w, total_bar_h))

            y_bottom = self.PAD_T + area_h      # baseline

            # Collect non-zero segments to know which is last (topmost)
            active_segments = [
                (key, d["segments"].get(key, 0))
                for key in self._type_keys
                if d["segments"].get(key, 0) > 0
            ]

            # stack segments bottom → top
            for seg_idx, (key, seg_val) in enumerate(active_segments):
                seg_h = area_h * (seg_val / max_v)
                y_top = y_bottom - seg_h
                is_last = (seg_idx == len(active_segments) - 1)

                color = self._type_colors[key]

                if is_last:
                    # Segment paling atas — rounded top, sama seperti VerticalBarChart
                    shapes.append(cv.Rect(
                        x=bx, y=y_top, width=bar_w, height=max(seg_h, 1),
                        border_radius=ft.border_radius.only(top_left=4, top_right=4),
                        paint=ft.Paint(style=ft.PaintingStyle.FILL, color=color),
                    ))
                else:
                    # Segment bawah — kotak biasa
                    shapes.append(cv.Rect(
                        x=bx, y=y_top, width=bar_w, height=max(seg_h, 1),
                        border_radius=0,
                        paint=ft.Paint(style=ft.PaintingStyle.FILL, color=color),
                    ))

                y_bottom = y_top   # next segment goes on top

            # total label di atas bar
            shapes.append(_cv_text_top_center(
                bx + bar_w / 2,
                bar_top_y - 15,
                str(d["total"]), 11, c_primary,
            ))

            # x-axis label — diagonal 45°
            shapes.append(cv.Text(
                x=bx + bar_w / 2,
                y=h - self.PAD_B + 6,
                value=d["label"],
                rotate=0.785,
                style=ft.TextStyle(size=11, color=c_text2),
            ))

        # ── axes ──────────────────────────────────────────────────────────────
        axis_p = ft.Paint(style=ft.PaintingStyle.STROKE, stroke_width=1, color=c_border)
        shapes.append(cv.Path(
            [cv.Path.MoveTo(self.PAD_L, self.PAD_T),
             cv.Path.LineTo(self.PAD_L, h - self.PAD_B),
             cv.Path.LineTo(w - self.PAD_R, h - self.PAD_B)],
            axis_p,
        ))

        self._canvas.shapes = shapes
        self._canvas.update()

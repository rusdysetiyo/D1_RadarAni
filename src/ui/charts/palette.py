import math
import flet as ft
import flet.canvas as cv

# ── Palette ───────────────────────────────────────────────────────────────────
C_SAKURA    = "#C07090"
C_SAKURA_LT = "#F9F0F5"
C_SAKURA_DK = "#A05070"
C_TEXT      = "#3D2535"
C_TEXT2     = "#8B6A7A"
C_TEXT3     = "#B0909A"
C_BORDER    = "#EDE0E8"
C_WHITE     = "#FFFFFF"

CHART_COLORS = [
    "#C07090", "#D4A8C0", "#A0506A", "#E8D0DE", "#B08090",
    "#906070", "#E0B0C8", "#F0E4EB", "#C890A8", "#F4D8E8",
]
C_HOVER = "#FF5080"


def _rgba(hex_color: str, alpha: float) -> str:
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    a = int(alpha * 255)
    return f"#{a:02X}{r:02X}{g:02X}{b:02X}"


def _arc_points(cx, cy, r, angle_start, angle_sweep, steps=32):
    """
    Kembalikan list titik (x,y) di sepanjang busur.
    Digunakan untuk menggambar donut slice sebagai Polygon/LineTo chain
    karena cv.Path.Arc tidak dilanjut dari titik terakhir Path.
    """
    pts = []
    for k in range(steps + 1):
        a = angle_start + angle_sweep * k / steps
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


# ─────────────────────────────────────────────────────────────────────────────
# cv.Text helper — x,y selalu top-left corner di Flet canvas
# Untuk right-align  : x = target_right - estimated_width
# Untuk center-align : x = center - estimated_width/2
# Estimasi lebar teks = jumlah karakter * font_size * 0.6
# ─────────────────────────────────────────────────────────────────────────────
def _text_w(text: str, size: float) -> float:
    return len(text) * size * 0.60

def _text_h(size: float) -> float:
    return size * 1.25

def _cv_text_center(x, y, text, size, color, bold=False):
    """cv.Text dengan anchor tengah (x,y adalah center)."""
    tw = _text_w(text, size)
    th = _text_h(size)
    return cv.Text(
        x=x - tw / 2,
        y=y - th / 2,
        value=text,
        style=ft.TextStyle(
            size=size, color=color,
            weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL,
        ),
    )

def _cv_text_right(x, y, text, size, color):
    """cv.Text dengan anchor kanan-tengah (x = right edge, y = vertical center)."""
    tw = _text_w(text, size)
    th = _text_h(size)
    return cv.Text(
        x=x - tw,
        y=y - th / 2,
        value=text,
        style=ft.TextStyle(size=size, color=color),
    )

def _cv_text_left(x, y, text, size, color, bold=False):
    """cv.Text dengan anchor kiri-tengah (x = left edge, y = vertical center)."""
    th = _text_h(size)
    return cv.Text(
        x=x,
        y=y - th / 2,
        value=text,
        style=ft.TextStyle(
            size=size, color=color,
            weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL,
        ),
    )

def _cv_text_top_center(x, y, text, size, color, bold=False):
    """cv.Text dengan anchor atas-tengah (x = center, y = top)."""
    tw = _text_w(text, size)
    return cv.Text(
        x=x - tw / 2,
        y=y,
        value=text,
        style=ft.TextStyle(
            size=size, color=color,
            weight=ft.FontWeight.BOLD if bold else ft.FontWeight.NORMAL,
        ),
    )

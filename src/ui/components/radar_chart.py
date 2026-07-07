import flet as ft
import flet.canvas as cv
import math


def detail_radar_chart(global_scores, personal_scores, labels, theme, size=300):
    cx = cy = size / 2
    max_r = size / 2 - 40
    n = len(labels)
    grid_levels = 5
    shapes = []

    def petal_path(angle_deg, length, width_factor=0.46, notch_depth=0.11):
        rad = math.radians(angle_deg)
        rad_perp = math.radians(angle_deg + 90)

        w = length * width_factor

        notch_dist = length * 0.92
        notch_lx = cx + notch_dist * math.cos(rad) + w * 0.22 * math.cos(rad_perp)
        notch_ly = cy + notch_dist * math.sin(rad) + w * 0.22 * math.sin(rad_perp)
        notch_rx = cx + notch_dist * math.cos(rad) - w * 0.22 * math.cos(rad_perp)
        notch_ry = cy + notch_dist * math.sin(rad) - w * 0.22 * math.sin(rad_perp)

        indent_x = cx + (length - length * notch_depth) * math.cos(rad)
        indent_y = cy + (length - length * notch_depth) * math.sin(rad)

        c1x = cx + length * 0.50 * math.cos(rad) + w * 0.95 * math.cos(rad_perp)
        c1y = cy + length * 0.50 * math.sin(rad) + w * 0.95 * math.sin(rad_perp)
        c2x = notch_lx - length * 0.15 * math.cos(rad) + w * 0.45 * math.cos(rad_perp)
        c2y = notch_ly - length * 0.15 * math.sin(rad) + w * 0.45 * math.sin(rad_perp)

        c5x = cx + length * 0.50 * math.cos(rad) - w * 0.95 * math.cos(rad_perp)
        c5y = cy + length * 0.50 * math.sin(rad) - w * 0.95 * math.sin(rad_perp)
        c6x = notch_rx - length * 0.15 * math.cos(rad) - w * 0.45 * math.cos(rad_perp)
        c6y = notch_ry - length * 0.15 * math.sin(rad) - w * 0.45 * math.sin(rad_perp)

        ci1x = indent_x + w * 0.20 * math.cos(rad_perp)
        ci1y = indent_y + w * 0.20 * math.sin(rad_perp)
        ci2x = indent_x - w * 0.20 * math.cos(rad_perp)
        ci2y = indent_y - w * 0.20 * math.sin(rad_perp)

        return [
            cv.Path.MoveTo(cx, cy),
            cv.Path.CubicTo(c1x, c1y, c2x, c2y, notch_lx, notch_ly),
            cv.Path.CubicTo(ci1x, ci1y, ci2x, ci2y, notch_rx, notch_ry),
            cv.Path.CubicTo(c6x, c6y, c5x, c5y, cx, cy),
            cv.Path.Close(),
        ]

    # Grid rings (berbentuk bunga — gunakan petal_path di setiap level)
    for level in range(1, grid_levels + 1):
        level_length = max_r * level / grid_levels
        for i in range(n):
            angle_deg = -90 + i * 360 / n
            shapes.append(ft.canvas.Path(
                elements=petal_path(angle_deg, level_length),
                paint=ft.Paint(color=theme["radar_grid"], stroke_width=0.8,
                               style=ft.PaintingStyle.STROKE)
            ))

    # Axis lines
    for i in range(n):
        angle = math.radians(-90 + i * 360 / n)
        shapes.append(ft.canvas.Path(
            elements=[
                ft.canvas.Path.MoveTo(cx, cy),
                ft.canvas.Path.LineTo(cx + max_r * math.cos(angle), cy + max_r * math.sin(angle)),
            ],
            paint=ft.Paint(color=theme["radar_grid"], stroke_width=0.8)
        ))

    # Global petals
    for i, score in enumerate(global_scores):
        angle_deg = -90 + i * 360 / n
        length = (score / 10) * max_r
        cmds = petal_path(angle_deg, length)

        shapes.append(ft.canvas.Path(
            elements=cmds,
            paint=ft.Paint(color=theme["radar_g_area"], style=ft.PaintingStyle.FILL)
        ))
        shapes.append(ft.canvas.Path(
            elements=cmds,
            paint=ft.Paint(color=theme["radar_g_border"], stroke_width=1.5, style=ft.PaintingStyle.STROKE)
        ))
        for frac in [0.65, 0.4]:
            sub_cmds = petal_path(angle_deg, length * frac, width_factor=0.28)
            shapes.append(ft.canvas.Path(
                elements=sub_cmds,
                paint=ft.Paint(color=theme["radar_g_area"], stroke_width=0.6, style=ft.PaintingStyle.STROKE)
            ))

    # Personal petals
    if any(s > 0 for s in personal_scores):
        for i, score in enumerate(personal_scores):
            angle_deg = -90 + i * 360 / n
            length = (score / 10) * max_r
            cmds = petal_path(angle_deg, length)

            shapes.append(ft.canvas.Path(
                elements=cmds,
                paint=ft.Paint(color=theme["radar_p_area"], style=ft.PaintingStyle.FILL)
            ))
            shapes.append(ft.canvas.Path(
                elements=cmds,
                paint=ft.Paint(color=theme["radar_p_border"], stroke_width=1.5, style=ft.PaintingStyle.STROKE)
            ))

    # Labels dengan skor eksak
    def _fmt(s):
        """Format angka: tampilkan bilangan bulat jika utuh, 1 desimal jika tidak."""
        try:
            f = float(s)
            return str(int(f)) if f == int(f) else f"{f:.1f}"
        except Exception:
            return "–"

    has_personal = any(s > 0 for s in personal_scores)
    label_r = max_r + 22

    for i, label in enumerate(labels):
        angle = math.radians(-90 + i * 360 / n)
        lx = cx + label_r * math.cos(angle)
        ly = cy + label_r * math.sin(angle)

        # Baris 1: nama kategori
        shapes.append(ft.canvas.Text(
            x=lx, y=ly - 7,
            value=label,
            alignment=ft.Alignment(0, 0),
            style=ft.TextStyle(size=11, color=theme["radar_labels"], weight=ft.FontWeight.W_500),
        ))

        g_str = _fmt(global_scores[i])
        if has_personal:
            p_str = _fmt(personal_scores[i])
            # Baris 2: skor dataset-1 (warna g) · "/" · skor dataset-2 (warna p)
            shapes.append(ft.canvas.Text(
                x=lx - 12, y=ly + 7,
                value=g_str,
                alignment=ft.Alignment(0, 0),
                style=ft.TextStyle(size=10, color=theme["radar_g_border"], weight=ft.FontWeight.BOLD),
            ))
            shapes.append(ft.canvas.Text(
                x=lx, y=ly + 7,
                value="/",
                alignment=ft.Alignment(0, 0),
                style=ft.TextStyle(size=10, color=theme["radar_labels"]),
            ))
            shapes.append(ft.canvas.Text(
                x=lx + 12, y=ly + 7,
                value=p_str,
                alignment=ft.Alignment(0, 0),
                style=ft.TextStyle(size=10, color=theme["radar_p_border"], weight=ft.FontWeight.BOLD),
            ))
        else:
            # Baris 2: satu skor saja, warna dataset global
            shapes.append(ft.canvas.Text(
                x=lx, y=ly + 7,
                value=g_str,
                alignment=ft.Alignment(0, 0),
                style=ft.TextStyle(size=10, color=theme["radar_g_border"], weight=ft.FontWeight.BOLD),
            ))

    # Center dot
    shapes.append(ft.canvas.Circle(cx, cy, 4, ft.Paint(color=theme["radar_grid"], style=ft.PaintingStyle.FILL)))

    return ft.Container(
        width=size,
        height=size,
        content=ft.canvas.Canvas(shapes=shapes, width=size, height=size)
    )
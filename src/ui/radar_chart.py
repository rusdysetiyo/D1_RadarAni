import flet as ft
import flet.canvas as cv
import math
import asyncio


def _ease_out_cubic(t: float) -> float:
    return 1 - (1 - t) ** 3


def _ease_out_elastic(t: float) -> float:
    if t <= 0: return 0
    if t >= 1: return 1
    return (2 ** (-10 * t)) * math.sin((t * 10 - 0.75) * (2 * math.pi) / 3) + 1


class CustomRadarChart(ft.Container):
    def __init__(self, global_scores, personal_scores, size=300):
        super().__init__()
        self.global_scores   = global_scores
        self.personal_scores = [s if s else 0 for s in personal_scores]
        self.size            = size
        self.center_x        = size / 2
        self.center_y        = size / 2
        self.max_radius      = (size / 2) - 40
        self.labels          = ["Plot", "Visual", "Audio", "Character", "Direction"]
        self.angles          = [-math.pi / 2 + i * (2 * math.pi / 5) for i in range(5)]
        self._animating      = False

        self.static_canvas   = cv.Canvas(width=self.size, height=self.size)

        self.personal_fill   = cv.Path(
            elements=[],
            paint=ft.Paint(style=ft.PaintingStyle.FILL, color="#55FFB7C5"),
        )
        self.personal_stroke = cv.Path(
            elements=[],
            paint=ft.Paint(style=ft.PaintingStyle.STROKE, color="#FF69B4", stroke_width=2),
        )
        self.personal_canvas = cv.Canvas(
            shapes=[self.personal_fill, self.personal_stroke],
            width=self.size, height=self.size,
        )

        self.content = ft.Stack(
            width=self.size, height=self.size,
            controls=[self.static_canvas, self.personal_canvas],
        )

        self._draw_static_background()
        self._redraw_personal(self.personal_scores)

    def _get_sakura_path(self, scores):
        path_elements = []
        for i in range(5):
            a        = self.angles[i]
            val      = scores[i] if scores[i] else 0
            r        = self.max_radius * (val / 10)
            val_prev = scores[i - 1] if scores[i - 1] else 0
            r_prev   = self.max_radius * (val_prev / 10)
            r_valley = max(self.max_radius * 0.05, (r + r_prev) * 0.1)

            valley_angle = a - math.pi / 5
            vx = self.center_x + r_valley * math.cos(valley_angle)
            vy = self.center_y + r_valley * math.sin(valley_angle)

            if i == 0:
                path_elements.append(cv.Path.MoveTo(vx, vy))

            cleft_r = r * 0.85
            cx_p    = self.center_x + cleft_r * math.cos(a)
            cy_p    = self.center_y + cleft_r * math.sin(a)

            cp1_angle = a - math.pi / 10
            cp1x = self.center_x + r * 1.25 * math.cos(cp1_angle)
            cp1y = self.center_y + r * 1.25 * math.sin(cp1_angle)
            path_elements.append(cv.Path.QuadraticTo(cp1x, cp1y, cx_p, cy_p))

            cp2_angle = a + math.pi / 10
            cp2x = self.center_x + r * 1.25 * math.cos(cp2_angle)
            cp2y = self.center_y + r * 1.25 * math.sin(cp2_angle)

            val_next = scores[(i + 1) % 5] if scores[(i + 1) % 5] else 0
            r_next   = self.max_radius * (val_next / 10)
            r_v_next = max(self.max_radius * 0.05, (r + r_next) * 0.1)
            vn_angle = a + math.pi / 5
            vnx = self.center_x + r_v_next * math.cos(vn_angle)
            vny = self.center_y + r_v_next * math.sin(vn_angle)
            path_elements.append(cv.Path.QuadraticTo(cp2x, cp2y, vnx, vny))

        path_elements.append(cv.Path.Close())
        return path_elements

    def _redraw_personal(self, scores):
        path = self._get_sakura_path(scores)
        self.personal_fill.elements   = path
        self.personal_stroke.elements = path

    def _draw_static_background(self):
        self.static_canvas.shapes.clear()

        for step in range(2, 11, 2):
            self.static_canvas.shapes.append(cv.Path(
                elements=self._get_sakura_path([step] * 5),
                paint=ft.Paint(style=ft.PaintingStyle.STROKE, color="#E8D5E0", stroke_width=1),
            ))

        for i, angle in enumerate(self.angles):
            x_end = self.center_x + self.max_radius * math.cos(angle)
            y_end = self.center_y + self.max_radius * math.sin(angle)
            self.static_canvas.shapes.append(
                cv.Line(self.center_x, self.center_y, x_end, y_end,
                        paint=ft.Paint(color="#E0D0D8"))
            )
            tx = self.center_x + (self.max_radius + 20) * math.cos(angle)
            ty = self.center_y + (self.max_radius + 20) * math.sin(angle)
            self.static_canvas.shapes.append(
                cv.Text(tx - 15, ty - 10, self.labels[i],
                        ft.TextStyle(size=12, color="#A08090", weight=ft.FontWeight.W_500))
            )

        global_path = self._get_sakura_path(self.global_scores)
        self.static_canvas.shapes.append(cv.Path(
            elements=global_path,
            paint=ft.Paint(style=ft.PaintingStyle.FILL, color="#332196F3"),
        ))
        self.static_canvas.shapes.append(cv.Path(
            elements=global_path,
            paint=ft.Paint(style=ft.PaintingStyle.STROKE, color="#2196F3", stroke_width=2),
        ))

    async def bloom(self, target_scores):
        """
        Tiap petal 'tumbuh' dari nilai sekarang ke target secara individual.
        Petal 0 mulai duluan, petal 1 delay 30ms, dst — efek mekar satu per satu.
        """
        if self._animating:
            return
        self._animating = True

        from_scores = self.personal_scores.copy()
        to_scores   = [s if s else 0 for s in target_scores]

        fps        = 60
        duration_s = 0.65
        frames     = int(fps * duration_s)
        frame_dt   = duration_s / frames
        petal_delay = 0.035  # 35ms delay antar petal

        for frame in range(frames + 1):
            t_global     = frame / frames
            interpolated = []

            for i in range(5):
                # t lokal per petal — mulai setelah delay-nya
                delay_frac = (i * petal_delay) / duration_s
                t_local    = max(0.0, min(1.0,
                    (t_global - delay_frac) / max(0.001, 1.0 - delay_frac)
                ))
                eased = _ease_out_elastic(t_local)
                val   = from_scores[i] + (to_scores[i] - from_scores[i]) * eased
                interpolated.append(max(0, val))

            self._redraw_personal(interpolated)
            try:
                self.personal_canvas.update()
            except Exception:
                break

            await asyncio.sleep(frame_dt)

        # Final value presisi
        self._redraw_personal(to_scores)
        try:
            self.personal_canvas.update()
        except Exception:
            pass

        self.personal_scores = to_scores.copy()
        self._animating      = False

    def update_personal_scores(self, target_scores, page: ft.Page):
        """Dipanggil dari event handler — non-blocking."""
        page.run_task(self.bloom, target_scores)
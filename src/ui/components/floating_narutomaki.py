import flet as ft
import asyncio
import random
import math
import base64


def _narutomaki_svg(size: int = 100, color: str = "#F04878") -> str:
    cx, cy = size / 2, size / 2
    r = size / 2 - 2
    uid = abs(hash(color + str(size))) % 9999

    def hex_shift(h, delta):
        h = h.lstrip('#')
        r_, g_, b_ = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
        return f"#{max(0,min(255,r_+delta)):02x}{max(0,min(255,g_+delta)):02x}{max(0,min(255,b_+delta)):02x}"

    c_light  = hex_shift(color, +50)
    c_border = hex_shift(color, +20)
    c_dark   = hex_shift(color, -30)

    steps = 60
    spiral_pts = []
    for i in range(steps + 1):
        t = i / steps
        sr = size * 0.08 + (size * 0.32 - size * 0.08) * t
        angle = math.radians(-90 + t * 540)
        x = cx + sr * math.cos(angle)
        y = cy + sr * math.sin(angle)
        spiral_pts.append(f"{x:.2f},{y:.2f}")

    spiral_d = "M " + " L ".join(spiral_pts)

    n_scallop = 16  # jumlah gerigi
    pts_outer = []
    pts_inner = []
    for i in range(n_scallop * 2 + 1):
        angle = math.radians(i * 360 / (n_scallop * 2))
        # Selang-seling radius luar (puncak gerigi) dan dalam (lembah)
        rad = r if i % 2 == 0 else r * 0.86
        pts_outer.append((
            cx + rad * math.cos(angle),
            cy + rad * math.sin(angle)
        ))

    scallop_d = "M " + " L ".join([f"{x:.2f},{y:.2f}" for x, y in pts_outer]) + " Z"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
        width="{size}" height="{size}" viewBox="0 0 {size} {size}">
        <defs>
            <radialGradient id="ng{uid}" cx="40%" cy="35%" r="65%">
                <stop offset="0%"   stop-color="#FFFFFF"/>
                <stop offset="70%"  stop-color="#FAF0F2"/>
                <stop offset="100%" stop-color="{c_light}"/>
            </radialGradient>
            <filter id="ns{uid}" x="-20%" y="-20%" width="140%" height="140%">
                <feDropShadow dx="{size * 0.04:.1f}" dy="{size * 0.05:.1f}"
                    stdDeviation="{size * 0.04:.1f}"
                    flood-color="{c_dark}" flood-opacity="0.30"/>
                <feDropShadow dx="{-size * 0.02:.1f}" dy="{-size * 0.02:.1f}"
                    stdDeviation="{size * 0.03:.1f}"
                    flood-color="#FFFFFF" flood-opacity="0.60"/>
            </filter>
        </defs>

        <!-- 1. Shape bergerigi sebagai base -->
        <path d="{scallop_d}"
            fill="url(#ng{uid})"
            filter="url(#ns{uid})"
            stroke="{c_border}" stroke-width="1.0" opacity="1"/>

        <!-- 2. Spiral -->
        <path d="{spiral_d}"
            fill="none" stroke="{color}"
            stroke-width="{size * 0.07:.1f}"
            stroke-linecap="round" stroke-linejoin="round"
            opacity="0.88"/>

        <!-- 3. Highlight -->
        <ellipse cx="{cx - r * 0.28}" cy="{cy - r * 0.30}"
            rx="{size * 0.12}" ry="{size * 0.07}"
            fill="white" opacity="0.45"
            transform="rotate(-30,{cx},{cy})"/>
    </svg>'''

    b64 = base64.b64encode(svg.encode()).decode()
    return f"data:image/svg+xml;base64,{b64}"


class FloatingNeuNaruto:
    CONFIGS = [
        # (rx, ry, size, opacity, amp_y, speed, color_base)
        (0.06, 0.12,  90, 0.90, 12, 1.5, "#B8B0CC"),
        (0.80, 0.08,  70, 0.80, 10, 1.9, "#C4A8B8"),
        (0.18, 0.68,  80, 0.85, 13, 1.4, "#A8B0C8"),
        (0.65, 0.75,  60, 0.75,  9, 2.1, "#B8B0CC"),
        (0.88, 0.42,  75, 0.82, 11, 1.7, "#C0B8D4"),
        (0.38, 0.88,  55, 0.70,  8, 2.3, "#C4A8B8"),
        (0.88, 0.18,  65, 0.78, 10, 1.8, "#A8B0C8"),
        (0.10, 0.38,  50, 0.65,  7, 2.2, "#B8B0CC"),
        (0.50, 0.10,  85, 0.88, 14, 1.6, "#C0B8D4"),
    ]

    def __init__(self, stack: ft.Stack, page: ft.Page):
        self.stack    = stack
        self.page     = page
        self._running = True
        self._items: list[dict] = []
        self._spawn()

    def _spawn(self):
        pw = self.page.window.width  or 900
        ph = self.page.window.height or 600

        for rx, ry, sz, op, amp, speed, base_col in self.CONFIGS:
            bx    = rx * pw - sz / 2
            by    = ry * ph - sz / 2
            phase = random.uniform(0, math.pi * 2)
            rot0  = random.uniform(0, math.pi * 2)
            rsped = random.uniform(0.2, 0.5) * random.choice([-1, 1])

            ctrl = ft.Container(
                content=ft.Image(
                    src=_narutomaki_svg(sz, base_col),
                    width=sz, height=sz,
                ),
                opacity=op,
                left=bx, top=by,
                rotate=ft.Rotate(angle=rot0),
            )
            self.stack.controls.append(ctrl)
            self._items.append({
                "ctrl": ctrl,
                "bx": bx, "by": by,
                "amp": amp, "speed": speed,
                "phase": phase,
                "base_op": op,
                "rot": rot0, "rsped": rsped,
            })

    async def float(self):
        t = 0.0
        while self._running:
            for it in self._items:
                c = it["ctrl"]
                c.top  = it["by"] + it["amp"] * math.sin(t * it["speed"] + it["phase"])
                c.left = it["bx"] + (it["amp"] * 0.35) * math.cos(t * it["speed"] * 0.65 + it["phase"])
                c.opacity = max(0.4, it["base_op"] + 0.06 * math.sin(t * it["speed"] * 0.4 + it["phase"]))
                it["rot"] += it["rsped"] * 0.012
                c.rotate = ft.Rotate(angle=it["rot"])
                c.update()
            await asyncio.sleep(0.04)
            t += 0.04

    def stop(self):
        self._running = False


class FloatingNeuNaruto:
    def __init__(self, stack: ft.Stack, page: ft.Page, theme: dict, max_petals: int = 5,
                 is_loading_screen: bool = False):
        self.stack = stack
        self.page = page
        self.theme = theme
        self._running = True
        self._items: list[dict] = []

        # --- LOGIKA WARNA DINAMIS ---
        # 1. Ambil list warna dari tema aktif
        theme_colors = self.theme.get("petal_colors", [self.theme["primary"]])

        # 2. Selipin warna "Signature" Airy Dreamy (#C9C7F8 / Periwinkle)
        # biar tetep ada aura kucu-keren-nya di semua tema
        self.petal_colors = theme_colors + ["#C9C7F8"]

        self.max_petals = max_petals
        self.base_speed = 1.8 if is_loading_screen else 0.6
        self._spawn()

    def _spawn(self):
        pw = self.page.window.width or 900
        ph = self.page.window.height or 600

        for _ in range(self.max_petals):
            # --- SAFE ZONE (Tengah Bolong) ---
            while True:
                rx = random.uniform(0.02, 0.98)
                ry = random.uniform(0.02, 0.98)
                # Area tengah 40% horizontal & 60% vertikal dijagain kosong
                is_in_center = (0.3 < rx < 0.7) and (0.2 < ry < 0.8)
                if not is_in_center:
                    break

            sz = random.randint(50, 95)
            op = random.uniform(0.65, 0.90)
            amp = random.uniform(8, 15)
            speed = random.uniform(0.8, 1.2) * self.base_speed

            # AMBIL WARNA: Random dari list yang udah kita campur tadi
            base_col = random.choice(self.petal_colors)

            bx = rx * pw - sz / 2
            by = ry * ph - sz / 2
            phase = random.uniform(0, math.pi * 2)
            rot0 = random.uniform(0, math.pi * 2)
            rsped = random.uniform(0.1, 0.3) * random.choice([-1, 1])

            ctrl = ft.Container(
                content=ft.Image(
                    src=_narutomaki_svg(sz, base_col),   # Warna dinamis di sini!
                    width=sz, height=sz,
                ),
                opacity=op,
                left=bx, top=by,
                rotate=ft.Rotate(angle=rot0),
            )
            self.stack.controls.insert(0, ctrl)

            self._items.append({
                "ctrl": ctrl, "bx": bx, "by": by, "amp": amp,
                "speed": speed, "phase": phase, "base_op": op,
                "rot": rot0, "rsped": rsped,
            })

    async def float(self):
        t = 0.0
        while self._running:
            for it in self._items:
                c = it["ctrl"]
                c.top = it["by"] + it["amp"] * math.sin(t * it["speed"] + it["phase"])
                c.left = it["bx"] + (it["amp"] * 0.35) * math.cos(t * it["speed"] * 0.65 + it["phase"])
                c.opacity = max(0.4, it["base_op"] + 0.06 * math.sin(t * it["speed"] * 0.4 + it["phase"]))
                it["rot"] += it["rsped"] * 0.012
                c.rotate = ft.Rotate(angle=it["rot"])

            # UPDATE-NYA SEKALI AJA DI LUAR LOOP BIAR GAK NGE-LAG BANGET
            self.stack.update()

            await asyncio.sleep(0.04)
            t += 0.04

    def stop(self):
        self._running = False
import flet as ft
import random
import asyncio


class HujanSakura:

    def __init__(self, target_container, theme):
        self.target = target_container
        self.theme = theme
        self.petals = []
        self.is_running = True

        for _ in range(25):
            petal = ft.Container(
                width=10, height=14,
                bgcolor=random.choice(theme["petal_colors"]),
                border_radius=ft.border_radius.only(top_left=15, bottom_right=15, top_right=2, bottom_left=2),
                opacity=0.6,
                left=random.randint(0, 1200),
                top=random.randint(-200, -50),  # Sembunyikan aman di atas luar layar
                rotate=ft.Rotate(angle=random.uniform(0, 3.14)),
            )
            self.petals.append(petal)

    async def turun(self):
        await asyncio.sleep(0.4)

        if not self.is_running or not self.target.page:
            return

        for petal in self.petals:
            self.target.controls.append(petal)

        try:
            self.target.update()
        except:
            return

        for petal in self.petals:
            asyncio.create_task(self._animasi_per_kelopak(petal))

    async def _animasi_per_kelopak(self, petal):
        await asyncio.sleep(random.uniform(0.0, 3.0))

        while self.is_running:
            try:
                if not self.target.page:
                    break

                durasi = random.randint(6000, 10000)
                petal.animate_position = ft.Animation(durasi, ft.AnimationCurve.LINEAR)
                petal.animate_rotation = ft.Animation(durasi, ft.AnimationCurve.LINEAR)
                petal.opacity = 0.6

                petal.top = 1000
                petal.left += random.randint(-100, 100)
                petal.rotate.angle += random.uniform(2, 4)
                petal.update()

                await asyncio.sleep(durasi / 1000)

                if not self.is_running or not self.target.page:
                    break

                petal.animate_position = ft.Animation(0)
                petal.animate_rotation = ft.Animation(0)
                petal.opacity = 0
                petal.update()

                await asyncio.sleep(0.05)

                petal.top = random.randint(-100, -40)
                petal.left = random.randint(0, 1200)
                petal.rotate.angle = random.uniform(0, 3.14)
                petal.update()

                await asyncio.sleep(random.uniform(0.1, 1.5))

            except Exception:
                break

    def stop(self):
        self.is_running = False
        try:
            if self.target and hasattr(self.target, "controls"):
                for petal in self.petals:
                    if petal in self.target.controls:
                        self.target.controls.remove(petal)
                self.target.update()
        except Exception:
            pass
        self.petals.clear()
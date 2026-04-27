import flet as ft
import asyncio
from src.ui.sakura_anim import get_sakura_svg

C_TEXT3     = "#4A4A4A"
C_SAKURA_LT = "#D890A8"

def buat_bloom_screen(pesan: str):
    sakura_img = ft.Image(
        src=get_sakura_svg(size=160),
        width=160, height=160,
        fit=ft.BoxFit.CONTAIN,
        opacity=0,
        scale=0.3,
        rotate=ft.Rotate(angle=-0.2, alignment=ft.Alignment(0, 0)),
        animate_opacity=ft.Animation(duration=600, curve=ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(duration=700, curve=ft.AnimationCurve.EASE_OUT),
        animate_rotation=ft.Animation(duration=700, curve=ft.AnimationCurve.EASE_OUT),
    )

    label = ft.Text(
        pesan, size=13, color=C_TEXT3,
        weight=ft.FontWeight.W_400,
        opacity=0,
        animate_opacity=ft.Animation(duration=400, curve=ft.AnimationCurve.EASE_IN),
    )

    dots = ft.Text(
        "●  ●  ●", size=11, color=C_SAKURA_LT,
        opacity=0,
        animate_opacity=ft.Animation(duration=500, curve=ft.AnimationCurve.EASE_IN_OUT),
    )

    container = ft.Container(
        expand=True,
        bgcolor="#FCF8FA",
        content=ft.Column(
            controls=[
                ft.Container(expand=True),
                ft.Row([sakura_img], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=20),
                ft.Row([label], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=8),
                ft.Row([dots], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(expand=True),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
        ),
    )
    return container, sakura_img, label, dots

async def animasi_bloom(sakura_img, label, dots):
    await asyncio.sleep(0.08)

    sakura_img.opacity = 1.0
    sakura_img.scale = 1.0
    sakura_img.rotate = ft.Rotate(angle=0.0, alignment=ft.Alignment(0, 0))
    sakura_img.update()

    await asyncio.sleep(0.5)

    label.opacity = 1.0
    label.update()

    await asyncio.sleep(0.25)

    for _ in range(3):
        dots.opacity = 1.0
        dots.update()
        await asyncio.sleep(0.4)
        dots.opacity = 0.2
        dots.update()
        await asyncio.sleep(0.3)
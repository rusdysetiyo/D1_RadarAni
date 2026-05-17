import flet as ft
import asyncio
from ui.components.sakura_anim import get_sakura_svg
from src.ui.components.floating_narutomaki import FloatingNeuNaruto


# 1. Tambahin 'page' di argumen buat dikirim ke FloatingNeuSakura
def buat_bloom_screen(pesan: str, theme, page: ft.Page):
    sakura_img = ft.Image(
        src=get_sakura_svg(size=160),
        width=160, height=160,
        fit=ft.BoxFit.CONTAIN,
        opacity=0,
        scale=0.3,
        rotate=ft.Rotate(angle=-12.56, alignment=ft.Alignment(0, 0)),
        animate_opacity=ft.Animation(duration=2000, curve=ft.AnimationCurve.DECELERATE),
        animate_scale=ft.Animation(duration=2500, curve=ft.AnimationCurve.DECELERATE),
        animate_rotation=ft.Animation(duration=2500, curve=ft.AnimationCurve.DECELERATE),
    )

    label = ft.Text(
        pesan, size=13,
        color=theme["text_main"],
        weight=ft.FontWeight.W_400,
        opacity=0,
        animate_opacity=ft.Animation(duration=400, curve=ft.AnimationCurve.EASE_IN),
    )

    dots = ft.Text(
        "●  ●  ●", size=11,
        color=theme["primary"],
        opacity=0,
        animate_opacity=ft.Animation(duration=500, curve=ft.AnimationCurve.EASE_IN_OUT),
    )

    # 2. Pisahin UI utama ke variabel sendiri
    main_ui = ft.Column(
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
    )

    # 3. Bikin Stack buat numpuk background (bunga) sama foreground (UI utama)
    main_stack = ft.Stack(expand=True)

    # 4. Panggil Floating Sakura-nya (otomatis masuk ke layer paling belakang Stack)
    efek_scallops = FloatingNeuNaruto(
        stack=main_stack,
        page=page,
        theme=theme,
        max_petals=8,  # Bikin agak rame biar lucu pas loading
        is_loading_screen=True
    )

    # 5. Masukin UI Utama ke Stack (numpuk di atas bunganya)
    main_stack.controls.append(main_ui)

    container = ft.Container(
        expand=True,
        bgcolor=theme["bg"],
        content=main_stack,  # <--- Contentnya sekarang diganti jadi Stack
    )

    # Return efek_bunga juga biar animasinya bisa dijalankan/dimatikan
    return container, sakura_img, label, dots, efek_scallops


# 6. Update animasi_bloom buat jalanin efek bunganya
async def animasi_bloom(sakura_img, label, dots, efek_bunga):
    # Nyalain animasi bunga ngambangnya (jalan di background)
    task_bunga = asyncio.create_task(efek_bunga.float())

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
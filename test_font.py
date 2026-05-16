import flet as ft
import base64

# --- SVG PATTERN DATA ---
SEIGAIHA_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="100" height="50" viewBox="0 0 100 50">
    <g fill="none" stroke="{color}" stroke-width="1" opacity="1">
        <path d="M0 50c10 0 20-5 25-15 5 10 15 15 25 15s20-5 25-15c5 10 15 15 25 15"/>
        <path d="M0 35c10 0 20-5 25-15 5 10 15 15 25 15s20-5 25-15c5 10 15 15 25 15"/>
        <path d="M0 20c10 0 20-5 25-15 5 10 15 15 25 15s20-5 25-15c5 10 15 15 25 15"/>
    </g>
</svg>
"""

ASANOHA_SVG = """
<svg xmlns="http://www.w3.org/2000/svg" width="60" height="104" viewBox="0 0 60 104">
    <g fill="none" stroke="{color}" stroke-width="1">
        <path d="M30 0 L60 17.32 L60 51.96 L30 69.28 L0 51.96 L0 17.32 Z"/>
        <path d="M30 0 L30 69.28 M0 17.32 L60 51.96 M0 51.96 L60 17.32"/>
        <path d="M30 34.64 L0 17.32 M30 34.64 L60 17.32 M30 34.64 L30 0 M30 34.64 L0 51.96 M30 34.64 L60 51.96 M30 34.64 L30 69.28"/>
    </g>
</svg>
"""


def get_svg_uri(svg_code, color):
    # Mengubah SVG menjadi Base64 Data URI yang dibaca Flet
    colored_svg = svg_code.replace("{color}", color.replace("#", "%23"))
    b64 = base64.b64encode(colored_svg.encode()).decode()
    return f"data:image/svg+xml;base64,{b64}"


def main(page: ft.Page):
    page.title = "RadarAni Japanese Pattern Tester"
    page.bgcolor = "#FFF7F9"
    page.window_width = 500
    page.window_height = 700

    theme = {
        "primary": "#FFB7C5",
        "text_main": "#4A2E35",
        "bg": "#FFF7F9"
    }

    # LAYER BACKGROUND (Pola)
    pattern_bg = ft.Container(
        expand=True,
        image=ft.DecorationImage(
            src=get_svg_uri(SEIGAIHA_SVG, theme["primary"]),
            repeat=ft.ImageRepeat.REPEAT,
        ),
        opacity=0.1  # Opacity awal
    )

    # FUNGSI UPDATE POLA & OPACITY
    def ganti_pola(e):
        pola_terpilih = ASANOHA_SVG if e.control.value == "asanoha" else SEIGAIHA_SVG
        pattern_bg.image.src = get_svg_uri(pola_terpilih, theme["primary"])
        page.update()

    def ubah_opacity(e):
        pattern_bg.opacity = float(e.control.value)
        page.update()

    # LAYER DEPAN (Panel UI Mockup)
    panel_ui = ft.Container(
        bgcolor=ft.Colors.with_opacity(0.8, "white"),
        padding=30,
        border_radius=15,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.with_opacity(0.1, "black")),
        content=ft.Column([
            ft.Text("レーダアニ", size=12, color=theme["text_main"]),
            ft.Text("RadarAni Pattern", size=24, weight="bold", color=theme["text_main"]),
            ft.Divider(color=theme["primary"]),

            ft.Container(height=10),
            ft.Text("Pilih Vibe Pola:", weight="bold", color=theme["text_main"]),
            ft.RadioGroup(
                value="seigaiha",
                content=ft.Column([
                    ft.Radio(value="seigaiha", label="Seigaiha (Ombak - Tenang)"),
                    ft.Radio(value="asanoha", label="Asanoha (Bintang - Geometris)"),
                ]),
                on_change=ganti_pola
            ),

            ft.Container(height=20),
            ft.Text("Atur Ketebalan Pola (Opacity):", weight="bold", color=theme["text_main"]),
            ft.Slider(
                min=0.01, max=0.4, divisions=20, value=0.1,
                label="{value}",
                on_change=ubah_opacity
            )
        ], tight=True)
    )

    # BUNGKUS DENGAN STACK
    main_stack = ft.Stack([
        pattern_bg,  # Indeks 0 (Paling Belakang)
        ft.Container(content=panel_ui, alignment=ft.Alignment.CENTER, expand=True)  # Indeks 1 (Tengah Depan)
    ], expand=True)

    page.add(main_stack)
    page.update()


# Gass pakai target=main. Abaikan warning merah di terminal!
ft.app(target=main)
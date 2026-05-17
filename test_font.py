import flet as ft

class ThemeManager:
    # 1. Aesthetic Sakura + Matcha
    SAKURA_MATCHA = {
        "primary": "#E8CEDB",
        "primary_light": "#F5E4EE",
        "bg": "#FAF7F2",
        "card": "#FFFFFF",
        "text": "#5C4D53",
        "border_color": "#E5D4DF",
        "shadow_hover": "#99DBC1CE",
        "shadow_default": "#4DDBC1CE",
        "shadow_card_h": "#66DBC1CE",
        "shadow_card_d": "#26DBC1CE",
        "desc": "Tema Sakura: Soft pink dengan gradasi dan colored elevation."
    }

    # 2. Aesthetic Matcha + Sakura
    MATCHA_SAKURA = {
        "primary": "#C3D3B4",
        "primary_light": "#DBE8D0",
        "bg": "#F5F7F2",
        "card": "#FFFFFF",
        "text": "#4A5348",
        "border_color": "#D0DDC1",
        "shadow_hover": "#99B7C7A8",
        "shadow_default": "#4DB7C7A8",
        "shadow_card_h": "#66B7C7A8",
        "shadow_card_d": "#26B7C7A8",
        "desc": "Tema Matcha: Hijau pastel kalem yang bikin mata adem."
    }

    # 3. Dark Anime (Dark Mode with Sakura & Matcha Accents)
    DARK_ANIME = {
        "primary": "#E8CEDB",          # Sakura Pink tetep ada
        "primary_light": "#C3D3B4",    # Gradasi campur Matcha Green!
        "bg": "#121212",               # Dark background (hampir hitam)
        "card": "#1E1E1E",             # Card sedikit lebih terang
        "text": "#F5F5F5",             # Teks putih
        "border_color": "#333333",     # Border abu-abu gelap
        "shadow_hover": "#80E8CEDB",   # Glow efek pink pas di hover (Cyber-pastel vibe)
        "shadow_default": "#33E8CEDB",
        "shadow_card_h": "#60C3D3B4",  # Glow efek hijau buat card
        "shadow_card_d": "#1AC3D3B4",
        "desc": "Tema Dark: Elegan dengan sentuhan glow Pink Sakura dan Hijau Matcha."
    }

    # 4. Universal Clean (Ramah semua kalangan / Standard App)
    UNIVERSAL_CLEAN = {
        "primary": "#3B82F6",          # Biru standar aplikasi modern
        "primary_light": "#60A5FA",    # Biru muda buat gradasi
        "bg": "#F8F9FA",               # Abu-abu sangat terang (nyaman di mata)
        "card": "#FFFFFF",             # Card putih bersih
        "text": "#1F2937",             # Abu-abu sangat gelap (High contrast)
        "border_color": "#E5E7EB",     # Border tipis netral
        "shadow_hover": "#4D000000",   # Bayangan hitam/abu standar (opacity 30%)
        "shadow_default": "#1A000000", # Bayangan hitam tipis (opacity 10%)
        "shadow_card_h": "#33000000",
        "shadow_card_d": "#0D000000",
        "desc": "Tema Universal: Bersih, profesional, dan nyaman untuk semua orang."
    }

def main(page: ft.Page):
    page.title = "RadarAni Premium UI Tester"
    page.padding = 40
    current_theme = ThemeManager.SAKURA_MATCHA

    # --- FUNGSI HOVER ---
    def button_hover(e):
        is_hover = str(e.data).lower() == "true"
        if is_hover:
            e.control.shadow = ft.BoxShadow(
                spread_radius=1, blur_radius=15,
                color=current_theme["shadow_hover"], offset=ft.Offset(0, 6)
            )
        else:
            e.control.shadow = ft.BoxShadow(
                spread_radius=0, blur_radius=4,
                color=current_theme["shadow_default"], offset=ft.Offset(0, 2)
            )
        e.control.update()

    def card_hover(e):
        is_hover = str(e.data).lower() == "true"
        if is_hover:
            e.control.shadow = ft.BoxShadow(
                spread_radius=0, blur_radius=20,
                color=current_theme["shadow_card_h"], offset=ft.Offset(0, 8)
            )
            e.control.offset = ft.Offset(0, -0.02)
        else:
            e.control.shadow = ft.BoxShadow(
                spread_radius=-1, blur_radius=8,
                color=current_theme["shadow_card_d"], offset=ft.Offset(0, 3)
            )
            e.control.offset = ft.Offset(0, 0)
        e.control.update()

    # --- KOMPONEN UI ---
    header_text = ft.Text("RadarAni Premium", size=32, weight=ft.FontWeight.BOLD)
    desc_text = ft.Text()

    test_button = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.AUTO_AWESOME, size=20),
            ft.Text("Explore Anime", weight=ft.FontWeight.BOLD)
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        width=200, height=50,
        border_radius=25,
        on_hover=button_hover,
        animate=300,
        animate_offset=300,
        offset=ft.Offset(0, 0)
    )

    test_card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Icon(ft.Icons.FAVORITE_ROUNDED),
                ft.Text("Top Picks", weight=ft.FontWeight.BOLD, size=16),
            ]),
            ft.Text("Card ini berubah mengikuti tema yang dipilih. Tes efek hover-nya!", size=13)
        ]),
        padding=25,
        border_radius=16,
        on_hover=card_hover,
        animate=300,
        animate_offset=300,
        offset=ft.Offset(0, 0)
    )

    # --- FUNGSI UPDATE TEMA ---
    def update_ui():
        page.bgcolor = current_theme["bg"]
        header_text.color = current_theme["primary"] if current_theme != ThemeManager.DARK_ANIME else current_theme["text"]
        desc_text.value = current_theme["desc"]
        desc_text.color = current_theme["text"]

        # Penyesuaian warna text di tombol kalau temanya Dark atau Universal (biar tetep kebaca)
        btn_text_color = "#121212" if current_theme == ThemeManager.DARK_ANIME else ("#FFFFFF" if current_theme == ThemeManager.UNIVERSAL_CLEAN else current_theme["text"])

        # Update Button
        test_button.content.controls[0].color = btn_text_color
        test_button.content.controls[1].color = btn_text_color
        test_button.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT,
            colors=[current_theme["primary_light"], current_theme["primary"]]
        )
        test_button.border = ft.Border.all(1, current_theme["border_color"])
        test_button.shadow = ft.BoxShadow(
            spread_radius=0, blur_radius=4, color=current_theme["shadow_default"], offset=ft.Offset(0, 2)
        )

        # Update Card
        test_card.bgcolor = current_theme["card"]
        test_card.content.controls[0].controls[0].color = current_theme["primary"]
        test_card.content.controls[0].controls[1].color = current_theme["text"]
        test_card.content.controls[1].color = current_theme["text"]
        test_card.border = ft.Border.all(1.5, current_theme["border_color"])
        test_card.shadow = ft.BoxShadow(
            spread_radius=-1, blur_radius=8, color=current_theme["shadow_card_d"], offset=ft.Offset(0, 3)
        )

        page.update()

    def change_theme(e):
        nonlocal current_theme
        val = e.control.value
        if val == "1":
            current_theme = ThemeManager.SAKURA_MATCHA
        elif val == "2":
            current_theme = ThemeManager.MATCHA_SAKURA
        elif val == "3":
            current_theme = ThemeManager.DARK_ANIME
        else:
            current_theme = ThemeManager.UNIVERSAL_CLEAN
        update_ui()

    theme_selector = ft.RadioGroup(
        content=ft.Row([
            ft.Radio(value="1", label="Sakura"),
            ft.Radio(value="2", label="Matcha"),
            ft.Radio(value="3", label="Dark"),
            ft.Radio(value="4", label="Universal"),
        ], alignment=ft.MainAxisAlignment.CENTER),
        on_change=change_theme, value="1"
    )

    page.add(
        ft.Column([
            ft.Text("Pilih Tema:", size=16, weight=ft.FontWeight.BOLD, color="#888888"),
            theme_selector,
            ft.Divider(height=40),
            header_text,
            desc_text,
            ft.Container(height=30),
            test_button,
            ft.Container(height=30),
            test_card
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    )

    # Panggil update pertama kali
    update_ui()

ft.run(main)
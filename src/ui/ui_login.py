import flet as ft
import time


class UILogin(ft.Container):
    def __init__(self, page, data_manager, auth_manager, screen_manager):
        super().__init__()
        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager

        self.expand = True
        self.is_register_mode = False

        # ── State Variables ──
        self.txt_username = ft.TextField(
            hint_text="Enter your username",
            hint_style=ft.TextStyle(color="#B8A0A8"),
            bgcolor="#FFF5F8",
            border_color="#F0D0D8",
            focused_border_color="#C07090",
            border_radius=8,
            height=45,
            content_padding=15,
            text_size=13,
            color="#4A1525"
        )
        self.txt_password = ft.TextField(
            hint_text="Enter your password",
            password=True,
            can_reveal_password=True,
            hint_style=ft.TextStyle(color="#B8A0A8"),
            bgcolor="#FFF5F8",
            border_color="#F0D0D8",
            focused_border_color="#C07090",
            border_radius=8,
            height=45,
            content_padding=15,
            text_size=13,
            color="#4A1525"
        )
        self.txt_confirm_pass = ft.TextField(
            hint_text="Confirm your password",
            password=True,
            can_reveal_password=True,
            hint_style=ft.TextStyle(color="#B8A0A8"),
            bgcolor="#FFF5F8",
            border_color="#F0D0D8",
            focused_border_color="#C07090",
            border_radius=8,
            height=45,
            content_padding=15,
            text_size=13,
            color="#4A1525"
        )

        self.content = self._build_ui()

    # ── Helper Methods ──
    def _build_input_group(self, label, input_control):
        return ft.Column(
            spacing=5,
            controls=[
                ft.Text(label, size=11, weight=ft.FontWeight.BOLD, color="#6D3A4A"),
                input_control
            ]
        )

    def _toggle_mode(self, e):
        self.is_register_mode = not self.is_register_mode

        self.txt_username.value = ""
        self.txt_password.value = ""
        self.txt_confirm_pass.value = ""

        self.card_container.content = self._build_card_content()
        self.card_container.height = 550 if self.is_register_mode else 450
        self.card_container.update()

    def _on_btn_hover(self, e):
        e.control.scale = 1.03 if e.data == "true" else 1.0
        e.control.update()

    def _handle_submit(self, e):
        uname = self.txt_username.value.strip()
        pwd = self.txt_password.value

        if not uname or not pwd:
            self._show_snackbar("Please fill in all fields!", ft.Colors.RED_400)
            return

        if self.is_register_mode:
            cpwd = self.txt_confirm_pass.value
            if pwd != cpwd:
                self._show_snackbar("Passwords do not match!", ft.Colors.RED_400)
                return

            sukses = self.auth_manager.register(uname, pwd)

            if sukses:
                self._show_snackbar("Registration successful! Please log in.", ft.Colors.GREEN_500)
                time.sleep(0.5)
                self._toggle_mode(None)
            else:
                self._show_snackbar("Registration failed! Username might already exist.", ft.Colors.RED_400)
        else:
            sukses = self.auth_manager.login(uname, pwd)

            if sukses:
                self._show_snackbar("Login successful!", ft.Colors.GREEN_500)
                self.screen_manager.tampilkan_home()
            else:
                users = self.data_manager._read_json(self.data_manager.users_file) or []
                user_exists = any(u.get("username") == uname for u in users)

                if user_exists:
                    self._show_snackbar("Invalid password! Please try again.", ft.Colors.RED_400)
                else:
                    self._show_snackbar("Account not found. Please sign up if you are new!", ft.Colors.RED_400)

    def _show_snackbar(self, message, color):
        self.my_page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor=color)
        self.my_page.snack_bar.open = True
        self.my_page.update()

    # ── UI Construction ──
    def _build_card_content(self):
        title = "Sign Up" if self.is_register_mode else "Log in"
        toggle_text_1 = "Already have an account? " if self.is_register_mode else "Don't have an account? "
        toggle_text_2 = "Login" if self.is_register_mode else "Sign Up"

        inputs = [
            self._build_input_group("Username", self.txt_username),
            self._build_input_group("Password", self.txt_password)
        ]

        if self.is_register_mode:
            inputs.append(self._build_input_group("Confirm Password", self.txt_confirm_pass))

        submit_btn = ft.Container(
            content=ft.Text(title, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
            alignment=ft.Alignment(0.0, 0.0),
            height=45,
            border_radius=10,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1.0, 0.0),
                end=ft.Alignment(1.0, 0.0),
                colors=["#D86B8C", "#A54A6A"]
            ),
            shadow=ft.BoxShadow(blur_radius=15, color="#60A54A6A", offset=ft.Offset(0, 5)),
            on_hover=self._on_btn_hover,
            on_click=self._handle_submit,
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )

        return ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=25,
            controls=[
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=2,
                    controls=[
                        ft.Text("RadarAni", size=24, weight=ft.FontWeight.BOLD, color="#4A1525"),
                        ft.Text("レーダアニ", size=11, color="#905A6A")
                    ]
                ),
                ft.Column(spacing=15, controls=inputs),
                ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=15,
                    controls=[
                        submit_btn,
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(toggle_text_1, size=12, color="#888888"),
                                ft.GestureDetector(
                                    on_tap=self._toggle_mode,
                                    content=ft.Text(toggle_text_2, size=12, weight=ft.FontWeight.BOLD, color="#D86B8C")
                                )
                            ]
                        )
                    ]
                )
            ]
        )

    def _build_ui(self):
        self.card_container = ft.Container(
            width=400,
            height=450,
            padding=40,
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.WHITE),
            border=ft.border.all(1, ft.Colors.with_opacity(0.5, ft.Colors.WHITE)),
            shadow=ft.BoxShadow(blur_radius=30, color="#15000000", offset=ft.Offset(0, 10)),
            content=self._build_card_content(),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )

        circle_1 = ft.Container(
            width=500, height=500,
            left=-100, top=-100,
            gradient=ft.RadialGradient(
                colors=[ft.Colors.with_opacity(0.4, "#FFA5B5"), ft.Colors.TRANSPARENT]
            )
        )

        circle_2 = ft.Container(
            width=600, height=600,
            right=-150, bottom=-150,
            gradient=ft.RadialGradient(
                colors=[ft.Colors.with_opacity(0.3, "#D86B8C"), ft.Colors.TRANSPARENT]
            )
        )

        return ft.Stack(
            controls=[
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(-1.0, -1.0),
                        end=ft.Alignment(1.0, 1.0),
                        colors=["#E8F2FC", "#FFF0F5", "#FCE4EC"]
                    )
                ),
                circle_1,
                circle_2,
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0.0, 0.0),
                    content=self.card_container
                )
            ]
        )
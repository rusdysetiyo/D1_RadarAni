import flet as ft
import time


class UILogin(ft.Container):
    def __init__(self, page, data_manager, auth_manager, screen_manager, theme):
        super().__init__()
        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager
        self._theme = theme

        self.expand = True
        self.is_register_mode = False

        self._err_username = ft.Text("", size=10, color="#EF4444")
        self._err_password = ft.Text("", size=10, color="#EF4444")
        self._err_confirm = ft.Text("", size=10, color="#EF4444")

        # ── Validator realtime ──
        def _validate_field(field: ft.TextField, err_text: ft.Text, e=None):
            val = field.value or ""
            has_space  = " " in val
            too_short  = 0 < len(val) < 5
            too_long   = len(val) > 30
            empty      = len(val) == 0

            if empty:
                field.border_color = self._theme["border_color"]
                field.focused_border_color = self._theme["error"]
                err_text.value = ""
            elif has_space:
                field.border_color = self._theme["border_color"]
                field.focused_border_color = self._theme["error"]
                err_text.value = "No spaces allowed."
            elif too_short:
                field.border_color = self._theme["border_color"]
                field.focused_border_color = self._theme["error"]
                err_text.value = f"Too short — minimum 5 characters ({len(val)}/5)."
            elif too_long:
                field.border_color = self._theme["border_color"]
                field.focused_border_color = self._theme["error"]
                err_text.value = f"Too long — maximum 30 characters ({len(val)}/30)."
            else:
                field.border_color = self._theme["border_color"]
                field.focused_border_color = self._theme["success"]
                err_text.value = ""

            if field.page: field.update()
            if err_text.page: err_text.update()

        self.txt_username = ft.TextField(
            hint_text="Enter your username (5-30 chars, no spaces)",
            hint_style=ft.TextStyle(color=self._theme["text_muted"]),
            bgcolor=ft.Colors.with_opacity(0.4, self._theme["primary_light"]),            border_color=self._theme["border_color"],
            focused_border_color=self._theme["primary"],
            border_radius=8,
            height=45,
            content_padding=15,
            text_size=13,
            color=self._theme["text_secondary"],
            on_change=lambda e: _validate_field(self.txt_username, self._err_username, e),
        )
        self.txt_password = ft.TextField(
            hint_text="Enter your password (5-30 chars, no spaces)",
            password=True,
            can_reveal_password=True,
            hint_style=ft.TextStyle(color=self._theme["text_muted"]),
            bgcolor=ft.Colors.with_opacity(0.4, self._theme["primary_light"]),
            border_color=self._theme["border_color"],
            focused_border_color=self._theme["primary"],
            border_radius=8,
            height=45,
            content_padding=15,
            text_size=13,
            color=self._theme["text_secondary"],
            on_change=lambda e: _validate_field(self.txt_password, self._err_password, e),
        )
        self.txt_confirm_pass = ft.TextField(
            hint_text="Confirm your password",
            password=True,
            can_reveal_password=True,
            hint_style=ft.TextStyle(color=self._theme["text_muted"]),
            bgcolor=ft.Colors.with_opacity(0.4, self._theme["primary_light"]),
            border_color=self._theme["border_color"],
            focused_border_color=self._theme["primary"],
            border_radius=8,
            height=45,
            content_padding=15,
            text_size=13,
            color=self._theme["text_secondary"],
            on_change=lambda e: _validate_field(self.txt_confirm_pass, self._err_confirm, e),
        )

        self._validate_field = _validate_field
        self.content = self._build_ui()

    def _is_valid_input(self, val: str) -> bool:
        return 5 <= len(val) <= 30 and " " not in val

    # ── Helper Methods ──
    def _build_input_group(self, label, input_control, err_text: ft.Text):
        return ft.Column(
            spacing=3,
            controls=[
                ft.Text(label, size=11, weight=ft.FontWeight.BOLD, color=self._theme["text_secondary"]),
                input_control,
                err_text,   # ← teks error di bawah field
            ]
        )

    def _toggle_mode(self, e):
        self.is_register_mode = not self.is_register_mode
        for field in [self.txt_username, self.txt_password, self.txt_confirm_pass]:
            field.value = ""
            field.border_color = self._theme["border_color"]
            field.focused_border_color = self._theme["primary"]
        self.card_container.content = self._build_card_content()
        self.card_container.height = 550 if self.is_register_mode else 450
        self.card_container.update()

    def _on_btn_hover(self, e):
        e.control.scale = 1.03 if e.data == "true" else 1.0
        e.control.update()

    def _handle_submit(self, e):
        # Ambil value as-is (case sensitive)
        uname = self.txt_username.value or ""
        pwd = self.txt_password.value or ""

        # Validasi format — tidak di-strip, tidak di-lower
        if not self._is_valid_input(uname) or not self._is_valid_input(pwd):
            self._validate_field(self.txt_username, self._err_username)
            self._validate_field(self.txt_password, self._err_password)
            self._show_snackbar("Invalid username or password!", ft.Colors.RED_400)
            return

        if self.is_register_mode:
            cpwd = self.txt_confirm_pass.value or ""
            if pwd != cpwd:   # case sensitive
                self._show_snackbar("Passwords do not match!", ft.Colors.RED_400)
                return

            sukses = self.auth_manager.register(uname, pwd)  # kirim as-is
            if sukses:
                self._show_snackbar("Registration successful! Please log in.", ft.Colors.GREEN_500)
                import time; time.sleep(0.5)
                self._toggle_mode(None)
            else:
                self._show_snackbar("Username already exists!", ft.Colors.RED_400)
        else:
            sukses = self.auth_manager.login(uname, pwd)  # kirim as-is, case sensitive di backend
            if sukses:
                self._show_snackbar("Login successful!", ft.Colors.GREEN_500)
                self.screen_manager.tampilkan_home()
            else:
                users = self.data_manager._read_json(self.data_manager.users_file) or []
                # Cek username case sensitive
                user_exists = any(u.get("username") == uname for u in users)
                if user_exists:
                    self._show_snackbar("Invalid password! Please try again.", ft.Colors.RED_400)
                else:
                    self._show_snackbar("Account not found. Please sign up!", ft.Colors.RED_400)

    def _show_snackbar(self, pesan: str, warna: str):
        snack = ft.SnackBar(content=ft.Text(pesan), bgcolor=warna)
        self.my_page.overlay.append(snack)
        snack.open = True
        self.my_page.update()

    # ── UI Construction ──
    def _build_card_content(self):
        title = "Sign Up" if self.is_register_mode else "Log in"
        toggle_text_1 = "Already have an account? " if self.is_register_mode else "Don't have an account? "
        toggle_text_2 = "Login" if self.is_register_mode else "Sign Up"
    
        inputs = [
            self._build_input_group("Username", self.txt_username, self._err_username),
            self._build_input_group("Password", self.txt_password, self._err_password),
        ]

        if self.is_register_mode:
            inputs.append(self._build_input_group("Confirm Password", self.txt_confirm_pass, self._err_confirm))

        submit_btn = ft.Container(
            content=ft.Text(title, color=self._theme["card"], weight=ft.FontWeight.BOLD),
            alignment=ft.Alignment(0.0, 0.0),
            height=45,
            border_radius=10,
            bgcolor=self._theme["primary"],
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
                        ft.Text("RadarAni", size=24, weight=ft.FontWeight.BOLD, color=self._theme["text_main"]),
                        ft.Text("レーダアニ", size=11, color=self._theme["text_main"])
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
                                ft.Text(toggle_text_1, size=12, color=self._theme["text_muted"]),
                                ft.GestureDetector(
                                    on_tap=self._toggle_mode,
                                    content=ft.Text(toggle_text_2, size=12, weight=ft.FontWeight.BOLD, color=self._theme["text_secondary"])
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
            bgcolor=ft.Colors.with_opacity(0.85, self._theme["card"]),
            border=ft.border.all(1, ft.Colors.with_opacity(0.5, self._theme["border_color"])),
            shadow=ft.BoxShadow(blur_radius=30, color=self._theme["primary_light"], offset=ft.Offset(0, 10)),
            content=self._build_card_content(),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT)
        )

        circle_1 = ft.Container(
            width=500, height=500,
            left=-100, top=-100,
            gradient=ft.RadialGradient(
                colors=[ft.Colors.with_opacity(0.4, self._theme["primary"]), ft.Colors.TRANSPARENT]
            )
        )

        circle_2 = ft.Container(
            width=600, height=600,
            right=-150, bottom=-150,
            gradient=ft.RadialGradient(
                colors=[ft.Colors.with_opacity(0.3, self._theme["primary_light"]), ft.Colors.TRANSPARENT]
            )
        )

        return ft.Stack(
            controls=[
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(-1.0, -1.0),
                        end=ft.Alignment(1.0, 1.0),
                        colors=[self._theme["bg"], self._theme["bg_secondary"]]
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
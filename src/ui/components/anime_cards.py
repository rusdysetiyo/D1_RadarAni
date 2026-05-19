import flet as ft
import os
import random
from src.ui.components.icons import _sakura_icon_svg

COMP_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(COMP_DIR, "..", "..", ".."))

class AnimeCardHome(ft.Container):
    def __init__(self, anime: dict, skor_global, skor_personal, theme, is_favorite=False, on_click_callback=None):
        super().__init__()
        self.anime = anime
        self.is_favorite = is_favorite
        self.theme = theme
        self._on_click_cb = on_click_callback

        self.width = 120
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=[self.theme["card"], self.theme["bg"]]
        )
        self.border = ft.Border.all(1, self.theme["border_color"])
        self.border_radius = ft.border_radius.only(top_left=15, bottom_right=15, top_right=4, bottom_left=4)
        self.clip_behavior = ft.ClipBehavior.ANTI_ALIAS
        self.margin = ft.padding.only(left=6, right=6, top=10, bottom=20)

        self.base_shadow = ft.BoxShadow(
            blur_radius=8,
            color=ft.Colors.with_opacity(0.08, self.theme["text_main"]),
            offset=ft.Offset(0, 4)
        )
        self.shadow = [self.base_shadow]

        self.on_click = lambda _: self._on_click_cb(anime.get("anime_id", "")) if on_click_callback else None
        self.on_hover = self._on_hover
        self.animate = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)
        self.rotate = ft.Rotate(angle=random.uniform(-0.015, 0.015))

        is_rated = skor_personal is not None
        pill_bg = self.theme["pill_rated"] if is_rated else ft.Colors.with_opacity(0.85, self.theme["text_muted"])
        pill_txt = f"★ {skor_personal:.1f}" if is_rated else "not rated"
        pill_color = self.theme["card"]

        self._status_pill = ft.Container(
            content=ft.Text(pill_txt, size=8, color=pill_color, weight=ft.FontWeight.W_800),
            bgcolor=pill_bg,
            border_radius=ft.border_radius.only(top_left=10, bottom_right=10),
            padding=ft.padding.symmetric(horizontal=8, vertical=2),
            top=6, right=6, opacity=1.0,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT)
        )

        self._fav_icon = ft.Container(
            content=ft.Image(src=_sakura_icon_svg(), width=22, height=22),
            top=-30, right=6, opacity=0,
            shadow=ft.BoxShadow(blur_radius=8, spread_radius=1, color="#80000000", offset=ft.Offset(0, 2)),
            animate_position=ft.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            animate_rotation=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            rotate=ft.Rotate(angle=-1)
        )

        genres = anime.get("genre", [])[:3]
        sg_str = (f"★ {skor_global:.1f}  ·  {anime.get('episodes', '?')} eps" if skor_global else f"{anime.get('episodes', '?')} eps")

        self._overlay = ft.Container(
            width=120, height=162,
            bgcolor=self.theme["overlay_bg"],
            border_radius=ft.border_radius.only(top_left=15, top_right=4),
            padding=8,
            content=ft.Column(
                controls=[
                    ft.Container(expand=True),
                    ft.Text(anime.get("title", ""), size=9, color="#FFFFFF", weight=ft.FontWeight.BOLD, max_lines=2),
                    ft.Text(sg_str, size=8, color=self.theme["overlay_text"]),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(g, size=7, color=self.theme["pill_text"], weight=ft.FontWeight.W_800),
                                bgcolor=ft.Colors.with_opacity(0.85, self.theme["pill_genre_bg"]),
                                border_radius=ft.border_radius.only(top_left=6, bottom_right=6),
                                padding=ft.padding.symmetric(horizontal=6, vertical=2),
                            ) for g in genres
                        ], spacing=3, run_spacing=2, wrap=True,
                    ),
                ], spacing=3,
            ),
            visible=False,
        )

        thumb = anime.get("cover_path", "")
        poster_path = os.path.abspath(os.path.join(ROOT_DIR, thumb)) if thumb else ""

        poster = ft.Container(
            width=120, height=162,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            border_radius=ft.border_radius.only(top_left=15, top_right=4),
            content=ft.Image(
                src=poster_path if (poster_path and os.path.exists(poster_path)) else "",
                width=120, height=162, fit="cover",
            ) if (poster_path and os.path.exists(poster_path)) else ft.Icon(ft.Icons.PHOTO, color=self.theme["text_muted"])
        )

        info = ft.Container(
            padding=ft.padding.only(left=7, right=7, top=4, bottom=5),
            content=ft.Column(
                controls=[
                    ft.Text(
                        anime.get("title", "—"), size=9, color=self.theme["text_main"],
                        weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.Icon(ft.Icons.LANGUAGE, size=9, color=self.theme["text_secondary"]),
                            ft.Text(f"{skor_global:.1f}" if skor_global else "—", size=8,
                                    color=self.theme["accent_star"], weight=ft.FontWeight.BOLD),
                            ft.Text("·", size=8, color=self.theme["border_color"]),
                            ft.Text(f"{anime.get('episodes', '?')} eps", size=8,
                                    color=self.theme["text_secondary"]),
                        ], spacing=3, alignment=ft.MainAxisAlignment.CENTER
                    ),
                ], spacing=2, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

        self.content = ft.Column(
            controls=[
                ft.Stack(controls=[poster, self._overlay, self._status_pill, self._fav_icon], width=120, height=162),
                info,
            ], spacing=0,
        )

    def _on_hover(self, e):
        is_hovered = str(e.data).lower() == "true"
        self._overlay.visible = is_hovered
        if is_hovered:
            self._status_pill.opacity = 0
            self._fav_icon.top = 6
            self._fav_icon.opacity = 1.0 if self.is_favorite else 0.4
            self._fav_icon.rotate.angle = 0
            self.rotate = ft.Rotate(angle=0.02)

            glow_shadow = ft.BoxShadow(
                blur_radius=25, spread_radius=1,
                color=ft.Colors.with_opacity(0.5, self.theme["primary"])
            )
            self.shadow = [glow_shadow]
        else:
            self._status_pill.opacity = 1.0
            self._fav_icon.top = -30
            self._fav_icon.opacity = 0
            self._fav_icon.rotate.angle = -1
            self.rotate = ft.Rotate(angle=0)
            self.shadow = [self.base_shadow]

        self.border = ft.Border.all(1.5 if is_hovered else 1,
                                    self.theme["card_hover_border"] if is_hovered else self.theme["border_color"])
        self.scale = 1.03 if is_hovered else 1.0
        self.update()


class AnimeCardKatalog(ft.Container):
    def __init__(self, anime: dict, skor_global, skor_personal, theme, is_favorite=False, on_click_callback=None):
        super().__init__()
        self.anime = anime
        self.theme = theme
        self.is_favorite = is_favorite
        self._on_click_cb = on_click_callback

        self.width = 140
        self.height = 210
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=[self.theme["card"], self.theme["bg_secondary"]]
        )
        self.border = ft.Border.all(1, self.theme["border_color"])
        self.border_radius = 10
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE
        self.on_click = lambda _: self._on_click_cb(anime.get("anime_id", "")) if on_click_callback else None
        self.on_hover = self._on_hover
        self.scale = 1.0
        self.shadow = None
        self.animate = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)
        self.animate_scale = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)

        is_rated = skor_personal is not None
        if is_rated:
            pill_bg = self.theme["pill_rated"]
            pill_txt = f"★ {skor_personal}"
            pill_color = self.theme["pill_text"]
        else:
            pill_bg = ft.Colors.with_opacity(0.85, self.theme["text_muted"])
            pill_txt = "unrated"
            pill_color = self.theme["card"]

        self._status_pill = ft.Container(
            content=ft.Text(pill_txt, size=9, color=pill_color, weight=ft.FontWeight.BOLD),
            bgcolor=pill_bg,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=6, vertical=3),
            top=8, right=8, opacity=1.0,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

        self._fav_icon = ft.Container(
            content=ft.Image(src=_sakura_icon_svg(), width=24, height=24),
            top=8, right=8, opacity=0, offset=ft.Offset(0, -1),
            rotate=ft.Rotate(angle=-1, alignment=ft.Alignment(0, 0)),
            animate_offset=ft.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            animate_rotation=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )

        thumb = anime.get("cover_path", "")
        poster_path = os.path.abspath(os.path.join(ROOT_DIR, thumb)) if thumb else ""

        if poster_path and os.path.exists(poster_path):
            poster = ft.Image(src=poster_path, width=140, height=162, fit=ft.BoxFit.COVER, border_radius=10)
        else:
            poster = ft.Container(
                width=140, height=162, bgcolor=self.theme["bg_secondary"],
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
                content=ft.Text(anime.get("title", "")[:14], size=9, color=self.theme["text_muted"], text_align=ft.TextAlign.CENTER),
                alignment=ft.Alignment.CENTER,
            )

        genres = anime.get("genre", [])[:3]
        sg_str = (f"★ {skor_global:.1f}  ·  {anime.get('episodes', '?')} eps" if skor_global else f"{anime.get('episodes', '?')} eps")

        self._overlay = ft.Container(
            width=140, height=162,
            bgcolor=self.theme["overlay_bg"],
            border_radius=10, padding=8,
            content=ft.Column(
                controls=[
                    ft.Container(expand=True),
                    ft.Text(anime.get("title", ""), size=10, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, max_lines=2),
                    ft.Text(sg_str, size=9, color="#F0F0F0", weight=ft.FontWeight.W_600),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(g, size=8, color=self.theme["pill_text"], weight=ft.FontWeight.BOLD),
                                bgcolor=ft.Colors.with_opacity(0.85, self.theme["pill_genre_bg"]),
                                border_radius=8, padding=ft.padding.symmetric(horizontal=6, vertical=1),
                            ) for g in genres
                        ], spacing=3, run_spacing=2, wrap=True,
                    ),
                ], spacing=4,
            ),
            visible=False,
        )

        info = ft.Container(
            padding=ft.padding.only(left=7, right=7, top=4, bottom=5),
            content=ft.Column(
                controls=[
                    ft.Text(anime.get("title", "—"), size=10, color=self.theme["text_main"],
                            weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row(controls=[
                        ft.Icon(ft.Icons.LANGUAGE, size=9, color=self.theme["text_secondary"]),
                        ft.Text(f"{skor_global:.1f}" if skor_global else "—", size=9, color=self.theme["accent_star"], weight=ft.FontWeight.BOLD),
                        ft.Text("·", size=8, color=self.theme["border_color"]),
                        ft.Text(f"{anime.get('episodes', '?')} eps", size=8, color=self.theme["text_secondary"]),
                    ], spacing=3),
                ], spacing=2, tight=True,
            ),
        )

        self.content = ft.Column(controls=[ft.Stack(controls=[poster, self._overlay, self._status_pill, self._fav_icon], width=140, height=162), info], spacing=0)

    def _on_hover(self, e):
        is_hovered = str(e.data).lower() == "true"
        self._overlay.visible = is_hovered
        if is_hovered:
            self._status_pill.opacity = 0
            self._fav_icon.opacity = 1.0 if self.is_favorite else 0.4
            self._fav_icon.offset = ft.Offset(0, 0)
            self._fav_icon.rotate = ft.Rotate(angle=0, alignment=ft.Alignment(0, 0))
        else:
            self._status_pill.opacity = 1.0
            self._fav_icon.opacity = 0
            self._fav_icon.offset = ft.Offset(0, -1)
            self._fav_icon.rotate = ft.Rotate(angle=-1, alignment=ft.Alignment(0, 0))

        self.border = ft.Border.all(1.5 if is_hovered else 1, self.theme["card_hover_border"] if is_hovered else self.theme["border_color"])
        self.scale = 1.03 if is_hovered else 1.0
        self.shadow = ft.BoxShadow(
            spread_radius=1, blur_radius=12,
            color=ft.Colors.with_opacity(0.3, self.theme["card_hover_border"]),
            offset=ft.Offset(0, 4),
        ) if is_hovered else None

        self._status_pill.update()
        self._fav_icon.update()
        self.update()

class AnimeListItem(ft.Container):
    def __init__(self, anime: dict, skor_global, skor_personal, theme, is_favorite=False, on_click_callback=None):
        super().__init__()
        self.theme = theme
        self._on_click_cb = on_click_callback

        self.gradient = ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT,
            end=ft.Alignment.CENTER_RIGHT,
            colors=[self.theme["card"], self.theme["bg_secondary"]]
        )
        self.border = ft.Border.all(1, self.theme["border_color"])
        self.border_radius = 10
        self.padding = ft.padding.symmetric(horizontal=14, vertical=10)
        self.on_click = lambda _: on_click_callback(anime.get("anime_id", "")) if on_click_callback else None
        self.on_hover = self._on_hover
        self.animate = ft.Animation(duration=120, curve=ft.AnimationCurve.EASE_IN_OUT)

        is_rated = skor_personal is not None

        thumb = anime.get("cover_path", "")
        poster_path = os.path.abspath(os.path.join(ROOT_DIR, thumb)) if thumb else ""

        genres = anime.get("genre", [])[:3]

        if poster_path and os.path.exists(poster_path):
            poster = ft.Image(
                src=poster_path, width=48, height=64,
                fit=ft.BoxFit.COVER, border_radius=6,
            )
        else:
            poster = ft.Container(
                width=48, height=64, bgcolor=self.theme["bg_secondary"],
                border_radius=6,
                content=ft.Text("IMG", size=8, color=self.theme["text_muted"]),
                alignment=ft.Alignment.CENTER,
            )

        genre_chips = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(g, size=9, color=self.theme["text_secondary"]),
                    bgcolor=self.theme["bg_secondary"],
                    border=ft.Border.all(1, self.theme["border_color"]),
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                ) for g in genres
            ], spacing=4,
        )

        sp_txt = f"you: {skor_personal:.1f}" if is_rated else "you: N/A"
        sp_col = self.theme["primary"] if is_rated else self.theme["text_muted"]

        if is_favorite:
            rated_badge = ft.Container(
                content=ft.Row([
                    ft.Image(src=_sakura_icon_svg(), width=10, height=10, color=ft.Colors.WHITE),
                    ft.Text("FAVORITE", size=8, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                ], spacing=4),
                bgcolor=self.theme["primary"], border_radius=8,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
            )
        else:
            rated_badge = ft.Container(
                content=ft.Text(
                    f"★ {skor_personal:.1f}" if is_rated else "not rated",
                    size=8, color=self.theme["pill_text"] if is_rated else self.theme["card"],
                    weight=ft.FontWeight.BOLD
                ),
                bgcolor=self.theme["pill_rated"] if is_rated else ft.Colors.with_opacity(0.85, self.theme["text_muted"]),
                border_radius=8, padding=ft.padding.symmetric(horizontal=6, vertical=2),
            )

        self.content = ft.Row(
            controls=[
                poster,
                ft.Column(
                    controls=[
                        ft.Row(controls=[
                            ft.Text(anime.get("title", "—"), size=13, color=self.theme["text_main"],
                                    weight=ft.FontWeight.BOLD, expand=True,
                                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            rated_badge,
                        ]),
                        genre_chips,
                        ft.Row(controls=[
                            ft.Text(f"★ {skor_global:.1f}" if skor_global else "★ —",
                                    size=11, color=self.theme["accent_star"], weight=ft.FontWeight.BOLD),
                            ft.Text("·", size=11, color=self.theme["text_muted"]),
                            ft.Text(sp_txt, size=11, color=sp_col, weight=ft.FontWeight.BOLD),
                            ft.Text("·", size=11, color=self.theme["text_muted"]),
                            ft.Text(f"{anime.get('episodes', '?')} eps", size=11, color=self.theme["text_muted"]),
                        ], spacing=5),
                    ], spacing=5, tight=True, expand=True,
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=self.theme["text_muted"], size=18),
            ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _on_hover(self, e):
        is_hovered = str(e.data).lower() == "true"
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT, end=ft.Alignment.CENTER_RIGHT,
            colors=[self.theme["bg_secondary"], self.theme["primary_light"]] if is_hovered else [self.theme["card"], self.theme["bg_secondary"]]
        )
        self.border = ft.Border.all(1.5 if is_hovered else 1, self.theme["card_hover_border"] if is_hovered else self.theme["border_color"])
        self.update()
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap, QColor


class AnimeCard(QWidget):
    """
    Card anime dengan hover overlay yang berfungsi di PyQt5.
    Teknik: overlay QLabel ditaruh sebagai child widget,
    visibility-nya dikontrol via enterEvent/leaveEvent.
    """
    diklik = pyqtSignal(str)

    def __init__(self, anime: dict, skor_global, skor_personal):
        super().__init__()
        self.anime_id = anime.get("anime_id", "")
        self.setAttribute(Qt.WA_Hover, True)  # ← WAJIB untuk QSS :hover
        self.setFixedSize(140, 220)
        self._bangun_ui(anime, skor_global, skor_personal)
        self._bangun_overlay(anime, skor_global)
        self.setCursor(Qt.PointingHandCursor)

    # ── Build ──────────────────────────────────

    def _bangun_ui(self, anime, skor_global, skor_personal):
        self.setObjectName("animeCard")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Poster
        self._poster = QLabel()
        self._poster.setFixedHeight(165)
        self._poster.setAlignment(Qt.AlignCenter)
        self._poster.setScaledContents(True)
        self._poster.setStyleSheet(
            "background-color: #EDE0E8;"
            "border-radius: 9px 9px 0 0;"
        )

        thumb_path = anime.get("thumbnail_path", "")
        if thumb_path:
            px = QPixmap(thumb_path)
            if not px.isNull():
                self._poster.setPixmap(px)
            else:
                self._set_poster_placeholder(anime.get("title", ""))
        else:
            self._set_poster_placeholder(anime.get("title", ""))

        layout.addWidget(self._poster)

        # Info bawah
        info = QWidget()
        info.setStyleSheet("background: transparent;")
        info_layout = QVBoxLayout(info)
        info_layout.setContentsMargins(6, 4, 6, 5)
        info_layout.setSpacing(2)

        title = QLabel(anime.get("title", "—"))
        title.setObjectName("cardTitle")
        title.setWordWrap(False)

        score_row = QHBoxLayout()
        score_row.setSpacing(4)
        score_row.setContentsMargins(0, 0, 0, 0)

        g = QLabel(f"★ {skor_global:.1f}" if skor_global else "★ —")
        g.setObjectName("scoreGlobal")
        sep = QLabel("·")
        sep.setStyleSheet("color:#C0A0B0; font-size:9px;")

        if skor_personal is not None:
            p = QLabel(f"you: {skor_personal:.1f}")
            p.setObjectName("scorePersonal")
        else:
            p = QLabel("you: N/A")
            p.setObjectName("scoreNA")

        score_row.addWidget(g)
        score_row.addWidget(sep)
        score_row.addWidget(p)
        score_row.addStretch()

        info_layout.addWidget(title)
        info_layout.addLayout(score_row)
        layout.addWidget(info)

        # Rated badge (pojok kanan atas)
        is_rated = skor_personal is not None
        badge = QLabel("★ rated" if is_rated else "not rated")
        badge.setObjectName("ratedBadge" if is_rated else "unratedBadge")
        badge.setParent(self)  # overlay, bukan di layout
        badge.adjustSize()
        badge.move(self.width() - badge.width() - 6, 6)
        badge.raise_()

    def _bangun_overlay(self, anime, skor_global):
        """
        Overlay gelap yang muncul saat hover.
        Ditaruh sebagai child langsung, BUKAN di layout.
        """
        self._overlay = QWidget(self)
        self._overlay.setGeometry(0, 0, 140, 165)  # cover poster saja
        self._overlay.setStyleSheet(
            "background-color: rgba(30, 15, 25, 0.82);"
            "border-radius: 9px 9px 0 0;"
        )
        self._overlay.hide()

        # Konten overlay
        ol_layout = QVBoxLayout(self._overlay)
        ol_layout.setContentsMargins(8, 8, 8, 8)
        ol_layout.setSpacing(4)
        ol_layout.addStretch()

        # Judul
        ol_title = QLabel(anime.get("title", "—"))
        ol_title.setWordWrap(True)
        ol_title.setStyleSheet(
            "color: #FFFFFF; font-size: 10px; font-weight: 600;"
            "background: transparent;"
        )
        ol_layout.addWidget(ol_title)

        # Meta: rating + episode
        eps = anime.get("episodes", "?")
        btype = anime.get("broadcast_type", "TV")
        meta = QLabel(f"★ {skor_global:.1f}  ·  {eps} eps  ·  {btype}"
                      if skor_global else f"{eps} eps · {btype}")
        meta.setStyleSheet(
            "color: #D4A8BC; font-size: 9px; background: transparent;"
        )
        ol_layout.addWidget(meta)

        # Genre tags
        genres = anime.get("genre", [])[:3]  # maks 3 genre
        if genres:
            tag_row = QHBoxLayout()
            tag_row.setSpacing(3)
            tag_row.setContentsMargins(0, 0, 0, 0)
            for g in genres:
                tag = QLabel(g)
                tag.setStyleSheet(
                    "background-color: rgba(192, 112, 144, 0.55);"
                    "color: #F5D0E0;"
                    "font-size: 8px;"
                    "border-radius: 8px;"
                    "padding: 1px 6px;"
                )
                tag_row.addWidget(tag)
            tag_row.addStretch()
            ol_layout.addLayout(tag_row)

    # ── Events ────────────────────────────────

    def enterEvent(self, event):
        self._overlay.show()
        self._overlay.raise_()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._overlay.hide()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.diklik.emit(self.anime_id)
        super().mousePressEvent(event)

    def resizeEvent(self, event):
        # Pastikan overlay ikut resize kalau card di-resize
        self._overlay.setGeometry(0, 0, self.width(), 165)
        super().resizeEvent(event)

    # ── Helpers ───────────────────────────────

    def _set_poster_placeholder(self, title: str):
        self._poster.setText(title[:15])
        self._poster.setStyleSheet(
            self._poster.styleSheet() +
            "font-size: 9px; color: #A08090; padding: 4px;"
        )
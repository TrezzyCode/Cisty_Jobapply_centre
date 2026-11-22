import os
import sys
import math
import time
import json
import base64
import threading
import webbrowser
import shutil
from datetime import datetime
from email.message import EmailMessage
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from PySide6.QtCore import (
    Qt, Signal, Property, QTimer, QEasingCurve, QPropertyAnimation, QRectF, QPointF
)
from PySide6.QtGui import (
    QColor, QPainter, QLinearGradient, QIcon, QPixmap, QPen, QPalette,
    QPainterPath, QTransform
)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFrame, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget, QLineEdit,
    QComboBox, QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
    QTabWidget, QPlainTextEdit, QCheckBox, QFileDialog, QMessageBox,
    QScrollArea, QFormLayout, QButtonGroup, QSizePolicy,
    QGraphicsOpacityEffect, QAbstractItemView
)

from main import (
    APP_DIR, RESOURCE_DIR, DATA_DIR, TOKEN_PATH, TRANSIT_LINES, LINE_STATIONS,
    LINE_CHOICES, db, load_settings, save_settings, import_excel
)


COLORS = {
    'ink': '#2B2724', 'muted': '#716A63', 'accent': '#B75334',
    'accent_dark': '#984329', 'accent_soft': '#EED8CB', 'green': '#4B6F5C',
    'line': '#D9D0C5', 'surface': '#FFFCF8', 'glass': '#F8F3EC',
    'soft': '#F2ECE4', 'danger': '#A8433B'
}


def reduce_motion_enabled():
    """Respect the explicit dev override and Windows' client-animation setting."""
    override = os.environ.get('QT_REDUCE_MOTION', '').strip().lower()
    if override in {'1', 'true', 'yes', 'on'}:
        return True
    if override in {'0', 'false', 'no', 'off'}:
        return False
    if sys.platform == 'win32':
        try:
            import ctypes
            animations_enabled = ctypes.c_int(1)
            spi_get_client_area_animation = 0x1042
            ctypes.windll.user32.SystemParametersInfoW(
                spi_get_client_area_animation, 0,
                ctypes.byref(animations_enabled), 0
            )
            return not bool(animations_enabled.value)
        except Exception:
            pass
    return False


def cisty_mark_path(rect):
    """Return the approved squircle-C silhouette mapped into ``rect``."""
    source = QPainterPath(QPointF(800, 120))
    source.lineTo(320, 120)
    source.cubicTo(190, 120, 120, 190, 120, 320)
    source.lineTo(120, 680)
    source.cubicTo(120, 810, 190, 880, 320, 880)
    source.lineTo(800, 880)
    source.cubicTo(855, 880, 895, 850, 910, 805)
    source.lineTo(840, 650)
    source.cubicTo(825, 700, 800, 730, 740, 730)
    source.lineTo(350, 730)
    source.cubicTo(300, 730, 270, 700, 270, 650)
    source.lineTo(270, 350)
    source.cubicTo(270, 300, 300, 270, 350, 270)
    source.lineTo(740, 270)
    source.cubicTo(800, 270, 825, 300, 840, 350)
    source.lineTo(910, 195)
    source.cubicTo(895, 150, 855, 120, 800, 120)
    source.closeSubpath()
    transform = QTransform()
    transform.translate(rect.left(), rect.top())
    transform.scale(rect.width() / 1000.0, rect.height() / 1000.0)
    return transform.map(source)


APP_QSS = f"""
* {{ font-family: "Segoe UI Variable Text", "Segoe UI"; font-size: 13px; color: {COLORS['ink']}; }}
QWidget#root {{ background: transparent; }}
QFrame#glass, QFrame#surface {{
    border: 1px solid {COLORS['line']}; border-radius: 18px;
    background: {COLORS['glass']};
}}
QFrame#surface {{ background: {COLORS['surface']}; border-color: {COLORS['line']}; }}
QFrame#profileCard {{ background: #F5ECE4; border: 1px solid #DECFC2; border-radius: 16px; }}
QLabel#title {{ font-size: 26px; font-weight: 600; }}
QLabel#pageTitle {{ font-size: 23px; font-weight: 600; }}
QLabel#sectionTitle {{ font-size: 18px; font-weight: 600; }}
QLabel#muted {{ color: {COLORS['muted']}; }}
QLabel#metric {{ font-size: 21px; font-weight: 600; font-variant-numeric: tabular-nums; }}
QLabel#success {{ color: {COLORS['green']}; font-weight: 600; }}
QLabel#profileName {{ font-size: 18px; font-weight: 600; color: {COLORS['ink']}; }}
QPushButton {{
    min-height: 36px; padding: 0 14px; border-radius: 10px;
    border: 1px solid {COLORS['line']}; background: #FFFDF9;
    font-weight: 500;
}}
QPushButton:hover {{ background: #FFF9F3; border-color: #BBAA9C; }}
QPushButton:pressed {{ background: #F0E3D9; padding-top: 2px; }}
QPushButton:disabled {{ color: #9B938C; background: #EEE9E3; }}
QPushButton#primary {{ color: white; background: {COLORS['accent']}; border: none; min-height: 40px; }}
QPushButton#primary:hover {{ background: {COLORS['accent_dark']}; }}
QPushButton#successButton {{ color: white; background: {COLORS['green']}; border: none; min-height: 38px; }}
QPushButton#quiet {{ color: {COLORS['accent_dark']}; background: transparent; border: none; padding: 0 8px; }}
QPushButton#quiet:hover {{ background: #EADDD2; }}
QPushButton#nav {{
    min-height: 42px; text-align: left; padding-left: 13px; border: none;
    background: transparent; color: #514A44; font-weight: 500;
}}
QPushButton#nav:hover {{ background: #F1E8DF; }}
QPushButton#nav:checked {{ color: #342B25; background: {COLORS['accent_soft']}; border: 1px solid #DEC0AF; }}
QLineEdit, QComboBox, QPlainTextEdit {{
    color: {COLORS['ink']}; background: #FFFDF9; border: 1px solid {COLORS['line']};
    border-radius: 9px; padding: 7px; selection-background-color: {COLORS['accent_soft']};
    selection-color: {COLORS['ink']};
}}
QLineEdit:focus, QComboBox:focus, QPlainTextEdit:focus {{ border: 2px solid {COLORS['accent']}; padding: 6px; }}
QComboBox {{ min-height: 34px; padding-right: 26px; }}
QComboBox::drop-down {{ border: none; width: 26px; }}
QComboBox QAbstractItemView {{
    color: {COLORS['ink']}; background: #FFFDF9; alternate-background-color: #FAF4ED;
    border: 1px solid #CFC4B8; border-radius: 10px; padding: 6px;
    selection-background-color: {COLORS['accent_soft']}; selection-color: {COLORS['ink']};
    outline: 0; min-width: 180px;
}}
QComboBox QAbstractItemView::item {{ min-height: 32px; padding: 3px 9px; }}
QTableWidget {{
    color: {COLORS['ink']}; background: {COLORS['surface']}; alternate-background-color: #FAF6F0;
    border: 1px solid {COLORS['line']}; border-radius: 12px; gridline-color: #E8E0D7;
    outline: 0;
}}
QTableWidget::item {{ padding: 8px; border-bottom: 1px solid #E9E1D8; }}
QTableWidget::item:selected {{ color: {COLORS['ink']}; background: {COLORS['accent_soft']}; }}
QHeaderView::section {{
    color: #504942; background: #F4EEE7; border: none; border-right: 1px solid #E1D8CE;
    border-bottom: 1px solid #D5CAC0; padding: 10px 8px; font-weight: 600;
}}
QTabWidget::pane {{ color: {COLORS['ink']}; border: 1px solid {COLORS['line']}; border-radius: 12px; background: {COLORS['surface']}; top: -1px; }}
QTabBar::tab {{ color: #685F57; min-height: 36px; min-width: 84px; padding: 0 10px; background: transparent; font-weight: 500; }}
QTabBar::tab:selected {{ color: {COLORS['accent_dark']}; border-bottom: 2px solid {COLORS['accent']}; background: #FFF9F4; }}
QScrollArea {{ border: none; background: {COLORS['surface']}; }}
QScrollArea > QWidget > QWidget, QWidget#panelBody {{ color: {COLORS['ink']}; background: {COLORS['surface']}; }}
QCheckBox {{ color: {COLORS['ink']}; spacing: 8px; }}
QCheckBox::indicator {{ width: 17px; height: 17px; border: 1px solid #BFB3A8; border-radius: 5px; background: #FFFDF9; }}
QCheckBox::indicator:checked {{ background: {COLORS['accent']}; border-color: {COLORS['accent']}; }}
QScrollBar:vertical {{
    width: 14px; margin: 4px 2px; border: none; background: transparent;
}}
QScrollBar::handle:vertical {{
    min-height: 48px; margin: 0 2px; border: none; border-radius: 5px;
    background: #C7B9AD;
}}
QScrollBar::handle:vertical:hover {{ background: #A99586; }}
QScrollBar::handle:vertical:pressed {{ background: {COLORS['accent']}; }}
QScrollBar::sub-line:vertical, QScrollBar::add-line:vertical {{
    height: 0; border: none; background: transparent;
}}
QScrollBar::sub-page:vertical, QScrollBar::add-page:vertical {{ background: transparent; }}
QScrollBar:horizontal {{
    height: 14px; margin: 2px 4px; border: none; background: transparent;
}}
QScrollBar::handle:horizontal {{
    min-width: 64px; margin: 2px 0; border: none; border-radius: 5px;
    background: #C7B9AD;
}}
QScrollBar::handle:horizontal:hover {{ background: #A99586; }}
QScrollBar::handle:horizontal:pressed {{ background: {COLORS['accent']}; }}
QScrollBar::sub-line:horizontal, QScrollBar::add-line:horizontal {{
    width: 0; border: none; background: transparent;
}}
QScrollBar::sub-page:horizontal, QScrollBar::add-page:horizontal {{ background: transparent; }}
QScrollBar::handle:disabled {{ background: transparent; }}
QAbstractScrollArea::corner {{ border: none; background: transparent; }}
QSplitter::handle {{ background: transparent; width: 8px; height: 8px; }}
"""


def line_icon(kind, color='#655D56'):
    """Small single-colour line icons keep the navigation visually consistent."""
    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(QPen(QColor(color), 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
    if kind == 'applications':
        painter.drawRoundedRect(QRectF(5, 3.5, 14, 17), 2.5, 2.5)
        painter.drawLine(QPointF(8, 8), QPointF(16, 8))
        painter.drawLine(QPointF(8, 12), QPointF(16, 12))
        painter.drawLine(QPointF(8, 16), QPointF(13, 16))
    elif kind == 'conversations':
        painter.drawRoundedRect(QRectF(3, 4, 18, 13), 4, 4)
        path = QPainterPath(QPointF(8, 17)); path.lineTo(7, 21); path.lineTo(12, 17)
        painter.drawPath(path)
        painter.drawEllipse(QPointF(8, 10.5), 1, 1); painter.drawEllipse(QPointF(12, 10.5), 1, 1); painter.drawEllipse(QPointF(16, 10.5), 1, 1)
    elif kind == 'workspace':
        painter.drawEllipse(QRectF(8, 3, 8, 8))
        painter.drawArc(QRectF(4.5, 11, 15, 11), 0, 180 * 16)
    elif kind == 'import':
        painter.drawRoundedRect(QRectF(3.5, 4, 17, 16), 3, 3)
        painter.drawLine(QPointF(12, 2.5), QPointF(12, 14))
        painter.drawLine(QPointF(8.5, 10.5), QPointF(12, 14))
        painter.drawLine(QPointF(15.5, 10.5), QPointF(12, 14))
    painter.end()
    return QIcon(pixmap)


class AvatarWidget(QWidget):
    clicked = Signal()

    def __init__(self, size, image_path='', name='', parent=None):
        super().__init__(parent)
        self._diameter = size
        self._image_path = image_path or ''
        self._name = name or ''
        self._hovered = False
        self.setFixedSize(size, size)
        self.setCursor(Qt.PointingHandCursor)
        self.setToolTip('Open My Workspace')
        self.setAccessibleName('Profile avatar')

    def set_profile(self, image_path='', name=''):
        self._image_path = image_path or ''
        self._name = name or ''
        self.update()

    def _initials(self):
        words = [word for word in self._name.strip().split() if word]
        if not words:
            return 'ME'
        return ''.join(word[0] for word in words[:2]).upper()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(2, 2, self.width()-4, self.height()-4)
        clip = QPainterPath(); clip.addEllipse(rect)
        painter.save(); painter.setClipPath(clip)
        image = QPixmap(self._image_path) if self._image_path and Path(self._image_path).is_file() else QPixmap()
        if not image.isNull():
            scaled = image.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            source_x = max(0, (scaled.width()-self.width())//2)
            source_y = max(0, (scaled.height()-self.height())//2)
            painter.drawPixmap(self.rect(), scaled, scaled.rect().adjusted(source_x, source_y, -source_x, -source_y))
        else:
            painter.fillPath(clip, QColor('#EED8CB'))
            font = painter.font(); font.setPointSize(max(9, int(self._diameter*.22))); font.setBold(True)
            painter.setFont(font); painter.setPen(QColor('#6E3C2C'))
            painter.drawText(self.rect(), Qt.AlignCenter, self._initials())
        painter.restore()
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor('#B75334' if self._hovered else '#D6BCAA'), 2 if self._hovered else 1.2))
        painter.drawEllipse(rect)

    def enterEvent(self, event):
        self._hovered = True; self.update(); super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False; self.update(); super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class WarmComboBox(QComboBox):
    """A readable light popup with a short, non-bouncy materialisation."""
    def showPopup(self):
        super().showPopup()
        popup = self.view().window()
        if reduce_motion_enabled():
            popup.setWindowOpacity(1.0)
            return
        popup.setWindowOpacity(0.0)
        animation = QPropertyAnimation(popup, b'windowOpacity', self)
        animation.setDuration(140)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        self._popup_animation = animation
        animation.start()


class Backdrop(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor('#F8F4EE'))
        gradient.setColorAt(.52, QColor('#F4EFE8'))
        gradient.setColorAt(1, QColor('#EEE7DE'))
        painter.fillRect(self.rect(), gradient)
        painter.setPen(QPen(QColor(151, 102, 75, 22), 2.0, Qt.SolidLine, Qt.RoundCap))
        route = QPainterPath(QPointF(-30, self.height() * .72))
        route.cubicTo(self.width() * .22, self.height() * .58, self.width() * .36, self.height() * .83, self.width() * .58, self.height() * .65)
        route.cubicTo(self.width() * .72, self.height() * .54, self.width() * .84, self.height() * .68, self.width() + 30, self.height() * .48)
        painter.drawPath(route)
        for x, y in ((.18,.64),(.39,.74),(.61,.63),(.82,.61)):
            painter.setBrush(QColor(247, 240, 232, 210))
            painter.drawEllipse(QPointF(self.width()*x, self.height()*y), 5, 5)
        super().paintEvent(event)


class CistyMarkWidget(QWidget):
    """The approved C mark with a short, non-looping electric reveal."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._phase = 0.04
        self._reduced_motion = reduce_motion_enabled()
        self.setMinimumSize(180, 180)
        self.setAccessibleName('Cisty logo')

    def get_phase(self):
        return self._phase

    def set_phase(self, value):
        self._phase = max(0.0, min(1.0, float(value)))
        self.update()

    phase = Property(float, get_phase, set_phase)

    @staticmethod
    def _ease_out(value):
        value = max(0.0, min(1.0, value))
        return 1.0 - (1.0 - value) ** 3

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        side = min(self.width(), self.height()) * .86
        rect = QRectF(
            (self.width() - side) / 2,
            (self.height() - side) / 2,
            side,
            side,
        )
        path = cisty_mark_path(rect)
        reveal = self._ease_out(self._phase / .28)
        scale = 1.0 if self._reduced_motion else .96 + .04 * reveal

        painter.save()
        painter.translate(rect.center())
        painter.scale(scale, scale)
        painter.translate(-rect.center())
        painter.setOpacity(reveal)
        painter.fillPath(path, QColor(COLORS['accent']))

        if not self._reduced_motion and .08 < self._phase < .82:
            energy_progress = (self._phase - .08) / .74
            energy = math.sin(math.pi * energy_progress)

            glow = QColor('#D67B58')
            glow.setAlpha(int(38 * energy))
            glow_pen = QPen(glow, max(3.0, side * .018), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(glow_pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawPath(path)

            current = QColor('#F1B296')
            current.setAlpha(int(210 * energy))
            current_pen = QPen(current, max(1.1, side * .006), Qt.CustomDashLine, Qt.RoundCap, Qt.RoundJoin)
            current_pen.setDashPattern([.45, 1.35, .14, 1.05])
            current_pen.setDashOffset(-self._phase * 18)
            painter.setPen(current_pen)
            painter.drawPath(path)

            bolt_color = QColor('#C85E3B')
            bolt_color.setAlpha(int(180 * energy))
            painter.setPen(QPen(bolt_color, max(1.0, side * .005), Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            for points in (
                ((.78, .21), (.83, .14), (.85, .20), (.91, .12)),
                ((.20, .62), (.13, .66), (.19, .70), (.10, .75)),
                ((.76, .79), (.82, .85), (.84, .79), (.91, .87)),
            ):
                bolt = QPainterPath(QPointF(
                    rect.left() + points[0][0] * rect.width(),
                    rect.top() + points[0][1] * rect.height(),
                ))
                for x, y in points[1:]:
                    bolt.lineTo(
                        rect.left() + x * rect.width(),
                        rect.top() + y * rect.height(),
                    )
                painter.drawPath(bolt)
        painter.restore()


class StartupWindow(QWidget):
    """A brief Cisty brand reveal shown while the main workspace becomes ready."""

    finished = Signal()

    def __init__(self):
        super().__init__(None, Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self._reduced_motion = reduce_motion_enabled()
        self._closing = False
        self._animations = []
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(520, 480)
        self.setAccessibleName('Cisty startup screen')

        outer = QVBoxLayout(self)
        outer.setContentsMargins(28, 28, 28, 28)
        card = QFrame()
        card.setObjectName('startupCard')
        card.setStyleSheet(f"""
            QFrame#startupCard {{
                background: #F7F3EC;
                border: 1px solid #E5D7CA;
                border-radius: 34px;
            }}
            QLabel#startupTitle {{
                color: {COLORS['ink']};
                font-family: "Segoe UI Variable Display", "Segoe UI";
                font-size: 38px;
                font-weight: 550;
            }}
            QLabel#startupSignature {{
                color: #8A5C48;
                font-family: "Segoe UI Variable Text", "Segoe UI";
                font-size: 14px;
                font-weight: 600;
                letter-spacing: 3px;
            }}
        """)
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(76, 54, 76, 50)
        layout.setSpacing(0)
        layout.addStretch(1)
        self.mark = CistyMarkWidget()
        self.mark.setFixedSize(224, 224)
        layout.addWidget(self.mark, 0, Qt.AlignHCenter)
        layout.addSpacing(12)

        self.title = QLabel('Cisty')
        self.title.setObjectName('startupTitle')
        self.title.setAlignment(Qt.AlignCenter)
        self.title_effect = QGraphicsOpacityEffect(self.title)
        self.title_effect.setOpacity(0.0)
        self.title.setGraphicsEffect(self.title_effect)
        layout.addWidget(self.title)
        layout.addSpacing(10)

        self.signature = QLabel('Trez')
        self.signature.setObjectName('startupSignature')
        self.signature.setAlignment(Qt.AlignCenter)
        self.signature_effect = QGraphicsOpacityEffect(self.signature)
        self.signature_effect.setOpacity(0.0)
        self.signature.setGraphicsEffect(self.signature_effect)
        layout.addWidget(self.signature)
        layout.addStretch(1)

    def showEvent(self, event):
        screen = QApplication.primaryScreen()
        if screen:
            area = screen.availableGeometry()
            self.move(
                area.x() + (area.width() - self.width()) // 2,
                area.y() + (area.height() - self.height()) // 2,
            )
        super().showEvent(event)

    def _fade_in(self, effect, duration):
        animation = QPropertyAnimation(effect, b'opacity', self)
        animation.setDuration(duration)
        animation.setStartValue(effect.opacity())
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animations.append(animation)
        animation.start()

    def start(self):
        if self._reduced_motion:
            self.mark.set_phase(1.0)
            self.title_effect.setOpacity(1.0)
            self.signature_effect.setOpacity(1.0)
            QTimer.singleShot(520, self._begin_exit)
            return

        logo_animation = QPropertyAnimation(self.mark, b'phase', self)
        logo_animation.setDuration(1050)
        logo_animation.setStartValue(.04)
        logo_animation.setEndValue(1.0)
        logo_animation.setEasingCurve(QEasingCurve.Linear)
        self._animations.append(logo_animation)
        logo_animation.start()
        QTimer.singleShot(250, lambda: self._fade_in(self.title_effect, 320))
        QTimer.singleShot(500, lambda: self._fade_in(self.signature_effect, 260))
        QTimer.singleShot(1280, self._begin_exit)

    def _begin_exit(self):
        if self._closing:
            return
        self._closing = True
        fade = QPropertyAnimation(self, b'windowOpacity', self)
        fade.setDuration(110 if self._reduced_motion else 180)
        fade.setStartValue(self.windowOpacity())
        fade.setEndValue(0.0)
        fade.setEasingCurve(QEasingCurve.OutCubic)
        fade.finished.connect(self._complete)
        self._animations.append(fade)
        fade.start()

    def _complete(self):
        self.close()
        self.finished.emit()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._begin_exit()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Escape, Qt.Key_Enter, Qt.Key_Return, Qt.Key_Space):
            self._begin_exit()
            event.accept()
            return
        super().keyPressEvent(event)


class AnimatedStack(QStackedWidget):
    def setCurrentIndexAnimated(self, index):
        if index == self.currentIndex():
            return
        self.setCurrentIndex(index)
        page = self.currentWidget()
        effect = QGraphicsOpacityEffect(page)
        page.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect, b'opacity', self)
        animation.setDuration(180 if reduce_motion_enabled() else 240)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.finished.connect(lambda: page.setGraphicsEffect(None))
        self._animation = animation
        animation.start()


class MainWindow(QMainWindow):
    task_ok = Signal(str, object)
    task_error = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Cisty — Internship Workspace')
        self.resize(1500, 900)
        self.setMinimumSize(860, 560)
        self.settings = load_settings()
        self.selected_id = None
        self._bulk_running = False
        self._conversation_syncing = False
        self._filter_widgets = []
        self._build_ui()
        self.setStyleSheet(APP_QSS)
        self.task_ok.connect(self._task_complete)
        self.task_error.connect(self._task_failed)
        self.refresh()
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(lambda: self.refresh_conversation(silent=True))
        self.poll_timer.start(60_000)
        if not self.settings.get('profile_ready'):
            QTimer.singleShot(100, lambda: self.switch_page(2))

    def _glass(self, name='glass'):
        frame = QFrame()
        frame.setObjectName(name)
        return frame

    def _build_ui(self):
        root = Backdrop()
        root.setObjectName('root')
        self.setCentralWidget(root)
        shell = QHBoxLayout(root)
        shell.setContentsMargins(10, 10, 10, 10)
        shell.setSpacing(12)
        shell.addWidget(self._build_navigation())
        self.pages = AnimatedStack()
        self.pages.addWidget(self._build_applications_page())
        self.pages.addWidget(self._build_conversations_page())
        self.pages.addWidget(self._build_workspace_page())
        shell.addWidget(self.pages, 1)

    def _build_navigation(self):
        nav = self._glass()
        nav.setObjectName('glass')
        nav.setFixedWidth(188)
        self.nav_panel = nav
        layout = QVBoxLayout(nav)
        layout.setContentsMargins(10, 16, 10, 12)
        self.nav_avatar = AvatarWidget(48, self.settings.get('profile_avatar_path',''), self.settings.get('student_name',''))
        self.nav_avatar.clicked.connect(lambda: self.switch_page(2))
        layout.addWidget(self.nav_avatar, 0, Qt.AlignHCenter)
        layout.addSpacing(14)
        self.nav_group = QButtonGroup(self)
        self.nav_group.setExclusive(True)
        items = [('Applications', 'applications'), ('Conversations', 'conversations'), ('My Workspace', 'workspace')]
        self.nav_buttons = []
        for index, (text, icon) in enumerate(items):
            button = QPushButton(text)
            button.setObjectName('nav')
            button.setCheckable(True)
            button.setIcon(line_icon(icon))
            button.clicked.connect(lambda checked=False, i=index: self.switch_page(i))
            self.nav_group.addButton(button, index)
            self.nav_buttons.append(button)
            layout.addWidget(button)
        self.nav_buttons[0].setChecked(True)
        layout.addStretch()
        privacy = QLabel('Private local workspace')
        privacy.setObjectName('muted')
        privacy.setWordWrap(True)
        privacy.setAlignment(Qt.AlignCenter)
        layout.addWidget(privacy)
        return nav

    def _build_applications_page(self):
        page = QWidget()
        outer = QVBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(10)
        header = QHBoxLayout()
        title_block = QVBoxLayout()
        title = QLabel('Cisty')
        title.setObjectName('title')
        subtitle = QLabel('Companies, routes and applications in one place')
        subtitle.setObjectName('muted')
        title_block.addWidget(title); title_block.addWidget(subtitle)
        title_block.setSpacing(1)
        header.addLayout(title_block)
        header.addStretch()
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search companies, stations, or contacts')
        self.search.setClearButtonEnabled(True)
        self.search.setMinimumWidth(280)
        self.search.textChanged.connect(lambda _text: self.refresh())
        header.addWidget(self.search)
        import_button = QPushButton('Import Excel')
        import_button.setIcon(line_icon('import'))
        import_button.clicked.connect(self.import_file)
        header.addWidget(import_button)
        outer.addLayout(header)
        outer.addWidget(self._build_metrics())
        outer.addWidget(self._build_filters())
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self._build_company_table())
        self.splitter.addWidget(self._build_inspector())
        self.splitter.setStretchFactor(0, 7)
        self.splitter.setStretchFactor(1, 3)
        self.splitter.setSizes([920, 420])
        outer.addWidget(self.splitter, 1)
        return page

    def _build_metrics(self):
        frame = self._glass()
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(18, 8, 18, 8)
        self.metric_values = {}
        for key, label in [('total', 'Companies'), ('visible', 'Visible'), ('stations', 'Stations calculated'), ('replies', 'Replies')]:
            block = QHBoxLayout()
            value = QLabel('0')
            value.setObjectName('metric')
            block.addWidget(value)
            block.addWidget(QLabel(label))
            block.addStretch()
            layout.addLayout(block, 1)
            self.metric_values[key] = value
        return frame

    def _build_filters(self):
        frame = self._glass()
        self.filter_grid = QGridLayout(frame)
        self.filter_grid.setContentsMargins(12, 9, 12, 9)
        self.filter_grid.setHorizontalSpacing(10)
        self.filter_grid.setVerticalSpacing(6)
        self.industry_filter = WarmComboBox()
        self.region_filter = WarmComboBox()
        self.distance_filter = WarmComboBox()
        self.status_filter = WarmComboBox()
        self.line_filter = WarmComboBox()
        self.distance_filter.addItems(['All distances', '≤ 1 km straight-line', '≤ 3 km straight-line', '≤ 5 min walk', '≤ 10 min walk', 'Route verified', 'Distance unknown'])
        self.status_filter.addItems(['All applications', 'Ready to apply', 'Not applied', 'Draft ready', 'Applied', 'Replied', 'Interview', 'Rejected', 'No response'])
        self.line_filter.addItems(['All transit lines'] + list(TRANSIT_LINES))
        for label, combo in [
            ('Industry', self.industry_filter), ('Region', self.region_filter),
            ('Distance', self.distance_filter), ('Status', self.status_filter),
            ('Transit line', self.line_filter)
        ]:
            holder = QWidget()
            column = QVBoxLayout(holder)
            column.setContentsMargins(0, 0, 0, 0)
            column.setSpacing(2)
            caption = QLabel(label)
            caption.setStyleSheet('font-weight: 600;')
            column.addWidget(caption)
            column.addWidget(combo)
            combo.currentTextChanged.connect(lambda _text: self.refresh())
            self._filter_widgets.append(holder)
        self._reflow_filters(5)
        tools = QHBoxLayout()
        refresh = QPushButton('Refresh list')
        refresh.clicked.connect(self.refresh)
        resume = QPushButton('Select resume PDF')
        resume.clicked.connect(self.choose_resume)
        self.bulk_button = QPushButton('Calculate stations')
        self.bulk_button.clicked.connect(lambda: self.calculate_all_nearest_stations(False))
        self.recalculate_button = QPushButton('Recalculate stations')
        self.recalculate_button.clicked.connect(lambda: self.calculate_all_nearest_stations(True))
        for button in (refresh, resume, self.bulk_button, self.recalculate_button):
            tools.addWidget(button)
        tools.addStretch()
        self.filter_grid.addLayout(tools, 3, 0, 1, 5)
        return frame

    def _reflow_filters(self, columns):
        for widget in self._filter_widgets:
            self.filter_grid.removeWidget(widget)
        for index, widget in enumerate(self._filter_widgets):
            self.filter_grid.addWidget(widget, index // columns, index % columns)
        for column in range(5):
            self.filter_grid.setColumnStretch(column, 1 if column < columns else 0)

    def _build_company_table(self):
        frame = self._glass('surface')
        frame.setObjectName('surface')
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(['Company', 'Industry', 'City', 'Nearest station', 'Distance', 'Contact', 'Status'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.table.verticalScrollBar().setSingleStep(34)
        self.table.horizontalScrollBar().setSingleStep(56)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for column in range(1, 7):
            header.setSectionResizeMode(column, QHeaderView.ResizeToContents)
        self.table.itemSelectionChanged.connect(self.on_select)
        layout.addWidget(self.table)
        return frame

    def _build_inspector(self):
        frame = self._glass()
        frame.setMinimumWidth(350)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(12, 12, 12, 12)
        self.inspector_tabs = QTabWidget()
        self.inspector_tabs.addTab(self._build_company_tab(), 'Company')
        self.inspector_tabs.addTab(self._build_email_tab(), 'Email')
        self.inspector_tabs.addTab(self._build_conversation_tab(), 'Conversation')
        layout.addWidget(self.inspector_tabs)
        return frame

    def _build_company_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.verticalScrollBar().setSingleStep(28)
        body = QWidget()
        body.setObjectName('panelBody')
        layout = QVBoxLayout(body)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(9)
        self.company_title = QLabel('Select a company')
        self.company_title.setObjectName('sectionTitle')
        self.company_title.setWordWrap(True)
        self.company_status = QLabel('No company selected')
        self.company_status.setObjectName('success')
        self.company_details = QLabel('Choose a row to review the company, route and verified contact.')
        self.company_details.setWordWrap(True)
        self.company_details.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.company_title)
        layout.addWidget(self.company_status)
        layout.addWidget(self.company_details)
        form = QFormLayout()
        form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.email_edit = QLineEdit()
        self.email_verified = QCheckBox('I verified this recruitment contact')
        email_box = QWidget(); email_layout = QVBoxLayout(email_box); email_layout.setContentsMargins(0,0,0,0)
        email_layout.addWidget(self.email_edit); email_layout.addWidget(self.email_verified)
        form.addRow('Contact email', email_box)
        self.station_line = WarmComboBox(); self.station_line.addItems(LINE_CHOICES)
        self.station = WarmComboBox(); self.station.addItems(LINE_STATIONS)
        self.distance_value = QLabel('Not calculated'); self.distance_value.setObjectName('muted'); self.distance_value.setWordWrap(True)
        self.walk_edit = QLineEdit(); self.walk_edit.setPlaceholderText('Final verified walk minutes')
        self.application_status = WarmComboBox(); self.application_status.addItems(['Not applied','Draft ready','Applied','Replied','Interview','Rejected','No response'])
        form.addRow('Transit line', self.station_line)
        form.addRow('Nearest station', self.station)
        form.addRow('Distance', self.distance_value)
        form.addRow('Final walk', self.walk_edit)
        form.addRow('Status', self.application_status)
        layout.addLayout(form)
        save = QPushButton('Save details'); save.setObjectName('primary'); save.clicked.connect(self.save_company)
        calculate = QPushButton('Calculate nearest station'); calculate.clicked.connect(self.calculate_nearest_station)
        route = QPushButton('Open route'); route.clicked.connect(self.open_map)
        layout.addWidget(save); layout.addWidget(calculate); layout.addWidget(route)
        layout.addStretch()
        scroll.setWidget(body)
        return scroll

    def _build_email_tab(self):
        body = QWidget(); body.setObjectName('panelBody'); layout = QVBoxLayout(body); layout.setContentsMargins(12,12,12,12)
        hint = QLabel('Generate the message, create a Gmail draft, then review before sending.')
        hint.setObjectName('muted'); hint.setWordWrap(True)
        self.email_preview = QPlainTextEdit(); self.email_preview.setPlaceholderText('Select a company and generate a preview.')
        generate = QPushButton('Generate preview'); generate.clicked.connect(self.generate_preview)
        draft = QPushButton('Create Gmail draft'); draft.clicked.connect(lambda: self.gmail_action(False))
        send = QPushButton('Review & send'); send.setObjectName('successButton'); send.clicked.connect(lambda: self.gmail_action(True))
        layout.addWidget(hint); layout.addWidget(self.email_preview,1); layout.addWidget(generate); layout.addWidget(draft); layout.addWidget(send)
        return body

    def _build_conversation_tab(self):
        body = QWidget(); body.setObjectName('panelBody'); layout = QVBoxLayout(body); layout.setContentsMargins(12,12,12,12)
        self.conversation_status = QLabel('Select a company that was emailed through this app.')
        self.conversation_status.setObjectName('muted'); self.conversation_status.setWordWrap(True)
        self.conversation_text = QPlainTextEdit(); self.conversation_text.setReadOnly(True)
        self.reply_text = QPlainTextEdit(); self.reply_text.setPlaceholderText('Write a reply in this tracked conversation')
        self.reply_text.setMaximumHeight(120)
        refresh = QPushButton('Refresh conversation'); refresh.clicked.connect(self.refresh_conversation)
        send = QPushButton('Send reply'); send.setObjectName('primary'); send.clicked.connect(self.send_reply)
        layout.addWidget(self.conversation_status); layout.addWidget(self.conversation_text,1); layout.addWidget(self.reply_text); layout.addWidget(refresh); layout.addWidget(send)
        return body

    def _build_conversations_page(self):
        page = QWidget(); layout = QVBoxLayout(page); layout.setContentsMargins(18,14,18,18)
        title = QLabel('System conversations'); title.setObjectName('pageTitle')
        hint = QLabel('Only Gmail threads created by this application are stored and displayed here.')
        hint.setObjectName('muted')
        card = self._glass(); card_layout = QVBoxLayout(card)
        note = QLabel('Select a company from Applications, then open its Conversation tab. This page never scans or displays unrelated inbox email.')
        note.setWordWrap(True); note.setAlignment(Qt.AlignCenter); note.setObjectName('muted')
        card_layout.addStretch(); card_layout.addWidget(note); card_layout.addStretch()
        layout.addWidget(title); layout.addWidget(hint); layout.addWidget(card,1)
        return page

    def _build_workspace_page(self):
        page = QWidget(); outer = QVBoxLayout(page); outer.setContentsMargins(18,14,18,18)
        title = QLabel('My Workspace'); title.setObjectName('pageTitle')
        hint = QLabel('Your profile, documents and service keys stay on this Windows account.')
        hint.setObjectName('muted')
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.verticalScrollBar().setSingleStep(28)
        card = self._glass(); content = QVBoxLayout(card); content.setContentsMargins(22,18,22,18)

        profile_card = QFrame(); profile_card.setObjectName('profileCard')
        profile_layout = QHBoxLayout(profile_card); profile_layout.setContentsMargins(18,16,18,16); profile_layout.setSpacing(16)
        self.workspace_avatar = AvatarWidget(
            84,
            self.settings.get('profile_avatar_path', ''),
            self.settings.get('student_name', '')
        )
        self.workspace_avatar.setToolTip('Choose profile photo')
        self.workspace_avatar.setAccessibleName('Choose profile photo')
        self.workspace_avatar.clicked.connect(self.choose_avatar)
        profile_layout.addWidget(self.workspace_avatar, 0, Qt.AlignVCenter)

        profile_copy = QVBoxLayout(); profile_copy.setSpacing(3)
        self.profile_name_label = QLabel(self.settings.get('student_name', '') or 'Your profile')
        self.profile_name_label.setObjectName('profileName')
        self.profile_email_label = QLabel(self.settings.get('sender_email', '') or 'Add your Gmail address')
        self.profile_email_label.setObjectName('muted')
        self.profile_email_label.setWordWrap(True)
        profile_copy.addWidget(self.profile_name_label)
        profile_copy.addWidget(self.profile_email_label)
        profile_copy.addStretch()
        profile_layout.addLayout(profile_copy, 1)

        avatar_actions = QVBoxLayout(); avatar_actions.setSpacing(6)
        choose_photo = QPushButton('Choose photo'); choose_photo.clicked.connect(self.choose_avatar)
        remove_photo = QPushButton('Remove'); remove_photo.setObjectName('quiet'); remove_photo.clicked.connect(self.remove_avatar)
        avatar_actions.addWidget(choose_photo); avatar_actions.addWidget(remove_photo)
        profile_layout.addLayout(avatar_actions)
        content.addWidget(profile_card)
        content.addSpacing(6)

        form = QFormLayout(); form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        labels = {
            'student_name':'Your full name', 'course':'Course / programme',
            'internship_period':'Internship period', 'phone':'Phone number',
            'sender_email':'Your Gmail address', 'resume_path':'Resume PDF',
            'credentials_path':'Google OAuth credentials.json', 'geoapify_api_key':'Geoapify free API key'
        }
        self.profile_fields = {}
        for key, label in labels.items():
            edit = QLineEdit(str(self.settings.get(key, '')))
            if key == 'geoapify_api_key': edit.setEchoMode(QLineEdit.Password)
            self.profile_fields[key] = edit
            if key in ('resume_path','credentials_path'):
                row = QWidget(); row_layout = QHBoxLayout(row); row_layout.setContentsMargins(0,0,0,0)
                row_layout.addWidget(edit,1)
                browse = QPushButton('Browse')
                browse.clicked.connect(lambda checked=False, k=key: self.browse_profile_file(k))
                row_layout.addWidget(browse)
                form.addRow(label,row)
            else:
                form.addRow(label,edit)
        self.profile_fields['student_name'].textChanged.connect(self._update_profile_preview)
        self.profile_fields['sender_email'].textChanged.connect(self._update_profile_preview)
        content.addLayout(form)
        self.workspace_status = QLabel('Changes are saved locally for this Windows account.')
        self.workspace_status.setObjectName('muted')
        save = QPushButton('Save workspace'); save.setObjectName('primary'); save.clicked.connect(self.save_workspace)
        content.addWidget(self.workspace_status); content.addWidget(save,0,Qt.AlignRight)
        content.addStretch(); scroll.setWidget(card)
        outer.addWidget(title); outer.addWidget(hint); outer.addWidget(scroll,1)
        return page

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if not hasattr(self, 'splitter'):
            return
        narrow = self.width() < 1080
        desired = Qt.Vertical if narrow else Qt.Horizontal
        if self.splitter.orientation() != desired:
            self.splitter.setOrientation(desired)
            self.splitter.setSizes([420, 360] if narrow else [920, 420])
        compact_nav = self.width() < 980
        self.nav_panel.setFixedWidth(70 if compact_nav else 188)
        for button, full in zip(self.nav_buttons, ('Applications','Conversations','My Workspace')):
            button.setText('' if compact_nav else full)
            button.setToolTip(full)
        columns = 2 if self.width() < 1050 else (3 if self.width() < 1350 else 5)
        self._reflow_filters(columns)

    def switch_page(self, index):
        self.nav_buttons[index].setChecked(True)
        self.pages.setCurrentIndexAnimated(index)

    @staticmethod
    def _region_label(row):
        return ' — '.join(x for x in [str(row['city'] or '').strip(), str(row['state'] or '').strip()] if x)

    def _set_combo_items(self, combo, items, fallback):
        current = combo.currentText() or fallback
        combo.blockSignals(True); combo.clear(); combo.addItems(items)
        index = combo.findText(current)
        combo.setCurrentIndex(index if index >= 0 else 0)
        combo.blockSignals(False)

    def refresh(self):
        selected = self.selected_id
        con = db(); rows = con.execute('SELECT * FROM companies ORDER BY name').fetchall()
        replies = con.execute("SELECT COUNT(*) FROM system_messages WHERE direction='inbound'").fetchone()[0]
        con.close()
        industries = sorted({str(r['industry']).strip() for r in rows if str(r['industry']).strip()})
        regions = sorted({self._region_label(r) for r in rows if self._region_label(r)})
        self._set_combo_items(self.industry_filter, ['All industries'] + industries, 'All industries')
        self._set_combo_items(self.region_filter, ['All regions','Kuala Lumpur / Selangor'] + regions, 'All regions')
        q = self.search.text().strip().lower()
        shown = []
        for r in rows:
            hay = ' '.join(str(r[k] or '') for k in ['name','industry','address','city','state','station','hr_email']).lower()
            if q and q not in hay: continue
            local = str(r['state']).lower() in ('selangor','wilayah persekutuan kuala lumpur') or str(r['city']).lower() in ('kuala lumpur','petaling jaya')
            route_checked = bool(r['route_verified']) and r['station'] in LINE_STATIONS and r['walk_minutes'] is not None
            verified = route_checked and int(r['walk_minutes']) <= 10
            ready = verified and bool(r['hr_email']) and '@' in r['hr_email'] and bool(r['email_verified']) and r['status'] != 'Applied'
            industry, region = self.industry_filter.currentText(), self.region_filter.currentText()
            line, distance, status = self.line_filter.currentText(), self.distance_filter.currentText(), self.status_filter.currentText()
            if industry != 'All industries' and r['industry'] != industry: continue
            if line != 'All transit lines' and r['station_line'] and r['station_line'] != line: continue
            if region == 'Kuala Lumpur / Selangor' and not local: continue
            if region not in ('All regions','Kuala Lumpur / Selangor') and self._region_label(r) != region: continue
            if distance == '≤ 1 km straight-line' and not (r['walk_distance_meters'] is not None and int(r['walk_distance_meters']) <= 1000): continue
            if distance == '≤ 3 km straight-line' and not (r['walk_distance_meters'] is not None and int(r['walk_distance_meters']) <= 3000): continue
            if distance == '≤ 5 min walk' and not (verified and int(r['walk_minutes']) <= 5): continue
            if distance == '≤ 10 min walk' and not verified: continue
            if distance == 'Route verified' and not route_checked: continue
            if distance == 'Distance unknown' and (r['walk_distance_meters'] is not None or r['walk_minutes'] is not None): continue
            if status == 'Ready to apply' and not ready: continue
            if status not in ('All applications','Ready to apply') and r['status'] != status: continue
            shown.append(r)
        if self.line_filter.currentText() != 'All transit lines':
            target = self.line_filter.currentText()
            shown.sort(key=lambda r: (0 if r['station_line'] == target else 1, str(r['name']).lower()))
        self.table.blockSignals(True); self.table.setRowCount(len(shown))
        selected_row = -1
        for row_index, r in enumerate(shown):
            distance = f"{r['walk_distance_meters']/1000:.1f} km" if r['walk_distance_meters'] is not None else '—'
            contact = 'Verified' if r['email_verified'] else ('Check needed' if r['hr_email'] else 'Missing')
            values = [r['name'], r['industry'], r['city'], r['station'] or 'Needs calculation', distance, contact, r['status']]
            for column, value in enumerate(values):
                item = QTableWidgetItem(str(value or '—'))
                if column == 0: item.setData(Qt.UserRole, r['id'])
                self.table.setItem(row_index, column, item)
            if r['id'] == selected: selected_row = row_index
        self.table.blockSignals(False)
        if selected_row >= 0: self.table.selectRow(selected_row)
        self.metric_values['total'].setText(f'{len(rows):,}')
        self.metric_values['visible'].setText(f'{len(shown):,}')
        self.metric_values['stations'].setText(f"{sum(1 for r in rows if r['station_line']):,}")
        self.metric_values['replies'].setText(f'{replies:,}')

    def current_company(self):
        if not self.selected_id: return None
        con = db(); row = con.execute('SELECT * FROM companies WHERE id=?',(self.selected_id,)).fetchone(); con.close(); return row

    def on_select(self):
        items = self.table.selectedItems()
        if not items: return
        item = self.table.item(items[0].row(), 0)
        self.selected_id = int(item.data(Qt.UserRole))
        row = self.current_company()
        if not row: return
        self.company_title.setText(row['name'])
        self.company_status.setText(row['status'] or 'Not applied')
        address = ', '.join(str(x) for x in [row['address'],row['postcode'],row['city'],row['state'],row['country']] if x)
        self.company_details.setText(f"Industry  {row['industry']}\nAddress  {address}\nWebsite  {row['website'] or '—'}")
        self.email_edit.setText(row['hr_email'] or '')
        self.email_verified.setChecked(bool(row['email_verified']))
        line = row['station_line'] or self._station_line_for(row['station']) or 'MRT Putrajaya Line'
        self.station_line.setCurrentText(line)
        self.station.setCurrentText(row['station'] or LINE_STATIONS[0])
        parts = []
        if row['walk_distance_meters'] is not None: parts.append(f"{row['walk_distance_meters']:,} m straight-line")
        if row['walk_minutes'] is not None: parts.append(f"{row['walk_minutes']} min verified walk")
        if row['station_calculated_at']: parts.append('saved '+row['station_calculated_at'])
        self.distance_value.setText(' • '.join(parts) or 'Not calculated')
        self.walk_edit.setText('' if row['walk_minutes'] is None else str(row['walk_minutes']))
        self.application_status.setCurrentText(row['status'] or 'Not applied')
        self.email_preview.clear(); self.reply_text.clear(); self.load_conversation()
        self._fade_inspector()

    def _fade_inspector(self):
        page = self.inspector_tabs.currentWidget()
        effect = QGraphicsOpacityEffect(page); page.setGraphicsEffect(effect)
        animation = QPropertyAnimation(effect,b'opacity',self); animation.setDuration(180)
        animation.setStartValue(.55); animation.setEndValue(1.0); animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.finished.connect(lambda: page.setGraphicsEffect(None)); self._inspector_animation = animation; animation.start()

    @staticmethod
    def _station_line_for(station):
        return next((line for line, stations in TRANSIT_LINES.items() if station in stations), '')

    def import_file(self):
        path, _ = QFileDialog.getOpenFileName(self,'Import company Excel','','Excel files (*.xlsx *.xlsm)')
        if not path: return
        try:
            added, updated, candidates = import_excel(path); self.refresh()
            QMessageBox.information(self,'Import complete',f'Companies added: {added:,}\nRecords updated: {updated:,}\nEmail candidates matched: {candidates:,}')
        except Exception as error:
            QMessageBox.critical(self,'Import failed',str(error))

    def choose_resume(self):
        path, _ = QFileDialog.getOpenFileName(self,'Choose resume PDF','','PDF files (*.pdf)')
        if path:
            self.settings['resume_path'] = path; save_settings(self.settings)
            self.profile_fields['resume_path'].setText(path)

    def browse_profile_file(self, key):
        pattern = 'PDF files (*.pdf)' if key == 'resume_path' else 'JSON files (*.json)'
        path, _ = QFileDialog.getOpenFileName(self,'Choose file','',pattern)
        if path: self.profile_fields[key].setText(path)

    def _update_profile_preview(self):
        name = self.profile_fields['student_name'].text().strip()
        email = self.profile_fields['sender_email'].text().strip()
        avatar_path = self.settings.get('profile_avatar_path', '')
        self.profile_name_label.setText(name or 'Your profile')
        self.profile_email_label.setText(email or 'Add your Gmail address')
        self.workspace_avatar.set_profile(avatar_path, name)
        self.nav_avatar.set_profile(avatar_path, name)

    def choose_avatar(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 'Choose profile photo', '',
            'Images (*.png *.jpg *.jpeg *.webp *.bmp)'
        )
        if not path:
            return
        source = Path(path)
        suffix = source.suffix.lower() if source.suffix else '.png'
        destination = DATA_DIR / f'profile_avatar{suffix}'
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            if source.resolve() != destination.resolve():
                shutil.copy2(source, destination)
            self.settings['profile_avatar_path'] = str(destination)
            save_settings(self.settings)
            self._update_profile_preview()
            self.workspace_status.setText('Profile photo saved on this Windows account.')
        except Exception as error:
            QMessageBox.critical(self, 'Photo could not be saved', str(error))

    def remove_avatar(self):
        self.settings['profile_avatar_path'] = ''
        save_settings(self.settings)
        self._update_profile_preview()
        self.workspace_status.setText('Profile photo removed. Your initials are shown instead.')

    def save_workspace(self):
        for key, field in self.profile_fields.items(): self.settings[key] = field.text().strip()
        self.settings['profile_ready'] = True; save_settings(self.settings)
        self._update_profile_preview()
        self.workspace_status.setText('Workspace saved on this Windows account.')
        QTimer.singleShot(500, lambda: self.switch_page(0))

    def save_company(self):
        row = self.current_company()
        if not row:
            QMessageBox.warning(self,'Select company','Select a company first.'); return
        email = self.email_edit.text().strip(); raw = self.walk_edit.text().strip()
        if email and ('@' not in email or '.' not in email.split('@')[-1]):
            QMessageBox.critical(self,'Invalid email','Enter a valid recruitment email.'); return
        if self.email_verified.isChecked() and not email:
            QMessageBox.critical(self,'Email missing','Add a contact email before marking it verified.'); return
        minutes = None
        if raw:
            try: minutes = int(raw)
            except ValueError:
                QMessageBox.critical(self,'Invalid walk time','Enter a whole number from 0 to 240.'); return
            if not 0 <= minutes <= 240:
                QMessageBox.critical(self,'Invalid walk time','Enter a whole number from 0 to 240.'); return
        verified = False
        if minutes is not None:
            answer = QMessageBox.question(self,'Confirm route check',f'Have you personally verified the walking route from {self.station.currentText()} to the actual office entrance is {minutes} minutes?')
            verified = answer == QMessageBox.Yes
        source = row['email_source'] if email == (row['hr_email'] or '') and row['email_source'] else ('Manually entered' if email else '')
        now = datetime.now().isoformat(timespec='minutes')
        con = db(); con.execute('''UPDATE companies SET hr_email=?,email_source=?,email_verified=?,email_verified_at=?,station=?,station_line=?,walk_minutes=?,route_verified=?,status=?,station_calculation_source=CASE WHEN ? THEN 'manual_verified' ELSE station_calculation_source END,station_calculated_at=CASE WHEN ? THEN ? ELSE station_calculated_at END WHERE id=?''',
            (email,source,int(self.email_verified.isChecked()),now if self.email_verified.isChecked() else '',self.station.currentText(),self.station_line.currentText(),minutes,int(verified),self.application_status.currentText(),int(verified),int(verified),now,self.selected_id))
        con.commit(); con.close(); self.refresh(); self.on_select()

    @staticmethod
    def _straight_distance(a_lat,a_lon,b_lat,b_lon):
        radius=6371000; p1,p2=math.radians(a_lat),math.radians(b_lat)
        dp,dl=math.radians(b_lat-a_lat),math.radians(b_lon-a_lon)
        h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return int(2*radius*math.asin(math.sqrt(h)))

    @staticmethod
    def _geoapify(query, api_key):
        url='https://api.geoapify.com/v1/geocode/search?text='+quote(query)+'&filter=countrycode:my&limit=1&apiKey='+quote(api_key)
        with urlopen(Request(url,headers={'User-Agent':'ITInternshipAutoApply/2.0'}),timeout=30) as response:
            features=json.loads(response.read().decode('utf-8')).get('features',[])
        if not features: return None
        lon,lat=features[0]['geometry']['coordinates'][:2]; return float(lat),float(lon)

    def _station_points(self, con, api_key):
        points=[]
        for line, stations in TRANSIT_LINES.items():
            for station in stations:
                cached=con.execute('SELECT latitude,longitude FROM station_locations WHERE line=? AND station=?',(line,station)).fetchone()
                if cached: points.append((line,station,cached['latitude'],cached['longitude'])); continue
                mode='MRT' if line.startswith('MRT') else ('LRT' if line.startswith('LRT') else 'Monorail')
                location=self._geoapify(f'{station} {mode} station, Malaysia',api_key); time.sleep(.22)
                if location:
                    con.execute('INSERT OR REPLACE INTO station_locations(line,station,latitude,longitude,updated_at) VALUES(?,?,?,?,?)',(line,station,*location,datetime.now().isoformat(timespec='minutes')))
                    points.append((line,station,*location))
        con.commit(); return points

    def _save_nearest(self, con, company, points):
        if company['latitude'] is None or company['longitude'] is None or not points: return False
        distance,line,station=min(((self._straight_distance(company['latitude'],company['longitude'],lat,lon),line,station) for line,station,lat,lon in points),key=lambda item:item[0])
        con.execute("UPDATE companies SET station=?,station_line=?,walk_distance_meters=?,walk_minutes=NULL,route_verified=0,station_calculation_source='geoapify_auto',station_calculated_at=? WHERE id=?",(station,line,distance,datetime.now().isoformat(timespec='minutes'),company['id']))
        return True

    def calculate_nearest_station(self):
        row=self.current_company(); key=self.settings.get('geoapify_api_key','').strip()
        if not row: QMessageBox.warning(self,'Select company','Select a company first.'); return
        if not key: QMessageBox.critical(self,'Geoapify key required','Add the free Geoapify key in My Workspace.'); return
        self.distance_value.setText('Calculating nearest station…')
        self._run_task('single_station',self._single_station_worker,row['id'],key)

    def _single_station_worker(self, company_id, key):
        con=db(); company=con.execute('SELECT * FROM companies WHERE id=?',(company_id,)).fetchone(); points=self._station_points(con,key)
        if company['latitude'] is None or company['longitude'] is None:
            address=', '.join(str(x) for x in [company['address'],company['postcode'],company['city'],company['state'],'Malaysia'] if x)
            point=self._geoapify(address,key)
            if not point: con.close(); raise RuntimeError('Company address could not be located.')
            con.execute('UPDATE companies SET latitude=?,longitude=? WHERE id=?',(*point,company_id)); con.commit()
            company=con.execute('SELECT * FROM companies WHERE id=?',(company_id,)).fetchone()
        if not self._save_nearest(con,company,points): con.close(); raise RuntimeError('No station could be calculated.')
        con.commit(); result=con.execute('SELECT station,station_line,walk_distance_meters FROM companies WHERE id=?',(company_id,)).fetchone(); con.close()
        return dict(result)

    def calculate_all_nearest_stations(self, force=False):
        if self._bulk_running: return
        key=self.settings.get('geoapify_api_key','').strip()
        if not key: QMessageBox.critical(self,'Geoapify key required','Add the free Geoapify key in My Workspace.'); return
        industry,region=self.industry_filter.currentText(),self.region_filter.currentText()
        action='overwrite previous automatic results' if force else 'calculate companies without saved results'
        if QMessageBox.question(self,'Calculate stations',f'This will {action} for the selected industry and region. Manually verified routes remain protected. Continue?') != QMessageBox.Yes: return
        self._bulk_running=True; self.bulk_button.setEnabled(False); self.recalculate_button.setEnabled(False)
        self._run_task('bulk_station',self._bulk_station_worker,key,industry,region,force)

    def _bulk_station_worker(self,key,industry,region,force):
        con=db(); points=self._station_points(con,key)
        clauses=['COALESCE(route_verified,0)=0']; params=[]
        if not force: clauses.append("(latitude IS NULL OR longitude IS NULL OR COALESCE(station_line,'')='')")
        if industry!='All industries': clauses.append("COALESCE(industry,'')=?"); params.append(industry)
        if region=='Kuala Lumpur / Selangor':
            clauses.append("(LOWER(COALESCE(state,'')) IN (?,?) OR LOWER(COALESCE(city,'')) IN (?,?))"); params += ['selangor','wilayah persekutuan kuala lumpur','kuala lumpur','petaling jaya']
        elif region!='All regions':
            parts=region.split(' — ',1); city=parts[0] if len(parts)>1 else ''; state=parts[-1]
            if city: clauses.append("COALESCE(city,'')=?"); params.append(city)
            if state: clauses.append("COALESCE(state,'')=?"); params.append(state)
        companies=con.execute('SELECT * FROM companies WHERE '+' AND '.join(clauses)+' ORDER BY id',params).fetchall()
        located=failed=0
        for company in companies:
            if company['latitude'] is None or company['longitude'] is None:
                address=', '.join(str(x) for x in [company['address'],company['postcode'],company['city'],company['state'],'Malaysia'] if x)
                point=self._geoapify(address,key); time.sleep(.22)
                if not point: failed+=1; continue
                con.execute('UPDATE companies SET latitude=?,longitude=? WHERE id=?',(*point,company['id'])); con.commit()
                company=con.execute('SELECT * FROM companies WHERE id=?',(company['id'],)).fetchone()
            if self._save_nearest(con,company,points): located+=1
        con.commit(); con.close(); return {'located':located,'failed':failed,'force':force}

    def open_map(self):
        row=self.current_company()
        if not row: QMessageBox.warning(self,'Select company','Select a company first.'); return
        destination=', '.join(str(x) for x in [row['address'],row['city'],row['state'],'Malaysia'] if x)
        origin=(row['station'] or '')+' station, Malaysia'
        webbrowser.open('https://www.google.com/maps/dir/?api=1&travelmode=walking&origin='+quote(origin)+'&destination='+quote(destination))

    def make_email(self,row):
        subject=self.settings.get('email_subject','Application for IT Internship – {company}').format(company=row['name'])
        name=self.settings.get('student_name') or '[Your Name]'; course=self.settings.get('course') or '[Your Course]'
        period=self.settings.get('internship_period') or '[Internship Period]'; phone=self.settings.get('phone') or '[Phone Number]'
        body=(f'Dear Hiring Manager,\n\nI hope you are doing well. My name is {name}, and I am currently studying {course}. '
              f'I am writing to express my interest in an IT internship opportunity at {row["name"]}. '
              f'I would appreciate the opportunity to apply my knowledge, learn from your team, and gain practical industry experience.\n\n'
              f'My available internship period is {period}. I have attached my resume for your consideration. '
              f'Please let me know if there are any suitable internship opportunities or further documents required.\n\n'
              f'Thank you for your time and consideration.\n\nBest regards,\n{name}\n{course}\n{phone}\n{self.settings.get("sender_email","")}')
        return subject,body

    def generate_preview(self):
        row=self.current_company()
        if not row: QMessageBox.warning(self,'Select company','Select a company first.'); return
        subject,body=self.make_email(row); self.email_preview.setPlainText(f'To: {row["hr_email"] or "[Add verified HR email]"}\nSubject: {subject}\n\n{body}')

    def gmail_action(self, send=False):
        row=self.current_company()
        if not row: QMessageBox.warning(self,'Select company','Select a company first.'); return
        if not row['hr_email'] or not row['email_verified']:
            QMessageBox.critical(self,'Verified contact required','Verify the recruitment contact before using Gmail.'); return
        resume=self.settings.get('resume_path','')
        if not resume or not Path(resume).is_file(): QMessageBox.critical(self,'Resume missing','Select an existing resume PDF.'); return
        credentials=self.settings.get('credentials_path','')
        if not credentials or not Path(credentials).is_file(): QMessageBox.critical(self,'Gmail not configured','Select credentials.json in My Workspace.'); return
        subject,body=self.make_email(row)
        if QMessageBox.question(self,'Review Gmail action',f'To: {row["hr_email"]}\nSubject: {subject}\nAttachment: {resume}\n\nProceed to '+('send?' if send else 'create a draft?')) != QMessageBox.Yes: return
        self._run_task('gmail',self._gmail_worker,row['id'],row['hr_email'],subject,body,resume,send)

    def _gmail_service(self):
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request as GoogleRequest
        from googleapiclient.discovery import build
        scopes=['https://www.googleapis.com/auth/gmail.modify']; creds=None
        if TOKEN_PATH.exists(): creds=Credentials.from_authorized_user_file(str(TOKEN_PATH),scopes)
        granted=set(getattr(creds,'granted_scopes',None) or []) if creds else set()
        if not creds or not creds.valid or (granted and not set(scopes).issubset(granted)):
            if creds and creds.expired and creds.refresh_token: creds.refresh(GoogleRequest())
            else: creds=InstalledAppFlow.from_client_secrets_file(self.settings['credentials_path'],scopes).run_local_server(port=0)
            TOKEN_PATH.write_text(creds.to_json(),encoding='utf-8')
        return build('gmail','v1',credentials=creds)

    def _gmail_worker(self,cid,to,subject,body,resume,send):
        service=self._gmail_service(); message=EmailMessage(); message['To']=to; message['Subject']=subject; message.set_content(body)
        with open(resume,'rb') as file: message.add_attachment(file.read(),maintype='application',subtype='pdf',filename=Path(resume).name)
        raw=base64.urlsafe_b64encode(message.as_bytes()).decode()
        if send:
            result=service.users().messages().send(userId='me',body={'raw':raw}).execute(); status='Applied'; sent=datetime.now().isoformat(timespec='minutes')
            self._sync_gmail_thread(service,cid,result['threadId'])
        else:
            service.users().drafts().create(userId='me',body={'message':{'raw':raw}}).execute(); status='Draft ready'; sent=''
        con=db(); con.execute('UPDATE companies SET status=?,last_sent=? WHERE id=?',(status,sent,cid)); con.commit(); con.close()
        return {'send':send}

    @staticmethod
    def _message_headers(message):
        return {header['name'].lower():header.get('value','') for header in message.get('payload',{}).get('headers',[])}

    @classmethod
    def _message_body(cls,payload):
        if payload.get('body',{}).get('data') and payload.get('mimeType','').startswith('text/plain'):
            return base64.urlsafe_b64decode(payload['body']['data']+'===').decode('utf-8','replace')
        for part in payload.get('parts',[]) or []:
            text=cls._message_body(part)
            if text: return text
        return ''

    def _sync_gmail_thread(self,service,company_id,thread_id):
        thread=service.users().threads().get(userId='me',id=thread_id,format='full').execute(); con=db()
        for message in thread.get('messages',[]):
            headers=self._message_headers(message); direction='outbound' if 'SENT' in message.get('labelIds',[]) else 'inbound'
            con.execute('''INSERT OR REPLACE INTO system_messages(gmail_message_id,company_id,gmail_thread_id,direction,sender,recipient,subject,body,sent_at,internal_date) VALUES(?,?,?,?,?,?,?,?,?,?)''',
                (message['id'],company_id,thread_id,direction,headers.get('from',''),headers.get('to',''),headers.get('subject',''),self._message_body(message.get('payload',{})),headers.get('date',''),int(message.get('internalDate','0') or 0)))
        first=(thread.get('messages') or [{}])[0].get('id','')
        con.execute('''INSERT INTO system_threads(company_id,gmail_thread_id,recipient,initial_message_id,last_synced_at) VALUES(?,?,?,?,?) ON CONFLICT(company_id) DO UPDATE SET gmail_thread_id=excluded.gmail_thread_id,last_synced_at=excluded.last_synced_at''',(company_id,thread_id,'',first,datetime.now().isoformat(timespec='minutes')))
        inbound=con.execute("SELECT COUNT(*) FROM system_messages WHERE company_id=? AND direction='inbound'",(company_id,)).fetchone()[0]
        con.execute("UPDATE companies SET last_contact=?,status=CASE WHEN ? > 0 AND status IN ('Applied','No response') THEN 'Replied' ELSE status END WHERE id=?",(datetime.now().isoformat(timespec='minutes'),inbound,company_id))
        con.commit(); con.close()

    def load_conversation(self):
        self.conversation_text.clear()
        if not self.selected_id: return
        con=db(); thread=con.execute('SELECT * FROM system_threads WHERE company_id=?',(self.selected_id,)).fetchone(); messages=con.execute('SELECT * FROM system_messages WHERE company_id=? ORDER BY internal_date',(self.selected_id,)).fetchall(); con.close()
        if not thread: self.conversation_status.setText('No system-sent email for this company yet.'); return
        self.conversation_status.setText('Tracked Gmail thread • last synced: '+(thread['last_synced_at'] or 'Never'))
        blocks=[]
        for message in messages:
            label='YOU SENT' if message['direction']=='outbound' else 'THEY REPLIED'
            blocks.append(f"{label}  •  {message['sent_at']}\n{message['sender']} → {message['recipient']}\nSubject: {message['subject']}\n\n{message['body'].strip()}")
        self.conversation_text.setPlainText(('\n\n'+'─'*52+'\n\n').join(blocks))

    def refresh_conversation(self, silent=False):
        if not self.selected_id or self._conversation_syncing: return
        con=db(); thread=con.execute('SELECT gmail_thread_id FROM system_threads WHERE company_id=?',(self.selected_id,)).fetchone(); con.close()
        if not thread:
            if not silent: QMessageBox.information(self,'No tracked conversation','Send the first email through this app.')
            return
        if not self.settings.get('credentials_path') or not Path(self.settings['credentials_path']).is_file(): return
        self._conversation_syncing=True; self.conversation_status.setText('Refreshing this system thread…')
        self._run_task('conversation',self._conversation_worker,self.selected_id,thread['gmail_thread_id'],silent)

    def _conversation_worker(self,company_id,thread_id,silent):
        self._sync_gmail_thread(self._gmail_service(),company_id,thread_id); return {'silent':silent}

    def send_reply(self):
        body=self.reply_text.toPlainText().strip(); row=self.current_company()
        if not row or not body: QMessageBox.warning(self,'Reply','Select a company and write a reply first.'); return
        con=db(); thread=con.execute('SELECT gmail_thread_id FROM system_threads WHERE company_id=?',(row['id'],)).fetchone(); con.close()
        if not thread: QMessageBox.critical(self,'No conversation','The first email must be sent through this app.'); return
        if QMessageBox.question(self,'Review reply',f'To: {row["hr_email"]}\n\n{body}\n\nSend this reply?') != QMessageBox.Yes: return
        self._run_task('reply',self._reply_worker,dict(row),thread['gmail_thread_id'],body)

    def _reply_worker(self,company,thread_id,body):
        service=self._gmail_service(); thread=service.users().threads().get(userId='me',id=thread_id,format='full').execute()
        latest=(thread.get('messages') or [])[-1]; headers=self._message_headers(latest); subject=headers.get('subject','Application follow-up')
        if not subject.lower().startswith('re:'): subject='Re: '+subject
        message=EmailMessage(); message['To']=company['hr_email']; message['Subject']=subject
        if headers.get('message-id'): message['In-Reply-To']=headers['message-id']; message['References']=headers['message-id']
        message.set_content(body); raw=base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId='me',body={'raw':raw,'threadId':thread_id}).execute(); self._sync_gmail_thread(service,company['id'],thread_id)
        return None

    def _run_task(self,name,function,*args):
        def execute():
            try: self.task_ok.emit(name,function(*args))
            except HTTPError as error:
                detail=error.read().decode('utf-8','replace'); self.task_error.emit(name,f'HTTP {error.code}: {detail}')
            except Exception as error: self.task_error.emit(name,str(error))
        threading.Thread(target=execute,daemon=True).start()

    def _task_complete(self,name,result):
        if name == 'single_station':
            self.refresh(); self.on_select(); QMessageBox.information(self,'Station calculated',f"Nearest station: {result['station']}\nLine: {result['station_line']}\nStraight-line distance: {result['walk_distance_meters']:,} m")
        elif name == 'bulk_station':
            self._bulk_running=False; self.bulk_button.setEnabled(True); self.recalculate_button.setEnabled(True); self.refresh()
            QMessageBox.information(self,'Station calculation complete',f"Calculated: {result['located']:,}\nAddress not located: {result['failed']:,}")
        elif name == 'gmail':
            self.refresh(); self.load_conversation(); QMessageBox.information(self,'Gmail complete','Email sent and conversation tracking started.' if result['send'] else 'Gmail draft created.')
        elif name == 'conversation':
            self._conversation_syncing=False; self.refresh(); self.load_conversation()
        elif name == 'reply':
            self.reply_text.clear(); self.refresh(); self.load_conversation(); QMessageBox.information(self,'Reply sent','Your reply was sent in the tracked conversation.')

    def _task_failed(self,name,error):
        if name == 'bulk_station':
            self._bulk_running=False; self.bulk_button.setEnabled(True); self.recalculate_button.setEnabled(True)
        if name == 'conversation': self._conversation_syncing=False
        QMessageBox.critical(self,'Action failed',error)


def main():
    application = QApplication(sys.argv)
    application.setStyle('Fusion')
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor('#F4EFE8'))
    palette.setColor(QPalette.WindowText, QColor(COLORS['ink']))
    palette.setColor(QPalette.Base, QColor('#FFFDF9'))
    palette.setColor(QPalette.AlternateBase, QColor('#FAF6F0'))
    palette.setColor(QPalette.Text, QColor(COLORS['ink']))
    palette.setColor(QPalette.Button, QColor('#FFFDF9'))
    palette.setColor(QPalette.ButtonText, QColor(COLORS['ink']))
    palette.setColor(QPalette.Highlight, QColor(COLORS['accent_soft']))
    palette.setColor(QPalette.HighlightedText, QColor(COLORS['ink']))
    palette.setColor(QPalette.ToolTipBase, QColor('#2B2724'))
    palette.setColor(QPalette.ToolTipText, QColor('#FFF9F3'))
    application.setPalette(palette)
    application.setApplicationName('Cisty')
    application.setApplicationDisplayName('Cisty')
    icon_path = RESOURCE_DIR / 'assets' / 'cisty_app_icon.svg'
    app_icon = QIcon(str(icon_path)) if icon_path.exists() else QIcon()
    if not app_icon.isNull():
        application.setWindowIcon(app_icon)

    startup = StartupWindow()
    startup.show()
    application.processEvents()

    window = MainWindow()
    if not app_icon.isNull():
        window.setWindowIcon(app_icon)
    if not db().execute('SELECT COUNT(*) FROM companies').fetchone()[0]:
        workbook = RESOURCE_DIR / 'CareeReX_IT_highlight.xlsx'
        if workbook.exists():
            try: import_excel(workbook)
            except Exception: pass
        window.refresh()
    def reveal_main_window():
        window.show()
        window.raise_()
        window.activateWindow()
        if sys.platform == 'win32':
            try:
                import ctypes
                hwnd = int(window.winId())
                light = ctypes.c_int(0)
                # Windows 10/11: explicitly keep the native title bar in light mode.
                for attribute in (20, 19):
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd, attribute, ctypes.byref(light), ctypes.sizeof(light)
                    )
            except Exception:
                pass

    startup.finished.connect(reveal_main_window)
    startup.start()
    sys.exit(application.exec())


if __name__ == '__main__':
    main()

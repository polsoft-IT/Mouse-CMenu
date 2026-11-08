from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap

ICON_SIZES = (16, 20, 24, 32, 48, 64, 128, 256)
GEAR_COLOR = "#2D4B7C"


def _render_icon(size: int) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    scale = size / 256.0

    rounded = QPainterPath()
    rounded.addRoundedRect(QRectF(8 * scale, 8 * scale, 240 * scale, 240 * scale), 48 * scale, 48 * scale)
    painter.fillPath(rounded, QColor("#2D4B7C"))
    painter.setPen(QPen(QColor("#FFFFFF"), max(1, round(12 * scale))))
    painter.drawPath(rounded)

    row_height = 44 * scale
    for index, width in enumerate((150, 118, 150)):
        y = 78 * scale + index * (row_height + 16 * scale)
        painter.setPen(QPen(QColor("#FFFFFF"), max(1, round(16 * scale)), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(QPointF(56 * scale, y), QPointF((56 + width) * scale, y))

    painter.end()
    return pixmap


def app_icon() -> QIcon:
    icon = QIcon()
    for size in ICON_SIZES:
        icon.addPixmap(_render_icon(size))
    return icon


def _render_gear(size: int) -> QPixmap:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    scale = size / 256.0

    center = QPointF(128 * scale, 128 * scale)
    outer_radius = 106 * scale
    inner_radius = 82 * scale
    hole_radius = 34 * scale
    tooth_count = 8
    step = 2 * math.pi / tooth_count
    tooth_angle = step * 0.5

    path = QPainterPath()
    for index in range(tooth_count):
        start = index * step
        for angle, radius in (
            (start, outer_radius),
            (start + tooth_angle, outer_radius),
            (start + tooth_angle, inner_radius),
            (start + step, inner_radius),
        ):
            point = QPointF(
                center.x() + radius * math.cos(angle),
                center.y() + radius * math.sin(angle),
            )
            if path.elementCount() == 0:
                path.moveTo(point)
            else:
                path.lineTo(point)
    path.closeSubpath()
    path.setFillRule(Qt.FillRule.OddEvenFill)
    path.addEllipse(center, hole_radius, hole_radius)

    painter.fillPath(path, QColor(GEAR_COLOR))
    painter.end()
    return pixmap


def gear_icon() -> QIcon:
    icon = QIcon()
    for size in ICON_SIZES:
        icon.addPixmap(_render_gear(size))
    return icon

"""Render Cisty's SVG app icon to PNG and a multi-size Windows ICO."""

from pathlib import Path
import sys

from PIL import Image
from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
SOURCE = ASSETS / "cisty_app_icon.svg"
SIZES = (16, 24, 32, 48, 64, 128, 256, 512)


def render_png(renderer: QSvgRenderer, size: int) -> Path:
    image = QImage(size, size, QImage.Format_ARGB32_Premultiplied)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    target = ASSETS / f"cisty_app_icon_{size}.png"
    if not image.save(str(target), "PNG"):
        raise RuntimeError(f"Could not write {target}")
    return target


def main() -> int:
    app = QGuiApplication.instance() or QGuiApplication(sys.argv[:1])
    renderer = QSvgRenderer(str(SOURCE))
    if not renderer.isValid():
        raise RuntimeError(f"Invalid SVG: {SOURCE}")
    pngs = [render_png(renderer, size) for size in SIZES]
    images = [Image.open(path).convert("RGBA") for path in pngs]
    ico_path = ASSETS / "cisty_app_icon.ico"
    images[-1].save(
        ico_path,
        format="ICO",
        sizes=[(size, size) for size in SIZES if size <= 256],
    )
    for image in images:
        image.close()
    del app
    print(f"Generated {len(pngs)} PNG files and {ico_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

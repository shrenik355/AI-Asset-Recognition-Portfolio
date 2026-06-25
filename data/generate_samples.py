"""Generate original synthetic sample images for the demo and benchmark.

Produces clean, fully original asset-label images and a scannable UPC-A barcode.
No proprietary layouts or real device data are used — all values are obviously
fictitious samples. Run once to (re)create files under data/sample_images/.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent.parent / "data" / "sample_images"
OUT.mkdir(parents=True, exist_ok=True)


def _font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def make_label(filename: str, lines: list[tuple[str, bool]], width: int = 640) -> None:
    """Render a simple, high-contrast asset label image."""
    pad = 36
    line_h = 46
    height = pad * 2 + line_h * len(lines)
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    draw.rectangle([6, 6, width - 7, height - 7], outline="black", width=3)

    y = pad
    for text, bold in lines:
        draw.text((pad, y), text, fill="black", font=_font(30, bold=bold))
        y += line_h
    img.save(OUT / filename)
    print(f"wrote {filename}  ({width}x{height})")


def make_barcode(filename: str, code: str) -> None:
    """Render a scannable UPC-A barcode PNG using python-barcode."""
    try:
        from barcode import UPCA
        from barcode.writer import ImageWriter
    except Exception as exc:  # pragma: no cover
        print(f"skipping barcode ({exc})")
        return
    # python-barcode computes the UPC-A check digit from 11 digits.
    obj = UPCA(code[:11], writer=ImageWriter())
    path = OUT / filename.replace(".png", "")
    obj.save(str(path), options={"module_height": 12.0, "quiet_zone": 3.0})
    print(f"wrote {filename}")


if __name__ == "__main__":
    # A laptop label with a Luhn-valid IMEI is not realistic (laptops lack IMEI),
    # so we keep IMEI on the phone sample and an asset tag on the laptop sample.
    make_label(
        "asset_label_laptop.png",
        [
            ("ASSET LABEL  (SAMPLE)", True),
            ("Manufacturer: Dell", False),
            ("Model: Latitude 5420", False),
            ("Serial Number: SN-LT-100482", False),
            ("Asset Tag: ASSET-98765", False),
        ],
    )
    make_label(
        "asset_label_phone.png",
        [
            ("DEVICE LABEL  (SAMPLE)", True),
            ("Manufacturer: Apple", False),
            ("Model: iPhone 13", False),
            ("Serial Number: SN-PH-774120", False),
            ("IMEI: 490154203237518", False),
        ],
    )
    make_barcode("barcode_upc.png", "012345678905")

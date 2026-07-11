"""One-time helper: convert a background-removed photo into an ASCII portrait.

Usage: python3 ascii_portrait.py cutout.png portrait.txt
Not used by CI; generate.py reads the committed portrait.txt.
"""
import sys

from PIL import Image, ImageFilter, ImageOps

RAMP = "@#%*|!. "  # darkest -> lightest; transparent pixels also map to space
CHAR_ASPECT = 0.5  # monospace glyphs are roughly twice as tall as wide


def image_to_ascii(img, width=45):
    img = img.convert("RGBA")
    height = max(1, round(img.height / img.width * width * CHAR_ASPECT))
    img = img.resize((width, height))
    pixels = img.load()
    lines = []
    for y in range(height):
        chars = []
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a < 128:
                chars.append(" ")
                continue
            luminance = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255
            index = min(int(luminance * len(RAMP)), len(RAMP) - 1)
            chars.append(RAMP[index])
        lines.append("".join(chars))
    return lines


def preprocess(img, width, gamma=1.6):
    """Crop to the opaque subject, then brighten and sharpen for the ramp.

    Autocontrast + gamma lift the mid-tones (face, shirt folds) so the output
    uses the full ramp instead of collapsing into '@'; unsharp masking darkens
    facial contours (brow, nose, jaw) onto denser ramp chars; a 2x LANCZOS
    supersample to the target grid keeps thin features from aliasing away in
    image_to_ascii's final resize. Alpha is preserved throughout.
    """
    img = img.convert("RGBA")
    img = img.crop(img.getbbox())  # getbbox is alpha_only for RGBA
    alpha = img.getchannel("A")
    rgb = ImageOps.autocontrast(img.convert("RGB"), cutoff=2)
    lut = [round(255 * (i / 255) ** (1 / gamma)) for i in range(256)]
    rgb = rgb.point(lut * 3)
    rgb = rgb.filter(ImageFilter.UnsharpMask(radius=4, percent=200, threshold=2))
    rgb.putalpha(alpha)
    w = width * 2
    h = round(rgb.height / rgb.width * w)
    return rgb.resize((w, h), Image.LANCZOS)


PORTRAIT_WIDTH = 70  # single source of truth: preprocess supersamples to 2x this


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: python3 ascii_portrait.py <input.png> <output.txt>")
    img = preprocess(Image.open(sys.argv[1]), width=PORTRAIT_WIDTH)
    lines = image_to_ascii(img, width=PORTRAIT_WIDTH)
    with open(sys.argv[2], "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} lines to {sys.argv[2]}")


if __name__ == "__main__":
    main()

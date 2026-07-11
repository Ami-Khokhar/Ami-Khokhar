"""One-time helper: convert a background-removed photo into an ASCII portrait.

Usage: python3 ascii_portrait.py cutout.png portrait.txt
Not used by CI; generate.py reads the committed portrait.txt.
"""
import sys

from PIL import Image

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


def main():
    if len(sys.argv) != 3:
        sys.exit("usage: python3 ascii_portrait.py <input.png> <output.txt>")
    lines = image_to_ascii(Image.open(sys.argv[1]))
    with open(sys.argv[2], "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {len(lines)} lines to {sys.argv[2]}")


if __name__ == "__main__":
    main()

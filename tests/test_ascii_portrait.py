import unittest
from PIL import Image

from ascii_portrait import RAMP, image_to_ascii


def one_pixel(rgba):
    img = Image.new("RGBA", (1, 1))
    img.putpixel((0, 0), rgba)
    return img


class TestImageToAscii(unittest.TestCase):
    def test_black_pixel_is_densest_char(self):
        self.assertEqual(image_to_ascii(one_pixel((0, 0, 0, 255)), width=1), ["@"])

    def test_white_pixel_is_space(self):
        self.assertEqual(image_to_ascii(one_pixel((255, 255, 255, 255)), width=1), [" "])

    def test_transparent_pixel_is_space(self):
        self.assertEqual(image_to_ascii(one_pixel((0, 0, 0, 0)), width=1), [" "])

    def test_mid_gray_is_middle_ramp_char(self):
        self.assertEqual(image_to_ascii(one_pixel((128, 128, 128, 255)), width=1), ["|"])

    def test_rows_have_uniform_width(self):
        img = Image.new("RGBA", (10, 10), (0, 0, 0, 255))
        lines = image_to_ascii(img, width=6)
        self.assertTrue(lines)
        self.assertTrue(all(len(line) == 6 for line in lines))

    def test_ramp_shape(self):
        self.assertEqual(len(RAMP), 8)
        self.assertEqual(RAMP[0], "@")
        self.assertEqual(RAMP[-1], " ")


if __name__ == "__main__":
    unittest.main()

import math
import os
import shutil

from PIL import Image
from os.path import isfile, join


TEST_DIR = 'tests'
OUTPUT_DIR = 'output'


class SobelFilter(object):
    threshold = 10
    g_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
    g_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]

    def __init__(self, image):
        """
        :param image:
        :type image:
        """
        self.image = image

    def __apply_kernel(self, pixels):
        sum_x, sum_y = 0, 0

        for i in range(3):
            for j in range(3):
                channel_sum = sum(pixels[i][j])
                sum_x += self.g_x[i][j] * channel_sum
                sum_y += self.g_y[i][j] * channel_sum

        return int(math.sqrt(sum_x ** 2 + sum_y ** 2) / 4328 * 255)

    def apply_filter(self):
        new_image = Image.new("RGB", self.image.size, "white")

        for i in range(1, self.image.size[0] - 1):
            for j in range(1, self.image.size[1] - 1):

                kernel_pixels = []
                for w in range(i - 1, i + 2):
                    line = []
                    for h in range(j - 1, j + 2):
                        line.append(self.image.getpixel((w, h)))
                    kernel_pixels.append(line)

                new_pixel = self.__apply_kernel(kernel_pixels)
                new_image.putpixel((i, j), (new_pixel, new_pixel, new_pixel))

        return new_image


def main():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.mkdir(OUTPUT_DIR)

    test_files = [f for f in os.listdir(TEST_DIR) if isfile(join(TEST_DIR, f))]

    for file_name in test_files:
        print('Processing: ' + '/'.join([TEST_DIR, file_name]))
        image = Image.open(join(TEST_DIR, file_name))  # Can be many different formats.
        new_image = SobelFilter(image).apply_filter()
        new_image.save('/'.join([OUTPUT_DIR, file_name]))


if __name__== "__main__":
    main()

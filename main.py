import math
from PIL import Image


g_x = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]
g_y = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
threshold = 10


def apply_kernel(pixels):
    sum_x, sum_y = 0, 0

    for i in range(3):
        for j in range(3):
            channel_sum = sum(pixels[i][j])
            sum_x += g_x[i][j] * channel_sum
            sum_y += g_y[i][j] * channel_sum

    return int(math.sqrt(sum_x ** 2 + sum_y ** 2) / 4328 * 255)


def main():
    image = Image.open('tests/stadio.jpeg')  # Can be many different formats.
    pixels = image.load()
    print(pixels)

    new_image = Image.new("RGB", image.size, "white")

    for i in range(1, image.size[0] - 1):
        for j in range(1, image.size[1] - 1):

            kernel_pixels = []
            for w in range(i - 1, i + 2):
                line = []
                for h in range(j - 1, j + 2):
                    line.append(image.getpixel((w, h)))
                kernel_pixels.append(line)

            new_pixel = apply_kernel(kernel_pixels)
            new_image.putpixel((i, j), (new_pixel, new_pixel, new_pixel))

    new_image.save('alive_parrot.png')  # Save the modified pixels as .png
    pass


if __name__== "__main__":
    main()

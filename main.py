import argparse
import math
import os
import shutil

from PIL import Image

parser = argparse.ArgumentParser(description='Cartoonifier')
parser.add_argument('-e', '--edge', type=int, default=3, required=False,
                    help='Edge width')
parser.add_argument('-t', '--threshold', type=int, default=10, required=False,
                    help='Threshold for edge filter')
parser.add_argument('-f', '--file', type=str, required=True,
                    help='Path to file')
parser.add_argument('-p', '--palette', type=int, required=False, default=50,
                    help='The palette step')
parser.add_argument('-d', '--deviation', type=int, required=False, default=50,
                    help='The color expand allowed deviation')
args = parser.parse_args()


TEST_DIR = 'tests'
OUTPUT_DIR = 'output'
color_pallete = []


class SobelFilter(object):
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
                if new_pixel >= args.threshold:
                    new_pixel = 255
                else:
                    new_pixel = 0
                new_image.putpixel((i, j), (new_pixel, new_pixel, new_pixel))

        return new_image


def overlay_images(edges, image):
    new_image = Image.new("RGB", image.size, "white")
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            edge_pixel = edges.getpixel((i, j))
            img_pixel = image.getpixel((i, j))

            new_pixel = img_pixel
            if edge_pixel[0] == 255:
                new_pixel = (0, 0, 0)

            new_image.putpixel((i, j), new_pixel)

    return new_image


def get_distance(pixel1, pixel2):
    return math.sqrt((pixel1[0] - pixel2[0]) ** 2 + (pixel1[1] - pixel2[1]) ** 2 + (pixel1[2] - pixel2[2]) ** 2)


def get_intervals():
    global color_pallete
    for i in range(0, 255, args.palette):
        for j in range(0, 255, args.palette):
            for k in range(0, 255, args.palette):
                color_pallete.append((i + int(args.palette / 2),
                                      j + int(args.palette / 2),
                                      k + int(args.palette / 2)
                                      ))


def interval_reduce(image):
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            min_color, min_dist = None, 255
            for color in color_pallete:
                dist = get_distance(color, image.getpixel((i, j)))
                if dist < min_dist:
                    min_dist = dist
                    min_color = color

            image.putpixel((i, j), min_color)

    return image


def segmentation_reduce(image):
    step4 = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    step = step4

    image_map = [[0 for _ in range(image.size[1])] for _ in range(image.size[0])]
    index = 0
    pixel_mapping = dict()

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            if image_map[i][j]:
                continue

            index += 1
            queue = [(i, j)]

            while queue:
                position = queue.pop()

                if image_map[position[0]][position[1]]:
                    continue

                image_map[position[0]][position[1]] = index
                if index not in pixel_mapping:
                    pixel_mapping[index] = [image.getpixel(position), 1]
                else:
                    this_pixel = image.getpixel(position)
                    r = pixel_mapping[index][0][0] + this_pixel[0]
                    g = pixel_mapping[index][0][1] + this_pixel[1]
                    b = pixel_mapping[index][0][2] + this_pixel[2]
                    pixel_mapping[index][0] = (r, g, b)
                    pixel_mapping[index][1] += 1

                for direction in step:
                    new_pixel = (position[0] + direction[0], position[1] + direction[1])
                    if 0 <= new_pixel[0] < image.size[0] and 0 <= new_pixel[1] < image.size[1]:
                        if image_map[new_pixel[0]][new_pixel[1]]:
                            continue

                        if get_distance(image.getpixel(new_pixel), image.getpixel((i, j))) <= args.deviation:
                            queue.append(new_pixel)

    for key, value in pixel_mapping.items():
        pixel_mapping[key] = (int(value[0][0] / value[1]),
                              int(value[0][1] / value[1]),
                              int(value[0][2] / value[1]))

    for i in range(image.size[0]):
        for j in range(image.size[1]):
            image.putpixel((i, j), pixel_mapping[image_map[i][j]])

    return image


def zoom_edges(image):
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            pixel = image.getpixel((i, j))
            if pixel[0] == 255:
                # vertical expand
                for k in range(i, i - args.edge, -1):
                    if k < 0:
                        break
                    image.putpixel((k, j), (255, 255, 255))

                # horizontal expand
                for k in range(j, j - args.edge, -1):
                    if k < 0:
                        break
                    image.putpixel((i, k), (255, 255, 255))

    return image


def main():
    get_intervals()
    print('[INFO] Got {} color intervals.'.format(len(color_pallete)))

    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)

    os.mkdir(OUTPUT_DIR)

    print('Processing: ' + args.file)
    image = Image.open(args.file)  # Can be many different formats.

    file_name = os.path.basename(args.file)

    # apply the Sobel filter and get a binary edge image
    edges = SobelFilter(image).apply_filter()
    edges.save('/'.join([OUTPUT_DIR, 'edges_' + file_name]))

    # zoom edges
    edges = zoom_edges(edges)
    edges.save('/'.join([OUTPUT_DIR, 'zoomed_edges_' + file_name]))

    # combine the edges image with the original one
    combined = overlay_images(edges, image)
    combined.save('/'.join([OUTPUT_DIR, 'combined_' + file_name]))

    reduce = ''
    while reduce not in ('I', 'i', 'E', 'e'):
        reduce = input('Reduce color pallete (I/E): ')

    if reduce in ('I', 'i'):
        image = interval_reduce(combined)
    else:
        image = segmentation_reduce(combined)

    print('[INFO] Done applying reduce')
    image.save('/'.join([OUTPUT_DIR, file_name]))


if __name__ == "__main__":
    main()

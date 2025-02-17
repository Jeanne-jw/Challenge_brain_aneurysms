import numpy as np
from PIL import Image, ImageEnhance
from utils import get_raws, get_labels, load_data
from dataviz import view_sample, show_aneurysm


class DataEnhancer:
    def __init__(self, data):
        self.data = []
        raws = get_raws(data)
        labels = get_labels(data)
        sample_shape = raws[0].shape
        n_channels = sample_shape[0]

        for raw, label in zip(raws, labels):
            self.data.append([])
            for i in range(n_channels):
                self.data[-1].append([Image.fromarray(raw[i], mode='L'),
                                      Image.fromarray(label[i], mode='L')])

        self.data_shape = (len(self.data), *sample_shape)

    def raws(self):
        raws = np.empty(shape=self.data_shape, dtype=np.uint8)
        for i in range(self.data_shape[0]):
            for channel in range(self.data_shape[1]):
                raws[i][channel] = np.asarray(
                    self.data[i][channel][0], dtype=np.uint8)

        return raws

    def labels(self):
        labels = np.empty(shape=self.data_shape, dtype=np.uint8)
        for i in range(self.data_shape[0]):
            for channel in range(self.data_shape[1]):
                labels[i][channel] = np.asarray(
                    self.data[i][channel][1], dtype=np.uint8)

        return labels

    def rand_rotate(self, max_abs_rot):
        """
        Rotate all raws and labels by a random angle

        :param max_abs_rot: max rotation in degrees
        """
        for i in range(self.data_shape[0]):
            angle = 2 * (np.random.rand() - 0.5) * max_abs_rot

            for channel in range(self.data_shape[1]):
                raw, label = self.data[i][channel][0], self.data[i][channel][1]
                # todo : might have to use 'expand=True'
                self.data[i][channel][0] = raw.rotate(angle=angle)
                self.data[i][channel][1] = label.rotate(angle=angle)

    def sharpen(self, factor):
        """
        Sharpen labels and raws by a given factor

        :param factor: <= 1 : less sharp, == 1 : copy, >= 1 : more sharp
        """
        for i in range(self.data_shape[0]):
            for channel in range(self.data_shape[1]):
                raw, label = self.data[i][channel][0], self.data[i][channel][1]
                enhancer_raw = ImageEnhance.Sharpness(raw)
                enhancer_label = ImageEnhance.Sharpness(label)

                self.data[i][channel][0] = enhancer_raw.enhance(factor=factor)
                self.data[i][channel][1] = enhancer_label.enhance(
                    factor=factor)

    def contrast_raws(self, factor):
        """
        Contrast raws by a given factor

        :param factor: <= 1 : less contrast, == 1 : copy, >= 1 : more contrast
        """
        for i in range(self.data_shape[0]):
            for channel in range(self.data_shape[1]):
                raw = self.data[i][channel][0]
                enhancer_raw = ImageEnhance.Contrast(raw)

                self.data[i][channel][0] = enhancer_raw.enhance(factor=factor)

    def cluster_raws(self, n_colors: int, kmeans: int = 0, method=0):
        """
        Cluster images in clusters of colors

        :param n_colors: number of colors (clusters) to use, <= 256
        :param kmeans: convergence threshold, may be set to 0
        :param method: see https://pillow.readthedocs.io/en/stable/reference/Image.html#quantization-methods
        """
        for i in range(self.data_shape[0]):
            for channel in range(self.data_shape[1]):
                raw = self.data[i][channel][0]

                self.data[i][channel][0] = raw.quantize(
                    colors=n_colors, kmeans=kmeans, method=method)


def main():
    # For debugging purposes
    data = load_data('challenge_dataset/')
    enhancer = DataEnhancer(data=data)
    enhancer.rand_rotate(max_abs_rot=20.)  # rand_rotate : OK
    enhancer.contrast_raws(factor=1.4)  # contrast_raws : OK
    enhancer.sharpen(factor=1.15)  # sharpen : OK
    enhancer.cluster_raws(n_colors=3, kmeans=0)  # cluster_raws : OK
    raws = enhancer.raws()
    view_sample(raws, 0)
    labels = enhancer.labels()
    show_aneurysm(raws, labels, 0)


if __name__ == '__main__':
    main()

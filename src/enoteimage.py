import struct

from collections import namedtuple
from enum import Enum

from PIL import Image

from lzrw3 import lzrw3_decompress


class EnoteImageMode(Enum):
    thumbnail = 0
    full_size = 1
    uform_thumb = 2
    notebook = 3

    def dimensions(self):
        if self == EnoteImageMode.thumbnail:
            return (150, 175)
        elif self == EnoteImageMode.full_size:
            return (600, 700)
        elif self == EnoteImageMode.uform_thumb:
            return (156, 193)
        elif self == EnoteImageMode.notebook:
            return (220, 292)
        assert False

    def needs_endianness_hack(self):
        return (self == EnoteImageMode.full_size) or \
               (self == EnoteImageMode.uform_thumb)

    @classmethod
    def from_pixel_data_size(cls, size):
        for mode in cls:
            width, height = mode.dimensions()
            # every byte encodes two pixels
            if width * height == size * 2:
                return mode
        assert False


class EnoteImageLayer:
    def __init__(self, pixel_data):
        self.mode = EnoteImageMode.from_pixel_data_size(len(pixel_data))
        self.pixel_data = pixel_data

    def to_pil(self):
        corrected_data = []

        if self.mode.needs_endianness_hack():
            # note that this would skip the last byte if pixel_data could ever
            # have odd length (but it cannot)
            for i in range(len(self.pixel_data) // 2):
                a, b = self.pixel_data[2*i], self.pixel_data[2*i + 1]
                corrected_data.append(0x11 * (b >> 4))
                corrected_data.append(0x11 * (b & 0xF))
                corrected_data.append(0x11 * (a >> 4))
                corrected_data.append(0x11 * (a & 0xF))
        else:
            for a in self.pixel_data:
                corrected_data.append(0x11 * (a >> 4))
                corrected_data.append(0x11 * (a & 0xF))

        return Image.frombytes('L', self.mode.dimensions(),
            bytes(corrected_data))


class EnoteImage:
    def __init__(self, data):
        self.data = data
        self.layers = []
        self._parse_layers()

    def _parse_layers(self):
        num_layers, flag = struct.unpack('<HH', self.data[:4])
        needs_decompress = flag == 1

        layer_sizes = []
        for i in range(num_layers):
            size, = struct.unpack('<L', self.data[4+4*i:4+4*(i + 1)])
            layer_sizes.append(size)

        skip = 512

        for i, layer_size in enumerate(layer_sizes):
            pixel_data = self.data[skip:skip+layer_size]
            if needs_decompress:
                pixel_data = lzrw3_decompress(pixel_data)

            self.layers.append(EnoteImageLayer(pixel_data))

            size_padded = (layer_size >> 9) << 9
            if layer_size & ((1 << 9) - 1) != 0:
                size_padded += 1 << 9
            skip += size_padded

    def list_layers(self):
        return iter(self.layers)

import struct

from collections import namedtuple
from enum import Enum

from PIL import Image

from lzrw3 import lzrw3_decompress


class EnoteImageMode(Enum):
    thumbnail = 0
    full_size = 1
    uform_thumb = 2

    def dimensions(self):
        if self == EnoteImageMode.thumbnail:
            return (150, 175)
        elif self == EnoteImageMode.full_size:
            return (600, 700)
        elif self == EnoteImageMode.uform_thumb:
            return (156, 193)
        assert False


class EnoteImageLayer:
    def __init__(self, mode, pixel_data):
        dimensions = mode.dimensions()
        assert len(pixel_data) * 2 == dimensions[0] * dimensions[1]

        self.mode = mode
        self.pixel_data = pixel_data

    def to_pil(self):
        corrected_data = []

        if (self.mode == EnoteImageMode.full_size) or \
           (self.mode == EnoteImageMode.uform_thumb):
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
        num_layers, mode = struct.unpack('<HH', self.data[:4])
        mode = EnoteImageMode(mode)

        layer_sizes = []
        for i in range(num_layers):
            size, = struct.unpack('<L', self.data[4+4*i:4+4*(i + 1)])
            layer_sizes.append(size)

        skip = 512

        for i, layer_size in enumerate(layer_sizes):
            pixel_data = self.data[skip:skip+layer_size]
            if mode == EnoteImageMode.full_size:
                pixel_data = lzrw3_decompress(pixel_data)

            layer_mode = mode
            if (mode == EnoteImageMode.full_size) and \
               (len(layer_sizes) == 3) and (i > 0):
               # uforms contain 3 layers and are marked as full-size,
               # but the latter two layers are actually thumbs
               layer_mode = EnoteImageMode.uform_thumb

            self.layers.append(EnoteImageLayer(layer_mode, pixel_data))

            size_padded = (layer_size >> 9) << 9
            if layer_size & ((1 << 9) - 1) != 0:
                size_padded += 1 << 9
            skip += size_padded

    def list_layers(self):
        return iter(self.layers)

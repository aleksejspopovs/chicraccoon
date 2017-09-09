# Sharp electronic notebook internal image format

Image files (e.g. `PAGES/N000001/01/P0000001.RAW`) are organized like this:

| length (bytes) | field |
| -------------- | ----- |
| 512   | header             |
| 512*n | layer 1            |
| 512*m | layer 2 (optional) |
| 512*l | layer 3 (optional) |

Layers are ordered from bottom to top (so, in notes, layer 1 is marker and layer 2 is pen).

# Header

The header is organized like this:

| length (bytes) | field |
| -------------- | ----- |
| 2 | number of layers in file (observed: 1, 2, 3 (only in `UFORM/*`)) |
| 2 | mode (0 means thumbnail, 1 means full-size) |
| 4 | size of layer 1 data |
| 4 | size of layer 2 data (0 if not present) |
| 4 | size of layer 3 data (0 if not present) |
| 496 | padding (all zeroes) |

All integers are little-endian. Layer data sizes do not include padding.

# Layer data: thumbnails

Thumbnails are stored as raw pixels in row-major order, then padded with zeroes so that the total length is a multiple of 512.

Pairs of adjacent pixels XY are encoded as one byte `XY` (remember that pixels are 4 bits).

The size of the image is not stored anywhere, but it is 150x175 for a thumbnail.

# Layer data: full-size images

Layer data is compressed using Ross Williams' [LZRW3](https://web.archive.org/web/20170331101417/http://www.ross.net/compression/lzrw3.html), then padded with zeroes so that the total length is a multiple of 512.

After decompression, layer data contains raw pixels represented in almost row-major order. Quadruplets of adjacent pixels X, Y, Z, W are encoded as two bytes `ZW XY`, probably due to some endianness-related messup.

The size of the image is not stored anywhere, but it is 600x700 for a full-size image.

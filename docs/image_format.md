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
| 2 | compression (0 means uncompressed, 1 means LZRW3) |
| 4 | size of layer 1 data |
| 4 | size of layer 2 data (0 if not present) |
| 4 | size of layer 3 data (0 if not present) |
| 496 | padding (all zeroes) |

All integers are little-endian. Layer data sizes are *after* compression (if applicable), but do not include padding.

# Layer data: uncompressed

Layer data is stored as raw pixels in some order (see "Image sizes & pixel order" below), then padded with zeroes so that the total length is a multiple of 512.

# Layer data: LZRW3

Layer data is compressed using Ross Williams' [LZRW3](https://web.archive.org/web/20170331101417/http://www.ross.net/compression/lzrw3.html), then padded with zeroes so that the total length is a multiple of 512.

After decompression, layer data contains raw pixels in some order (see "Image sizes & pixel order" below).

# Image sizes & pixel order

Layer data does not contain any information about the dimensions of the image, so it is up to the application to figure that out, most likely either from the file name or the size of the uncompressed layer data. The order of pixels is also sometimes different in different images. Here's a table with the important information about all the image types I've found:

| description | dimensions | pixel order |
| ----------- | ---------- | ----------- |
| normal full-size images (pages of notes/schedule, refills) | 600x700 | messed up |
| most thumbnails | 150x175 | normal |
| uform thumbnails (layers 1 and 2 in `UFORM/*.RAW` contain two thumbnails for a refill in --- one "normal" and one "selected") | 156x193 | messed up |
| notebook covers | 220x292 | normal |

Size of layer data is always `(width * height) / 2` after uncompression (because each byte represents two pixels).

"Normal" pixel order means row-major order, where pairs of adjacent pixels with values X and Y (0 <= X, Y <= 15) are encoded as one byte `XY`.

"Messed up" order means *almost* row-major order, where quadruplets of adjacent pixels X, Y, Z, W are encoded as two bytes `ZW XY`, probably due to some endianness-related messup.

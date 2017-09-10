import io

from collections import namedtuple, OrderedDict

from chicraccoon.enoteimage import EnoteImage

def split_into_blocks(s, block_sizes):
    before = 0
    for size in block_sizes:
        yield s[before:before + size]
        before += size

EnoteBackupFile = namedtuple('EnoteBackupFile',
    ['filename', 'is_dir', 'size', 'mtime', 'offset'])

class EnoteBackup:
    def __init__(self, filename, mode='rb'):
        self.fileobj = open(filename, mode)
        self.files = OrderedDict()
        self._parse_files()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.fileobj.close()

    def _parse_int(self, s):
        return int(s[:-1], 8)

    def _parse_str(self, s):
        i = len(s)
        while (i > 0) and (s[i - 1] == 0):
            i -= 1
        return s[:i]

    def _parse_files(self):
        while True:
            header = self.fileobj.read(512)
            assert len(header) == 512

            if header == b'\x00' * 512:
                break

            filename, mode, _, _, size, mtime, cksum, _, _ \
                = split_into_blocks(header, [100, 8, 8, 8, 12, 12, 8, 1, 100])

            filename = self._parse_str(filename).replace(b'\\', b'/')
            size = self._parse_int(size)
            if filename.startswith(b'+,;='):
                mtime = 0
            else:
                mtime = int(mtime.strip(b'\x00'))
            is_dir = mode[1] == ord('4')

            self.files[filename] = EnoteBackupFile(filename=filename,
                is_dir=is_dir, size=size, mtime=mtime,
                offset=self.fileobj.tell())

            size_padded = (size >> 9) << 9
            if size & ((1 << 9) - 1) != 0:
                size_padded += 1 << 9
            self.fileobj.seek(size_padded, io.SEEK_CUR)

    def list_files(self):
        return iter(self.files.values())

    def find_file(self, path):
        if isinstance(path, str):
            path = path.encode('utf-8')

        return self.files.get(path)

    def extract_file(self, f):
        self.fileobj.seek(f.offset)
        data = self.fileobj.read(f.size)
        assert len(data) == f.size
        return data

    def extract_image(self, f):
        return EnoteImage(self.extract_file(f))

    def replace_file(self, f, data):
        assert len(data) == f.size
        self.fileobj.seek(f.offset)
        self.fileobj.write(data)

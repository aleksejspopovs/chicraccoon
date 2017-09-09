import io

# This is a Python implementation of LZRW3, a data compression algorithm
# invented by Ross Williams and placed in the public domain.
# More information about the algorithm, including a reference implementation in
# C, can be found at the Internet Archive copy of his website,
# https://web.archive.org/web/20170331101417/http://www.ross.net/compression/lzrw3.html

def lzrw3_decompress(instream):
    if isinstance(instream, bytes):
        instream = io.BytesIO(instream)
    elif isinstance(instream, list):
        instream = io.BytesIO(bytes(instream))


    def read_byte():
        byte = instream.read(1)
        if len(byte) == 0:
            return None
        return byte[0]


    result = []
    hash_table = [None for _ in range(4096)]

    _lzrw3_hash = lambda a, b, c: (((40543*((a<<8)^(b<<4)^c))>>4) & 0xFFF)
    lzrw3_hash = lambda p: _lzrw3_hash(result[p], result[p + 1], result[p + 2])
    def hash_table_get(x):
        if hash_table[x] is None:
            return b'123456789012345678'
        return result[hash_table[x]:]


    flag, *_ = [read_byte() for _ in range(4)]

    if flag == 1: # FLAG_COPY
        return instream.read()


    control = 1
    literals = 0

    while True:
        byte = read_byte()
        if byte is None:
            break

        if control == 1:
            control = 0x10000 | byte
            control |= read_byte() << 8
        elif control & 1:
            control >>= 1
            lenmt = byte
            p_ziv = len(result)
            p_hte = ((lenmt & 0xF0)<<4) | read_byte()
            lenmt &= 0xF

            for i in range(lenmt + 3):
                result.append(hash_table_get(p_hte)[i])

            if literals > 0:
                r = p_ziv - literals
                hash_table[lzrw3_hash(r)] = r
                if literals == 2:
                    r += 1
                    hash_table[lzrw3_hash(r)] = r
                literals = 0

            hash_table[p_hte] = p_ziv
        else:
            control >>= 1
            result.append(byte)

            literals += 1
            if literals == 3:
                r = len(result) - literals
                hash_table[lzrw3_hash(r)] = r
                literals -= 1


    return bytes(result)


def test_lzrw3():
    def test(comp, decomp):
        result = lzrw3_decompress(comp)
        assert result == decomp

    test(b'\x00\x00\x00\x00\xf0\xff\x68\x61\x68\x61\x0f\xe8',
         b'hahahahahahahahahahaha')

    test(b'\x01\x00\x00\x00I went down yesterday to the Piraeus with Glaucon the son of Ariston',
         b'I went down yesterday to the Piraeus with Glaucon the son of Ariston')

    test((b'\x00\x00\x00\x00\x00\x00\x49\x20\x77\x65\x6e\x74\x20\x64\x6f\x77'
          b'\x6e\x20\x79\x65\x73\x74\x00\x00\x65\x72\x64\x61\x79\x20\x74\x6f'
          b'\x20\x74\x68\x65\x20\x50\x69\x72\x00\x00\x61\x65\x75\x73\x20\x77'
          b'\x69\x74\x68\x20\x47\x6c\x61\x75\x63\x6f\x0a\x80\x6e\x32\x7d\x73'
          b'\xb0\xe4\x6f\x66\x20\x41\x72\x69\x73\x74\x6f\x6e\x2c\x30\x7d\x00'
          b'\x00\x61\x74\x20\x49\x20\x6d\x69\x67\x68\x74\x20\x6f\x66\x66\x65'
          b'\x72\x00\x40\x20\x75\x70\x20\x6d\x79\x20\x70\x72\x61\x79\x65\x72'
          b'\x73\x85\xc7\x67\x00\x40\x6f\x64\x64\x65\x73\x73\x20\x28\x42\x65'
          b'\x6e\x64\x69\x73\xd1\x50\x65\x00\x02\x20\x54\x68\x72\x61\x63\x69'
          b'\x61\x6e\xf0\xc5\x74\x65\x6d\x69\x73\x2e\x00\x00\x29\x3b\x20\x61'
          b'\x6e\x64\x20\x61\x6c\x73\x6f\x20\x62\x65\x63\x61\x08\x04\x75\x73'
          b'\x65\x30\xd5\x77\x61\x6e\x74\x65\x64\x81\xc7\x73\x65\x65\x20\x69'
          b'\x10\x06\x6e\x20\x77\x68\x30\xda\x6d\x61\x6e\x6e\x50\xe0\xf0\x8f'
          b'\x79\x20\x77\x6f\x75\x00\x10\x6c\x64\x20\x63\x65\x6c\x65\x62\x72'
          b'\x61\x74\x65\x30\x7d\x65\x20\x66\x00\x01\x65\x73\x74\x69\x76\x61'
          b'\x6c\x2c\x50\x1e\x69\x63\x68\x20\x77\x61\x73\x40\x08\x20\x61\x20'
          b'\x6e\x65\x77\x30\x7d\x69\x6e\x67\x2e\x32\xd5\x73\x20\x64\x65\x3e'
          b'\x0d\x6c\x01\x9e\x20\x0a\xf2\xb9\xf0\x8f\xf0\xf4\x6f\x63\xd0\x0d'
          b'\x69\xb3\xe4\xf1\x8f\x69\x6e\x68\x61\x08\xbc\x62\x69\x74\xc0\x7e'
          b'\x73\x3b\x20\x62\x75\x74\x30\x7d\x30\xda\x80\xec\xf1\x8f\x54\x64'
          b'\x71\x03\x00\x80\xd2\xb0\xff\x65\x71\x75\x61\x6c\x6c\x79\x2c\x20'
          b'\x69\x66\x20\x6e\x6f\x80\x00\x74\x20\x6d\x6f\x72\x65\x2c\xc0\x99'
          b'\x61\x75\x74\x69\x66\x75\x6c\x2e\x10\x00\x20\x57\x68\x65\xb0\x22'
          b'\x65\x20\x68\x61\x64\x20\x66\x69\x6e\x69\x73\xe2\x30\x68\x20\x0a'
          b'\x6f\x75\x72\xf0\xf4\x63\xae\xe1\x1f\x76\x69\x65\x77\x20\x0a\xf1'
          b'\x8f\x73\x70\x40\x71\x65\x63\x74\x61\x63\x6c\xc0\xc2\x77\xf0\xc0'
          b'\x75\x72\x6e\x20\x0a\xf0\x84\xf1\x8f\x64\x0c\x23\x69\x72\xc0\xe3'
          b'\xe8\xfa\x63\x69\x74\x79\x24\x8f\x84\xd0\x69\x6e\x73\x41\x0c\x20'
          b'\x50\x00\x07\x6f\x6c\x65\x6d\x61\x72\x63\x68\x30\x3f\xf1\x8f\x24'
          b'\x9a\x43\x65\x70\x68\x61\x82\xd1\x6c\x30\x3f\x63\x68\x61\x6e\x63'
          b'\x20\x0a\xf0\xb3\x63\x61\x74\x70\x66\x73\x01\x9e\xe0\x5a\xc2\x31'
          b'\x20\x30\x3f\x66\x72\x6f\x6d\xc0\xbd\xc0\xc3\x40\x0c\x63\x65\x20'
          b'\xb0\xff\x30\x89\x77\x65\x48\x8b\x72\x65\x20\x70\x63\x72\x74\xb0'
          b'\x51\x20\xb1\xe4\x40\xe0\x77\xb0\xb5\x68\x6f\x6d\xc0\xc2\x09\x30'
          b'\xe1\x1f\x74\x6f\xb0\x9a\x68\x69\x73\x20\x73\x65\x72\x76\xc0\x7e'
          b'\x81\xc7\x72\x75\x22\x00\x6e\x02\xcc\x62\x69\x64\x11\xff\x77\x61'
          b'\x69\x74\x20\x66\x6f\x72\x20\x68\x38\x0c\x69\x6d\x2e\x70\x9d\x50'
          b'\xda\x96\x1e\x6f\x6b\x20\x68\x61\xbd\x80\xec\x6d\x65\x20\x62\x83'
          b'\x20\x60\x80\x10\xb9\x63\x6c\x6f\x61\x6b\xc0\x99\x68\x69\x6e\x64'
          b'\x2c\x02\xcc\x73\x61\x18\x00\x69\x64\x3a\x6a\x63\x00\x4f\x69\x72'
          b'\x65\x73\x20\x79\x6f\x75\x20\x74\x6f\xc0\xff\x20\x77\x61\x69\x74'
          b'\x2e'),
         (b'I went down yesterday to the Piraeus with Glaucon the son of '
          b'Ariston, that I might offer up my prayers to the goddess (Bendis, '
          b'the Thracian Artemis.); and also because I wanted to see in what '
          b'manner they would celebrate the festival, which was a new thing. I '
          b'was delighted with the procession of the inhabitants; but that of '
          b'the Thracians was equally, if not more, beautiful. When we had '
          b'finished our prayers and viewed the spectacle, we turned in the '
          b'direction of the city; and at that instant Polemarchus the son of '
          b'Cephalus chanced to catch sight of us from a distance as we were '
          b'starting on our way home, and told his servant to run and bid us '
          b'wait for him. The servant took hold of me by the cloak behind, and '
          b'said: Polemarchus desires you to wait.'))


if __name__ == '__main__':
    test_lzrw3()

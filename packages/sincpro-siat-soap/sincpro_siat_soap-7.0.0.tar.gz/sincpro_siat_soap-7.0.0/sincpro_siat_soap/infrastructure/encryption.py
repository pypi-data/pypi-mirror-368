import struct
from base64 import b64encode
from hashlib import sha256


def long_to_bytes(n, blocksize=0):
    """long_to_bytes(n:long, blocksize:int) : string
    Convert a long integer to a byte string.

    If optional blocksize is given and greater than zero, pad the front of the
    byte string with binary zeros so that the length is a multiple of
    blocksize.
    """
    # after much testing, this algorithm was deemed to be the fastest
    s = b""

    pack = struct.pack
    while n > 0:
        s = pack(b">I", n & 0xFFFFFFFF) + s
        n = n >> 32
    # strip off leading zeros
    for i in range(len(s)):
        if s[i] != b"\000"[0]:
            break
    else:
        # only happens when n == 0
        s = b"\000"
        i = 0
    s = s[i:]
    # add back some pad bytes.  this could be done more efficiently w.r.t. the
    # de-padding being done above, but sigh...
    if blocksize > 0 and len(s) % blocksize:
        s = (blocksize - len(s) % blocksize) * b"\000" + s
    return s


def get_hash_base64(data: bytes | str, in_string_format=True) -> str | bytes:
    """Get the hash of a given data in base64 format."""
    data_to_transform = data

    if isinstance(data, str):
        data_to_transform: bytes = data.encode("utf-8")

    hash = sha256(data_to_transform)
    hash_base64 = b64encode(hash.digest())

    if in_string_format is True:
        return hash_base64.decode("utf-8")

    return hash_base64

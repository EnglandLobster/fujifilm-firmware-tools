import struct

from fujitools.dat import CODE_SIZES


def make_dat(payload: bytes, os_version: int = 6) -> bytes:
    model_size = CODE_SIZES[os_version]
    model_region = bytearray(b"3" * model_size)
    digits = b"00012301" + b"0" * (model_size // 2 - 8)
    model_region[1::2] = digits
    header = struct.pack("<I", os_version)
    versions = struct.pack("<4I", 1, 2, 0x12345678, 0)
    return header + bytes(model_region) + versions + payload


def make_literal_section(content: bytes) -> bytes:
    packed = b"".join(
        bytes([len(content[offset:offset + 127])]) + content[offset:offset + 127]
        for offset in range(0, len(content), 127)
    )
    pages = (len(packed) + 0x3FFF) // 0x4000
    header = struct.pack("<5I", len(content), len(packed), pages, 0x4000, 4)
    return header + packed


def xor_payload(data: bytes) -> bytes:
    return bytes(byte ^ 0xFF for byte in data)

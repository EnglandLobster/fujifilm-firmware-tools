"""Strict, read-only decoder for framed FFLZ sections observed in Fujifilm DAT files."""

from __future__ import annotations

import struct
from dataclasses import dataclass


class DecodeError(ValueError):
    """A section violates the observed framing or token format."""


@dataclass(frozen=True)
class Header:
    offset: int
    unpacked_size: int
    packed_size: int
    pages: int
    page_size: int
    tag: int

    @property
    def start(self) -> int:
        return self.offset + 20

    @property
    def end(self) -> int:
        return self.start + self.packed_size


def read_header(data: bytes, offset: int) -> Header:
    if offset < 0 or offset + 20 > len(data):
        raise DecodeError("truncated section header")
    header = Header(offset, *struct.unpack_from("<5I", data, offset))
    if header.page_size != 0x4000 or header.tag != 4:
        raise DecodeError("unsupported section framing")
    if not header.packed_size or not header.unpacked_size:
        raise DecodeError("empty section")
    if header.pages != (header.packed_size + 0x3FFF) // 0x4000:
        raise DecodeError("page count does not match packed size")
    if header.end > len(data):
        raise DecodeError("section exceeds input")
    return header


def find_headers(data: bytes) -> list[Header]:
    """Return framing candidates; decode each candidate to validate its output."""
    marker = struct.pack("<II", 0x4000, 4)
    result = []
    pos = data.find(marker)
    while pos >= 0:
        if pos >= 12:
            try:
                result.append(read_header(data, pos - 12))
            except DecodeError:
                pass
        pos = data.find(marker, pos + 1)
    return result


def decode_tokens(packed: bytes, expected_size: int, *, max_output: int = 0x4000000) -> bytes:
    """Decode bounded tokens and require the exact independently supplied size.

    00..7F copies the next N bytes literally. 80..FF is a two-byte
    back-reference: the low nibble of the second byte is the copy length.
    Zero-length literals are padding; zero-length references are rejected.
    """
    if not 0 <= expected_size <= max_output:
        raise DecodeError("output size exceeds configured limit")
    output = bytearray()
    pos = 0
    while pos < len(packed):
        token_pos = pos
        token = packed[pos]
        pos += 1
        if token < 0x80:
            length = token
            if pos + length > len(packed):
                raise DecodeError(f"truncated literal at {token_pos:#x}")
            if len(output) + length > expected_size:
                raise DecodeError(f"literal exceeds declared output at {token_pos:#x}")
            output.extend(packed[pos:pos + length])
            pos += length
        else:
            if pos >= len(packed):
                raise DecodeError(f"truncated reference at {token_pos:#x}")
            tail = packed[pos]
            pos += 1
            length = tail & 15
            distance = ((token & 127) << 4) | (tail >> 4)
            if not length or not 0 < distance <= len(output):
                raise DecodeError(f"invalid reference at {token_pos:#x}")
            if len(output) + length > expected_size:
                raise DecodeError(f"reference exceeds declared output at {token_pos:#x}")
            for _ in range(length):
                output.append(output[-distance])
    if len(output) != expected_size:
        raise DecodeError(f"output size {len(output):#x} != declared {expected_size:#x}")
    return bytes(output)


def decode_section(data: bytes, header: Header) -> bytes:
    return decode_tokens(data[header.start:header.end], header.unpacked_size)

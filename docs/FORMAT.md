# Observed firmware formats

This document describes only the formats implemented by the current decoder. It is not a specification for every Fujifilm firmware generation.

## DAT container

The parser recognizes DAT `os` versions 1, 2, 3, 4, 5, 6, and 8. All integers described here are little-endian.

| Offset | Meaning |
| --- | --- |
| `0x000` | 32-bit DAT `os` version |
| `0x004` | Model-code region: 64 bytes for `os=1`, 128 for `os=2`, otherwise 512 |
| after model region | Four 32-bit values: major version, minor version, checksum, end/type flag |
| after those values | Payload |

The model-code region stores digit characters at odd byte offsets, interleaved with `0x33`. The minor version is formatted as hexadecimal in the human-readable firmware version.

For the observed cameras, parts of the payload are obfuscated by XOR with `0xFF`, equivalent to bitwise inversion. The `xview` command applies this transform to the entire payload. This makes obfuscated code readable but inverts regions that were already plaintext; it is an analysis view, not a universally valid replacement firmware image.

## Framed FFLZ sections

The strict decoder recognizes a 20-byte section header in the XOR view:

| Header offset | Field | Observed requirement |
| --- | --- | --- |
| `+0` | `unpacked_size` | Exact required output size, nonzero |
| `+4` | `packed_size` | Token byte count, nonzero |
| `+8` | `pages` | `ceil(packed_size / 0x4000)` |
| `+12` | `page_size` | `0x4000` |
| `+16` | `tag` | `4` |
| `+20` | Token stream | Exactly `packed_size` bytes |

`find_headers()` locates framing candidates. A candidate is reported as decoded only after the token stream reaches the independently declared output length without violating bounds.

### Tokens

- `00..7F`: literal token. Copy the following `N` bytes verbatim. A zero-length literal is padding.
- `80..FF B`: two-byte back-reference. Copy `B & 0x0F` bytes from `((token & 0x7F) << 4) | (B >> 4)` bytes back in the output. `FF` has no special three-byte escape meaning in this format.

Back-references may overlap the bytes being produced. Zero-length references, references before the start of output, truncated tokens, output beyond the declared size, and short final output are rejected. The default maximum output per section is 64 MiB.

## Security and integrity boundary

XOR deobfuscation and FFLZ decompression are reading operations. Firmware signatures and update-package integrity checks are separate concerns. This project neither bypasses those checks nor produces flashable images.

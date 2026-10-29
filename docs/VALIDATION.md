# Validation

## Cross-model official firmware check

Date: 2026-10-29.

Three official DAT files were downloaded from Fujifilm and processed offline. The test covered DAT parsing, XOR `0xFF` view generation, strict FFLZ candidate discovery, and exact-length section decoding. No camera or flashing operation was performed.

| Camera | Version | Official source | DAT `os` | Candidates | Decoded | Rejected | Decoded bytes |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| X-T4 | 2.12 | [Fujifilm support](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t4/) | 6 | 4 | 4 | 0 | 33,543,940 |
| X100V | 3.01 | [Fujifilm support](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x100v/) | 6 | 2 | 2 | 0 | 14,873,408 |
| X-T5 | 4.31 | [Fujifilm support](https://www.fujifilm-x.com/global/support/download/firmware/cameras/x-t5/) | 6 | 4 | 4 | 0 | 49,025,752 |

Total: 10 recognized sections, 97,443,100 decoded bytes, zero rejected candidates.

Input SHA-256 values:

```text
X-T4 2.12   853d273b5603d3a2b93493f0ebd6a762b0b4b6bdc70317777775ae5f8ed93bc5
X100V 3.01  18351a9a552c06ec9c70483abca1b74ab2a29fa139f19aef244e178045323591
X-T5 4.31   790d6deecf26766188b0e506e40645e6b816addfeba39a52334349405421724e
```

Decoded content contained readable camera symbols, including `FUJIFILM`, `MOVIE`, `4K`, and `FPS`. Examples from the X-T5 output included `MODE_PIXEL_4K`, `MODE_PIXEL_4KHQ`, `HDDCI4K_5994`, and `MOVIE_REC_START`.

The original DAT files and generated binary output are intentionally not included in this repository. These results establish compatibility with the listed samples only.

## Synthetic tests

The test suite covers observed ARM-prefix decoding, overlapping back-references, `FF` token behavior, malformed and unbounded input, DAT parsing, and end-to-end CLI unpacking with synthetic data:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

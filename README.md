# Fujifilm Firmware Tools

[中文说明](README.zh-CN.md) · [Format notes](docs/FORMAT.md) · [Validation](docs/VALIDATION.md)

Offline, read-only tools for inspecting Fujifilm DAT firmware, creating an XOR `0xFF` deobfuscated view, and decompressing framed FFLZ sections. The package uses only the Python standard library and performs no camera, USB, or flashing operations.

## Features

- Parse DAT container versions, model codes, firmware versions, and payload offsets.
- Generate an XOR `0xFF` view of the DAT payload.
- Locate framed FFLZ sections and decode them with strict input and output bounds.
- Save decoded sections with SHA-256 hashes and a machine-readable `manifest.json`.
- Provide a Python API and the `fujitools` command-line tool.

## Validated firmware

The current decoder has been run against these official DAT files:

| Camera | Firmware | FFLZ sections decoded |
| --- | --- | ---: |
| Fujifilm X-T4 | 2.12 | 4/4 |
| Fujifilm X100V | 3.01 | 2/2 |
| Fujifilm X-T5 | 4.31 | 4/4 |

This demonstrates cross-model compatibility for the observed format, not support for every Fujifilm camera or container generation. See [validation details and source hashes](docs/VALIDATION.md).

## Installation

Python 3.10 or newer is required.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install .
```

For development, use an editable install:

```sh
python -m pip install -e .
```

You can also run directly from a checkout without installing:

```sh
PYTHONPATH=src python3 -m fujitools --help
```

On Windows PowerShell, set `$env:PYTHONPATH = "src"` before running `python -m fujitools`.

## Usage

Inspect an original firmware file:

```sh
fujitools info FWUP0024.DAT
fujitools info FWUP0024.DAT --json
```

Write only the XOR view:

```sh
fujitools xview FWUP0024.DAT -o firmware.xor.bin
```

Write the XOR view, all recognized FFLZ sections, and the manifest:

```sh
fujitools unpack FWUP0024.DAT -o out/xt4-2.12
```

Use `--strict` when automation should fail if no section decodes or any framing candidate is rejected:

```sh
fujitools unpack FWUP0024.DAT -o out/xt4-2.12 --strict
```

Output layout:

```text
out/xt4-2.12/
├── firmware.xor.bin
├── manifest.json
└── sections/
    ├── 00260060.bin
    └── ...
```

Firmware files are not distributed with this repository. Obtain them from Fujifilm's official support pages and review the applicable terms before use.

## Scope and limitations

- “Decryption” here means reversing the simple XOR `0xFF` obfuscation and decompressing FFLZ data.
- The XOR view transforms the entire payload. Regions already stored as plaintext become inverted in that view.
- FFLZ support targets the 20-byte framed sections described in [FORMAT.md](docs/FORMAT.md). Unknown or different formats are reported rather than silently modified.
- This project does not bypass firmware signatures, repack firmware, write camera memory, or flash devices.
- Successful section decoding does not mean every embedded resource or filesystem has been semantically unpacked.

## Development

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Tests use synthetic fixtures and do not require proprietary firmware or camera hardware. Contributions should follow [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT; see [LICENSE](LICENSE). Fujifilm firmware and camera names remain the property of their respective owners. This is an independent interoperability and research project, not an official Fujifilm product.

"""Command-line interface for offline Fujifilm firmware inspection and unpacking."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from . import __version__
from .dat import DatError, DatFile
from .fflz_sections import DecodeError, decode_section, find_headers


def cmd_info(args: argparse.Namespace) -> int:
    dat = DatFile.open(args.dat)
    if args.json:
        print(json.dumps(dat.to_dict(), indent=2))
    else:
        print(dat.summary())
    return 0


def cmd_xview(args: argparse.Namespace) -> int:
    dat = DatFile.open(args.dat)
    output = Path(args.output) if args.output else dat.path.with_suffix(".xor.bin")
    view = dat.xor_view()
    output.write_bytes(view)
    print(f"XOR view: {len(view):,} bytes -> {output}")
    return 0


def cmd_unpack(args: argparse.Namespace) -> int:
    dat = DatFile.open(args.dat)
    output = Path(args.output)
    sections_dir = output / "sections"
    sections_dir.mkdir(parents=True, exist_ok=True)

    view = dat.xor_view()
    xor_name = "firmware.xor.bin"
    (output / xor_name).write_bytes(view)

    records = []
    for header in find_headers(view):
        record = {
            "offset": header.offset,
            "offset_hex": f"0x{header.offset:08x}",
            "packed_size": header.packed_size,
            "unpacked_size": header.unpacked_size,
        }
        try:
            decoded = decode_section(view, header)
            relative_path = f"sections/{header.offset:08x}.bin"
            (output / relative_path).write_bytes(decoded)
            record.update(
                status="decoded",
                output=relative_path,
                sha256=hashlib.sha256(decoded).hexdigest(),
            )
        except DecodeError as error:
            record.update(status="rejected", error=str(error))
        records.append(record)

    decoded = sum(record["status"] == "decoded" for record in records)
    rejected = sum(record["status"] == "rejected" for record in records)
    manifest = {
        "tool": "fujifilm-firmware-tools",
        "tool_version": __version__,
        "input": dat.to_dict(),
        "xor_view": xor_name,
        "fflz": {
            "candidates": len(records),
            "decoded": decoded,
            "rejected": rejected,
            "decoded_bytes": sum(
                record["unpacked_size"] for record in records
                if record["status"] == "decoded"
            ),
            "sections": records,
        },
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        f"DAT {dat.version}: {decoded} FFLZ sections decoded, "
        f"{rejected} rejected -> {output}"
    )
    if args.strict and (rejected or not decoded):
        print("strict mode requires at least one decoded section and no rejected candidates")
        return 2
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fujitools",
        description="Offline Fujifilm DAT parsing, XOR deobfuscation and FFLZ decoding.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    info = subparsers.add_parser("info", help="inspect a DAT container")
    info.add_argument("dat", help="original Fujifilm DAT firmware")
    info.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    info.set_defaults(fn=cmd_info)

    xview = subparsers.add_parser("xview", help="write the payload XOR 0xFF view")
    xview.add_argument("dat", help="original Fujifilm DAT firmware")
    xview.add_argument("-o", "--output", help="output file (default: beside the DAT)")
    xview.set_defaults(fn=cmd_xview)

    unpack = subparsers.add_parser("unpack", help="write XOR view and decode all recognized FFLZ sections")
    unpack.add_argument("dat", help="original Fujifilm DAT firmware")
    unpack.add_argument("-o", "--output", required=True, help="output directory")
    unpack.add_argument(
        "--strict",
        action="store_true",
        help="fail if no section decodes or any framing candidate is rejected",
    )
    unpack.set_defaults(fn=cmd_unpack)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.fn(args)
    except (OSError, DatError) as error:
        parser.exit(1, f"error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())

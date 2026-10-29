"""Fujifilm DAT container parsing and XOR 0xFF view generation."""

from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass, field
from pathlib import Path

CODE_SIZES = {1: 64, 2: 128, 3: 512, 4: 512, 5: 512, 6: 512, 8: 512}


class DatError(ValueError):
    """The input is not a supported DAT container."""


@dataclass
class DatFile:
    path: Path
    os_ver: int = 0
    model_code: str = ""
    model_variants: dict[str, list[str]] = field(default_factory=dict)
    version: str = ""
    checksum: int = 0
    end_flag: int = 0
    payload_offset: int = 0
    sha256: str = ""

    @classmethod
    def open(cls, path: str | Path) -> "DatFile":
        p = Path(path)
        data = p.read_bytes()
        if len(data) < 4:
            raise DatError(f"truncated DAT header: {p}")
        os_ver, = struct.unpack_from("<I", data, 0)
        if os_ver not in CODE_SIZES:
            raise DatError(f"unsupported DAT format version {os_ver}: {p}")
        n = CODE_SIZES[os_ver]
        payload_offset = 4 + n + 16
        if len(data) < payload_offset:
            raise DatError(f"truncated DAT model or version block: {p}")

        code_raw = data[4:4 + n]
        digits = "".join(chr(code_raw[i]) for i in range(1, len(code_raw), 2))
        model_code = digits.rstrip("0\x00")
        major, minor, checksum, end = struct.unpack_from("<4I", data, 4 + n)

        variants: dict[str, list[str]] = {}
        for i in range(0, len(model_code) - 7, 8):
            group = model_code[i:i + 8]
            variants.setdefault(group[:6], []).append(group[6:])

        return cls(
            path=p,
            os_ver=os_ver,
            model_code=model_code,
            model_variants=variants,
            version=f"{major}.{minor:02X}",
            checksum=checksum,
            end_flag=end,
            payload_offset=payload_offset,
            sha256=hashlib.sha256(data).hexdigest(),
        )

    @property
    def raw(self) -> bytes:
        return self.path.read_bytes()

    def xor_view(self) -> bytes:
        """XOR the payload with 0xFF; plaintext resource regions become inverted."""
        data = self.raw
        return bytes(byte ^ 0xFF for byte in data[self.payload_offset:])

    def to_dict(self) -> dict:
        return {
            "file": self.path.name,
            "bytes": self.path.stat().st_size,
            "sha256": self.sha256,
            "os_version": self.os_ver,
            "firmware_version": self.version,
            "checksum": f"0x{self.checksum:08x}",
            "end_flag": self.end_flag,
            "model_code": self.model_code,
            "model_variants": self.model_variants,
            "payload_offset": self.payload_offset,
        }

    def summary(self) -> str:
        lines = [
            f"File:           {self.path.name} ({self.path.stat().st_size:,} bytes)",
            f"SHA-256:        {self.sha256}",
            f"DAT version:    os={self.os_ver}",
            f"Firmware:       {self.version}",
            f"Checksum:       0x{self.checksum:08x}",
            f"End flag:       {self.end_flag}",
            f"Model codes:    {self.model_code}",
            f"Payload offset: 0x{self.payload_offset:x}",
        ]
        for base, variants in self.model_variants.items():
            lines.append(f"  {base}: regional variants {', '.join(variants)}")
        return "\n".join(lines)

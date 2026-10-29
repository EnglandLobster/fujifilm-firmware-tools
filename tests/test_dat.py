import tempfile
import unittest
from pathlib import Path

from fixtures import make_dat
from fujitools.dat import DatError, DatFile


class DatFileTests(unittest.TestCase):
    def test_parses_header_and_generates_xor_view(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.DAT"
            path.write_bytes(make_dat(b"\x00\xff\x5a"))
            dat = DatFile.open(path)
            self.assertEqual(dat.os_ver, 6)
            self.assertEqual(dat.version, "1.02")
            self.assertEqual(dat.payload_offset, 0x214)
            self.assertEqual(dat.model_variants, {"000123": ["01"]})
            self.assertEqual(dat.xor_view(), b"\xff\x00\xa5")
            self.assertEqual(dat.to_dict()["bytes"], 535)

    def test_rejects_unknown_or_truncated_container(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.DAT"
            path.write_bytes(b"\x07\x00\x00\x00")
            with self.assertRaises(DatError):
                DatFile.open(path)
            path.write_bytes(b"\x06")
            with self.assertRaises(DatError):
                DatFile.open(path)


if __name__ == "__main__":
    unittest.main()

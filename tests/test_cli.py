import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from fixtures import make_dat, make_literal_section, xor_payload
from fujitools.cli import main


class CliTests(unittest.TestCase):
    def test_info_json_and_xview(self):
        with tempfile.TemporaryDirectory() as directory:
            dat_path = Path(directory) / "synthetic.DAT"
            dat_path.write_bytes(make_dat(b"\x00\xff"))
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                self.assertEqual(main(["info", str(dat_path), "--json"]), 0)
            self.assertEqual(json.loads(stdout.getvalue())["firmware_version"], "1.02")

            output = Path(directory) / "view.bin"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["xview", str(dat_path), "-o", str(output)]), 0)
            self.assertEqual(output.read_bytes(), b"\xff\x00")

    def test_unpack_writes_verified_section_and_manifest(self):
        content = b"FUJIFILM synthetic MOVIE MODE_PIXEL_4K" * 8
        clear_section = make_literal_section(content)
        with tempfile.TemporaryDirectory() as directory:
            dat_path = Path(directory) / "synthetic.DAT"
            dat_path.write_bytes(make_dat(xor_payload(clear_section)))
            output = Path(directory) / "out"
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["unpack", str(dat_path), "-o", str(output), "--strict"]), 0)

            section = output / "sections" / "00000000.bin"
            self.assertEqual(section.read_bytes(), content)
            self.assertEqual((output / "firmware.xor.bin").read_bytes(), clear_section)
            manifest = json.loads((output / "manifest.json").read_text())
            self.assertEqual(manifest["fflz"]["decoded"], 1)
            self.assertEqual(manifest["fflz"]["rejected"], 0)
            self.assertEqual(manifest["fflz"]["decoded_bytes"], len(content))


if __name__ == "__main__":
    unittest.main()

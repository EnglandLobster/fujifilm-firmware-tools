import unittest

from fujitools.fflz_sections import DecodeError, decode_tokens


class SectionDecoderTests(unittest.TestCase):
    def test_observed_arm_prefix(self):
        packed = bytes.fromhex("0b 00 00 ff ff aa aa 00 50 2d e9 0f 80 43")
        expected = bytes.fromhex("00 00 ff ff aa aa 00 50 2d e9 0f 50 2d e9")
        self.assertEqual(decode_tokens(packed, len(expected)), expected)

    def test_overlapping_copy_and_padding(self):
        self.assertEqual(decode_tokens(b"\x01A\x80\x1f\x00", 16), b"A" * 16)

    def test_ff_is_two_byte_reference(self):
        history = bytes(range(256)) * 7 + bytes(range(240))
        packed = b"".join(
            bytes([len(history[i:i + 127])]) + history[i:i + 127]
            for i in range(0, len(history), 127)
        )
        self.assertEqual(
            decode_tokens(packed + b"\xff\x0f", len(history) + 15),
            history + history[:15],
        )

    def test_rejects_malformed_or_unbounded_output(self):
        cases = [
            (b"\x02A", 2),
            (b"\x80", 1),
            (b"\x80\x11", 1),
            (b"\x01A", 0),
            (b"\x01A", 2),
            (b"\x80\x00", 0),
        ]
        for packed, size in cases:
            with self.subTest(packed=packed, size=size), self.assertRaises(DecodeError):
                decode_tokens(packed, size)


if __name__ == "__main__":
    unittest.main()

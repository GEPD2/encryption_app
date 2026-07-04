"""Round-trip and passthrough tests for the classical ciphers."""
import unittest

from crypto.classical import (
    encrypt_caesar, decrypt_caesar, affine_cipher,
    encrypt_vigenere, decrypt_vigenere,
)

SAMPLE = "The quick brown Fox, jumps over 13 lazy Dogs!"


class TestCaesar(unittest.TestCase):
    def test_roundtrip(self):
        for key in range(1, 26):
            self.assertEqual(decrypt_caesar(encrypt_caesar(SAMPLE, key), key), SAMPLE)

    def test_non_alpha_passthrough(self):
        self.assertEqual(encrypt_caesar("12 !?", 5), "12 !?")


class TestAffine(unittest.TestCase):
    def test_roundtrip(self):
        # a must be coprime with 26 for the cipher to be invertible.
        for a in (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
            for b in (0, 4, 11, 25):
                enc, fail = affine_cipher(SAMPLE, a, b, "encrypt")
                self.assertFalse(fail)
                dec, fail = affine_cipher(enc, a, b, "decrypt")
                self.assertFalse(fail)
                self.assertEqual(dec, SAMPLE)

    def test_non_invertible_key_fails(self):
        _, fail = affine_cipher(SAMPLE, 2, 3, "decrypt")
        self.assertTrue(fail)


class TestVigenere(unittest.TestCase):
    def test_roundtrip(self):
        for key in ("KEY", "LEMON", "a", "longkeyword"):
            self.assertEqual(decrypt_vigenere(encrypt_vigenere(SAMPLE, key), key), SAMPLE)

    def test_non_alpha_passthrough(self):
        self.assertEqual(encrypt_vigenere("42 ...", "KEY"), "42 ...")


if __name__ == "__main__":
    unittest.main()

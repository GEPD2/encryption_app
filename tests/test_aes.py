"""AES-256-GCM round-trip, tamper, and wrong-key tests."""
import os
import unittest

from cryptography.exceptions import InvalidTag

from crypto import aes


class TestAESGCM(unittest.TestCase):
    def setUp(self):
        self.key = os.urandom(32)
        self.msg = b"attack at dawn, bring coffee"

    def test_roundtrip(self):
        blob = aes.encrypt(self.key, self.msg)
        self.assertEqual(aes.decrypt(self.key, blob), self.msg)

    def test_roundtrip_with_aad(self):
        blob = aes.encrypt(self.key, self.msg, aad=b"header")
        self.assertEqual(aes.decrypt(self.key, blob, aad=b"header"), self.msg)

    def test_tamper_raises(self):
        blob = bytearray(aes.encrypt(self.key, self.msg))
        blob[-1] ^= 0x01
        with self.assertRaises(InvalidTag):
            aes.decrypt(self.key, bytes(blob))

    def test_wrong_key_raises(self):
        blob = aes.encrypt(self.key, self.msg)
        with self.assertRaises(InvalidTag):
            aes.decrypt(os.urandom(32), blob)

    def test_bad_key_length(self):
        with self.assertRaises(ValueError):
            aes.encrypt(os.urandom(16), self.msg)


if __name__ == "__main__":
    unittest.main()

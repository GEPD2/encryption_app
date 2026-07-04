"""AES-256-GCM authenticated encryption, keyed by a Kyber shared secret.

GCM is chosen over CBC on purpose: it authenticates, so a wrong key or a
tampered ciphertext raises rather than returning garbage. That failure mode is
the teaching point of the KEM+AES message mode.
"""
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

NONCE_BYTES = 12


def encrypt(key32: bytes, plaintext: bytes, aad: bytes = b"") -> bytes:
    """Encrypt plaintext. Returns nonce || ciphertext-with-tag as one blob."""
    if len(key32) != 32:
        raise ValueError("AES-256-GCM requires a 32-byte key")
    nonce = os.urandom(NONCE_BYTES)
    ct = AESGCM(key32).encrypt(nonce, plaintext, aad)
    return nonce + ct


def decrypt(key32: bytes, blob: bytes, aad: bytes = b"") -> bytes:
    """Decrypt a nonce || ciphertext blob. Raises InvalidTag on tamper/wrong key."""
    if len(key32) != 32:
        raise ValueError("AES-256-GCM requires a 32-byte key")
    nonce, ct = blob[:NONCE_BYTES], blob[NONCE_BYTES:]
    return AESGCM(key32).decrypt(nonce, ct, aad)

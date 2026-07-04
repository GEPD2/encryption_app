"""Public ML-KEM (Kyber) API for the toolkit.

A small UI-friendly surface that pulls its own randomness from os.urandom, so
callers never touch seeds. The deterministic mlkem_* functions remain available
for the test harness, which is the only place a fixed seed is allowed.

Educational build: this pure-Python ML-KEM is not constant-time and does not
securely erase keys. Not for production use.
"""
import os

from .params import BY_NAME, MLKEM512, MLKEM768, MLKEM1024, SS_BYTES
from .mlkem import mlkem_keygen, mlkem_encaps, mlkem_decaps

DEFAULT = "ML-KEM-768"


def keygen(param_name=DEFAULT):
    """Generate a keypair. Returns (ek, dk) as raw bytes."""
    p = BY_NAME[param_name]
    d, z = os.urandom(32), os.urandom(32)
    return mlkem_keygen(p, d, z)


def encaps(param_name, ek):
    """Encapsulate to an encapsulation key. Returns (shared_secret, ciphertext)."""
    p = BY_NAME[param_name]
    m = os.urandom(32)
    return mlkem_encaps(p, ek, m)


def decaps(param_name, dk, ct):
    """Decapsulate a ciphertext. Returns the shared_secret."""
    p = BY_NAME[param_name]
    return mlkem_decaps(p, dk, ct)


__all__ = [
    "keygen", "encaps", "decaps",
    "BY_NAME", "MLKEM512", "MLKEM768", "MLKEM1024", "SS_BYTES", "DEFAULT",
]

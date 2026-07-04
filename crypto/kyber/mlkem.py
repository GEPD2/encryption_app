"""Layer 3: ML-KEM, the IND-CCA2 KEM (FIPS 203).

The Fujisaki-Okamoto transform wraps the CPA-secure K-PKE so that a tampered
ciphertext cannot leak the secret. Decaps re-encrypts and, on a mismatch,
returns a pseudo-random secret (implicit rejection) rather than an error.

Not constant-time, does not zero secrets. Research/education only. In
particular, the ciphertext comparison in decaps below is a plain Python byte
compare and is not constant-time; a production KEM must compare in constant time.
"""
from .params import POLY_BYTES
from .primitives import H, G, J, byte_decode12_validate
from .kpke import kpke_keygen, kpke_encrypt, kpke_decrypt


def mlkem_keygen(p, d: bytes, z: bytes):
    """Run K-PKE keygen, then bundle dk = dkPKE || ek || H(ek) || z.

    H(ek) lets decaps re-derive the transform input; z is the secret that makes
    implicit rejection deterministic but unpredictable.
    """
    ek, dkpke = kpke_keygen(p, d)
    dk = dkpke + ek + H(ek) + bytes(z)
    return ek, dk


def mlkem_encaps(p, ek: bytes, m: bytes):
    """Encapsulate: derive (K, r) = G(m || H(ek)), encrypt m under coins r.

    The shared secret K and the coins come from the same hash, so the ciphertext
    is a deterministic function of m. Returns (shared_secret, ciphertext).

    Validates the encapsulation key first (FIPS 203): a wrong length or a
    non-canonical coefficient (>= q) is rejected rather than silently accepted.
    """
    if len(ek) != p.pke_pk_bytes:
        raise ValueError("encapsulation key has wrong length")
    for i in range(p.k):
        if byte_decode12_validate(ek[i * POLY_BYTES:(i + 1) * POLY_BYTES]) is None:
            raise ValueError("encapsulation key is non-canonical (coefficient >= q)")

    kr = G(bytes(m) + H(ek))                  # (K, r) = G(m || H(ek))
    shared_secret = kr[:32]
    ciphertext = kpke_encrypt(p, ek, m, kr[32:])
    return shared_secret, ciphertext


def mlkem_decaps(p, dk: bytes, c: bytes):
    """Decapsulate: recover m', re-derive (K', r'), and re-encrypt.

    If the fresh ciphertext c' equals the received c the sender was honest and
    K' is the key. Otherwise return J(z || c), a pseudo-random reject key, so a
    chosen-ciphertext attacker learns nothing from the failure.
    """
    if len(dk) != p.dk_bytes:
        raise ValueError("decapsulation key has wrong length")
    if len(c) != p.ct_bytes:
        raise ValueError("ciphertext has wrong length")

    off = p.pke_sk_bytes
    dkpke = dk[:off]
    ek = dk[off:off + p.pke_pk_bytes]
    off += p.pke_pk_bytes
    h = dk[off:off + 32]
    z = dk[off + 32:]

    mp = kpke_decrypt(p, dkpke, c)            # m'
    kr = G(bytes(mp) + h)                     # (K', r') = G(m' || H(ek))
    cprime = kpke_encrypt(p, ek, mp, kr[32:])
    reject_key = J(bytes(z) + bytes(c))       # J(z || c)

    # Plain byte compare, deliberately not constant-time (see module docstring).
    if bytes(c) == cprime:
        return kr[:32]
    return reject_key

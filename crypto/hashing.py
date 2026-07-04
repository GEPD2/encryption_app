"""Hash function registry and helpers.

Pure logic: every function takes bytes and returns a hex string. No file I/O and
no UI. The file-facing helpers that used to live here (reading files, saving
digests) now belong in ioutil; the UI wires the two together.

hashlib covers most algorithms natively. RIPEMD-160 comes from pycryptodomex
and Whirlpool from whirlpool-py, matching the original app's dependencies.
"""
import hashlib

try:
    from Cryptodome.Hash import RIPEMD160
except ImportError:  # pragma: no cover - optional dependency
    RIPEMD160 = None

try:
    import whirlpool
except ImportError:  # pragma: no cover - optional dependency
    whirlpool = None


def _ripemd160(data: bytes) -> str:
    if RIPEMD160 is None:
        raise RuntimeError("ripemd160 requires pycryptodomex")
    return RIPEMD160.new(data).hexdigest()


def _whirlpool(data: bytes) -> str:
    if whirlpool is None:
        raise RuntimeError("whirlpool requires whirlpool-py")
    return whirlpool.new(data).hexdigest()


HASH_FUNCTIONS = {
    "md5":       lambda data: hashlib.md5(data).hexdigest(),
    "sha1":      lambda data: hashlib.sha1(data).hexdigest(),
    "sha256":    lambda data: hashlib.sha256(data).hexdigest(),
    "sha384":    lambda data: hashlib.sha384(data).hexdigest(),
    "sha512":    lambda data: hashlib.sha512(data).hexdigest(),
    "sha3_256":  lambda data: hashlib.sha3_256(data).hexdigest(),
    "sha3_512":  lambda data: hashlib.sha3_512(data).hexdigest(),
    "blake2b":   lambda data: hashlib.blake2b(data).hexdigest(),
    "blake2s":   lambda data: hashlib.blake2s(data).hexdigest(),
    "ripemd160": _ripemd160,
    "whirlpool": _whirlpool,
}

# Expected hex-digest length per algorithm, used to sanity-check pasted hashes.
DIGEST_SIZES = {
    "md5": 32, "sha1": 40, "sha256": 64, "sha384": 96, "sha512": 128,
    "sha3_256": 64, "sha3_512": 128, "blake2b": 128, "blake2s": 64,
    "ripemd160": 40, "whirlpool": 128,
}

HASH_ALGORITHMS = list(HASH_FUNCTIONS.keys())


def hash_bytes(data: bytes, algorithm: str) -> str:
    """Hash raw bytes with the named algorithm and return a hex digest."""
    func = HASH_FUNCTIONS.get(algorithm.lower())
    if func is None:
        raise ValueError(f"algorithm {algorithm} not supported")
    return func(data)


def hash_text(text: str, algorithm: str, encoding: str = "utf-8") -> str:
    """Hash a string with the named algorithm and return a hex digest."""
    return hash_bytes(text.encode(encoding), algorithm)


def digest_size(algorithm: str) -> int:
    """Expected hex length of a digest, or 0 if the algorithm is unknown."""
    return DIGEST_SIZES.get(algorithm.lower(), 0)

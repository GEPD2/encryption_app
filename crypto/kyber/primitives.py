"""Layer 1: the low-level ML-KEM primitives (FIPS 203).

Hand-ported from the C reference kyber_fips203_hardened.c and verified against
C-generated ground truth. Everything here is parameterized by an MLKEMParams
object where it depends on the security level; the arithmetic itself (N, Q, the
zeta table) is shared across all three sets.

Two things this file is NOT: it is not constant-time, and it does not erase the
secret polynomials it builds. Python's big integers and garbage collector make
both impossible. This is a teaching implementation.

A note on the modular arithmetic: Python's % always returns a non-negative
result, so unlike the C we never add Q back after a subtraction to keep a
coefficient in range. That is the one systematic difference from the C source.
"""
import hashlib

from .params import N, Q, N_INV

# The five hash roles. All of ML-KEM's hashing is Keccak underneath; each role
# is just a rate and domain choice, so we lean on hashlib rather than porting
# Keccak by hand. SHAKE128 expands the matrix A; SHAKE256 samples noise and
# also serves as J. Never swap the two.

def H(data: bytes) -> bytes:
    """SHA3-256. Binds the encapsulation key into the FO transform."""
    return hashlib.sha3_256(data).digest()


def G(data: bytes) -> bytes:
    """SHA3-512. Derives (rho, sigma) in keygen and (K, r) in encaps."""
    return hashlib.sha3_512(data).digest()


def J(data: bytes) -> bytes:
    """SHAKE256 squeezed to 32 bytes. The implicit-rejection secret."""
    return hashlib.shake_256(data).digest(32)


def prf(seed: bytes, nonce: int, out_len: int) -> bytes:
    """PRF = SHAKE256(seed || nonce), used to draw the noise bytes."""
    return hashlib.shake_256(seed + bytes([nonce & 0xFF])).digest(out_len)


# zetas[k] = zeta^BitRev7(k) mod q with zeta=17, in the plain (non-Montgomery)
# domain. Copied verbatim from the C reference so the NTT matches byte-for-byte.
ZETAS = [
       1, 1729, 2580, 3289, 2642,  630, 1897,  848, 1062, 1919,  193,  797, 2786, 3260,  569, 1746,
     296, 2447, 1339, 1476, 3046,   56, 2240, 1333, 1426, 2094,  535, 2882, 2393, 2879, 1974,  821,
     289,  331, 3253, 1756, 1197, 2304, 2277, 2055,  650, 1977, 2513,  632, 2865,   33, 1320, 1915,
    2319, 1435,  807,  452, 1438, 2868, 1534, 2402, 2647, 2617, 1481,  648, 2474, 3110, 1227,  910,
      17, 2761,  583, 2649, 1637,  723, 2288, 1100, 1409, 2662, 3281,  233,  756, 2156, 3015, 3050,
    1703, 1651, 2789, 1789, 1847,  952, 1461, 2687,  939, 2308, 2437, 2388,  733, 2337,  268,  641,
    1584, 2298, 2037, 3220,  375, 2549, 2090, 1645, 1063,  319, 2773,  757, 2099,  561, 2466, 2594,
    2804, 1092,  403, 1026, 1143, 2150, 2775,  886, 1722, 1212, 1874, 1029, 2110, 2935,  885, 2154,
]


def poly_ntt(f):
    """Forward NTT, in place. Seven layers of Cooley-Tukey butterflies.

    The transform stops at 128 degree-1 pairs, not single points: 3329 has no
    primitive 512th root, so X^256+1 only factors into 128 quadratics.
    """
    k = 1
    length = 128
    while length >= 2:
        start = 0
        while start < N:
            z = ZETAS[k]
            k += 1
            for j in range(start, start + length):
                t = z * f[j + length] % Q
                f[j + length] = (f[j] - t) % Q
                f[j] = (f[j] + t) % Q
            start += 2 * length
        length >>= 1
    return f


def poly_intt(f):
    """Inverse NTT, in place. The same butterflies run backwards, then every
    coefficient is scaled by 128^-1 to undo the transform."""
    k = 127
    length = 2
    while length <= 128:
        start = 0
        while start < N:
            z = ZETAS[k]
            k -= 1
            for j in range(start, start + length):
                t = f[j]
                f[j] = (t + f[j + length]) % Q
                f[j + length] = z * ((f[j + length] - t) % Q) % Q
            start += 2 * length
        length <<= 1
    for i in range(N):
        f[i] = f[i] * N_INV % Q
    return f


def poly_basemul(a, b):
    """Multiply two polynomials in the NTT domain.

    Because the transform stops at quadratics, this is 128 degree-1 products
    (a0 + a1 X)(b0 + b1 X) mod (X^2 - gamma), where gamma alternates
    +zetas[64+g] and -zetas[64+g]. Python ints are unbounded, so the C's long
    casts (guarding a q^3 intermediate) are unnecessary here.
    """
    r = [0] * N
    for g in range(64):
        gp = ZETAS[64 + g]
        gn = Q - gp
        i = 4 * g
        r[i]     = (a[i] * b[i] + gp * a[i + 1] % Q * b[i + 1]) % Q
        r[i + 1] = (a[i] * b[i + 1] + a[i + 1] * b[i]) % Q
        i = 4 * g + 2
        r[i]     = (a[i] * b[i] + gn * a[i + 1] % Q * b[i + 1]) % Q
        r[i + 1] = (a[i] * b[i + 1] + a[i + 1] * b[i]) % Q
    return r


def poly_add(a, b):
    """Coefficient-wise add mod q."""
    return [(a[i] + b[i]) % Q for i in range(N)]


def poly_sub(a, b):
    """Coefficient-wise subtract mod q."""
    return [(a[i] - b[i]) % Q for i in range(N)]


def gen_a_entry(rho: bytes, R: int, C: int):
    """One entry of the public matrix A, sampled on demand and never stored.

    A[R][C] = SampleNTT(SHAKE128(rho || C || R)): stream bytes from the XOF and
    rejection-sample 12-bit candidates that land in [0, q). The result is
    already in the NTT domain. The byte order (C before R) and the reject rule
    must match the reference exactly or the matrix desyncs.
    """
    seed = bytes(rho) + bytes([C & 0xFF, R & 0xFF])
    shake = hashlib.shake_128(seed)
    out = []
    # Squeeze in blocks that are a multiple of 3, so a 3-byte read never
    # straddles a refill boundary and drops bytes. The stream is continuous, so
    # we grow the request and keep reading from where we left off.
    block = 168 * 4
    have = 0
    buf = b""
    bp = 0
    while len(out) < N:
        if bp + 3 > len(buf):
            have += block
            buf = shake.digest(have)
        b0, b1, b2 = buf[bp], buf[bp + 1], buf[bp + 2]
        bp += 3
        d1 = b0 | ((b1 & 0x0F) << 8)
        d2 = (b1 >> 4) | (b2 << 4)
        if d1 < Q and len(out) < N:
            out.append(d1)
        if d2 < Q and len(out) < N:
            out.append(d2)
    return out


def _getbit(buf, t):
    return (buf[t >> 3] >> (t & 7)) & 1


def cbd(buf: bytes, eta: int):
    """Centered binomial noise. For each coefficient take 2*eta random bits and
    subtract the popcount of the second half from the first, giving a small
    value in [-eta, +eta] stored as its positive representative mod q."""
    f = [0] * N
    for i in range(N):
        base = 2 * eta * i
        a = 0
        b = 0
        for j in range(eta):
            a += _getbit(buf, base + j)
        for j in range(eta):
            b += _getbit(buf, base + eta + j)
        v = a - b
        f[i] = v + Q if v < 0 else v
    return f


def sample_poly(seed: bytes, nonce: int, eta: int):
    """One noise polynomial: draw 64*eta bytes from PRF(seed, nonce), then CBD.
    The nonce keeps each sampled polynomial independent."""
    return cbd(prf(seed, nonce, 64 * eta), eta)


def compress_c(x: int, d: int) -> int:
    """Round a coefficient down to d bits. Lossy but the error stays small
    enough to decrypt."""
    return (((x << d) + Q // 2) // Q) & ((1 << d) - 1)


def decompress_c(y: int, d: int) -> int:
    """Inverse rounding of compress_c."""
    return (Q * y + (1 << (d - 1))) >> d


def byte_encode(f, d: int) -> bytes:
    """Pack 256 d-bit coefficients into a byte string, least significant bit
    first."""
    out = bytearray(32 * d)
    for i in range(N):
        v = f[i] & ((1 << d) - 1)
        for b in range(d):
            if (v >> b) & 1:
                out[(i * d + b) >> 3] |= 1 << ((i * d + b) & 7)
    return bytes(out)


def byte_decode(buf: bytes, d: int):
    """Unpack d-bit coefficients. At d=12 the values are also reduced mod q."""
    f = [0] * N
    for i in range(N):
        v = 0
        for b in range(d):
            v |= _getbit(buf, i * d + b) << b
        if d == 12:
            v %= Q
        f[i] = v
    return f


def byte_decode12_validate(buf: bytes):
    """FIPS 203 modulus check. Unpack 256 12-bit coefficients and return None if
    any is >= q, instead of silently reducing. Encaps uses this to reject a
    non-canonical encapsulation key."""
    f = [0] * N
    for i in range(N):
        v = 0
        for b in range(12):
            v |= _getbit(buf, i * 12 + b) << b
        if v >= Q:
            return None
        f[i] = v
    return f


def poly_compress(f, d: int) -> bytes:
    """Compress each coefficient to d bits, then pack."""
    return byte_encode([compress_c(f[i], d) for i in range(N)], d)


def poly_decompress(buf: bytes, d: int):
    """Unpack, then decompress each coefficient from d bits."""
    f = byte_decode(buf, d)
    return [decompress_c(f[i], d) for i in range(N)]

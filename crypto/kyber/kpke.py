"""Layer 2: K-PKE, the IND-CPA public-key encryption underneath ML-KEM.

This is the lattice maths. On its own it is only CPA-secure; the FO transform in
mlkem.py is what makes the full KEM safe against chosen-ciphertext attacks.

Not constant-time, does not zero secrets. Research/education only.
"""
from .params import N, POLY_BYTES
from .primitives import (
    G, sample_poly, poly_ntt, poly_intt, poly_basemul, poly_add, poly_sub,
    gen_a_entry, byte_encode, byte_decode, poly_compress, poly_decompress,
)


def kpke_keygen(p, d: bytes):
    """Derive seeds from d, sample secret s and error e, publish t = A*s + e.

    Everything runs in the NTT domain so the matrix product is cheap. The MLWE
    assumption is that e hides s, so t looks random.
    """
    rs = G(bytes(d) + bytes([p.k]))          # G(d || k) -> rho (public), sigma (secret)
    rho, sigma = rs[:32], rs[32:]

    s = []
    e = []
    for i in range(p.k):
        si = poly_ntt(sample_poly(sigma, i, p.eta1))
        ei = poly_ntt(sample_poly(sigma, p.k + i, p.eta1))
        s.append(si)
        e.append(ei)

    ek = bytearray()
    dk = bytearray()
    t = []
    for i in range(p.k):
        acc = [0] * N
        for j in range(p.k):
            a = gen_a_entry(rho, i, j)        # keygen uses A[i][j]
            acc = poly_add(acc, poly_basemul(a, s[j]))
        t.append(poly_add(acc, e[i]))

    for i in range(p.k):
        ek += byte_encode(t[i], 12)
        dk += byte_encode(s[i], 12)
    ek += rho                                 # public key = t || rho
    return bytes(ek), bytes(dk)


def kpke_encrypt(p, ek: bytes, m: bytes, coins: bytes):
    """Encrypt a 32-byte message m under fresh coins.

    Mirrors keygen but with the transpose A^T. u carries the randomness; v
    carries the message scaled by q/2, so a 0/1 bit becomes a far-apart 0 or
    ~1665 that survives the noise.
    """
    rho = ek[p.k * POLY_BYTES:]
    t = [byte_decode(ek[i * POLY_BYTES:(i + 1) * POLY_BYTES], 12) for i in range(p.k)]

    nonce = 0
    r = []
    for i in range(p.k):
        r.append(sample_poly(coins, nonce, p.eta1))
        nonce += 1
    e1 = []
    for i in range(p.k):
        e1.append(sample_poly(coins, nonce, p.eta2))
        nonce += 1
    e2 = sample_poly(coins, nonce, p.eta2)

    rhat = [poly_ntt(list(r[i])) for i in range(p.k)]

    u = []
    for i in range(p.k):
        acc = [0] * N
        for j in range(p.k):
            a = gen_a_entry(rho, j, i)        # note the swapped indices: this is A^T
            acc = poly_add(acc, poly_basemul(a, rhat[j]))
        poly_intt(acc)
        u.append(poly_add(acc, e1[i]))

    acc = [0] * N
    for j in range(p.k):
        acc = poly_add(acc, poly_basemul(t[j], rhat[j]))
    poly_intt(acc)
    mu = poly_decompress(m, 1)                # message bit -> 0 or q/2
    v = poly_add(poly_add(acc, e2), mu)

    c = bytearray()
    for i in range(p.k):
        c += poly_compress(u[i], p.du)
    c += poly_compress(v, p.dv)
    return bytes(c)


def kpke_decrypt(p, dk: bytes, c: bytes):
    """Recover the message: w = v - s^T u.

    The noise terms nearly cancel, leaving v's message plus a small error;
    rounding each coefficient back to 0 or q/2 recovers the bit, as long as the
    total noise stayed below q/4.
    """
    u = [poly_decompress(c[i * 32 * p.du:(i + 1) * 32 * p.du], p.du) for i in range(p.k)]
    v = poly_decompress(c[p.ct_c1_bytes:p.ct_c1_bytes + p.ct_c2_bytes], p.dv)
    s = [byte_decode(dk[i * POLY_BYTES:(i + 1) * POLY_BYTES], 12) for i in range(p.k)]

    acc = [0] * N
    for j in range(p.k):
        poly_ntt(u[j])
        acc = poly_add(acc, poly_basemul(s[j], u[j]))
    poly_intt(acc)
    w = poly_sub(v, acc)
    return poly_compress(w, 1)                # round back to message bits

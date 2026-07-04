"""ML-KEM parameter sets (FIPS 203). One config object per security level.

ML-KEM-512/768/1024 are the same algorithm; they differ only in the module
rank k, the two noise widths, and the two compression widths. Selecting a level
means picking one of these frozen config objects at runtime, not maintaining
three copies of the implementation.

This is a research/education build. The pure-Python core is NOT constant-time
and does NOT securely erase secrets; both are impossible in CPython. Do not use
it to protect real data.
"""
from dataclasses import dataclass

N = 256
Q = 3329
N_INV = 3303          # 128^-1 mod q, the final scaling in the inverse NTT
SEED_BYTES = 32
POLY_BYTES = 384      # 256 coeffs packed at 12 bits each
SS_BYTES = 32


@dataclass(frozen=True)
class MLKEMParams:
    name: str
    k: int
    eta1: int
    eta2: int
    du: int
    dv: int

    @property
    def pke_pk_bytes(self):  return self.k * POLY_BYTES + SEED_BYTES   # t || rho
    @property
    def pke_sk_bytes(self):  return self.k * POLY_BYTES                # s
    @property
    def ct_c1_bytes(self):   return self.k * 32 * self.du             # compressed u
    @property
    def ct_c2_bytes(self):   return 32 * self.dv                     # compressed v
    @property
    def ct_bytes(self):      return self.ct_c1_bytes + self.ct_c2_bytes
    @property
    def dk_bytes(self):      return 2 * self.k * POLY_BYTES + 2 * SEED_BYTES + SEED_BYTES


MLKEM512  = MLKEMParams("ML-KEM-512",  k=2, eta1=3, eta2=2, du=10, dv=4)
MLKEM768  = MLKEMParams("ML-KEM-768",  k=3, eta1=2, eta2=2, du=10, dv=4)
MLKEM1024 = MLKEMParams("ML-KEM-1024", k=4, eta1=2, eta2=2, du=11, dv=5)

BY_NAME = {p.name: p for p in (MLKEM512, MLKEM768, MLKEM1024)}

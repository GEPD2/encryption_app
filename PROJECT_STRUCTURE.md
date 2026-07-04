# Project Structure

Crypto Toolkit is a Kivy desktop app spanning classical ciphers, a set of hash
functions, and a post-quantum module (ML-KEM / CRYSTALS-Kyber, FIPS 203). The
codebase is split into four layers so the cryptography is testable without a
display and reusable outside the UI.

## Layout

```
crypto_toolkit/
├── app.py                       Entry point: builds the ScreenManager, registers screens
├── requirements.txt             Runtime dependencies
├── README.md                    Project overview, features, install, and usage
├── PROJECT_STRUCTURE.md         This file
│
├── crypto/                      Pure cryptographic logic (no Kivy, no file dialogs)
│   ├── classical.py             Caesar, Affine, Vigenere as pure functions
│   ├── hashing.py               Hash registry, bytes in and hex out
│   ├── aes.py                   AES-256-GCM, keyed by a Kyber shared secret
│   └── kyber/                   Hand-ported ML-KEM, verified against the C reference
│       ├── params.py            ML-KEM-512/768/1024 config objects
│       ├── primitives.py        Layer 1: hashes, NTT, basemul, noise, compress/encode
│       ├── kpke.py              Layer 2: IND-CPA K-PKE (keygen, encrypt, decrypt)
│       ├── mlkem.py             Layer 3: IND-CCA2 KEM via the FO transform
│       └── __init__.py          Public API: keygen, encaps, decaps
│
├── ioutil/                      File and dialog helpers, isolated from crypto and UI
│   └── files.py                 Read/write plus the tkinter file dialogs
│
├── ui/                          Presentation only, calls crypto and ioutil
│   ├── theme.py                 Color, font, and spacing tokens plus styled widgets
│   ├── main_screen.py           Categorized main menu
│   ├── classical_screens.py     Caesar, Affine, Vigenere screens
│   ├── hash_screen.py           One screen reused for every hash algorithm
│   └── kyber_screen.py          Post-quantum screen: Raw KEM and KEM+AES modes
│
├── tests/                       Headless tests, no display required
│   ├── test_kyber_kat.py        Known-answer tests incl. the cross-implementation KAT
│   ├── test_aes.py              Round-trip, tamper, and wrong-key checks
│   └── test_classical.py        Round-trip and passthrough for each cipher
│
└── kyber_fips203_hardened.c     C reference the Python core was ported from
```

The pre-refactor single-file app (`encryption_app_pure_python.py`) is kept
locally for reference but is gitignored, since the package supersedes it.

## Layering rules

The dependency direction is one way: `ui` depends on `crypto` and `ioutil`;
`crypto` depends on nothing in this project.

- `crypto/` never imports Kivy, tkinter, or any UI or file-dialog code. This is
  what makes it unit-testable without a display.
- The Kyber core is parameterized, not copied. ML-KEM-512/768/1024 differ only
  in a handful of parameters selected at runtime from one implementation.
- File dialogs live only in `ioutil`. Screens call `ioutil` functions that
  return bytes or a status string; they never open a dialog themselves.
- Screens hold state and render it; they contain no cryptographic logic.

## The Kyber core, read top to bottom

Each layer uses only the one below it.

1. `primitives.py`  The maths and sampling: Keccak-based hashes, the NTT and its
   inverse, pointwise multiplication, centered-binomial noise, matrix sampling,
   and byte packing.
2. `kpke.py`  IND-CPA public-key encryption. Correct but only CPA-secure on its
   own.
3. `mlkem.py`  The Fujisaki-Okamoto transform, which turns K-PKE into a
   CCA-secure KEM. A tampered ciphertext yields a pseudo-random secret rather
   than an error.

The pure-Python core is a research and education build. It is not constant-time
and does not securely erase secrets, both of which are impossible in CPython.
Every Kyber-touching module and the Kyber screen state this.

## Running

Install dependencies and launch the app:

```
pip install -r requirements.txt
python app.py
```

Run the test suite (no display needed):

```
python -m unittest discover -s tests
```

## How the Kyber core is validated

The C reference `kyber_fips203_hardened.c` produces a `SHA3-256(ek || ct || K)`
digest for fixed seeds at each security level. `tests/test_kyber_kat.py` pins
those digests and asserts the Python core reproduces them byte-for-byte. This
cross-implementation check is what catches a wrong-but-self-consistent port,
which its own round-trip would pass. To regenerate the digests from source:

```
gcc -O2 -o kyber_fips203_hardened kyber_fips203_hardened.c
./kyber_fips203_hardened
```

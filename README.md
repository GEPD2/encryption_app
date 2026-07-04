# Cryptography Toolbox

A multi-algorithm encryption and hashing GUI built with Python and Kivy. It
spans classical ciphers, eleven cryptographic hashes, and a post-quantum module:
a pure-Python, hand-ported ML-KEM (CRYSTALS-Kyber, FIPS 203) with all three
security levels. The app's identity is the classical-to-post-quantum span, not
just a collection of breakable ciphers.

## Features

**Classical ciphers** (educational, easily broken)
- Caesar (shift substitution)
- Affine (linear substitution)
- Vigenere (polyalphabetic substitution)
- Frequency-analysis visualization for each

**Hash functions** (eleven algorithms)
- MD5, SHA-1, SHA-256, SHA-384, SHA-512
- SHA3-256, SHA3-512, BLAKE2b, BLAKE2s, RIPEMD-160, Whirlpool
- Hash text or files, verify against a pasted digest, compare two files, save a digest

**Post-quantum: ML-KEM (Kyber), FIPS 203**
- ML-KEM-512, ML-KEM-768, and ML-KEM-1024, selectable at runtime
- Raw KEM mode: generate a keypair, encapsulate, decapsulate, and see the shared
  secrets match
- KEM + AES message mode: derive a shared secret and encrypt a message with
  AES-256-GCM, so a wrong key or tampered ciphertext fails loudly instead of
  returning garbage

## Architecture

The codebase is split into four layers so the cryptography is testable without a
display and reusable outside the UI. The dependency direction is one way: the UI
depends on the crypto and I/O layers; the crypto layer depends on nothing in the
project.

```
crypto/     Pure cryptographic logic (no Kivy, no file dialogs)
  kyber/    Hand-ported ML-KEM, verified byte-for-byte against a C reference
ioutil/     File helpers and the file dialogs, isolated in one place
ui/         Presentation only; screens call crypto and ioutil
tests/      Headless known-answer and round-trip tests
app.py      Entry point that wires the screens together
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for a file-by-file breakdown and
the layering rules.

## Installation

Prerequisites: Python 3.8+, Kivy 2.0+, and Tkinter (for file dialogs).

```
pip install -r requirements.txt
```

The one new dependency over the classical build is `cryptography`, which
provides AES-256-GCM for the KEM+AES message mode.

## Usage

```
python app.py
```

The main menu is organized into three categories: classical ciphers, hash
functions, and post-quantum. Open the post-quantum screen to run a full KEM
exchange and watch the shared secrets agree.

## Testing

The test suite is headless and needs no display:

```
python -m unittest discover -s tests
```

It covers empty-string hash vectors, the NTT round-trip and pointwise-multiply
identity, serialized-size checks, KEM round-trips with fresh randomness,
implicit rejection on a tampered ciphertext, and the AES tamper and wrong-key
paths. The strongest check is a cross-implementation known-answer test: the Kyber
core must reproduce, byte-for-byte, the `SHA3-256(ek || ct || K)` digests that
the C reference produces for fixed seeds. Self-consistency alone would pass a
wrong-but-consistent port; matching an independent implementation is what proves
correctness.

## Security notice

This is a research and education build.

- The classical ciphers are not secure. They exist to teach and to be broken.
  MD5 and SHA-1 are cryptographically compromised; prefer SHA-256 or SHA-3 for
  anything real.
- The pure-Python ML-KEM is **not constant-time** and does **not** securely erase
  secret keys. Both are impossible in CPython. It reproduces the FIPS 203
  algorithm correctly, but it must not be used to protect real data. Every
  Kyber-touching module and the post-quantum screen state this limitation.

## Credits

Refactored and extended from the original single-file
[encryption_app](https://github.com/GEPD2/encryption_app). The Kyber core was
hand-ported from a C reference implementation of FIPS 203 and validated against
it.

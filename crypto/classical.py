"""Classical ciphers: Caesar, Affine, Vigenere.

Pure functions, moved out of the old single-file app. No Kivy, no file dialogs,
no I/O, so they can be unit-tested headless. These are educational and easily
broken; the UI labels them as such.

Every function preserves non-alphabetic characters and case.
"""


def encrypt_caesar(text: str, key: int) -> str:
    result = []
    for char in text:
        if char.isupper():
            result.append(chr((ord(char) + key - 65) % 26 + 65))
        elif char.islower():
            result.append(chr((ord(char) + key - 97) % 26 + 97))
        else:
            result.append(char)
    return "".join(result)


def decrypt_caesar(text: str, key: int) -> str:
    return encrypt_caesar(text, -key)


def affine_cipher(text: str, a: int, b: int, mode: str):
    """Encrypt or decrypt with the affine cipher over the 26-letter alphabet.

    Returns (result, failed). Decryption fails when a is not invertible mod 26;
    in that case result is the untouched input and failed is True.
    """
    m = 26
    a_inv = None
    if mode == "decrypt":
        try:
            a_inv = pow(a, -1, m)
        except ValueError:
            return text, True

    result = []
    for char in text:
        if char.isalpha():
            base = ord("A") if char.isupper() else ord("a")
            x = ord(char) - base
            if mode == "encrypt":
                y = (a * x + b) % m
            else:
                y = a_inv * (x - b) % m
            result.append(chr(y + base))
        else:
            result.append(char)
    return "".join(result), False


def _extend_key(text: str, key: str) -> str:
    """Repeat the keyword up to the length of the text."""
    if not key:
        return key
    full = (key * (len(text) // len(key) + 1))[:len(text)]
    return full


def encrypt_vigenere(text: str, key: str) -> str:
    key = _extend_key(text, key)
    result = []
    for i, char in enumerate(text):
        if char.isupper():
            result.append(chr((ord(char) + ord(key[i]) - 2 * ord("A")) % 26 + ord("A")))
        elif char.islower():
            result.append(chr((ord(char) + ord(key[i]) - 2 * ord("a")) % 26 + ord("a")))
        else:
            result.append(char)
    return "".join(result)


def decrypt_vigenere(text: str, key: str) -> str:
    key = _extend_key(text, key)
    result = []
    for i, char in enumerate(text):
        if char.isupper():
            result.append(chr((ord(char) - ord(key[i]) + 26) % 26 + ord("A")))
        elif char.islower():
            result.append(chr((ord(char) - ord(key[i]) + 26) % 26 + ord("a")))
        else:
            result.append(char)
    return "".join(result)

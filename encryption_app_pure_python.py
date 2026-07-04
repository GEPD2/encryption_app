# library to run the app
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from tkinter.filedialog import askopenfilename, askdirectory
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import hashlib
from Cryptodome.Hash import RIPEMD160
import whirlpool

# ==================== UTILITY FUNCTIONS ====================

def position(text) -> str:
    """Format text to display with line breaks"""
    if not text:
        return ""
    copy = ""
    start = 0
    end = 120
    number = len(text)
    n = 0
    
    if number <= 120:
        return text
    elif number > 120 and number % 120 != 0:
        while n < number // 120:
            for i in range(start, end):
                copy += text[i]
            copy += "\n"
            start += 120
            end += 120
            n += 1
        for i in range(start, len(text)):
            copy += text[i]
    else:
        while n <= number // 120:
            for i in range(start, end):
                copy += text[i]
            copy += "\n"
            start += 120
            end += 120
            n += 1
    return copy

def show_frequency_analysis_in_text(text):
    """Show frequency analysis plot"""
    counter = Counter(text)
    data_words = list(counter.keys())
    words_counts = list(counter.values())
    indexes = np.arange(len(data_words))
    width = 0.7
    plt.bar(indexes, words_counts, width)
    plt.xticks(indexes + width * 0.5, data_words)
    plt.show()

def read_data(filenumber, mode):
    """Read data from file"""
    data = []
    path = askopenfilename(title=filenumber)
    if not path:
        return "No file selected"
    try:
        with open(path, mode=mode, encoding='utf-8' if 'r' in mode else None) as file:
            for x in file:
                clean = x.strip()
                data.append(clean)
        return data
    except Exception as e:
        return f"Error reading file: {str(e)}"

def check_hash_size_given(data1, algorithm):
    """Validate hash size"""
    if not data1:
        return False
    sizes = {
        "sha512": 128, "sha256": 64, "sha384": 96, "sha3_512": 128,
        "sha3_256": 64, "sha1": 40, "blake2b": 128, "blake2s": 64,
        "ripemd160": 40, "whirlpool": 128, "md5": 32
    }
    return len(data1) == sizes.get(algorithm, 0)

# ==================== ENCRYPTION FUNCTIONS ====================

def _encrypt_caesar(text, key):
    """Encrypt text using Caesar cipher"""
    result = ""
    for char in text:
        if char.isupper():
            result += chr((ord(char) + key - 65) % 26 + 65)
        elif char.islower():
            result += chr((ord(char) + key - 97) % 26 + 97)
        else:
            result += char
    return result

def _decrypt_caesar(text, key):
    """Decrypt text using Caesar cipher"""
    result = ""
    for char in text:
        if char.isupper():
            result += chr((ord(char) - key - 65) % 26 + 65)
        elif char.islower():
            result += chr((ord(char) - key - 97) % 26 + 97)
        else:
            result += char
    return result

def affine_cipher(text, a, b, mode):
    """Encrypt/decrypt using Affine cipher"""
    result = ''
    m = 26
    fail = False
    
    for char in text:
        if char.isalpha():
            x = ord(char) - ord('A' if char.isupper() else 'a')
            if mode == 'encrypt':
                new_x = (a * x + b) % m
            elif mode == 'decrypt':
                try:
                    a_inv = pow(a, -1, m)
                    new_x = a_inv * (x - b) % m
                except ValueError:
                    fail = True
                    break
            if not fail:
                new_char = chr(new_x + ord('A' if char.isupper() else 'a'))
            else:
                new_char = char
        else:
            new_char = char
        result += new_char
    
    return result, fail

def extend_key(unencrypted, key):
    """Extend Vigenere key to match text length"""
    key = list(key)
    if len(unencrypted) == len(key):
        return "".join(key)
    for i in range(len(unencrypted) - len(key)):
        key.append(key[i % len(key)])
    return "".join(key)

def encrypt_vigenere(unencrypted, key):
    """Encrypt using Vigenere cipher"""
    encrypted_text = []
    key = extend_key(unencrypted, key)
    for i in range(len(unencrypted)):
        char = unencrypted[i]
        if char.isupper():
            encrypted_char = chr((ord(char) + ord(key[i]) - 2 * ord('A')) % 26 + ord('A'))
        elif char.islower():
            encrypted_char = chr((ord(char) + ord(key[i]) - 2 * ord('a')) % 26 + ord('a'))
        else:
            encrypted_char = char
        encrypted_text.append(encrypted_char)
    return "".join(encrypted_text)

def decrypt_vigenere(encrypted, key):
    """Decrypt using Vigenere cipher"""
    decrypted_text = []
    key = extend_key(encrypted, key)
    for i in range(len(encrypted)):
        char = encrypted[i]
        if char.isupper():
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord('A'))
        elif char.islower():
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord('a'))
        else:
            decrypted_char = char
        decrypted_text.append(decrypted_char)
    return "".join(decrypted_text)

# ==================== HASH OPERATIONS ====================

def compare(data, hashreturned):
    """Compare hash with file data"""
    if isinstance(data, list) and data:
        if data[0] == hashreturned:
            return "Verification succeeded."
        else:
            return "Verification failed."
    return "No file given or file empty"

def compare_file_string_(data, original_hash, hash_algo):
    """Compare hash with string from file"""
    if not original_hash:
        return "No hash was given through input"
    
    if not isinstance(data, list) or not data:
        return "No file given or file empty"
    
    hash_functions = {
        "md5": lambda d: hashlib.md5(d.encode()).hexdigest(),
        "sha512": lambda d: hashlib.sha512(d.encode()).hexdigest(),
        "sha256": lambda d: hashlib.sha256(d.encode()).hexdigest(),
        "sha384": lambda d: hashlib.sha384(d.encode()).hexdigest(),
        "sha3_512": lambda d: hashlib.sha3_512(d.encode()).hexdigest(),
        "sha3_256": lambda d: hashlib.sha3_256(d.encode()).hexdigest(),
        "blake2b": lambda d: hashlib.blake2b(d.encode()).hexdigest(),
        "blake2s": lambda d: hashlib.blake2s(d.encode()).hexdigest(),
        "ripemd160": lambda d: RIPEMD160.new(d.encode()).hexdigest(),
        "whirlpool": lambda d: whirlpool.new(d.encode()).hexdigest(),
        "sha1": lambda d: hashlib.sha1(d.encode()).hexdigest()
    }
    
    func = hash_functions.get(hash_algo.lower())
    if not func:
        return f"Algorithm {hash_algo} not supported"
    
    hash_returned = func(data[0])
    if original_hash == hash_returned:
        return "Verification succeeded."
    else:
        return "Verification failed."

def hash_data_from_file(data, algorithm):
    """Hash file content and save to new file"""
    if not isinstance(data, list):
        return "No file given"
    
    hash_functions = {
        "md5": lambda d: hashlib.md5(d.encode()).hexdigest(),
        "sha512": lambda d: hashlib.sha512(d.encode()).hexdigest(),
        "sha256": lambda d: hashlib.sha256(d.encode()).hexdigest(),
        "sha384": lambda d: hashlib.sha384(d.encode()).hexdigest(),
        "sha3_512": lambda d: hashlib.sha3_512(d.encode()).hexdigest(),
        "sha3_256": lambda d: hashlib.sha3_256(d.encode()).hexdigest(),
        "blake2b": lambda d: hashlib.blake2b(d.encode()).hexdigest(),
        "blake2s": lambda d: hashlib.blake2s(d.encode()).hexdigest(),
        "ripemd160": lambda d: RIPEMD160.new(d.encode()).hexdigest(),
        "whirlpool": lambda d: whirlpool.new(d.encode()).hexdigest(),
        "sha1": lambda d: hashlib.sha1(d.encode()).hexdigest()
    }
    
    func = hash_functions.get(algorithm.lower())
    if not func:
        return f"Algorithm {algorithm} not supported"
    
    hash_returned = ""
    for x in data:
        hash_returned += func(x) + "\n"
    
    store_path = askdirectory()
    if not store_path:
        return "No directory selected"
    
    store_path += f"/{algorithm}_results.txt"
    try:
        with open(store_path, "w") as store:
            store.write(hash_returned)
        return "Hash stored successfully"
    except Exception as e:
        return f"Error saving file: {str(e)}"

def hash_input_to_file(data, algorithm):
    """Hash input and save to file"""
    if not data:
        return "No data to hash"
    
    hash_functions = {
        "md5": lambda d: hashlib.md5(d.encode()).hexdigest(),
        "sha512": lambda d: hashlib.sha512(d.encode()).hexdigest(),
        "sha256": lambda d: hashlib.sha256(d.encode()).hexdigest(),
        "sha384": lambda d: hashlib.sha384(d.encode()).hexdigest(),
        "sha3_512": lambda d: hashlib.sha3_512(d.encode()).hexdigest(),
        "sha3_256": lambda d: hashlib.sha3_256(d.encode()).hexdigest(),
        "blake2b": lambda d: hashlib.blake2b(d.encode()).hexdigest(),
        "blake2s": lambda d: hashlib.blake2s(d.encode()).hexdigest(),
        "ripemd160": lambda d: RIPEMD160.new(d.encode()).hexdigest(),
        "whirlpool": lambda d: whirlpool.new(d.encode()).hexdigest(),
        "sha1": lambda d: hashlib.sha1(d.encode()).hexdigest()
    }
    
    func = hash_functions.get(algorithm.lower())
    if not func:
        return f"Algorithm {algorithm} not supported"
    
    hashed = func(data)
    
    path = askdirectory()
    if not path:
        return "No directory selected"
    
    filename = f"/{algorithm}_results.txt"
    try:
        with open(path + filename, "w") as file:
            file.write(hashed + "\n")
        return "Hash stored successfully"
    except Exception as e:
        return f"Error saving file: {str(e)}"

def compare_files_functionality(data1, data2, algorithm):
    """Compare two files using hashes"""
    if not isinstance(data1, list) or not isinstance(data2, list):
        return "One or both files not found"
    
    hash_functions = {
        "md5": lambda d: hashlib.md5(d.encode()).hexdigest(),
        "sha512": lambda d: hashlib.sha512(d.encode()).hexdigest(),
        "sha256": lambda d: hashlib.sha256(d.encode()).hexdigest(),
        "sha384": lambda d: hashlib.sha384(d.encode()).hexdigest(),
        "sha3_512": lambda d: hashlib.sha3_512(d.encode()).hexdigest(),
        "sha3_256": lambda d: hashlib.sha3_256(d.encode()).hexdigest(),
        "blake2b": lambda d: hashlib.blake2b(d.encode()).hexdigest(),
        "blake2s": lambda d: hashlib.blake2s(d.encode()).hexdigest(),
        "ripemd160": lambda d: RIPEMD160.new(d.encode()).hexdigest(),
        "whirlpool": lambda d: whirlpool.new(d.encode()).hexdigest(),
        "sha1": lambda d: hashlib.sha1(d.encode()).hexdigest()
    }
    
    func = hash_functions.get(algorithm.lower())
    if not func:
        return f"Algorithm {algorithm} not supported"
    
    hash1 = [func(x) for x in data1]
    hash2 = [func(x) for x in data2]
    
    l1, l2 = len(hash1), len(hash2)
    if l1 != l2:
        return "Files have different number of lines"
    
    success = sum(1 for i in range(l1) if hash1[i] == hash2[i])
    if success == l1:
        return "All hashes match - files are identical"
    else:
        return f"{success}/{l1} hashes match - files differ"

# ==================== MASTER DICTIONARIES ====================

HASH_FUNCTIONS = {
    "md5": lambda data: hashlib.md5(data).hexdigest(),
    "sha1": lambda data: hashlib.sha1(data).hexdigest(),
    "sha256": lambda data: hashlib.sha256(data).hexdigest(),
    "sha384": lambda data: hashlib.sha384(data).hexdigest(),
    "sha512": lambda data: hashlib.sha512(data).hexdigest(),
    "sha3_256": lambda data: hashlib.sha3_256(data).hexdigest(),
    "sha3_512": lambda data: hashlib.sha3_512(data).hexdigest(),
    "blake2b": lambda data: hashlib.blake2b(data).hexdigest(),
    "blake2s": lambda data: hashlib.blake2s(data).hexdigest(),
    "ripemd160": lambda data: RIPEMD160.new(data).hexdigest(),
    "whirlpool": lambda data: whirlpool.new(data).hexdigest()
}

ENCRYPTION_ALGORITHMS = ["caesar", "affine", "vigenere"]
HASH_ALGORITHMS = list(HASH_FUNCTIONS.keys())

# ==================== SCREEN CLASSES ====================

class HashScreen(Screen):
    def __init__(self, algorithm, **kwargs):
        super().__init__(**kwargs)
        self.algorithm = algorithm
        self.name = algorithm
        
        layout = FloatLayout()

        # Title label
        title_label = Label(
            text=f"{algorithm.upper()} Hashing",
            size_hint=(.4, .05),
            pos=(300, 700),
            font_size='24sp'
        )

        # Results label
        self.result_label = Label(
            text="Results will appear here...",
            size_hint=(.8, .3),
            pos=(100, 350),
            text_size=(800, None)
        )

        # Input field
        self.textinput = TextInput(
            hint_text=f"Enter text to hash with {algorithm}",
            font_size="20sp",
            size_hint=(.6, .05),
            pos=(200, 600),
            multiline=False
        )

        # Buttons layout
        buttons_layout = GridLayout(
            cols=2,
            spacing=10,
            size_hint=(.4, .2),
            pos=(200, 150)
        )

        # Hash button
        hash_button = Button(
            text=f"Hash Text",
            font_size="16sp",
            on_release=self.hash_input
        )

        # File operations buttons
        hash_file_btn = Button(
            text="Hash File",
            font_size="16sp",
            on_release=self.hash_file
        )

        compare_hash_btn = Button(
            text="Compare with File Hash",
            font_size="16sp",
            on_release=self.compare_with_file_hash
        )

        compare_string_btn = Button(
            text="Compare with File Text",
            font_size="16sp",
            on_release=self.compare_with_file_text
        )

        compare_files_btn = Button(
            text="Compare Two Files",
            font_size="16sp",
            on_release=self.compare_files
        )

        save_hash_btn = Button(
            text="Save Hash to File",
            font_size="16sp",
            on_release=self.save_hash_to_file
        )

        buttons_layout.add_widget(hash_button)
        buttons_layout.add_widget(hash_file_btn)
        buttons_layout.add_widget(compare_hash_btn)
        buttons_layout.add_widget(compare_string_btn)
        buttons_layout.add_widget(compare_files_btn)
        buttons_layout.add_widget(save_hash_btn)

        # Back button
        back_button = Button(
            text="Back",
            font_size="20sp",
            size_hint=(.15, .05),
            pos=(50, 50),
            on_release=self.go_back
        )

        # Add all widgets
        layout.add_widget(title_label)
        layout.add_widget(self.result_label)
        layout.add_widget(self.textinput)
        layout.add_widget(buttons_layout)
        layout.add_widget(back_button)
        self.add_widget(layout)

    def hash_input(self, instance):
        data = self.textinput.text.strip()
        if not data:
            self.result_label.text = "Please enter some text to hash"
            return
        
        data_bytes = data.encode()
        func = HASH_FUNCTIONS.get(self.algorithm)
        if not func:
            self.result_label.text = f"Algorithm {self.algorithm} not implemented"
            return
        
        try:
            hashed = func(data_bytes)
            self.result_label.text = f"Hash result:\n{hashed}"
        except Exception as e:
            self.result_label.text = f"Error: {str(e)}"

    def hash_file(self, instance):
        data = read_data("file1", "r")
        result = hash_data_from_file(data, self.algorithm)
        self.result_label.text = result

    def compare_with_file_hash(self, instance):
        original_hash = self.textinput.text.strip()
        if not original_hash:
            self.result_label.text = "Please enter a hash to compare"
            return
        
        if not check_hash_size_given(original_hash, self.algorithm):
            self.result_label.text = "Input hash does not have the right size"
            return
        
        data = read_data("file1", "rb")
        result = compare(data, original_hash)
        self.result_label.text = result

    def compare_with_file_text(self, instance):
        original_hash = self.textinput.text.strip()
        if not original_hash:
            self.result_label.text = "Please enter a hash to compare"
            return
        
        if not check_hash_size_given(original_hash, self.algorithm):
            self.result_label.text = "Input hash does not have the right size"
            return
        
        data = read_data("file1", "r")
        result = compare_file_string_(data, original_hash, self.algorithm)
        self.result_label.text = result

    def compare_files(self, instance):
        data1 = read_data("file1", "r")
        data2 = read_data("file2", "r")
        result = compare_files_functionality(data1, data2, self.algorithm)
        self.result_label.text = result

    def save_hash_to_file(self, instance):
        data = self.textinput.text.strip()
        if not data:
            self.result_label.text = "Please enter text to hash and save"
            return
        
        result = hash_input_to_file(data, self.algorithm)
        self.result_label.text = result

    def go_back(self, instance):
        self.manager.current = "main"

class CaesarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "caesar"
        
        layout = FloatLayout()

        # Title
        title = Label(
            text="Caesar Cipher",
            size_hint=(.4, .05),
            pos=(300, 700),
            font_size='24sp'
        )

        # Results label
        self.result_label = Label(
            text="Results will appear here...",
            size_hint=(.8, .2),
            pos=(100, 400),
            text_size=(800, None)
        )

        # Text input
        self.text_input = TextInput(
            hint_text="Enter text to encrypt/decrypt",
            font_size="20sp",
            size_hint=(.6, .05),
            pos=(200, 600),
            multiline=False
        )

        # Key input
        self.key_input = TextInput(
            hint_text="Enter key (1-25)",
            font_size="20sp",
            size_hint=(.2, .05),
            pos=(200, 520),
            multiline=False
        )

        # Buttons layout
        buttons_layout = GridLayout(
            cols=3,
            spacing=10,
            size_hint=(.6, .1),
            pos=(200, 300)
        )

        encode_btn = Button(text="Encode", on_release=self.encode)
        decode_btn = Button(text="Decode", on_release=self.decode)
        freq_btn = Button(text="Frequency Analysis", on_release=self.frequency_analysis)
        back_btn = Button(text="Back", on_release=self.go_back)

        buttons_layout.add_widget(encode_btn)
        buttons_layout.add_widget(decode_btn)
        buttons_layout.add_widget(freq_btn)
        buttons_layout.add_widget(back_btn)

        layout.add_widget(title)
        layout.add_widget(self.result_label)
        layout.add_widget(self.text_input)
        layout.add_widget(self.key_input)
        layout.add_widget(buttons_layout)
        self.add_widget(layout)

    def encode(self, instance):
        text = self.text_input.text.strip()
        key_str = self.key_input.text.strip()
        
        if not text:
            self.result_label.text = "Please enter text"
            return
        if not key_str:
            self.result_label.text = "Please enter key"
            return
        
        try:
            key = int(key_str)
            if key <= 0 or key > 25:
                self.result_label.text = "Key must be between 1 and 25"
                return
            
            encrypted = _encrypt_caesar(text, key)
            self.result_label.text = f"Encrypted:\n{position(encrypted)}"
        except ValueError:
            self.result_label.text = "Key must be a number"

    def decode(self, instance):
        text = self.text_input.text.strip()
        key_str = self.key_input.text.strip()
        
        if not text:
            self.result_label.text = "Please enter text"
            return
        if not key_str:
            self.result_label.text = "Please enter key"
            return
        
        try:
            key = int(key_str)
            if key <= 0 or key > 25:
                self.result_label.text = "Key must be between 1 and 25"
                return
            
            decrypted = _decrypt_caesar(text, key)
            self.result_label.text = f"Decrypted:\n{position(decrypted)}"
        except ValueError:
            self.result_label.text = "Key must be a number"

    def frequency_analysis(self, instance):
        text = self.text_input.text.strip()
        if text:
            show_frequency_analysis_in_text(text)
        else:
            self.result_label.text = "Please enter text first"

    def go_back(self, instance):
        self.manager.current = "main"

class AffineScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "affine"
        
        layout = FloatLayout()

        # Title
        title = Label(
            text="Affine Cipher",
            size_hint=(.4, .05),
            pos=(300, 700),
            font_size='24sp'
        )

        # Results label
        self.result_label = Label(
            text="Results will appear here...",
            size_hint=(.8, .2),
            pos=(100, 400),
            text_size=(800, None)
        )

        # Text input
        self.text_input = TextInput(
            hint_text="Enter text to encrypt/decrypt",
            font_size="20sp",
            size_hint=(.6, .05),
            pos=(200, 600),
            multiline=False
        )

        # Key inputs
        self.key1_input = TextInput(
            hint_text="Key 1",
            font_size="20sp",
            size_hint=(.2, .05),
            pos=(200, 520),
            multiline=False
        )

        self.key2_input = TextInput(
            hint_text="Key 2", 
            font_size="20sp",
            size_hint=(.2, .05),
            pos=(620, 520),
            multiline=False
        )

        # Buttons layout
        buttons_layout = GridLayout(
            cols=3,
            spacing=10,
            size_hint=(.6, .1),
            pos=(200, 300)
        )

        encode_btn = Button(text="Encode", on_release=self.encode)
        decode_btn = Button(text="Decode", on_release=self.decode)
        freq_btn = Button(text="Frequency Analysis", on_release=self.frequency_analysis)
        back_btn = Button(text="Back", on_release=self.go_back)

        buttons_layout.add_widget(encode_btn)
        buttons_layout.add_widget(decode_btn)
        buttons_layout.add_widget(freq_btn)
        buttons_layout.add_widget(back_btn)

        layout.add_widget(title)
        layout.add_widget(self.result_label)
        layout.add_widget(self.text_input)
        layout.add_widget(self.key1_input)
        layout.add_widget(self.key2_input)
        layout.add_widget(buttons_layout)
        self.add_widget(layout)

    def encode(self, instance):
        text = self.text_input.text.strip()
        key1_str = self.key1_input.text.strip()
        key2_str = self.key2_input.text.strip()
        
        if not text:
            self.result_label.text = "Please enter text"
            return
        if not key1_str or not key2_str:
            self.result_label.text = "Please enter both keys"
            return
        
        try:
            key1, key2 = int(key1_str), int(key2_str)
            encrypted, fail = affine_cipher(text, key1, key2, 'encrypt')
            if fail:
                self.result_label.text = "Encryption failed - check keys"
            else:
                self.result_label.text = f"Encrypted:\n{position(encrypted)}"
        except ValueError:
            self.result_label.text = "Keys must be numbers"

    def decode(self, instance):
        text = self.text_input.text.strip()
        key1_str = self.key1_input.text.strip()
        key2_str = self.key2_input.text.strip()
        
        if not text:
            self.result_label.text = "Please enter text"
            return
        if not key1_str or not key2_str:
            self.result_label.text = "Please enter both keys"
            return
        
        try:
            key1, key2 = int(key1_str), int(key2_str)
            decrypted, fail = affine_cipher(text, key1, key2, 'decrypt')
            if fail:
                self.result_label.text = "Decryption failed - key 1 must be coprime with 26"
            else:
                self.result_label.text = f"Decrypted:\n{position(decrypted)}"
        except ValueError:
            self.result_label.text = "Keys must be numbers"

    def frequency_analysis(self, instance):
        text = self.text_input.text.strip()
        if text:
            show_frequency_analysis_in_text(text)
        else:
            self.result_label.text = "Please enter text first"

    def go_back(self, instance):
        self.manager.current = "main"

class VigenereScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "vigenere"
        
        layout = FloatLayout()

        # Title
        title = Label(
            text="Vigenere Cipher",
            size_hint=(.4, .05),
            pos=(300, 700),
            font_size='24sp'
        )

        # Results label
        self.result_label = Label(
            text="Results will appear here...",
            size_hint=(.8, .2),
            pos=(100, 400),
            text_size=(800, None)
        )

        # Text input
        self.text_input = TextInput(
            hint_text="Enter text to encrypt/decrypt",
            font_size="20sp",
            size_hint=(.6, .05),
            pos=(200, 600),
            multiline=False
        )

        # Key input
        self.key_input = TextInput(
            hint_text="Enter key word",
            font_size="20sp",
            size_hint=(.6, .05),
            pos=(200, 520),
            multiline=False
        )

        # Buttons layout
        buttons_layout = GridLayout(
            cols=3,
            spacing=10,
            size_hint=(.6, .1),
            pos=(200, 300)
        )

        encode_btn = Button(text="Encode", on_release=self.encode)
        decode_btn = Button(text="Decode", on_release=self.decode)
        freq_btn = Button(text="Frequency Analysis", on_release=self.frequency_analysis)
        back_btn = Button(text="Back to Main", on_release=self.go_back)

        buttons_layout.add_widget(encode_btn)
        buttons_layout.add_widget(decode_btn)
        buttons_layout.add_widget(freq_btn)
        buttons_layout.add_widget(back_btn)

        layout.add_widget(title)
        layout.add_widget(self.result_label)
        layout.add_widget(self.text_input)
        layout.add_widget(self.key_input)
        layout.add_widget(buttons_layout)
        self.add_widget(layout)

    def encode(self, instance):
        text = self.text_input.text.strip()
        key = self.key_input.text.strip()
        
        if not text:
            self.result_label.text = "Please enter text"
            return
        if not key:
            self.result_label.text = "Please enter key"
            return
        
        encrypted = encrypt_vigenere(text, key)
        self.result_label.text = f"Encrypted:\n{position(encrypted)}"

    def decode(self, instance):
        text = self.text_input.text.strip()
        key = self.key_input.text.strip()
        
        if not text:
            self.result_label.text = "Please enter text"
            return
        if not key:
            self.result_label.text = "Please enter key"
            return
        
        decrypted = decrypt_vigenere(text, key)
        self.result_label.text = f"Decrypted:\n{position(decrypted)}"

    def frequency_analysis(self, instance):
        text = self.text_input.text.strip()
        if text:
            show_frequency_analysis_in_text(text)
        else:
            self.result_label.text = "Please enter text first"

    def go_back(self, instance):
        self.manager.current = "main"

# Main menu screen
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "main"
        
        # Single GridLayout for everything
        layout = GridLayout(
            cols=5,  # 5 columns for compact layout
            spacing=3,
            padding=10
        )

        # Title spanning all columns
        title = Label(
            text="Cryptography Toolbox",
            font_size='20sp'
        )
        layout.add_widget(title)
        
        # Add empty cells to complete the row (title spans 5 columns)
        for _ in range(4):
            layout.add_widget(Label())

        # Warning spanning all columns
        warning = Label(
            text="Weak ciphers warning!",
            font_size='20sp',
            color=(1, 0, 0, 1)
        )
        layout.add_widget(warning)
        
        # Add empty cells to complete the row
        for _ in range(4):
            layout.add_widget(Label())

        # Section label - Encryption
        encryption_label = Label(
            text="Encryption:",
            font_size='20sp',
            color=(0, 0.5, 1, 1)
        )
        layout.add_widget(encryption_label)
        
        # Add empty cells
        for _ in range(4):
            layout.add_widget(Label())

        # Add encryption buttons with fixed sizes
        for algo in ENCRYPTION_ALGORITHMS:
            btn = Button(
                text=algo.upper(),
                font_size="20sp",
                size_hint_x=0.8,   # Control width (0.0-1.0)
                size_hint_y=0.2,   # Control height
                on_release=self.go_to_screen
            )
            layout.add_widget(btn)
        
        # Add 2 empty cells to complete the 5-column row
        layout.add_widget(Label())
        layout.add_widget(Label())

        # Section label - Hashes
        hash_label = Label(
            text="Hash Algorithms:",
            font_size='20sp',
            color=(0, 0.5, 1, 1)
        )
        layout.add_widget(hash_label)
        
        # Add empty cells
        for _ in range(4):
            layout.add_widget(Label())

        # Add all hash buttons with fixed sizes
        for algo in HASH_ALGORITHMS:
            btn = Button(
                text=algo.upper(),
                font_size="20sp",
                size_hint_x=0.6,   # Control width
                size_hint_y=0.4,  # Control height
                on_release=self.go_to_screen
            )
            layout.add_widget(btn)

        self.add_widget(layout)

    def go_to_screen(self, instance):
        screen_name = instance.text.lower()
        self.manager.current = screen_name

# Screen Manager
class CryptoApp(App):
    def build(self):
        Window.maximize()
        sm = ScreenManager(transition=FadeTransition())
        
        # Add main screen first
        sm.add_widget(MainScreen())
        
        # Add encryption screens
        sm.add_widget(CaesarScreen())
        sm.add_widget(AffineScreen())
        sm.add_widget(VigenereScreen())
        
        # Add hash screens
        for algorithm in HASH_ALGORITHMS:
            sm.add_widget(HashScreen(algorithm))
        
        return sm

if __name__ == "__main__":
    CryptoApp().run()

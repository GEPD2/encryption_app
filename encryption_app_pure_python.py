#general library about gui
import kivy
#library to run the app
from kivy.app import App
#library for the screen managment, the screen gui and the transition which is a fade one 
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
#library for creating a button
from kivy.uix.button import Button
#library to create a label
from kivy.uix.label import Label
#library to create a textinput
from kivy.uix.textinput import TextInput
#library to create the floatlayout, how the buttons,labels and generaly the objects appear
from kivy.uix.floatlayout import FloatLayout
#library that returns the path of the file and it's name connected in a string format for later use
from tkinter.filedialog import askopenfilename
#library that returns the path of a folder and its name connected in a string format for later use
from tkinter.filedialog import askdirectory
#library to plot the data in the matplotlib
import matplotlib.pyplot as plt
#library that will create the x axxis for the plot
import numpy as np
#library that counts letters in a given string
from collections import Counter
#window managment
from kivy.core.window import Window
#another gui library
import tkinter as tk
#library for hashes
import hashlib

class MainWindow(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        layout=FloatLayout()

        label=Label(text="i suggest you not to encrypt a file with caesar,affine and vigener and send it over the internet,it can be decrypted easily",
                    size_hint=(.4, .1),pos=(100,700))
        #ceasar button
        def go_to_caesar(instance):
            self.manager.current = "caesar"
        self.ceasar_button = Button(
            text="ceasar encoding",
            font_size="20sp",
            size_hint=(.1, .1),
            pos=(250, 300),
            on_release=go_to_caesar  #lambda x: setattr(self.manager, "current", "caesar")
        )
        #affine button
        def go_to_affine(instance):
            self.manager.current= "affine"
        self.affine_button=Button(
            text="affine encoding",
            font_size="20sp",
            size_hint= (.1 , .1),
            pos=(350 , 400),
            on_release=go_to_affine
        )
        #vigenere button
        def go_to_vigenere(instance):
            self.manager.current="vigenere"
        self.vigener_button=Button(
            text="vigener encoding",
            font_size="20sp",
            size_hint=(.1 , .1),
            pos=(450 , 300),
            on_release=go_to_vigenere
        )
        #md5 button
        def go_to_md5(instance):
            self.manager.current="md5"
        self.md5_button=Button(
            text="md5 hashing",
            font_size="20sp",
            size_hint=(.1 , .1),
            pos=(450 , 200),
            on_release=go_to_md5
        )
        #sha button
        def go_to_sha512(instance):
            self.manager.current="sha512"
        self.sha256_button=Button(
            text="sha512 hashing",
            font_size="20sp",    
            size_hint=(.1 , .1), 
            pos=(250 , 200),
            on_release=go_to_sha512
        )
        #
        #btn6=Button()
        #more algorithms

        #adding the buttons to the layout
        layout.add_widget(label)
        layout.add_widget(self.ceasar_button)
        layout.add_widget(self.affine_button)
        layout.add_widget(self.vigener_button)
        layout.add_widget(self.md5_button)
        layout.add_widget(self.sha256_button)

        #adding the layout too
        self.add_widget(layout)

class Caesar(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout=FloatLayout()

        #labels 
        self.label_ceasar=Label(
            text="caesar results and warnings! No numbers included or space or special characters aren getting encrypted.",
            size_hint=(.6,.1),
            pos=(400,550)
        )
        label=Label(
            text="Give the key. It must be greater than 0 of course.",
            size_hint=(.6,.1),
            pos=(400,750)
        )

        #text inputs
        self.textinput_ceasar=TextInput(
            font_size="20sp",
            size_hint=(.5,.04),
            pos=(500,850),
            multiline=False
        )
        self.textinput_ceasar_key=TextInput(
            multiline=False,
            font_size="20sp",
            size_hint=(.5,.05),
            pos=(500,700)
        )
        #encoding
        def encode_caesar(instance):
            #storing the memory address
            unencrypted_ceasar=self.textinput_ceasar
            #then we convert the data that it has storde to text, string format
            unencrypted_ceasar=unencrypted_ceasar.text
            encrypted=""
            #storing the memory address
            caesar_key=self.textinput_ceasar_key
            #then we convert the data that it has storde to text, string format
            caesar_key=caesar_key.text
            #storing the memory address
            message=self.label_ceasar
            if caesar_key == "":
                message.text="no key given"
            else:
                #converting the key1 from str to int
                caesar_key=int(caesar_key)
                #checking if the key is correct based on caesar encryption method and showing different warnings based on the given key
                if caesar_key < 0:
                #change the stored data from the text
                    message.text="Key can't be negative."
                elif caesar_key == 0:
                    #change the stored data from the text
                    message.text="Key can't be zero\n Otherwise the text is going to remain the same"
                elif caesar_key > 0 and caesar_key <= 25:
                    if unencrypted_ceasar == "":
                        #change the stored data from the text
                        message.text="No text given please insert a text"
                    else:
                        #encrypting data
                        encrypted=_encrypt_caesar(unencrypted_ceasar, caesar_key)
                        #using specific format to show to the user the encrypted message
                        #change the stored data from the text
                        message.text=position(text=encrypted)
                else:
                    message.text="Key can't be greater than 25."
        def decode_caesar_with_given_key(instance):
            #storing the memory address
            text=self.textinput_ceasar
            #then we convert the data that it has storde to text, string format
            text=text.text
            #storing the memory address
            message=self.label_ceasar
            #storing the memory address
            caesar_key=self.textinput_ceasar_key
            #then we convert the data that it has storde to text, string format
            caesar_key=caesar_key.text
            if caesar_key == "":
                message.text="no key given"
            else:
                #converting the key1 from str to int
                caesar_key=int(caesar_key)
                #checking if the key is correct based on caesar encryption method and showing different warnings based on the given key
                if caesar_key < 0:
                #change the stored data from the text
                    message.text="Key can't be negative."
                elif caesar_key == 0:
                    #change the stored data from the text
                    message.text="Key can't be zero\n Otherwise the text is going to remain the same"
                elif caesar_key > 0 and caesar_key <= 25:
                    if text == "":
                        #change the stored data from the text
                        message.text="No text given please insert a text"
                    else:
                        #encrypting data
                        decode=_decrypt_caesar(text,caesar_key)
                        #using specific format to show to the user the encrypted message
                        #change the stored data from the text
                        message.text=position(text=decode)
                else:
                    #change the stored data from the text
                    message.text="Key can't be greater than 25." 
        def show_frequency_caesar(instance):
            y=show_frequency_analysis_in_text(text=self.textinput_ceasar)
        #buttons
        self.encode_ceasar_button=Button(
            text="encode data",
            font_size="20sp",
            size_hint=(.1,.05),
            pos=(1500,750),
            on_release=encode_caesar
        )
        self.decode_ceasar_button=Button(
            text="decode data",
            font_size="20sp",
            size_hint=(.1,.05),
            pos=(1500,700),
            on_release=decode_caesar_with_given_key
        )
        self.show_frequency_analysis_in_unencrypted_text_ceasar_button=Button(
            text="frequency analysis",
            font_size="20sp",
            size_hint=(.15,.05),
            pos=(1500,650),
            on_release=show_frequency_caesar
        )
        def go_back(instance):
            self.manager.current="main"
        self.button_back_from_caesar=Button(
            text="back",
            font_size="20sp",
            size_hint=(.1,.05),
            pos=(1500,600),
            on_release=go_back
        )

        #adding the widgets
        layout.add_widget(self.label_ceasar)
        layout.add_widget(self.textinput_ceasar)
        layout.add_widget(label)
        layout.add_widget(self.textinput_ceasar_key)
        layout.add_widget(self.encode_ceasar_button)
        layout.add_widget(self.decode_ceasar_button)
        layout.add_widget(self.show_frequency_analysis_in_unencrypted_text_ceasar_button)
        layout.add_widget(self.button_back_from_caesar)

        #adding the layout too
        self.add_widget(layout)

class Affine(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout=FloatLayout()

        #labels
        self.label_Affine=Label(
            text="affine results and warnings!",
            size_hint=(.5,.1),
            pos=(0,600)
        )
        self.label_affine_key1=Label(
            text="Give the 2 keys. they must be greater than 0 of course.",
            size_hint=(.6,.1),
            pos=(400,600)
        )
        self.label_affine_key_1=Label(
            text="key 1",
            size_hint=(.4,.1),
            pos=(500,650)
        )
        self.label_affine_key_2=Label(
            text="Key 2",
            size_hint=(.4,.1),
            pos=(750,650)
        )
        #textinputs
        self.textinput_affine=TextInput(
            font_size="20sp",
            size_hint=(.4,.05),
            pos=(0,750),
            multiline=False
        )
        self.textinput_affine_key1=TextInput(
            size_hint=(.1,.05),
            pos=(800,750),
            multiline=False
        )
        self.textinput_affine_key2=TextInput(
            size_hint=(.1,.05),
            pos=(1025,750),
            multiline=False
        )
        #functionality for the buttons
        def encode_affine(instance):
            global fail
            #storing the memory address
            unencrypted_affine=self.textinput_affine
            #then we convert the data that it has storde to text, string format
            unencrypted_affine=unencrypted_affine.text
            #storing the memory address
            key1=self.textinput_affine_key1
            #then we convert the data that it has storde to text, string format
            key1=key1.text
            #storing the memory address
            key2=self.textinput_affine_key2
            #then we convert the data that it has storde to text, string format
            key2=key2.text
            check_keys=0
            #storing the memory address
            label=self.label_Affine
            if key1 == "":
                check_keys=1
            if key2 == "":
                check_keys =1
            if key1== "" and key2 == "":
                label.text="No keys given"
                check_keys=2
            if check_keys ==1:
                label.text="one of the keys is missing"
            if check_keys==0:
                #converting the key1 from str to int
                key1=int(key1)
                #converting the key2 from str to int
                key2=int(key2)
                #checking if the keys are correct based on affine encryption method and showing different messages to the user based on the keys given
                if key1 < 0 and key2 < 0:
                    #change the stored data from the text
                    label.text="Both keys can't be negative."
                elif key1 < 0 and key2 == 0:
                    #change the stored data from the text
                    label.text="Key 1 can't be negative and key 2 zero"
                elif key1 < 0 and key2 > 0:
                    #change the stored data from the text
                    label.text="Key 1 can't be negative."
                elif key1 == 0 and key2 < 0:
                    #change the stored data from the text
                    label.text="Key 2 can't be negative and key 1 zero"
                elif key1 == 0 and key2 == 0:
                    #change the stored data from the text
                    label.text="Both keys can't be zero."
                elif key1 == 0 and key2 > 0:
                    #change the stored data from the text
                    label.text="Key 1 can't zero"
                    #change the stored data from the text
                elif key1 > 0 and key2 < 0:
                    #change the stored data from the text
                    label.text="Key 2 can't be negative"
                elif key1 > 0 and key2 == 0:
                    #change the stored data from the text
                    label.text="key can't be zero"
                else:
                    encrypted=affine_cipher(text=unencrypted_affine, a=key1, b=key2, mode='encrypt')
                    #showing the data in a specific format
                    label.text=position(encrypted)
        def affine_decode(instance):
            global fail
            #storing the memory address
            label=self.label_Affine
            #storing the memory address
            text=self.textinput_affine
            #then we convert the data that it has storde to text, string format
            text=text.text
            #storing the memory address
            key1=self.textinput_affine_key1
            #then we convert the data that it has storde to text, string format
            key1=key1.text
            #storing the memory address
            key2=self.textinput_affine_key2
            check_keys=0
            if key1 == "":
                check_keys=1
            if key2 == "":
                check_keys =1
            if key1== "" and key2 == "":
                label.text="No keys given"
                check_keys=2
            if check_keys ==1:
                label.text="one of the keys is missing"
            if check_keys ==0:
                #then we convert the data that it has storde to text, string format
                key2=key2.text
                #converting the key from str to int
                key2=int(key2)
                #converting the key from str to int
                key1=int(key1)
                #checking if the keys are correct based on affine encryption method and showing different messages to the user based on the keys given
                if key1 < 0 and key2 < 0:
                    #change the stored data from the text
                    label.text="Both keys can't be negative."
                elif key1 < 0 and key2 == 0:
                    #change the stored data from the text
                    label.text="Key 1 can't be negative and key 2 zero"
                elif key1 < 0 and key2 > 0:
                    #change the stored data from the text
                    label.text="Key 1 can't be negative."
                elif key1 == 0 and key2 < 0:
                    #change the stored data from the text
                    label.text="Key 2 can't be negative and key 1 zero"
                elif key1 == 0 and key2 == 0:
                    #change the stored data from the text
                    label.text="Both keys can't be zero."
                elif key1 == 0 and key2 > 0:
                    #change the stored data from the text
                    label.text="Key 1 can't zero"
                elif key1 > 0 and key2 < 0:
                    #change the stored data from the text
                    label.text="Key 2 can't be negative"
                elif key1 > 0 and key2 == 0:
                    #change the stored data from the text
                    label.text="key can't be zero"
                else:
                    encrypted=affine_cipher(text=text, a=key1, b=key2, mode='decrypt')
                    if fail == False:                   
                        #showing the data in a specific format
                        label.text=position(encrypted)
                    else:
                        label.text="base is not invertible for the given modulus"
        def show_frequency_affine(instance):
            y=show_frequency_analysis_in_text(text=self.textinput_affine)
        def go_back(instance):
            self.manager.current="main"
        #buttons
        self.encode_affine_button=Button(
            text="encode data",
            font_size="20sp",
            size_hint=(.1,.05),
            pos=(1225,750),
            on_release=encode_affine
        )
        self.decode_affine_button=Button(
            text="decode data",
            font_size="20sp",
            size_hint=(.1,.05),
            pos=(1425,750),
            on_release=affine_decode
        )
        self.show_frequency_analysis_in_unencrypted_text_affine_button=Button(
            text="frequency analysis",
            font_size="20sp",
            size_hint=(.125,.05),
            pos=(1625,750),
            on_release=show_frequency_affine
        )
        self.button_back_from_affine=Button(
            text="back",
            font_size="20sp",
            size_hint=(.1,.05),
            pos=(1625,700),
            on_release=go_back
        )

        #adding the widgets
        layout.add_widget(self.label_Affine)
        layout.add_widget(self.textinput_affine)
        layout.add_widget(self.label_affine_key1)
        layout.add_widget(self.label_affine_key_1)
        layout.add_widget(self.textinput_affine_key1)
        layout.add_widget(self.label_affine_key_2)
        layout.add_widget(self.textinput_affine_key2)
        layout.add_widget(self.encode_affine_button)
        layout.add_widget(self.decode_affine_button)
        layout.add_widget(self.show_frequency_analysis_in_unencrypted_text_affine_button)
        layout.add_widget(self.button_back_from_affine)

        #adding layout too
        self.add_widget(layout)

#function that makes the key to have the same size with the text eg hello key=to returns totot
def extend_key(unencrypted, key):
    key = list(key)
    if len(unencrypted) == len(key):
        return key
    else:
        for i in range(len(unencrypted) - len(key)):
            key.append(key[i % len(key)])
    return "".join(key)
#def to encrypt with given key based on vigener cipher board
def encrypt_vigenere(unencrypted, key):
    encrypted_text = []
    key = extend_key(unencrypted, key)
    for i in range(len(unencrypted)):
        char = unencrypted[i]
        if char.isupper():
            #converting the char to a number in the ascii board and then based to the vigener we then convert the new valuw to a char
            encrypted_char = chr((ord(char) + ord(key[i]) - 2 * ord('A')) % 26 + ord('A'))
        elif char.islower():
            #converting the char to a number in the ascii board and then based to the vigener we then convert the new valuw to a char
            encrypted_char = chr((ord(char) + ord(key[i]) - 2 * ord('a')) % 26 + ord('a'))
        else:
            encrypted_char = char
        encrypted_text.append(encrypted_char)
    return "".join(encrypted_text)
#def to decrypt with given key based on vigener cipher
def decrypt_vigenere(encrypted, key):
    decrypted_text = []
    key = extend_key(encrypted, key)
    for i in range(len(encrypted)):
        char = encrypted[i]
        if char.isupper():
            #converting the char to a number in the ascii board and then based to the vigener we then convert the new valuw to a char
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord('A'))
        elif char.islower():
            #converting the char to a number in the ascii board and then based to the vigener we then convert the new valuw to a char
            decrypted_char = chr((ord(char) - ord(key[i]) + 26) % 26 + ord('a'))
        else:
            decrypted_char = char
        decrypted_text.append(decrypted_char)
    return "".join(decrypted_text)
#defining the class that will contain the functions about the calcuation of the vigener encryption,decryption,frequency analysis and to save to a file the data
class Vigener(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout=FloatLayout()
        
        #labels
        self.label_vigener=Label(
            text="vigener cypher warnings and results",
            size_hint=(.1,.05),
            pos=(300,600)
        )
        self.label_vigener_key=Label(
            text="Give the key word.",
            size_hint=(.1,.05),
            pos=(1000,700)
        )
        #textinputs
        self.textinput_vigener=TextInput(
            font_size="20sp",
            size_hint=(.4,.05),
            pos=(0,750),
            multiline=False
        )
        self.textinput_vigener_key=TextInput(
            font_size="20sp",
            size_hint=(.4,.05),
            pos=(800,750),
            multiline=False
        )
        #functionality of the buttons
        def encode_vigener(instance):
            #storing the memory address
            unencrypted=self.textinput_vigener
            #then we convert the data that it has storde to text, string format
            unencrypted=unencrypted.text
            #storing the memory address
            key=self.textinput_vigener_key
            key=key.text
            #storing the memory address
            label=self.label_vigener
            if key == "":
                label.text="No key given"
            else:
                encrypt=encrypt_vigenere(unencrypted=unencrypted,key=key)
                #formating the data
                show=position(encrypt)
                #change the stored value from the text
                label.text=show
        def decode_vigener(instance):
            #storing the memory address
            unencrypted=self.textinput_vigener
            #then we convert the data that it has storde to text, string format
            unencrypted=unencrypted.text
            #storing the memory address
            key=self.textinput_vigener_key
            #then we convert the data that it has storde to text, string format
            key=key.text
            #storing the memory address
            label=self.label_vigener
            if key == "":
                #then we convert the data that it has storde to text, string format and put new data
                label.text="no key given"
            else:
                encrypt=decrypt_vigenere(encrypted=unencrypted,key=key)
                #formating data
                show=position(encrypt)
                #change the stored data from the text
                label.text=show
        def show_frequency_vigener(instance):
            y=show_frequency_analysis_in_text(text=self.textinput_vigener)
        def go_back(instance):
            self.manager.current="main"
        #buttons
        self.encode_vigener_button=Button(
            text="encode data",
            font_size="20sp",
            size_hint=(.1,.05),
            pos=(1000,650),
            on_release=encode_vigener
        )
        self.decode_vigener_button=Button(
            text="decode data",
            font_size="20sp",
            size_hint=(.1,.05),
            pos=(1200,650),
            on_release=decode_vigener
        )
        self.show_frequency_analysis_in_unencrypted_text_vigener_button=Button(
            text="frequency analysis",
            font_size="20sp",
            size_hint=(.125,.05),
            pos=(1400,650),
            on_release=show_frequency_vigener
        )
        self.button_back_from_vigener=Button(
            text="back",
            font_size="20sp",
            size_hint=(.125,.05),
            pos=(1400,600),
            on_release=go_back
        )
        #adding the widgets
        layout.add_widget(self.label_vigener)
        layout.add_widget(self.textinput_vigener)
        layout.add_widget(self.label_vigener_key)
        layout.add_widget(self.textinput_vigener_key)
        layout.add_widget(self.encode_vigener_button)
        layout.add_widget(self.decode_vigener_button)
        layout.add_widget(self.show_frequency_analysis_in_unencrypted_text_vigener_button)
        layout.add_widget(self.button_back_from_vigener)
        #adding the layout
        self.add_widget(layout)
#check system to decrypt if the user wants
#class for md5
class md5(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout=FloatLayout()

        #labels
        self.label_md5=Label(
            text="md5 results",
            size_hint=(.2,.05),
            pos=(200,600)
        )
        #textinputs
        self.textinput_md5=TextInput(
            font_size="20sp",
            size_hint=(.4,.05),
            pos=(0,750),
            multiline=False
        )
        #functionality of the buttons
        def md5_hashing(instance):
            #storing the memory address
            user_data=self.textinput_md5 
            #retrive data from the memory
            user_data=user_data.text
            #hash what the user is giving
            hashed=hashlib.md5(user_data.encode())
            #converting the data after hash in a text format
            hashed=hashed.hexdigest()
            #storing the memory address
            label=self.label_md5
            #formating data
            show=position(hashed)
            #then we convert the data that it has storde to text, string format and put new data
            label.text=show
        def compare_file(instance):
            # File to check
            file_name = askopenfilename()
            #original hash
            original_hash=self.textinput_md5 
            #retrive data from the memory
            label=self.label_md5
            original_hash=original_hash.text
            md5_returned=""
            #value if the file was given
            find=True
            try:
                file=open(file_name,"rb")
            except TypeError:
                #file wasn't given
                find=False
            if find==True:
                #we open the file in read binary mode
                file=open(file_name, 'rb')
                # read contents of the file
                for x in file:
                    #we remove the \n in the end
                    data=x.strip()
                    #we encrypt the data from the file by line
                    md5_returned+= hashlib.md5(data).hexdigest()+"\n"
                #we close the file
                file.close()
                # Finally compare original MD5 with freshly calculated
                if original_hash == md5_returned:
                    label.text="MD5 verification succeed."
                else:
                    label.text="MD5 verification failed."
            else:
                label.text="No file given"
        def compare_file_string(instance):
            # File to check
            file_name = askopenfilename()
            #original hash
            original_hash=self.textinput_md5 
            #retrive data from the memory
            label=self.label_md5
            original_hash=original_hash.text
            md5_returned=""
            #value if the file was given
            find=True
            try:
                file=open(file_name,"rb")
            except TypeError:
                #file wasn't given
                find=False
            if find==True:
                #we open the file in read binary mode
                file=open(file_name, 'rb')
                # read contents of the file
                for x in file:
                    #we remove the \n in the end
                    data=x.strip()
                    #we encrypt the data from the file by line
                    md5_returned+= hashlib.md5(data).hexdigest()+"\n"
                #we close the file
                file.close()
                # Finally compare original MD5 with freshly calculated
                if original_hash == md5_returned:
                    label.text="MD5 verification succeed."
                else:
                    label.text="MD5 verification failed."
            else:
                label.text="No file given"
        def hash_file(instance):
            #data to hash from file
            file_name = askopenfilename()
            #storing the memory address
            label=self.label_md5
            md5_returned=""
            #value if the file was given
            find=True
            try:
                file=open(file_name, 'r')
            except TypeError:
                #file wasn't given
                find=False
            if find == True:
                #we open the file in read mode
                file=open(file_name, 'r')
                for x in file:
                    #we remove the \n in the end
                    data=x.strip()
                    #we hash the data
                    md5_returned+= hashlib.md5(data.encode()).hexdigest()+"\n"
                #we close the file
                file.close()
                #new file path
                store_to_a_new_file=askdirectory()
                store_to_a_new_file+="/md5_results.txt"
                if store_to_a_new_file == "/md5_results.txt":
                    label.text="no directory/folder given"
                else:
                    #we open the file and store it to a variable named store
                    with open(store_to_a_new_file,"w") as store:
                        #we store the hashes
                        data_stored=store.write(md5_returned)
                    #we close the file
                    store.close()
            else:
                label.text="no file given"
        def compare_files(instance):
            #get paths of file_name1 and file_name2 in string format
            file_name1=askopenfilename()
            file_name2=askopenfilename()
            data1=""
            data2=""
            md5_returned1=[]
            md5_returned2=[]
            label=self.label_md5
            #values if the file was given
            find1=True
            find2=True
            try:
                file1=open(file_name1,"r")
            except TypeError:
                #if file isn't given
                find1=False
            try:
                file2=open(file_name2,"r")
            except TypeError:
                #if file isn't given
                find2=False
            if find1== True and find2== True:
                #both files were given and we open them in read mode
                file1=open(file_name1,"r")
                file2=open(file_name2,"r")
                for x in file1:
                    #we remove the \n in the ned
                    data1=x.strip()
                    #we hash
                    md5_returned1.append(hashlib.md5(data1.encode()).hexdigest()+"\n")
                for y in file2:
                    #we remove the \n in the ned
                    data2=y.strip()
                    #we hash
                    md5_returned2.append(hashlib.md5(data2.encode()).hexdigest()+"\n")
                #closing both files
                file1.close()
                file2.close()
                #we check if both boards which have hashes have the same lenghth,if so they have the same number of data
                l1=len(md5_returned1)
                l2=len(md5_returned2)
                #is used to count the successful hashes,those that are equal
                success=0
                #we check if we have the same amount of hashes
                if l1==l2:
                    #we check for successful hashes and if their number is equal with the length of the board this means all hashes are successful
                    for i in range(l1):
                        if md5_returned1[i]==md5_returned2[i]:
                            success+=1
                    if success == l1:
                        label.text="all hashes are the same,so success"
                    else:
                        label.text="some hashes are different,so it failed"
                else:
                    label.text="one file contains more hashes than the other"
            elif find1 == True and file2 == False:
                label.text="file 2 is missing"
            else:
                label.text="file 1 is missing"
        def go_back(instance):
            self.manager.current="main"
        #buttons
        self.hash_md5_button=Button(
            text="hash data",
            font_size="20sp",
            size_hint=(.1,.05),
            pos=(1300,650),
            on_release=md5_hashing
        )
        self.hash_md5_file_compare_button=Button(
            text="compare hash with hashed file",
            font_size="20sp",
            size_hint=(.15,.05),
            pos=(1000,650),
            on_release=compare_file
        )
        self.hash_md5_file_compare_unhashed_button=Button(
            text="compare hash with unhashed file",
            font_size="20sp",
            size_hint=(.15,.05),
            pos=(700,650),
            on_release=compare_file_string
        )
        self.hash_md5_file_hash_button=Button(
            text="hash from file and store in new",
            font_size="20sp",
            size_hint=(.2,.05),
            pos=(300,650),
            on_release=hash_file
        )
        self.hash_md5_files_compare_button=Button(
            text="compare files with hashes",
            font_size="20sp",
            size_hint=(.15,.05),
            pos=(0,650),
            on_release=compare_files
        )
        self.button_back_from_md5=Button(
            text="back",
            font_size="20sp",
            size_hint=(.1,.05),
            pos=(1500,650),
            on_release=go_back
        )
        #adding widgets
        layout.add_widget(self.label_md5)
        layout.add_widget(self.textinput_md5)
        layout.add_widget(self.hash_md5_button)
        layout.add_widget(self.hash_md5_file_compare_button)
        layout.add_widget(self.hash_md5_file_compare_unhashed_button)
        layout.add_widget(self.hash_md5_file_hash_button)
        layout.add_widget(self.hash_md5_files_compare_button)
        layout.add_widget(self.button_back_from_md5)
        #adding layout too
        self.add_widget(layout)
class sha512(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout=FloatLayout()

        #labels
        self.label_sha512=Label(
            text="sha512 results",
            size_hint=(.4,.05),
            pos=(300,600)
        )
        #textinputs
        self.textinput_sha512=TextInput(
            font_size="20sp",
            size_hint=(.4,.05),
            pos=(0,750),
            multiline=False
        )
        #functionality of the buttons
        def sha512_hashing(instance):
            #string address
            label=self.label_sha512 
            data=self.textinput_sha512
            #formating data from adress to text
            data=data.text
            #removing \n in the end
            data=data.strip()
            #encode data
            data=data.encode()
            #hash with sha512
            hashed=hashlib.sha512(data).hexdigest()
            #show the hash to the user by updating the text in label
            label.text=position(hashed)
        def compare_file_sha512(instance):
            # File to check
            file_name = askopenfilename()
            #original hash
            original_hash=self.textinput_sha512
            #retrive data from the memory
            label=self.label_sha512
            original_hash=original_hash.text
            sha512_returned=""
            #value if the file was given
            find=True
            try:
                file=open(file_name,"rb")
            except TypeError:
                #file wasn't given
                find=False
            if find==True:
                #we open the file in read binary mode
                file=open(file_name, 'rb')
                # read contents of the file
                for x in file:
                    #we remove the \n in the end
                    data=x.strip()
                    #we encrypt the data from the file by line
                    sha512_returned+= hashlib.sha512(data).hexdigest()+"\n"
                #we close the file
                file.close()
                # Finally compare original MD5 with freshly calculated
                if original_hash == sha512_returned:
                    label.text="sha512 verification succeed."
                else:
                    label.text="sha512 verification failed."
            else:
                label.text="No file given"
        def compare_file_string_sha512(instance):
            # File to check
            file_name = askopenfilename()
            #original hash
            original_hash=self.textinput_sha512
            #retrive data from the memory
            label=self.label_sha512
            original_hash=original_hash.text
            sha512_returned=""
            #value if the file was given
            find=True
            try:
                file=open(file_name,"rb")
            except TypeError:
                #file wasn't given
                find=False
            if find==True:
                #we open the file in read binary mode
                file=open(file_name, 'rb')
                # read contents of the file
                for x in file:
                    #we remove the \n in the end
                    data=x.strip()
                    #we encrypt the data from the file by line
                    sha512_returned+= hashlib.md5(data.encode()).hexdigest()+"\n"
                #we close the file
                file.close()
                # Finally compare original MD5 with freshly calculated
                if original_hash == sha512_returned:
                    label.text="sha512 verification succeed."
                else:
                    label.text="sha512 verification failed."
            else:
                label.text="No file given"
        def hash_file_sha512(instance):
            file_name = askopenfilename()
            #original hash
            original_hash=self.textinput_sha512
            #retrive data from the memory
            label=self.label_sha512
            original_hash=original_hash.text
            sha512_returned=""
            #value if the file was given
            find=True
            try:
                file=open(file_name, 'r')
            except TypeError:
                #file wasn't given
                find=False
            if find == True:
                #we open the file in read mode
                file=open(file_name, 'r')
                for x in file:
                    #we remove the \n in the end
                    data=x.strip()
                    #we hash the data
                    sha512_returned+= hashlib.sha512(data.encode()).hexdigest()+"\n"
                #we close the file
                file.close()
                #new file path
                store_to_a_new_file=askdirectory()
                store_to_a_new_file+="/sha512_results.txt"
                if store_to_a_new_file == "/sha512_results.txt":
                    label.text="no directory/folder given"
                else:
                    #we open the file and store it to a variable named store
                    with open(store_to_a_new_file,"w") as store:
                        #we store the hashes
                        data_stored=store.write(sha512_returned)
                    #we close the file
                    store.close()
            else:
                label.text="no file given"
        def compare_files_sha512(instance):
            #get paths of file_name1 and file_name2 in string format
            file_name1=askopenfilename()
            file_name2=askopenfilename()
            data1=""
            data2=""
            sha512_returned1=[]
            sha512_returned2=[]
            label=self.label_sha512
            #values if the file was given
            find1=True
            find2=True
            try:
                file1=open(file_name1,"r")
            except TypeError:
                #if file isn't given
                find1=False
            try:
                file2=open(file_name2,"r")
            except TypeError:
                #if file isn't given
                find2=False
            if find1== True and find2== True:
                #both files were given and we open them in read mode
                file1=open(file_name1,"r")
                file2=open(file_name2,"r")
                for x in file1:
                    #we remove the \n in the ned
                    data1=x.strip()
                    #we hash
                    sha512_returned1.append(hashlib.sha512(data1.encode()).hexdigest()+"\n")
                for y in file2:
                    #we remove the \n in the ned
                    data2=y.strip()
                    #we hash
                    sha512_returned2.append(hashlib.sha512(data2.encode()).hexdigest()+"\n")
                #closing both files
                file1.close()
                file2.close()
                #we check if both boards which have hashes have the same lenghth,if so they have the same number of data
                l1=len(sha512_returned1)
                l2=len(sha512_returned2)
                #is used to count the successful hashes,those that are equal
                success=0
                #we check if we have the same amount of hashes
                if l1==l2:
                    #we check for successful hashes and if their number is equal with the length of the board this means all hashes are successful
                    for i in range(l1):
                        if sha512_returned1[i]==sha512_returned2[i]:
                            success+=1
                    if success == l1:
                        label.text="all hashes are the same,so success"
                    else:
                        label.text="some hashes are different,so it failed"
                else:
                    label.text="one file contains more hashes than the other"
            elif find1 == True and file2 == False:
                label.text="file 2 is missing"
            else:
                label.text="file 1 is missing"
        def go_back(instance):
            self.manager.current="main"
        #buttons
        self.hash_sha512_button=Button(
            text="hash data",
            font_size="20sp",
            size_hint=(.1,.05),
            pos=(1300,650),
            on_release=sha512_hashing
        )
        self.hash_sha512_file_compare_button=Button(
            text="compare hash with hashed file",
            font_size="20sp",
            size_hint=(.15,.05),
            pos=(1000,650),
            on_release=compare_file_sha512
        )
        self.hash_sha512_file_compare_unhashed_button=Button(
            text="compare hash with unhashed file",
            font_size="20sp",
            size_hint=(.15,.05),
            pos=(700,650),
            on_release=compare_file_string_sha512
        )
        self.hash_sha512_file_hash_button=Button(
            text="hash from file and store in new",
            font_size="20sp",
            size_hint=(.2,.05),
            pos=(300,650),
            on_release=hash_file_sha512
        )
        self.hash_sha512_files_compare_button=Button(
            text="compare files with hashes",
            font_size="20sp",
            size_hint=(.15,.05),
            pos=(0,650),
            on_release=compare_files_sha512
        )
        self.button_back_from_sha512=Button(
            text="back",
            font_size="20sp",
            size_hint=(.1,.05),
            pos=(1500,650),
            on_release=go_back
        )
        #adding widgets
        layout.add_widget(self.label_sha512)
        layout.add_widget(self.textinput_sha512)
        layout.add_widget(self.hash_sha512_button)
        layout.add_widget(self.hash_sha512_file_compare_button)
        layout.add_widget(self.hash_sha512_file_compare_unhashed_button)
        layout.add_widget(self.hash_sha512_file_hash_button)
        layout.add_widget(self.hash_sha512_files_compare_button)
        layout.add_widget(self.button_back_from_sha512)
        #adding layout too
        self.add_widget(layout)
#-----------------------------------------------------#
#              Main Functionality

#creating a def in order to format the text in the screen
def position(text) -> str: #it returns a string
    copy=""
    start=0
    end=120
    number=len(text)
    n=0
    if number==120:
        while n <= number//120:
            n+=1
            for i in range(start,end):
                copy+=text[i]
            copy+="\n"
            start+=120
            end+=120
    elif number <120:
        for i in range(0,len(text)):
            copy+=text[i]
    elif number>120 and number%120!=0:
        while n < number//120:
            n+=1
            for i in range(start,end):
                copy+=text[i]
            copy+="\n"
            start+=120
            end+=120
        end=n*120
        for i in range (end,len(text)):
            copy+=text[i]
    elif number>120 and number%120==0:
        while n <= number//120:
            n+=1
            for i in range(start,end):
                copy+=text[i]
            copy+="\n"
            start+=120
            end+=120
    return copy
def show_frequency_analysis_in_text(text):
    text=text.text
    #convert the data that it has storde to text, string format
    counter = Counter(text)
    data_words = counter.keys()
    words_counts = counter.values()
    indexes = np.arange(len(data_words))
    width = 0.7
    plt.bar(indexes, words_counts, width)
    plt.xticks(indexes + width * 0.5, data_words)
    plt.show()
def _encrypt_caesar(text,key):
    result = ""
    for char in text:
        # Encrypt uppercase characters
        if (char.isupper()):
            result += chr((ord(char) + key-65) % 26 + 65)
        # Encrypt lowercase characters
        else:
            result += chr((ord(char) + key - 97) % 26 + 97)
    return result
#function to decrypt caesar cipher with given key
def _decrypt_caesar(text,key):
    result = ""
    for char in text:
        # Encrypt uppercase characters
        if (char.isupper()):
            #chr makes an integer into a letter based on ascii board and ord makes a letter into an integer based on the same board
            result += chr((ord(char) - key-65) % 26 + 65)
        # Encrypt lowercase characters
        else:
            #chr makes an integer into a letter based on ascii board and ord makes a letter into an integer based on the same board
            result += chr((ord(char) - key - 97) % 26 + 97)
    return result
#affine cypher encryption and decryption
fail=False
def affine_cipher(text, a, b, mode='encrypt'):
    global fail
    fail=False
    result = ''
    m = 26  # size of the alphabet
    for char in text:
        if char.isalpha():
            #ord makes a character into an number from ascii board
            x = ord(char) - ord('A' if char.isupper() else 'a')
            if mode == 'encrypt':
                #we encrypt based on the formula c=(k1*plain_text + key2) mod 26
                new_x = (a * x + b) % m
            elif mode == 'decrypt':
                # Find the modular multiplicative inverse of a
                try:
                    a_inv = pow(a, -1, m)
                except ValueError:
                    fail=True
                    break
                if fail == False:
                    a_inv = pow(a, -1, m)
                    #we decrypt based on the formula p=(1/a)*(c-key2) mod 26
                    new_x = a_inv * (x - b) % m
                    #chr converts a number from ascii board into a letter
            if fail == False:
                new_char = chr(new_x + ord('A' if char.isupper() else 'a'))
        else:
            new_char = char
        result += new_char
    return result

#Screen Manager
class MyScreenManager(ScreenManager):
    def __init__(self, **kwargs):
        super().__init__(transition=FadeTransition(), **kwargs)
        self.add_widget(MainWindow(name="main"))
        self.add_widget(Caesar(name="caesar"))
        self.add_widget(Affine(name="affine"))
        self.add_widget(Vigener(name="vigenere"))
        self.add_widget(md5(name="md5"))
        self.add_widget(sha512(name="sha512"))

# --------- App ---------
class EncryptionApp(App):
    def build(self):
        Window.maximize()
        return MyScreenManager()


if __name__ == "__main__":
    EncryptionApp().run()


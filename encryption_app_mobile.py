
#general library about gui
import kivy
#library to run the app
from kivy.app import App
#library to build the app
from kivy.lang import Builder
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
#building the app, it's main body and the Builder.load_string() will do the formating
Builder.load_string("""
<MyScreenManager>:
    #in MyScreenManager class we name the other classes we have to call them with the new name later
    Main_window:
        name: "main_app"
    Caesar:
        name: "caesar"
    Affine:
        name: "affine"
    Vigener:
        name: "vigener"
    md5:
        name: "md5"
    sha512:
        name: "sha512"
             
<main_window>
    FloatLayout:
        Label:
            text: "i suggest you not to encrypt a file with: "
            size_hint: .1 , .1 #size settings first x axis and after y axis
            pos: 400 , 800 #position in the screen first x axis and after y axis
        Label:
            text: "caesar,affine and vigener and send it"
            size_hint: .1 , .1 #size settings first x axis and after y axis
            pos: 400 , 750 #position in the screen first x axis and after y axis
        Label:
            text: "over the internet it can be decrypted easily"
            size_hint: .1 , .1 #size settings first x axis and after y axis
            pos: 400 , 700 #position in the screen first x axis and after y axis
        Button:
            text: "ceasar encoding" #text on the button
            id: ceasar_button #an id to call it in a function
            font_size: "10sp"  #size of letters
            size_hint: .25 , .05 #size settings first x axis and after y axis
            pos: 250 , 400 #position in the screen first x axis and after y axis
            on_release: 
                #after releasing the button we give it to do something inside the function,it can be whatever we want 
                app.root.current = "caesar"
        Button:
            text: "affine encoding" #text on the button
            id: affine_button #an id to call it in a function
            font_size: "10sp"  #size of letters
            size_hint: .25 , .05 #size settings first x axis and after y axis
            pos: 400 , 525 #position in the screen first x axis and after y axis
            on_release: 
                #after releasing the button we give it to do something inside the function,it can be whatever we want 
                app.root.current = "affine"
        Button:
            text: "vigener encoding"  #text on the button
            id: vigener_button  #an id to call it in a function
            font_size: "10sp"    #size of letters
            size_hint: .25 , .05 #size settings first x axis and after y axis
            pos: 550 , 400 #position in the screen first x axis and after y axis
            on_release:
                #after releasing the button we give it to do something inside the function,it can be whatever we want
                app.root.current = "vigener"
        Button:
            text: "md5 hashing"  #text on the button
            id: md5_button  #an id to call it in a function
            font_size: "10sp"    #size of letters
            size_hint: .25 , .05 #size settings first x axis and after y axis
            pos: 550 , 275 #position in the screen first x axis and after y axis
            on_release:
                #after releasing the button we give it to do something inside the function,it can be whatever we want
                app.root.current = "md5" 
        Button:
            text: "sha512 hashing"  #text on the button
            id: sha256_button  #an id to call it in a function
            font_size: "10sp"    #size of letters
            size_hint: .25 , .05 #size settings first x axis and after y axis
            pos: 250 , 275 #position in the screen first x axis and after y axis
            on_release:
                #after releasing the button we give it to do something inside the function,it can be whatever we want
                app.root.current = "sha512"
<Caesar>:
    FloatLayout:
        orientation: 'vertical' 
        Label:
            text: "caesar results and warnings!" #text for user
            id: label_ceasar  #an id to call it in a function
            size_hint: .5 , .1 #size settings first x axis and after y axis
            pos: 50 , 1625 #position in the screen first x axis and after y axis
            font_size: "10sp"  #size of letters
        TextInput:
            id: textinput_ceasar  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .5 , .04 #size settings first x axis and after y axis
            pos: 50 , 2000 #position in the screen first x axis and after y axis
            multiline: False
        Label:
            text: "Give the key. It must be greater than 0 of course." #text for user
            id: label_ceasar_key  #an id to call it in a function
            size_hint: .6 , .1 #size settings first x axis and after y axis
            pos: 25 , 1825 #position in the screen first x axis and after y axis
            font_size: "10sp"  #size of letters
        TextInput:
            id: textinput_ceasar_key  #an id to call it in a function
            multiline: False #multiline not allowed
            font_size: "20sp" #size of letters
            size_hint: .5 , .04 #size settings first x axis and after y axis
            pos: 50 , 1800 #position in the screen first x axis and after y axis
            multiline: False
        Button:
            text: "encode data" #text on the button
            id: encode_ceasar_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 700 , 2000 #position in the screen first x axis and after y axis
            on_release:
                root.encode_caesar()
        Button:
            text: "decode data" #text on the button
            id: decode_ceasar_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 700 , 1900 #position in the screen first x axis and after y axis
            on_release:
                root.decode_caesar_with_given_key()
        Button:
            text: "frequency analysis" #text on the button
            id: show_frequency_analysis_in_unencrypted_text_ceasar_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 700 , 1800 #position in the screen first x axis and after y axis
            on_release:
                root.show_frequency_caesar()
        Button:
            text: "back" #text on the button
            id: button_back_from_caesar  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 700 , 1700 #position in the screen first x axis and after y axis
            on_release:
                app.root.current = "main_app"
<Affine>:
    FloatLayout:
        orientation: 'vertical' 
        Label:
            text: "affine results and warnings!" #text for user
            id: label_Affine  #an id to call it in a function
            size_hint: .5 , .1 #size settings first x axis and after y axis
            font_size: "10sp"
            pos: 200 , 1400 #position in the screen first x axis and after y axis
        TextInput:
            id: textinput_affine  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .4 , .04 #size settings first x axis and after y axis
            pos: 0 , 2000 #position in the screen first x axis and after y axis
            multiline: False
        Label:
            text: "Give the 2 keys. they must be greater than 0 of course." #text for user
            id: label_affine_key1  #an id to call it in a function
            size_hint: .6 , .1 #size settings first x axis and after y axis
            pos: 100 , 1800 #position in the screen first x axis and after y axis
            font_size: "10sp"
        Label:
            text: "key 1" #text for user
            id: label_affine_key_1  #an id to call it in a function
            size_hint: .1 , .04 #size settings first x axis and after y axis
            pos: 0 , 1600 #position in the screen first x axis and after y axis
            font_size: "10sp"
        TextInput:
            id: textinput_affine_key1  #an id to call it in a function
            multiline: False #multiline not allowed
            size_hint: .1 , .04 #size settings first x axis and after y axis
            pos: 0 , 1700 #position in the screen first x axis and after y axis
            multiline: False
        Label:
            text: "Key 2" #text for user
            id: label_affine_key_2  #an id to call it in a function
            size_hint: .1 , .04 #size settings first x axis and after y axis
            font_size: "10sp"
            pos: 200 , 1600 #position in the screen first x axis and after y axis
        TextInput:
            id: textinput_affine_key2  #an id to call it in a function
            multiline: False #multiline not allowed
            size_hint: .1 , .04 #size settings first x axis and after y axis
            pos: 200 , 1700 #position in the screen first x axis and after y axis
            multiline: False
        Button:
            text: "encode data" #text on the button
            id: encode_affine_button  #an id to call it in a function
            font_size: "10sp"  #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 800 , 2000 #position in the screen first x axis and after y axis
            on_release:
                root.encode_affine()
        Button:
            text: "decode data" #text on the button
            id: encode_affine_button  #an id to call it in a function
            font_size: "10sp"  #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 800 , 1900 #position in the screen first x axis and after y axis
            on_release:
                root.affine_decode()
        Button:
            text: "frequency analysis" #text on the button
            id: show_frequency_analysis_in_unencrypted_text_affine_button  #an id to call it in a function
            font_size: "10sp"  #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 800 , 1800 #position in the screen first x axis and after y axis
            on_release:
                root.show_frequency_affine()
        Button:
            text: "back" #text on the button
            id: button_back_from_affine  #an id to call it in a function
            font_size: "10sp"  #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 800 , 1700 #position in the screen first x axis and after y axis
            on_release:
                app.root.current = "main_app"
<Vigener>:
    FloatLayout:
        orientation: 'vertical' 
        Label:
            text: "vigener cypher warnings and results" #text for user
            id: label_vigener  #an id to call it in a function
            size_hint: .5 , .04 #size settings first x axis and after y axis
            pos: 200 , 1600 #position in the screen first x axis and after y axis  
            font_size: "10sp"
        TextInput:
            id: textinput_vigener  #an id to call it in a function
            font_size: "10sp"  #size of letters
            size_hint: .4 , .04 #size settings first x axis and after y axis
            pos: 0 , 2000 #position in the screen first x axis and after y axis
            multiline: False
        Label:
            text: "Give the key word." #text for user
            id: label_vigener_key  #an id to call it in a function
            size_hint: .1 , .04 #size settings first x axis and after y axis
            font_size: "10sp"
            pos: 100 , 1900 #position in the screen first x axis and after y axis
        TextInput:
            id: textinput_vigener_key  #an id to call it in a function
            multiline: False #multiline is not allow
            font_size: "10sp" #size of letters
            size_hint: .4 , .04 #size settings first x axis and after y axis
            pos: 0 , 1800 #position in the screen first x axis and after y axis
            multiline: False
        Button:
            text: "encode data" #text on the button
            id: encode_vigener_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 700 , 2000 #position in the screen first x axis and after y axis
            on_release:
                root.encode_vigener()
        Button:
            text: "decode data" #text on the button
            id: decode_vigener_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 700 , 1900 #position in the screen first x axis and after y axis
            on_release:
                root.decode_vigener()
        Button:
            text: "frequency analysis" #text on the button
            id: show_frequency_analysis_in_unencrypted_text_vigener_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 700 , 1800 #position in the screen first x axis and after y axis
            on_release:
                root.show_frequency_vigener()
        Button:
            text: "back" #text on the button
            id: button_back_from_vigener  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 700 , 1700 #position in the screen first x axis and after y axis
            on_release:
                app.root.current = "main_app"
<md5>:
    FloatLayout:
        orientation: 'vertical'
        Label:
            text: "md5 results" #text for user
            id: label_md5  #an id to call it in a function
            size_hint: .5 , .04 #size settings first x axis and after y axis
            font_size: "10sp"
            pos: 200 , 1400 #position in the screen first x axis and after y axis  
        TextInput:
            id: textinput_md5  #an id to call it in a function
            font_size: "10sp"  #size of letters
            size_hint: .4 , .04 #size settings first x axis and after y axis
            pos: 0 , 2000 #position in the screen first x axis and after y axis
            multiline: False
        Button:
            text: "hash data" #text on the button
            id: hash_md5_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 600 , 2000 #position in the screen first x axis and after y axis
            on_release:
                root.md5_hashing()
        Button:
            text: "compare hash with hashed file" #text on the button
            id: hash_md5_file_compare_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .35 , .04 #size settings first x axis and after y axis
            pos: 600 , 1900 #position in the screen first x axis and after y axis
            on_release:
                root.compare_file()
        Button:
            text: "compare hash with unhashed file" #text on the button
            id: hash_md5_file_compare_unhashed_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .4 , .04 #size settings first x axis and after y axis
            pos: 600 , 1800 #position in the screen first x axis and after y axis
            on_release:
                root.compare_file_string()
        Button:
            text: "hash from file and store in new" #text on the button
            id: hash_md5_file_hash_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .4 , .04 #size settings first x axis and after y axis
            pos: 600 , 1700 #position in the screen first x axis and after y axis
            on_release:
                root.hash_file()
        Button:
            text: "compare files with hashes" #text on the button
            id: hash_md5_files_compare_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .35 , .04 #size settings first x axis and after y axis
            pos: 600, 1600 #position in the screen first x axis and after y axis
            on_release:
                root.compare_files()
        Button:
            text: "back" #text on the button
            id: button_back_from_md5  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 600 , 1500 #position in the screen first x axis and after y axis
            on_release:
                app.root.current = "main_app"
<sha512>:
    FloatLayout:
        orientation: 'vertical'
        Label:
            text: "sha512 results" #text for user
            id: label_sha512  #an id to call it in a function
            font_size: "10sp"
            size_hint: .4 , .04 #size settings first x axis and after y axis
            pos: 300 , 1400 #position in the screen first x axis and after y axis  
        TextInput:
            id: textinput_sha512  #an id to call it in a function
            font_size: "10sp"  #size of letters
            size_hint: .4 , .04 #size settings first x axis and after y axis
            pos: 0 , 2000 #position in the screen first x axis and after y axis
            multiline: False
        Button:
            text: "hash data" #text on the button
            id: hash_sha512_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 600 , 2000 #position in the screen first x axis and after y axis
            on_release:
                root.sha512_hashing()
        Button:
            text: "compare hash with hashed file" #text on the button
            id: hash_sha512_file_compare_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .35 , .04 #size settings first x axis and after y axis
            pos: 600 , 1900 #position in the screen first x axis and after y axis
            on_release:
                root.compare_file_sha512()
        Button:
            text: "compare hash with unhashed file" #text on the button
            id: hash_sha512_file_compare_unhashed_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .4 , .04 #size settings first x axis and after y axis
            pos: 600 , 1800 #position in the screen first x axis and after y axis
            on_release:
                root.compare_file_string_sha512()
        Button:
            text: "hash from file and store in new" #text on the button
            id: hash_sha512_file_hash_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .4 , .04 #size settings first x axis and after y axis
            pos: 600 , 1700 #position in the screen first x axis and after y axis
            on_release:
                root.hash_file_sha512()
        Button:
            text: "compare files with hashes" #text on the button
            id: hash_sha512_files_compare_button  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .35 , .04 #size settings first x axis and after y axis
            pos: 600, 1600 #position in the screen first x axis and after y axis
            on_release:
                root.compare_files_sha512()
        Button:
            text: "back" #text on the button
            id: button_back_from_sha512  #an id to call it in a function
            font_size: "10sp" #size of letters
            size_hint: .2 , .04 #size settings first x axis and after y axis
            pos: 600 , 1500 #position in the screen first x axis and after y axis
            on_release:
                app.root.current = "main_app"
""")
#defining the class that will contain the main menu
class Main_window(Screen):
    pass
#creating a def in order to format the text in the screen
def position(text) -> str: #it returns a string
    copy=""
    start=0
    end=60
    number=len(text)
    n=0
    if number==60:
        while n <= number//60:
            n+=1
            for i in range(start,end):
                copy+=text[i]
            copy+="\n"
            start+=60
            end+=60
    elif number <60:
        for i in range(0,len(text)):
            copy+=text[i]
    elif number>60 and number%60!=0:
        while n < number//60:
            n+=1
            for i in range(start,end):
                copy+=text[i]
            copy+="\n"
            start+=60
            end+=60
        end=n*60
        for i in range (end,len(text)):
            copy+=text[i]
    elif number>60 and number%60==0:
        while n <= number//60:
            n+=1
            for i in range(start,end):
                copy+=text[i]
            copy+="\n"
            start+=60
            end+=60
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
#defining the class that will contain the functions about the calcuation of the ceasar encryption,decryption,frequency analysis and to save to a file the data
class Caesar(Screen):
    def encode_caesar(self):
        #storing the memory address
        unencrypted_ceasar=self.ids.textinput_ceasar
        #then we convert the data that it has storde to text, string format
        unencrypted_ceasar=unencrypted_ceasar.text
        encrypted=""
        #storing the memory address
        caesar_key=self.ids.textinput_ceasar_key
        #then we convert the data that it has storde to text, string format
        caesar_key=caesar_key.text
        #storing the memory address
        message=self.ids.label_ceasar
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
    def decode_caesar_with_given_key(self):
        #storing the memory address
        text=self.ids.textinput_ceasar
        #then we convert the data that it has storde to text, string format
        text=text.text
        #storing the memory address
        message=self.ids.label_ceasar
        #storing the memory address
        caesar_key=self.ids.textinput_ceasar_key
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
    def show_frequency_caesar(self):
        y=show_frequency_analysis_in_text(text=self.ids.textinput_ceasar)
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
#defining the class that will contain the functions about the calcuation of the affine encryption,decryption,frequency analysis and to save to a file the data
class Affine(Screen):
    def encode_affine(self):
        global fail
        #storing the memory address
        unencrypted_affine=self.ids.textinput_affine
        #then we convert the data that it has storde to text, string format
        unencrypted_affine=unencrypted_affine.text
        #storing the memory address
        key1=self.ids.textinput_affine_key1
        #then we convert the data that it has storde to text, string format
        key1=key1.text
        #storing the memory address
        key2=self.ids.textinput_affine_key2
        #then we convert the data that it has storde to text, string format
        key2=key2.text
        check_keys=0
        #storing the memory address
        label=self.ids.label_Affine
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
    def affine_decode(self):
        global fail
        #storing the memory address
        label=self.ids.label_Affine
        #storing the memory address
        text=self.ids.textinput_affine
        #then we convert the data that it has storde to text, string format
        text=text.text
        #storing the memory address
        key1=self.ids.textinput_affine_key1
        #then we convert the data that it has storde to text, string format
        key1=key1.text
        #storing the memory address
        key2=self.ids.textinput_affine_key2
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
    def show_frequency_affine(self):
        y=show_frequency_analysis_in_text(text=self.ids.textinput_affine)
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
    def encode_vigener(self):
        #storing the memory address
        unencrypted=self.ids.textinput_vigener
        #then we convert the data that it has storde to text, string format
        unencrypted=unencrypted.text
        #storing the memory address
        key=self.ids.textinput_vigener_key
        key=key.text
        #storing the memory address
        label=self.ids.label_vigener
        if key == "":
            label.text="No key given"
        else:
            encrypt=encrypt_vigenere(unencrypted=unencrypted,key=key)
            #formating the data
            show=position(encrypt)
            #change the stored value from the text
            label.text=show
    def decode_vigener(self):
        #storing the memory address
        unencrypted=self.ids.textinput_vigener
        #then we convert the data that it has storde to text, string format
        unencrypted=unencrypted.text
        #storing the memory address
        key=self.ids.textinput_vigener_key
        #then we convert the data that it has storde to text, string format
        key=key.text
        #storing the memory address
        label=self.ids.label_vigener
        if key == "":
            #then we convert the data that it has storde to text, string format and put new data
            label.text="no key given"
        else:
            encrypt=decrypt_vigenere(encrypted=unencrypted,key=key)
            #formating data
            show=position(encrypt)
            #change the stored data from the text
            label.text=show
    def show_frequency_vigener(self):
        y=show_frequency_analysis_in_text(text=self.ids.textinput_vigener)
#check system to decrypt if the user wants
#class for md5
class md5(Screen):
    def md5_hashing(self):
        #storing the memory address
        user_data=self.ids.textinput_md5 
        #retrive data from the memory
        user_data=user_data.text
        #hash what the user is giving
        hashed=hashlib.md5(user_data.encode())
        #converting the data after hash in a text format
        hashed=hashed.hexdigest()
        #storing the memory address
        label=self.ids.label_md5
        #formating data
        show=position(hashed)
        #then we convert the data that it has storde to text, string format and put new data
        label.text=show
    def compare_file(self):
        # File to check
        file_name = askopenfilename()
        #original hash
        original_hash=self.ids.textinput_md5 
        #retrive data from the memory
        label=self.ids.label_md5
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
    def compare_file_string(self):
        # File to check
        file_name = askopenfilename()
        #original hash
        original_hash=self.ids.textinput_md5 
        #retrive data from the memory
        label=self.ids.label_md5
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
                md5_returned+= hashlib.md5(data.encode()).hexdigest()+"\n"
            #we close the file
            file.close()
            # Finally compare original MD5 with freshly calculated
            if original_hash == md5_returned:
                label.text="MD5 verification succeed."
            else:
                label.text="MD5 verification failed."
        else:
            label.text="No file given"
    def hash_file(self):
        #data to hash from file
        file_name = askopenfilename()
        #storing the memory address
        label=self.ids.label_md5
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
    def compare_files(self):
        #get paths of file_name1 and file_name2 in string format
        file_name1=askopenfilename()
        file_name2=askopenfilename()
        data1=""
        data2=""
        md5_returned1=[]
        md5_returned2=[]
        label=self.ids.label_md5
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
class sha512(Screen):
    def sha512_hashing(self):
        #string address
        label=self.ids.label_sha512 
        data=self.ids.textinput_sha512
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
    def compare_file_sha512(self):
        # File to check
        file_name = askopenfilename()
        #original hash
        original_hash=self.ids.textinput_sha512
        #retrive data from the memory
        label=self.ids.label_sha512
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
    def compare_file_string_sha512(self):
        # File to check
        file_name = askopenfilename()
        #original hash
        original_hash=self.ids.textinput_sha512
        #retrive data from the memory
        label=self.ids.label_sha512
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
    def hash_file_sha512(self):
        file_name = askopenfilename()
        #original hash
        original_hash=self.ids.textinput_sha512
        #retrive data from the memory
        label=self.ids.label_sha512
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
    def compare_files_sha512(self):
        #get paths of file_name1 and file_name2 in string format
        file_name1=askopenfilename()
        file_name2=askopenfilename()
        data1=""
        data2=""
        sha512_returned1=[]
        sha512_returned2=[]
        label=self.ids.label_sha512
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
#defining class about the screen managment
class MyScreenManager(ScreenManager):
    pass
#class that builds the app
class cryptography(App):
    #function that builds the app 
    def build(self):
        Window.maximize()
        return MyScreenManager()

#library to check the os running
from kivy.utils import platform
            
#we run the app
if __name__=="__main__":
    if platform == 'android':
        from jnius import autoclass
        from kivy.utils import platform

if platform == "android":
        from jnius import autoclass
        PythonActivity = autoclass("org.kivy.android.PythonActivity")
        ActivityInfo = autoclass("android.content.pm.ActivityInfo")
        activity = PythonActivity.mActivity
        # set orientation according to user's preference
        activity.setRequestedOrientation(ActivityInfo.SCREEN_ORIENTATION_USER)
        cryptography().run()

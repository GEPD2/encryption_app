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
#library that handles the images for the background
from kivy.core.image import Image
#library for the borders of an image in the background
from kivy.graphics import BorderImage
#libraries about the coulour of the background
from kivy.graphics import Color, Rectangle
#library about async images, those who are stored in the users disk
from kivy.uix.image import AsyncImage
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
#scroll event library
from kivy.uix.scrollview import ScrollView
#another gui library
import tkinter as tk
#library for hashes
import hashlib
#library to check what os is used in a generic way e.g. Linux or windows
import platform
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
<main_window>
    canvas.before:
        Rectangle:
            pos: self.pos #default posistion is in the midle
            size: self.size #screen size, the screen is the parent
            source: "cruptography/images/g13.jpg" #source of the photo for the background
    FloatLayout:
        Button:
            text: "ceasar encoding" #text on the button
            id: ceasar_button #an id to call it in a function
            font_size: "20sp"  #size of letters
            size_hint: .1 , .1 #size settings first x axis and after y axis
            pos: 250 , 300 #position in the screen first x axis and after y axis
            on_release: 
                #after releasing the button we give it to do something inside the function,it can be whatever we want 
                app.root.current = "caesar"
        Button:
            text: "affine encoding" #text on the button
            id: affine_button #an id to call it in a function
            font_size: "20sp"  #size of letters
            size_hint: .1 , .1 #size settings first x axis and after y axis
            pos: 350 , 400 #position in the screen first x axis and after y axis
            on_release: 
                #after releasing the button we give it to do something inside the function,it can be whatever we want 
                app.root.current = "affine"
        Button:
            text: "vigener encoding"  #text on the button
            id: vigener_button  #an id to call it in a function
            font_size: "20sp"    #size of letters
            size_hint: .1 , .1 #size settings first x axis and after y axis
            pos: 450 , 300 #position in the screen first x axis and after y axis
            on_release:
                #after releasing the button we give it to do something inside the function,it can be whatever we want
                app.root.current = "vigener"
        Button:
            text: "md5 hashing"  #text on the button
            id: md5_button  #an id to call it in a function
            font_size: "20sp"    #size of letters
            size_hint: .1 , .1 #size settings first x axis and after y axis
            pos: 450 , 200 #position in the screen first x axis and after y axis
            on_release:
                #after releasing the button we give it to do something inside the function,it can be whatever we want
                app.root.current = "md5"
<Caesar>:
    canvas.before:
        Rectangle:
            pos: self.pos  #default posistion is in the midle
            size: self.size  #screen size, the screen is the parent
            source: "cruptography/images/g10.png" #source of the photo for the background
    FloatLayout:
        orientation: 'vertical' 
        Label:
            text: "caesar results and warnings! No numbers included or space or special characters aren getting encrypted." #text for user
            id: label_ceasar  #an id to call it in a function
            size_hint: .6 , .1 #size settings first x axis and after y axis
            pos: 400 , 550 #position in the screen first x axis and after y axis
            padding: 10, 10
        TextInput:
            id: textinput_ceasar  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .5 , .04 #size settings first x axis and after y axis
            pos: 500 , 850 #position in the screen first x axis and after y axis
            multiline: False
        Label:
            text: "Give the key. It must be greater than 0 of course." #text for user
            id: label_ceasar_key  #an id to call it in a function
            size_hint: .6 , .1 #size settings first x axis and after y axis
            pos: 400 , 750 #position in the screen first x axis and after y axis
        TextInput:
            id: textinput_ceasar_key  #an id to call it in a function
            multiline: False #multiline not allowed
            font_size: "20sp" #size of letters
            size_hint: .5 , .05 #size settings first x axis and after y axis
            pos: 500 , 700 #position in the screen first x axis and after y axis
            multiline: False
        Button:
            text: "encode data" #text on the button
            id: encode_ceasar_button  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1500 , 750 #position in the screen first x axis and after y axis
            on_release:
                root.encode_caesar()
        Button:
            text: "decode data" #text on the button
            id: decode_ceasar_button  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1500 , 700 #position in the screen first x axis and after y axis
            on_release:
                root.decode_caesar_with_given_key()
        Button:
            text: "frequency analysis" #text on the button
            id: show_frequency_analysis_in_unencrypted_text_ceasar_button  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .15 , .05 #size settings first x axis and after y axis
            pos: 1500 , 650 #position in the screen first x axis and after y axis
            on_release:
                root.show_frequency_caesar()
        Button:
            text: "back" #text on the button
            id: button_back_from_caesar  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1500 , 600 #position in the screen first x axis and after y axis
            on_release:
                app.root.current = "main_app"
<Affine>:
    canvas.before:
        Rectangle:
            pos: self.pos #default posistion is in the midle
            size: self.size #screen size, the screen is the parent
            source: "cruptography/images/g11.jpg" #source of the photo for the background
    FloatLayout:
        orientation: 'vertical' 
        Label:
            text: "affine results and warnings!" #text for user
            id: label_Affine  #an id to call it in a function
            size_hint: .5 , .1 #size settings first x axis and after y axis
            pos: 0 , 600 #position in the screen first x axis and after y axis
            padding: 10, 10
        TextInput:
            id: textinput_affine  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .4 , .05 #size settings first x axis and after y axis
            pos: 0 , 750 #position in the screen first x axis and after y axis
            multiline: False
        Label:
            text: "Give the 2 keys. they must be greater than 0 of course." #text for user
            id: label_affine_key1  #an id to call it in a function
            size_hint: .6 , .1 #size settings first x axis and after y axis
            pos: 400 , 600 #position in the screen first x axis and after y axis
        Label:
            text: "key 1" #text for user
            id: label_affine_key_1  #an id to call it in a function
            size_hint: .4 , .1 #size settings first x axis and after y axis
            pos: 500 , 650 #position in the screen first x axis and after y axis
        TextInput:
            id: textinput_affine_key1  #an id to call it in a function
            multiline: False #multiline not allowed
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 800 , 750 #position in the screen first x axis and after y axis
            multiline: False
        Label:
            text: "Key 2" #text for user
            id: label_affine_key_2  #an id to call it in a function
            size_hint: .4 , .1 #size settings first x axis and after y axis
            pos: 750 , 650 #position in the screen first x axis and after y axis
        TextInput:
            id: textinput_affine_key2  #an id to call it in a function
            multiline: False #multiline not allowed
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1025 , 750 #position in the screen first x axis and after y axis
            multiline: False
        Button:
            text: "encode data" #text on the button
            id: encode_affine_button  #an id to call it in a function
            font_size: "20sp"  #size of letters
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1225 , 750 #position in the screen first x axis and after y axis
            on_release:
                root.encode_affine()
        Button:
            text: "decode data" #text on the button
            id: encode_affine_button  #an id to call it in a function
            font_size: "20sp"  #size of letters
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1425 , 750 #position in the screen first x axis and after y axis
            on_release:
                root.affine_decode()
        Button:
            text: "frequency analysis" #text on the button
            id: show_frequency_analysis_in_unencrypted_text_affine_button  #an id to call it in a function
            font_size: "20sp"  #size of letters
            size_hint: .125 , .05 #size settings first x axis and after y axis
            pos: 1625 , 750 #position in the screen first x axis and after y axis
            on_release:
                root.show_frequency_affine()
        Button:
            text: "back" #text on the button
            id: button_back_from_affine  #an id to call it in a function
            font_size: "20sp"  #size of letters
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1625 , 700 #position in the screen first x axis and after y axis
            on_release:
                app.root.current = "main_app"
<Vigener>:
    canvas.before:
        Rectangle:
            pos: self.pos #default posistion is in the midle
            size: self.size #screen size, the screen is the parent
            source: "cruptography/images/g14.jpg" #source of the photo for the background
    FloatLayout:
        orientation: 'vertical' 
        Label:
            text: 'vigener cypher warnings and results' #text for user
            id: label_vigener  #an id to call it in a function
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 300 , 600 #position in the screen first x axis and after y axis  
            padding: 10, 10
        TextInput:
            id: textinput_vigener  #an id to call it in a function
            font_size: "20sp"  #size of letters
            size_hint: .4 , .05 #size settings first x axis and after y axis
            pos: 0 , 750 #position in the screen first x axis and after y axis
            multiline: False
        Label:
            text: "Give the key word." #text for user
            id: label_vigener_key  #an id to call it in a function
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1000 , 700 #position in the screen first x axis and after y axis
        TextInput:
            id: textinput_vigener_key  #an id to call it in a function
            multiline: False #multiline is not allow
            font_size: "20sp" #size of letters
            size_hint: .4 , .05 #size settings first x axis and after y axis
            pos: 800 , 750 #position in the screen first x axis and after y axis
            multiline: False
        Button:
            text: "encode data" #text on the button
            id: encode_vigener_button  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1000 , 650 #position in the screen first x axis and after y axis
            on_release:
                root.encode_vigener()
        Button:
            text: "decode data" #text on the button
            id: decode_vigener_button  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1200 , 650 #position in the screen first x axis and after y axis
            on_release:
                root.decode_vigener()
        Button:
            text: "frequency analysis" #text on the button
            id: show_frequency_analysis_in_unencrypted_text_vigener_button  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .125 , .05 #size settings first x axis and after y axis
            pos: 1400 , 650 #position in the screen first x axis and after y axis
            on_release:
                root.show_frequency_vigener()
        Button:
            text: "back" #text on the button
            id: button_back_from_vigener  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1650 , 650 #position in the screen first x axis and after y axis
            on_release:
                app.root.current = "main_app"
<md5>:
    canvas.before:
        Rectangle:
            pos: self.pos #default posistion is in the midle
            size: self.size #screen size, the screen is the parent
            source: "cruptography/images/g15.jpg" #source of the photo for the background
    FloatLayout:
        orientation: 'vertical'
        Label:
            text: 'md5 results' #text for user
            id: label_md5  #an id to call it in a function
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 300 , 600 #position in the screen first x axis and after y axis  
            color: 'grey' #putting the color black
            markup: True #markup is for the letters to change colour
            padding: 10, 10
        TextInput:
            id: textinput_md5  #an id to call it in a function
            font_size: "20sp"  #size of letters
            size_hint: .4 , .05 #size settings first x axis and after y axis
            pos: 0 , 750 #position in the screen first x axis and after y axis
            multiline: False
        Button:
            text: "hash data" #text on the button
            id: hash_md5_button  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1000 , 650 #position in the screen first x axis and after y axis
            on_release:
                root.md5_hashing()
        Button:
            text: "compare hash from file" #text on the button
            id: hash_md5_file_compare_button  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .15 , .05 #size settings first x axis and after y axis
            pos: 1000 , 650 #position in the screen first x axis and after y axis
            on_release:
                root.compare_file()
        Button:
            text: "hash from file and store in new" #text on the button
            id: hash_md5_file_hash_button  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .2 , .05 #size settings first x axis and after y axis
            pos: 600 , 650 #position in the screen first x axis and after y axis
            on_release:
                root.hash_file()
        Button:
            text: "back" #text on the button
            id: button_back_from_md5  #an id to call it in a function
            font_size: "20sp" #size of letters
            size_hint: .1 , .05 #size settings first x axis and after y axis
            pos: 1300 , 650 #position in the screen first x axis and after y axis
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
    elif number>60 and number%120!=0:
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
    elif number>60 and number%120==0:
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
        file=open(file_name, 'rb')
        # read contents of the file
        line = file.readline().strip()
        data=file.readline().strip()
        md5_returned+= hashlib.md5(data.encode()).hexdigest()+"\n"
        while line:
            line=file.readline().strip()
            data = file.readline().strip()
            # pipe contents of the file through
            md5_returned+= hashlib.md5(data.encode()).hexdigest()+"\n"
        file.close()
        # Finally compare original MD5 with freshly calculated
        if original_hash == md5_returned:
            label.text="MD5 verification succeed."
        else:
            label.text="MD5 verification failed."
    def hash_file(self):
        #data to hash from file
        file_name = askopenfilename()
        #storing the memory address
        label=self.ids.label_md5
        md5_returned=""
        file=open(file_name, 'r')
        line = file.readline().strip()
        data=file.readline().strip()
        md5_returned+= hashlib.md5(data.encode()).hexdigest()+"\n"
        while line:
            data = file.readline().strip() 
            line=file.readline().strip()
            md5_returned+= hashlib.md5(data.encode()).hexdigest()+"\n"
        file.close()
        store_to_a_new_file=askdirectory()
        store_to_a_new_file+="md5_results.txt"
        with open(store_to_a_new_file,"w") as store:
            data_stored=store.write(md5_returned)
        store.close()
    def compare_files(sself):
        pass
#defining class about the screen managment
class MyScreenManager(ScreenManager):
    pass
#class that builds the app
class cryptography(App):
    #function that builds the app 
    def build(self):
        Window.maximize()
        return MyScreenManager()
#we run the app
if __name__=="__main__":
    cryptography().run()
#python version 3.11.2 debian version (mostly is already installed but if you want to install it, open the terminal and type sudo apt install python)
#installation on windows 11
#go to python.org site and dowwnload the version you like
#ether give admin privilage and check the create variables box or do it manually (it's up to you)
#open (Edit the system environment variables)
#go to Environmet variables
#double click on Path
#check if python path is there 
#else press button "New"
#paste path that you coppied before 
#press the button named New
#paste the previous path and add this (\Scripts)
#press the ok button 
#installation for matplotlib
#open windows terminal and type pip install matplotlib
#installation for kivy
#pip install kivy
#installation for numpy
#pip install numpy
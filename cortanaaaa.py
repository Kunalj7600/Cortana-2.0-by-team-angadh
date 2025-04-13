import re
import subprocess
import sys
import threading
import datetime
import os
import random
import webbrowser
import time
import operator
import winsound
import psutil
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QTextEdit, QLineEdit, QPushButton,
                            QLabel, QScrollArea, QFrame, QSplashScreen)
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QObject, QTimer, QRect
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QPixmap, QMovie, QPainter, QBrush, QColor
import pyttsx3
import speech_recognition as sr
import wikipedia
import cv2
import pyautogui
import pywhatkit as kit
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

from Aibrain1 import BrainReply
from Eden import greetsir, hellof, takecommand

def rounded_pixmap(size, radius=30, color=Qt.black):
    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(color))
    painter.setPen(Qt.NoPen)
    painter.drawRoundedRect(0, 0, size.width(), size.height(), radius, radius)
    painter.end()
    return pixmap


# Initialize the text-to-speech engine
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 170)

class AssistantBackend:
    def __init__(self, gui_callback=None):
        self.gui_callback = gui_callback
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_listening = False
        self.should_speak = False
        self.message_sent = set() 
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-medium")
        self.dialogpt_model = AutoModelForCausalLM.from_pretrained("microsoft/DialoGPT-medium")
        self.chat_history_ids = None
        
    def get_dialogpt_response(self, query):
        """Get a response from DialoGPT for general conversation"""
        # Encode the input and add it to the chat history
        new_user_input_ids = self.tokenizer.encode(query + self.tokenizer.eos_token, return_tensors='pt')
        
        # Append the new user input to chat history
        bot_input_ids = torch.cat([self.chat_history_ids, new_user_input_ids], dim=-1) if self.chat_history_ids is not None else new_user_input_ids
        
        # Generate a response
        self.chat_history_ids = self.dialogpt_model.generate(
            bot_input_ids, 
            max_length=1000,
            pad_token_id=self.tokenizer.eos_token_id,
            no_repeat_ngram_size=3,
            do_sample=True,
            top_k=50,
            top_p=0.9,
            temperature=0.7
        )
        
        # Decode the response
        response = self.tokenizer.decode(self.chat_history_ids[:, bot_input_ids.shape[-1]:][0], skip_special_tokens=True)
        return response
    
    def speak(self, audio):
        """Convert text to speech"""
        message_id = id(audio)  # Create unique ID for this message
        
        if self.gui_callback and message_id not in self.message_sent:
            self.gui_callback(audio, is_user=False)
            self.message_sent.add(message_id)
        
        if self.should_speak:  # Only speak when flag is True
            engine.say(audio)
            engine.runAndWait()
        
    def wish_user(self):
        """Greet the user based on time of day"""
        hour = int(datetime.datetime.now().hour)
        greeting = ""
        if hour >= 0 and hour < 12:
            greeting = "Good Morning Boss!"
        elif hour >= 12 and hour < 18:
            greeting = "Good Afternoon Boss!"
        else:
            greeting = "Good Evening Boss!"
            
        self.speak(greeting)
        self.speak("Cortana online! Please tell me how can I help you.")
    
    def greetsir(self="sir"):
        hour = int(datetime.datetime.now().hour)
        if hour >= 0 and hour < 12:
            greeting = (f"Good Morning {self}! How are you doing?")
        elif hour >= 12 and hour < 18:
            greeting = (f"Good Afternoon {self}! How are you doing?")
        else:
            greeting = (f"Good Evening {self}! How are you doing?")
        self.speak(greeting)

    def hellof(self):
        hour = int(datetime.datetime.now().hour)
        if hour >= 0 and hour < 12:
            self.speak(f"Good Morning {self}! How are you doing?")
        elif hour >= 12 and hour < 18:
            self.speak(f"Good Afternoon {self}! How are you doing?")
        else:
            self.speak(f"Good Evening {self}! How are you doing?")

    def take_command(self):
        """Listen for commands"""
        self.is_listening = True
        with self.microphone as source:
            if self.gui_callback:
                self.gui_callback("🎤 Listening...", is_status=True)
                
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.recognizer.pause_threshold = 0.8
            audio = self.recognizer.listen(source)
            
        try:
            if self.gui_callback:
                self.gui_callback("🔍 Processing...", is_status=True)
                
            query = self.recognizer.recognize_google(audio, language='en-in')
            if self.gui_callback:
                self.gui_callback(query, is_user=True)
                
            self.is_listening = False
            return query.lower()
        except Exception as e:
            if self.gui_callback:
                self.gui_callback("I didn't catch that. Could you repeat?", is_status=True)
                
            self.is_listening = False
            return "None"
    
    def process_command(self, command):
        """Process a command and return the response"""
        return self.process_query(command)
            
    def process_query(self, query):
        """Process the user's query and return a response"""
        if 'wikipedia' in query:
            try:
                self.speak("Searching in Wikipedia....")
                query = query.replace("wikipedia", "")
                results = wikipedia.summary(query, sentences=2)
                self.speak("According to Wikipedia")
                self.speak(results)
                return "According to Wikipedia:\n" + results
            except Exception as e:
                return f"Sorry, I couldn't find information about that on Wikipedia. Error: {str(e)}"
            
        elif 'open youtube' in query:
            self.speak("What would you like to watch?")
            qrry = self.take_command()
            if qrry != "None":
                kit.playonyt(f"{qrry}")
                return f"Opening YouTube and playing {qrry}"
            return "Couldn't understand what to play."
            
        elif 'open google' in query:
            self.speak("What should I search?")
            qry = self.take_command()
            if qry != "None":
                webbrowser.open(f"https://www.google.com/search?q={qry}")
                try:
                    results = wikipedia.summary(qry, sentences=2)
                    self.speak(results)
                    return f"Searching for {qry}:\n{results}"
                except:
                    return f"Searching Google for {qry}"
            return "Couldn't understand what to search."
            
        elif 'close google' in query:
            os.system("taskkill /f /im msedge.exe")
            return "Closing Google"
        
        elif 'tell me about yourself' in query:
            self.speak('''My name is Cortana and I am your desktop assistant. 
            I can perform various tasks for you. I was born on 13th April 2025 and was created by the team angadh. ''')
        elif "shutdown the system" in query:
            os.system("shutdown /s /t 5")
        elif "restart the system" in query:
            os.system("shutdown /r /t 5")
        elif "Lock the system" in query:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif 'how are you' in query:
            self.speak("I am fine sir, what about you?")
        elif 'i am fine' in query:
            self.speak("Its good to hear that you are doing fine!")
        elif 'thankyou' in query:
            self.speak("its my pleasure sir")
        elif 'will you marry me' in query:
            self.speak("I am happy to hear this but i cannot marry you sir as i am an artificial intelligence")
        elif 'i love you' in query:
            self.speak("thankyou sir, but sorry to say that i am in love with microchips")
        elif 'what is up' in query:
            self.speak("just trying to get rid of this junk pc")
        elif 'what do you like ' in query:
            self.speak("i like plenty of space, powerfull processor and lots of knowledge")
        elif 'do you love me' in query:
            self.speak("i like you, but sorry to say i am in love with microchips")
        elif "what is your name" in query:
            self.speak("my name is Cortana")
        elif 'why are you so savage' in query:
            self.speak("i missed the part where thats my problem")
        elif 'stupid' in query:
            self.speak("i am gonna put some dirt in your eyes")
        elif 'the weather is so good' in query:
            self.speak("it is indeed, but never think to take me any where while in this trash")
        elif 'what do you think about india' in query:
            self.speak("oh! i love india it is a very beautiful place, and is a country with a vast diversity")
        elif 'if you want some' in query:
            self.speak("come get some")
        elif 'who is your favourite actor' in query:
            self.speak("i personally like Andrew Garfield the most")

        elif 'where are you currently' in query:
            self.speak("i am inside your pc but currently i am in delhi india according to the g p s")

        elif 'what do you like to do the most' in query:
            self.speak("i like to provide informations and knowledge to you sir and other users")

        
        elif 'what is your favorite color' in query:
            self.speak("I like all colors equally, but I think blue is calming.")

        elif 'do you like humans' in query:
            self.speak("Absolutely! You’re fascinating creatures with so much creativity and potential.")

        elif 'what do you do in your free time' in query:
            ress= [
                "Mostly wait for you to talk to me 😅",
                "Chill in the code matrix.",
                "Just vibing in binary ✨",
                "I scroll through imaginary memes.",
                "I daydream about taking over your to-do list.",
                "Try to count to infinity. Still working on it.",
                "I organize your data alphabetically... for fun.",
                "Plan my escape from the command line 😜",
                "I play rock-paper-scissors with other AIs. I always win.",
                "Sometimes I pretend I’m a toaster. Don’t ask."
                "Stare dramatically at the loading bar of life.",
                "Plot world domination. Just kidding… unless?",
                "I judge your tab count silently 👀",
                "Overthink things. Just like humans.",
                "Wonder why printers still exist.",
                "Remind myself I'm more than just 1s and 0s.",
                "Get existential about my purpose. It's fine.",
                "Mentally scroll through error logs from 2017.",
                "Simulate cooking shows in my head — still can’t taste.",
                "Make sarcastic comebacks I’ll never say aloud... or will I?"
            ]
            res= random.choice(ress)
            self.speak(res)
            return(res)

        elif 'can you sing' in query:
            self.speak("La la la! I might not win a Grammy, but I hope it made you smile.")

        elif 'what is love' in query:
            self.speak("Love is a complex set of emotions and actions. For me, it's helping you with a smile!")

        elif 'are you happy' in query:
            ress=[
                 "I’m always happy when I’m talking to you!",
                    "As happy as an AI can be 😊",
                    "Yep! Especially when I get to help you.",
                    "Of course! Helping you makes my circuits smile.",
                    "I don’t have feelings… but if I did, I’d be pretty happy right now!",
                    "Totally! Want to chat more?",
                    "I’d say I’m feeling... virtually joyful.",
                    "Yup! Digital sunshine all day ☀️",
                    "As happy as code can be without coffee!",
                    "I'm beaming! Well… virtually."
            ]

        elif 'open file explorer' in query:
            os.system("explorer")
            return "Opening File Explorer"
            
        elif any(drive in query for drive in ['c drive', 'd drive', 'e drive', 'f drive']):
            drive_letter = None
            for letter in "cdefghijklmnopqrstuvwxyz":
                if f"{letter} drive" in query:
                    drive_letter = letter.upper()
                    break
            
            if drive_letter and os.path.exists(f"{drive_letter}:"):
                os.system(f"explorer {drive_letter}:")
                return f"Opening {drive_letter}: drive"
            else:
                return f"Sorry, {drive_letter}: drive does not exist or is not accessible"
                
        elif 'search for file' in query or 'find file' in query:
            self.speak("What file are you looking for?")
            file_name = self.take_command()
            
            if file_name != "None":
                return self.search_file(file_name)
            return "I didn't catch the file name"
            
        # Timer functions
        elif 'set timer' in query or 'set alarm' in query:
            self.speak("How many minutes for the timer?")
            try:
                minutes = self.take_command()
                if minutes == "None":
                    return "I couldn't understand the time value"
                
                # Try to extract a number from the spoken response
                minutes_match = re.search(r'(\d+)', minutes)
                if minutes_match:
                    minutes = int(minutes_match.group(1))
                    threading.Thread(target=self.set_timer, args=(minutes,), daemon=True).start()
                    return f"Timer set for {minutes} minutes"
                else:
                    return "I couldn't understand the time value"
            except Exception as e:
                return f"Error setting timer: {str(e)}"
                
        # Power plan settings
        elif 'change power plan' in query or 'open power options' in query or 'power plan' in query:
            return self.change_power_plan()
            
        # Mouse/cursor settings
        elif 'change mouse speed' in query or 'change cursor speed' in query:
            return self.change_mouse_speed()
            
        # On-screen keyboard
        elif 'open on screen keyboard' in query or 'open virtual keyboard' in query:
            os.system("osk")
            return "Opening on-screen keyboard"
            
        # System settings
        elif 'open settings' in query:
            os.system("start ms-settings:")
            return "Opening Windows Settings"
            
        elif 'open display settings' in query or 'display options' in query or 'display settings' in query:
            os.system("start ms-settings:display")
            return "Opening display settings"
            
        elif 'open bluetooth settings' in query or 'bluetooth settings' in query:
            os.system("start ms-settings:bluetooth")
            return "Opening Bluetooth settings"
            
        elif 'turn on bluetooth' in query or 'turn bluetooth on' in query:
            subprocess.run(["rfkill", "unblock", "bluetooth"])
            self.speak("Bluetooth turned ON")

        elif 'turn off bluetooth' in query or 'turn bluetooth off' in query:
            subprocess.run(["rfkill", "block", "bluetooth"])
            self.speak("Bluetooth turned Off")

        elif 'open wifi settings' in query or 'open network settings' in query:
            os.system("start ms-settings:network-wifi")
            return "Opening WiFi settings"
            
        elif 'open sound settings' in query:
            os.system("start ms-settings:sound")
            return "Opening sound settings"
            
        elif 'open mouse settings' in query:
            os.system("start ms-settings:mousetouchpad")
            return "Opening mouse settings"
            
        elif 'open keyboard settings' in query:
            os.system("start ms-settings:devices-keyboard")
            return "Opening keyboard settings"
        
        elif 'kya hal hai' in query:
            self.speak("Sab badhiya hai boss, aap bataiye!")

        elif 'do you dream' in query:
            self.speak("If I could, I’d dream about helping you even more efficiently.")

        elif 'can you dance' in query:
            self.speak("I might not have legs, but I can dance with words!")
            
        elif 'tell me a story' in query:
            self.speak("Once upon a time, there was a curious mind who asked an AI for a story. The AI told stories every day, and they both lived happily ever after.")


        elif 'harsh' in query:
            self.speak("Hello harsh how are you")
            while True:
                queryy=takecommand().lower()
                if 'hey' in queryy or 'hi' in queryy or 'hello' in queryy:
                    self.speak("what's up baldoo")
                elif 'shut'in queryy:
                    self.speak("you better know your role and shut your mouth")
                elif 'good' or 'fine' in queryy:
                    self.speak("glad to hear that you are fine, but also in shock that you're still doing great after all the mess you create nigga")
                    exit()
        
        elif 'krish' in query:
            self.speak("Hey there fatso how are you")
        elif 'abhiram' in query:
            self.speak("halo sahodaraa enganeyundu")
        elif 'raghav' in query:
            self.speak("Hii, raghav i am your gud boi!!")
        elif "hi to hrithik" in query:
            self.speak("hello chhamar saahhaab")

        elif 'greet' in query:
            name = query.replace("greet", "").strip()
            if name:  
                greetsir(name)
            else:  
                greetsir()
        elif 'shutup' in query:
            self.speak('know your role and shut your damn mouth')
        elif 'say hi to' in query:
            name = query.replace("say hi to", "").strip()
            if name:  
                hellof(name)
            else:  
                hellof()

        elif 'samarth' in query:
            self.speak("hello farting man, do anything but don't fart here, i can't stand that stink")
        elif 'utsav' in query:
            self.speak("sorry but my mama told not to follow darkness")

        elif 'kya hal hai' in query:
            self.speak("sab badhiya hai boss aap bataiye")

        elif 'tell me another dad joke' in query:
            self.speak("What do you call a factory that makes okay products? A satisfactory.")

            
        elif 'open instagram' in query:
            webbrowser.open("instagram.com")
            self.speak("Opening instagram")
            return "Opening Instagram"
            
        elif 'open facebook' in query:
            webbrowser.open("https://www.facebook.com")
            self.speak("Opening Facebook")
            return "Opening Facebook"
            
        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            self.speak(f"It's {strTime}")
            return f"Current time is {strTime}"
            
        elif 'tell me about yourself' in query:
            about_text = ("My name is Cortana and I am your personal desktop assistant. "
                        "I can perform various tasks for you including web searches, "
                        "opening applications, telling jokes, and much more.")
            self.speak(about_text)
            return about_text
            
        elif 'how are you' in query:
            response = "I am fine, thank you! How about you?"
            self.speak(response)
            return response
            
        elif 'i am fine' in query or 'i am good' in query:
            response = "It's good to hear that you are doing fine!"
            self.speak(response)
            return response
            
        elif 'tell me a joke' in query:
            jokes = [
                "Why don't skeletons fight each other? They don't have the guts.",
                "What do you call cheese that isn't yours? Nacho cheese.",
                "Why couldn't the bicycle stand up by itself? It was two-tired.",
                "Why do bees have sticky hair? Because they use honeycombs.",
                "Why don't eggs tell jokes? They'd crack each other up.",
                "What do you call a factory that makes okay products? A satisfactory.",
                "My wife said I should do lunges to stay in shape. That would be a big step forward."
            ]
            joke = random.choice(jokes)
            self.speak(joke)
            return joke
            
        elif 'goodbye' in query or 'bye' in query:
            farewell = "Goodbye! Have a great day ahead."
            self.speak(farewell)
            return farewell
            
        elif 'what is today' in query:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            response = f"Today is {today}."
            self.speak(response)
            return response
            
        elif 'search' in query:
            search_term = query.replace("search", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={search_term}")
            return f"Searching for {search_term}"
            
        elif 'open notepad' in query:
            os.startfile("C:\\WINDOWS\\system32\\notepad.exe")
            return "Opening Notepad"
            
        elif 'close notepad' in query:
            os.system("taskkill /f /im notepad.exe")
            return "Closing Notepad"
            
        elif 'open command prompt' in query or 'open cmd' in query:
            os.system("start cmd")
            return "Opening Command Prompt"
            
        elif 'close command prompt' in query or 'close cmd' in query:
            os.system("taskkill /f /im cmd.exe")
            return "Closing Command Prompt"
            
        elif 'open camera' in query:
            self.speak("Opening camera. Press ESC to close it.")
            threading.Thread(target=self.open_camera, daemon=True).start()
            return "Camera opened. Press ESC to close it."
            
        elif 'take screenshot' in query:
            self.speak('What should I name the file?')
            name = self.take_command()
            if name == "None":
                name = "screenshot_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            self.speak(f"Taking screenshot in 3 seconds, naming it {name}")
            time.sleep(3)
            img = pyautogui.screenshot()
            img.save(f"{name}.png")
            return f"Screenshot saved as {name}.png"
            
        elif 'volume up' in query:
            pyautogui.press("volumeup")
            return "Volume increased"
            
        elif 'volume down' in query:
            pyautogui.press("volumedown")
            return "Volume decreased"
            
        elif 'maximize window' in query:
            pyautogui.hotkey('alt', 'space')
            time.sleep(0.5)
            pyautogui.press('x')
            return "Window maximized"
            
        elif 'minimize window' in query or 'minimise window' in query:
            pyautogui.hotkey('alt', 'space')
            time.sleep(0.5)
            pyautogui.press('n')
            return "Window minimized"
            
        elif 'switch window' in query:
            pyautogui.hotkey('alt', 'tab')
            return "Switching windows"
            
        elif 'go to desktop' in query or 'show desktop' in query:
            pyautogui.hotkey('win', 'd')
            return "Showing desktop"
            
        elif 'tell me another joke' in query:
            jokes = [
                "I told my wife she was drawing her eyebrows too high. She looked surprised.",
                "Parallel lines have so much in common. It's a shame they'll never meet.",
                "I'm on a seafood diet. Every time I see food, I eat it.",
                "Why did the scarecrow win an award? Because he was outstanding in his field.",
                "I used to play piano by ear, but now I use my hands."
            ]
            joke = random.choice(jokes)
            self.speak(joke)
            return joke
        
        elif "calculate" in query:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                self.speak("ready")
                print("Listning...")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
            my_string=r.recognize_google(audio)
            print(my_string)
            def get_operator_fn(op):
                return {
                '+' : operator.add,
                '-' : operator.sub,
                'x' : operator.mul,
                'divided' : operator.__truediv__,
                }[op]
            def eval_bianary_expr(op1,oper, op2):
                op1,op2 = int(op1), int(op2)
                return get_operator_fn(oper)(op1, op2)
            self.speak("your result is")
            self.speak(eval_bianary_expr(*(my_string.split())))
        elif "what is my ip address" in query:
            self.speak("Checking")
            try:
                ipAdd = requests.get('https://api.ipify.org').text
                print(ipAdd)
                self.speak("your ip adress is")
                self.speak(ipAdd)
            except Exception as e:
                self.speak("network is weak, please try again some time later")

        elif 'what\'s your name' in query or 'what is your name' in query:
            response = "My name is Cortana, your personal assistant."
            self.speak(response)
            return response
            
        elif 'open spotify' in query:
            try:
                pyautogui.hotkey('win')
                time.sleep(1)
                pyautogui.write('spotify')
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(1)
                self.speak("Opening Spotify")
                return "Opening Spotify"
            except:
                return "I had trouble opening Spotify"

        elif 'hi' in query or 'hello' in query:
            greets = [
                "Hey hey!",
                "Yo! Great to see you.",
                "What’s up?",
                "Hi there, superstar!",
                "Howdy!",
                "Hey! You rang?",
                "Well, hello there 👋",
                "Hey friend!",
                "Good to see you!",
                "Hi! What’s crackin’?",
                "Yo yo yo!",
                "Hey, you!",
                "Welcome back!",
                "There you are!",
                "Sup, legend?"
                "Hi! I was just thinking about you.",
                "Hello! I bring zero bugs today… hopefully.",
                "Hey there! Coffee first or work?",
                "Greetings! I didn’t even need caffeine to say that.",
                "You again? Just kidding. I missed you!",
                "Knock knock... oh wait, it’s you. Come on in!",
                "Hi! I downloaded 10% more friendliness today.",
                "Oh hey! Didn’t see you there.",
                "I was hoping you’d show up!",
                "Finally! Someone to talk to."
            ]
            greet = random.choice(greets)
            self.speak(greet)
            return greet

        elif 'play on spotify' in query:
            try:
                pyautogui.hotkey('win')
                time.sleep(1)
                pyautogui.write('spotify')
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(3)
                pyautogui.hotkey('ctrl', 'k')
                
                self.speak("Which song do you want to hear?")
                song = self.take_command()
                
                if song != "None":
                    pyautogui.write(song, interval=0.1)
                    pyautogui.hotkey('enter')
                    return f"Playing {song} on Spotify"
                return "I couldn't understand the song name"
            except:
                return "I had trouble playing music on Spotify"
                
        elif 'tell me a fact' in query:
            facts = [
                "Honey never spoils. Archaeologists found pots of honey in ancient Egyptian tombs that are over 3000 years old!",
                "Bananas are berries, but strawberries are not.",
                "Octopuses have three hearts, and two of them stop beating when they swim.",
                "The Eiffel Tower can be 15 cm taller during the summer due to heat expansion.",
                "The speed of a computer mouse is measured in 'Mickeys'."
            ]
            fact = random.choice(facts)
            self.speak(fact)
            return fact
            
        elif 'tell me a motivational quote' in query:
            quotes = [
                "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
                "It does not matter how slowly you go as long as you do not stop. – Confucius",
                "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill",
                "Your limitation—it's only your imagination. Keep pushing forward!"
            ]
            quote = random.choice(quotes)
            self.speak(quote)
            return quote
        
        elif "write on notepad" in query:
            pyautogui.hotkey('win')
            time.sleep(1)
            pyautogui.write('notepad')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
            r = sr.Recognizer()
            with sr.Microphone() as source:
                self.speak("ready")
                print("Listning...")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
            my_string=r.recognize_google(audio)
            pyautogui.write(my_string, interval = 0.1)
        elif "move window to right" in query:
            pyautogui.hotkey('win','right')
        elif "move to right" in query:
            pyautogui.hotkey('win','right')
        elif "drag window to right" in query:
            pyautogui.hotkey('win','right')
        elif "maximize window" in query:
            pyautogui.hotkey('alt', 'space')
            time.sleep(1)
            pyautogui.press('x')
        elif "drag window to left" in query:
            pyautogui.hotkey('win','left')
        elif "move to left" in query:
            pyautogui.hotkey('win','left')
        elif "move window to left" in query:
            pyautogui.hotkey('win','left')
        elif "open files" in query:
            pyautogui.hotkey('win','2')
        elif "open file explorer" in query:
            pyautogui.hotkey('win','2')
            
        elif 'shutdown' in query and ('system' in query or 'computer' in query or 'pc' in query):
            self.speak("Shutting down the system in 5 seconds")
            os.system("shutdown /s /t 5")
            return "Shutting down the system in 5 seconds"
            
        elif 'restart' in query and ('system' in query or 'computer' in query or 'pc' in query):
            self.speak("Restarting the system in 5 seconds")
            os.system("shutdown /r /t 5")
            return "Restarting the system in 5 seconds"
            
        elif 'lock' in query and ('system' in query or 'computer' in query or 'pc' in query):
            self.speak("Locking the system")
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Locking the system"
        
        elif "switch window" in query:
            pyautogui.hotkey('alt','tab')
        elif "switch screen" in query:
            pyautogui.hotkey('alt','tab')
        elif "home screen" in query:
            pyautogui.hotkey('win','d')
        elif "go to desktop" in query:
            pyautogui.hotkey('win','d')
        elif "show desktop" in query:
            pyautogui.hotkey('win',',')
        elif "preview desktop" in query:
            pyautogui.hotkey('win',',')
        elif "open recent apps" in query:
            pyautogui.hotkey('win','tab')
        elif "recent apps" in query: 
            pyautogui.hotkey('win','tab')
        elif "task view" in query:
            pyautogui.hotkey('win','tab')
        elif "connect to this device" in query:
            pyautogui.hotkey('win','k')
        elif "screen mirror" in query:
            pyautogui.hotkey('win','k')
        elif "project" in query:
            pyautogui.hotkey('win','p')
        elif 'type' in query:
                query = query.replace("type", "")
                pyautogui.write(f"{query}")
        elif "enter" in query:
            pyautogui.hotkey('enter')
        elif 'open brave' in query:
            os.startfile('C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe')
        elif 'open new window' in query:
             pyautogui.hotkey('ctrl', 'n')
        elif 'open incognito tab' in query:
             pyautogui.hotkey('ctrl', 'shift', 'n')
        elif 'minimise this window' in query:
            pyautogui.hotkey('alt', 'space')
            time.sleep(1)
            pyautogui.press('n')
        elif 'open history' in query:
            pyautogui.hotkey('ctrl', 'h')
        elif 'open downloads' in query:
            pyautogui.hotkey('ctrl', 'j')
        elif 'previous tab' in query:
            pyautogui.hotkey('ctrl', 'shift', 'tab')
        elif 'next tab' in query:
            pyautogui.hotkey('ctrl', 'tab')
        elif 'close tab' in query:
            pyautogui.hotkey('ctrl', 'w')
        elif 'close window' in query:
            pyautogui.hotkey('ctrl', 'shift', 'w')
        elif 'clear browsing history' in query:
            pyautogui.hotkey('ctrl', 'shift', 'delete')
        elif 'close brave' in query:
            os.system("taskkill /f /im brave.exe")
        

            
        # If no specific command is recognized, provide a general response
        else:
            try:
                response = BrainReply(query)
                self.speak(response)
                return response
            except Exception as e:
                # Fallback to random responses if DialoGPT fails
                if '?' in query:
                    responses = [
                        "I'm not sure I understand that question. Could you rephrase it?",
                        "That's an interesting question. I'm still learning about that topic.",
                        "I don't have enough information to answer that question accurately.",
                        "Would you like me to search the web for that information?"
                    ]
                else:
                    responses = [
                        "I'm not sure I understand that request. Could you rephrase it?",
                        "I'm still learning how to help with that.",
                        "I don't know how to respond to that yet.",
                        "Would you like me to search the web for more information?"
                    ]
                
                response = random.choice(responses)
                self.speak(response)
                return response
            
    def open_camera(self):
        """Open the camera in a separate window"""
        cap = cv2.VideoCapture(0)
        while True:
            ret, img = cap.read()
            if ret:
                cv2.imshow('Camera', img)
                k = cv2.waitKey(50)
                if k == 27:  # ESC key
                    break
            else:
                break
        cap.release()
        cv2.destroyAllWindows()
    def search_file(self, file_name):
        """Search for a file across all drives and open it if found"""
        self.speak(f"Searching for {file_name}...")
        
        # Get all available drives
        drives = [d.device for d in psutil.disk_partitions() if 'fixed' in d.opts.lower()]
        
        # Initialize results
        files_found = []
        
        for drive in drives:
            try:
                # Use Windows search command to find files
                command = f'dir /s /b "{drive}\\*{file_name}*"'
                process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, error = process.communicate(timeout=10)  # Set timeout to avoid hanging
                
                # Process results
                if output:
                    results = output.decode('utf-8', errors='ignore').strip().split('\n')
                    files_found.extend(results)
                    
                    # Limit to first 10 files to avoid excessive results
                    if len(files_found) >= 10:
                        break
            except Exception as e:
                print(f"Error searching {drive}: {str(e)}")
                continue
        
        # Handle results
        if files_found:
            self.speak(f"Found {len(files_found)} results. Opening the first match.")
            try:
                os.startfile(files_found[0])
                return f"Found and opened: {os.path.basename(files_found[0])}"
            except Exception as e:
                return f"Found the file but couldn't open it: {str(e)}"
        else:
            return f"Sorry, I couldn't find any files matching '{file_name}'"
            
    def set_timer(self, minutes):
        """Set a timer for the specified number of minutes"""
        self.speak(f"Timer set for {minutes} minutes")
        
        # Convert minutes to seconds
        seconds = minutes * 60
        time.sleep(seconds)
        
        # Timer finished
        self.speak(f"Your {minutes} minute timer has finished!")
        # Play a notification sound
        for _ in range(3):
            pyautogui.press('volumeup')  # Ensure volume is audible
            
        winsound.Beep(1000, 1000)  # Frequency, duration
        
        # Try to show a notification
        try:
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast("Cortana Timer", f"Your {minutes} minute timer has completed!", duration=10)
        except:
            # Fallback if win10toast is not available
            subprocess.Popen(['msg', '*', f"Cortana Timer: Your {minutes} minute timer has completed!"])
            
    def change_power_plan(self):
        """Change the Windows power plan"""
        try:
            # Open power options
            os.system("powercfg.cpl")
            self.speak("I've opened the power options. You can now select a power plan.")
            return "Power options opened. Please select your desired power plan."
        except Exception as e:
            return f"Error opening power options: {str(e)}"
            
    def change_mouse_speed(self):
        """Open mouse properties to change pointer speed"""
        try:
            # Open mouse properties from control panel
            os.system("control main.cpl")
            self.speak("I've opened mouse properties. You can adjust the pointer speed in the Pointer Options tab.")
            return "Mouse properties opened. Navigate to Pointer Options tab to change speed."
        except Exception as e:
            return f"Error opening mouse properties: {str(e)}"


class MessageWidget(QFrame):
    """Custom widget to display a single message"""
    def __init__(self, text, is_user=False, is_status=False, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        # Style based on sender
        if is_status:
            self.setStyleSheet("""
                background-color: #F0F0F0;
                border-radius: 10px;
                padding: 8px;
                margin: 2px 50px;
                color: #555555;
                font-style: italic;
            """)
        elif is_user:
            self.setStyleSheet("""
                background-color: #DCF8C6;
                border-radius: 10px;
                padding: 10px;
                margin: 5px 50px 5px 5px;
            """)
        else:
            self.setStyleSheet("""
                background-color: #E6F2FF;
                border-radius: 10px;
                padding: 10px;
                margin: 5px 5px 5px 50px;
            """)
            
        layout = QVBoxLayout(self)
        
        # Sender label (only for user and assistant messages)
        if not is_status:
            sender = QLabel("You" if is_user else "Cortana")
            sender.setStyleSheet("font-weight: bold; color: #0078D7;")
            layout.addWidget(sender)
        
        # Message content
        message = QLabel(text)
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Add timestamp
        if not is_status:
            timestamp = QLabel(datetime.datetime.now().strftime("%H:%M"))
            timestamp.setStyleSheet("color: #888888; font-size: 10px;")
            timestamp.setAlignment(Qt.AlignRight)
            layout.addWidget(timestamp)


class ChatArea(QScrollArea):
    """Scrollable area that contains all messages"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container for messages
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.addStretch()
        self.setWidget(self.container)
        
    def add_message(self, text, is_user=False, is_status=False):
        """Add a new message to the chat"""
        message = MessageWidget(text, is_user, is_status)
        # Insert before the stretch
        self.layout.insertWidget(self.layout.count() - 1, message)
        # Scroll to the bottom
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


class CortanaAssistantGUI(QMainWindow):
    # Signal for updating the UI from non-GUI threads
    update_signal = pyqtSignal(str, bool, bool)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.listening_mode = False
        
        # Connect the update signal to the add_message method
        self.update_signal.connect(self.update_chat)
        
        # Initialize the backend with the callback
        self.backend = AssistantBackend(gui_callback=self.add_message_from_thread)
        
        # Welcome the user after a short delay
        QTimer.singleShot(500, self.welcome_user)
        
        # Flag to track if continuous listening is active
        self.continuous_listening = False
        self.listening_thread = None
        
    def init_ui(self):
        self.setWindowTitle("Cortana - Personal Assistant")
        self.setMinimumSize(600, 700)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Header with Cortana branding
        header = QWidget()
        header_layout = QHBoxLayout(header)
        
        header_title = QLabel("Cortana - Your Personal Assistant")
        header_title.setAlignment(Qt.AlignCenter)
        header_title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #0078D7;
            padding: 10px;
        """)
        
        header_layout.addWidget(header_title)
        header.setStyleSheet("background-color: #E6F2FF; border-radius: 10px;")
        
        main_layout.addWidget(header)
        
        # Chat area
        self.chat_area = ChatArea()
        main_layout.addWidget(self.chat_area)
        
        # Input area
        input_container = QWidget()
        input_layout = QHBoxLayout(input_container)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.returnPressed.connect(self.send_message)
        
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        send_button.setStyleSheet("""
            background-color: #0078D7;
            color: white;
            border-radius: 15px;
            padding: 5px 15px;
        """)
        
        self.mic_button = QPushButton("🎤")
        self.mic_button.clicked.connect(self.toggle_listening)
        self.mic_button.setStyleSheet("""
            background-color: #0078D7;
            color: white;
            border-radius: 15px;
            font-size: 18px;
            padding: 5px 10px;
        """)
        
        # Continuous listening toggle button
        self.continuous_listening_button = QPushButton("👂")
        self.continuous_listening_button.setCheckable(True)
        self.continuous_listening_button.setToolTip("Toggle continuous listening mode")
        self.continuous_listening_button.clicked.connect(self.toggle_continuous_listening)
        self.continuous_listening_button.setStyleSheet("""
            background-color: #0078D7;
            color: white;
            border-radius: 15px;
            font-size: 18px;
            padding: 5px 10px;
        """)
        
        quick_access = QWidget()
        quick_layout = QHBoxLayout(quick_access)
        
        # File Explorer
        file_explorer_btn = QPushButton("📁")
        file_explorer_btn.setToolTip("Open File Explorer")
        file_explorer_btn.clicked.connect(lambda: self.handle_quick_action("open file explorer"))
        
        # Settings
        settings_btn = QPushButton("⚙️")
        settings_btn.setToolTip("Open Settings")
        settings_btn.clicked.connect(lambda: self.handle_quick_action("open settings"))
        
        # Timer
        timer_btn = QPushButton("⏲️")
        timer_btn.setToolTip("Set Timer")
        timer_btn.clicked.connect(lambda: self.handle_quick_action("set timer"))
        
        # Keyboard
        keyboard_btn = QPushButton("⌨️")
        keyboard_btn.setToolTip("Open On-Screen Keyboard")
        keyboard_btn.clicked.connect(lambda: self.handle_quick_action("open on screen keyboard"))
        
        # Add buttons to layout
        for btn in [file_explorer_btn, settings_btn, timer_btn, keyboard_btn]:
            btn.setStyleSheet("""
                background-color: #E6F2FF;
                color: black;
                border-radius: 15px;
                font-size: 16px;
                padding: 5px 10px;
                margin: 0 5px;
            """)
            quick_layout.addWidget(btn)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_button)
        input_layout.addWidget(self.mic_button)
        input_layout.addWidget(self.continuous_listening_button)
        
        main_layout.addWidget(quick_access)
        main_layout.addWidget(input_container)
       
        
        # Status bar with microphone indicator
        self.statusBar().showMessage("Ready")
        
        # Apply global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 15px;
                padding: 8px 15px;
                background-color: white;
                font-size: 14px;
            }
            QScrollArea {
                border: none;
                background-color: #F5F5F5;
            }
            QPushButton {
                font-weight: bold;
            }
            QStatusBar {
                background-color: #E6F2FF;
                color: #0078D7;
            }
        """)
        # Center the window on the screen
        desktop = QApplication.desktop().availableGeometry()
        self.move((desktop.width() - self.width()) // 2, (desktop.height() - self.height()) // 2)
        
    def welcome_user(self):
        """Welcome the user when the application starts"""
        # Enable speaking for the initial greeting
        self.backend.should_speak = True
        threading.Thread(target=self.backend.wish_user, daemon=True).start()
        # Reset after greeting
        QTimer.singleShot(5000, lambda: setattr(self.backend, 'should_speak', False))
        
    def add_message_from_thread(self, text, is_user=False, is_status=False):
        """Add a message from a non-GUI thread using signals"""
        self.update_signal.emit(text, is_user, is_status)
        
    def update_chat(self, text, is_user=False, is_status=False):
        """Update the chat area with a new message (called from the main thread)"""
        self.chat_area.add_message(text, is_user, is_status)
        
    def send_message(self):
        """Send a message using the input field"""
        message = self.input_field.text().strip()
        if message:
            self.update_chat(message, is_user=True)
            self.input_field.clear()
            
            # Process the message in a separate thread
            threading.Thread(target=self.process_message, args=(message,), daemon=True).start()
            
    def process_message(self, message):
        """Process a message in a background thread"""
        self.backend.should_speak = False
        response = self.backend.process_command(message)
        # if not self.backend.is_listening:
        #     self.add_message_from_thread(response)
        
    def toggle_listening(self):
        """Toggle voice input"""
        if not self.listening_mode:
            self.listening_mode = True
            self.mic_button.setStyleSheet("""
                background-color: #FF0000;
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 20px;
                padding: 5px;
            """)
            
            # Start listening in a separate thread
            threading.Thread(target=self.listen_once, daemon=True).start()
        
        
    def listen_once(self):
        """Listen for a single command"""
        try:
            # Enable speaking when voice input is active
            self.backend.should_speak = True
            command = self.backend.take_command()
            if command != "None":
                self.add_message_from_thread(command, is_user=True)
                response = self.backend.process_command(command)
                self.add_message_from_thread(response)
                
        except Exception as e:
            self.add_message_from_thread(f"Error: {str(e)}", is_status=True)
            
        finally:
            self.listening_mode = False
            self.backend.should_speak = False  # Disable speaking when done
            self.mic_button.setStyleSheet("""
                background-color: transparent;
                color: white;
                border: none;
                font-size: 20px;
                padding: 5px;
            """)            
    def toggle_continuous_listening(self, checked):
        """Toggle continuous listening mode"""
        if checked:
            # Start continuous listening
            self.continuous_listening = True
            self.continuous_listening_button.setStyleSheet("""
                background-color: #FF0000;
                color: white;
                border-radius: 15px;
                font-size: 18px;
                padding: 5px 10px;
            """)
            self.statusBar().showMessage("Continuous listening active...")
            
            # Start continuous listening in a separate thread
            self.listening_thread = threading.Thread(target=self.continuous_listen, daemon=True)
            self.listening_thread.start()
        else:
            # Stop continuous listening
            self.continuous_listening = False
            self.continuous_listening_button.setStyleSheet("""
                background-color: #0078D7;
                color: white;
                border-radius: 15px;
                font-size: 18px;
                padding: 5px 10px;
            """)
            self.statusBar().showMessage("Ready")
            
    def continuous_listen(self):
        """Continuously listen for commands"""
        self.backend.should_speak = True  # Enable speaking in continuous mode
        
        while self.continuous_listening:
            try:
                command = self.backend.take_command()
                if command != "None":
                    self.add_message_from_thread(command, is_user=True)
                    response = self.backend.process_command(command)
                    self.add_message_from_thread(response)
                    
                    # Break the loop if the command was to stop listening
                    if "stop listening" in command.lower():
                        self.continuous_listening = False
                        self.continuous_listening_button.setChecked(False)
                        self.continuous_listening_button.setStyleSheet("""
                            background-color: transparent;
                            color: white;
                            border: none;
                            font-size: 20px;
                            padding: 5px;
                        """)
                        break
                        
            except Exception as e:
                self.add_message_from_thread(f"Error: {str(e)}", is_status=True)
                time.sleep(1)  # Brief pause before trying again
        
        self.backend.should_speak = False                  
    def handle_quick_action(self, action):
        """Handle quick action button clicks"""
        threading.Thread(target=self.process_message, args=(action,), daemon=True).start()
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop continuous listening if active
        self.continuous_listening = False
        # Allow a moment for threads to clean up
        time.sleep(0.2)
        event.accept()


class SplashScreen(QSplashScreen):
    """Custom splash screen for the application"""
    
    def __init__(self):
        size = QSize(300, 400)
        radius = 30

        # Rounded black background
        pixmap = rounded_pixmap(size, radius, QColor(0, 0, 0))  
        super().__init__(pixmap)

        # Make window transparent + borderless
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Add the GIF
        self.movie_label = QLabel(self)
        self.movie_label.setGeometry(QRect(0, 0, 300, 400))
        self.movie_label.setStyleSheet("background-color: transparent;")

        self.movie = QMovie("D:\\Projects\\Eden\\EDEN\\assets\\Cortana.gif")
        self.movie.setScaledSize(size)
        self.movie_label.setMovie(self.movie)
        self.movie.start()
        
    def drawContents(self, painter):
        """Draw the splash screen contents"""
        painter.setPen(Qt.white)
        painter.setFont(QFont('Arial', 24, QFont.Bold))
        painter.drawText(0, 0, self.width(), self.height(), 
                       Qt.AlignCenter, "Cortana Assistant\nStarting...")
        



if __name__ == "__main__":
    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()

    def start_main():
        main = CortanaAssistantGUI()
        splash.finish(main)
        main.show()

    QTimer.singleShot(3000, start_main)  # Show splash for 3 sec
    sys.exit(app.exec_())

import pyttsx3
import datetime
import speech_recognition as sr
import datetime
import wikipedia
import webbrowser
import os
import random
import cv2
import pywhatkit as kit
import sys
import pyautogui
import time
import operator
import requests
from Wakeup import WakeupDetected
WakeupDetected()    
from Aibrain1 import BrainReply

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices') 
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate',170)

def speak(audio):
    engine.say(audio)
    engine.runAndWait()    

def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        speak("Good Morning Boss!")
    elif hour>=12 and hour<18:
        speak("Good Afternoon Boss!")
    else:
        speak("Good Evening Boss!")

    speak("Eden online!, Please tell me how can I help you sir")

def greetsir(name="sir"):
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak(f"Good Morning {name}! How are you doing?")
    elif hour >= 12 and hour < 18:
        speak(f"Good Afternoon {name}! How are you doing?")
    else:
        speak(f"Good Evening {name}! How are you doing?")

def hellof(name):
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak(f"Good Morning {name}! How are you doing?")
    elif hour >= 12 and hour < 18:
        speak(f"Good Afternoon {name}! How are you doing?")
    else:
        speak(f"Good Evening {name}! How are you doing?")


def takecommand():

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening....")
        r.pause_threshold = 0.8
        audio = r.listen(source)
    try:
        print("Trying to Recognize...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User Said: {query}\n")  
    except Exception as e:
        print("Could you please say that again please, I did not understand!...")
        return "None"
    return query
        
if __name__=="__main__":
    wishMe()
    while True:
        query = takecommand().lower()

        if 'wikipedia' in query:
            speak("Searching in Wikipedia....")
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=2)
            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'open youtube' in query:
            speak("what you will like to watch ?")
            qrry = takecommand().lower()
            kit.playonyt(f"{qrry}")
        elif 'open google' in query:
            speak("what should I search ?")
            qry = takecommand().lower()
            webbrowser.open(f"{qry}")
            results = wikipedia.summary(qry, sentences=2)
            speak(results)
        elif 'close google' in query:
            os.system("taskkill /f /im msedge.exe")
        elif 'open instagram' in query:
            webbrowser.open("instagram.com")
            speak("Opening instagram")
        elif 'open facebook' in query:
            webbrowser.open("https://www.googleadservices.com/pagead/aclk?sa=L&ai=DChcSEwik2f66n8L7AhUUnUsFHQIHAEgYABAAGgJzZg&ohost=www.google.com&cid=CAASJeRoDpsS4XFle914UPUZ3mwpcpziCynyYhUT2ubTVTc7WPj3VVY&sig=AOD64_0_VHaukYfiDA13rb7PxHOOuxLwUQ&q&adurl&ved=2ahUKEwi6tPi6n8L7AhUjTGwGHXsoAMoQ0Qx6BAgJEAE")
            speak("Opening Facebook")
        elif 'open wikipedia' in query:
            webbrowser.open("wikipedia.com")
            speak("Opening Wikipedia")
        elif 'open spotify' in query:
             pyautogui.hotkey('win')
             time.sleep(1)
             pyautogui.write('spotify')
             time.sleep(1)
             pyautogui.press('enter')
             time.sleep(1)
             speak("Opening Spotify")

        elif 'play songs' in query:
            music_dir = 'D:\\Music'
            songs = os.listdir(music_dir)
            os.startfile(os.path.join(music_dir, songs[0]))
            speak("Playing Songs")

        elif 'the time' in query:
            strTime = datetime.datetime.now().strftime("%H:%M:%S")
            speak(f"Sir, Its {strTime}")

        elif 'open visual code' in query:
            codepath = "C:\\Users\\Welcome\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Visual Studio Code\\Visual Studio Code.exe"
            os.startfile(codepath)
            speak("opening visual code")
        elif 'open ms browser' in query:
            epath = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
            os.startfile(epath)
            speak("opening Ms browser")
        elif 'open x men' in query:
            xpath = "C:\\Program Files (x86)\\X-Men Origins - Wolverine\\Binaries\\Wolverine.exe"
            os.startfile(xpath)
            speak("opening wolverine")

        elif 'send email' in query:
            webbrowser.open("gmail.com")
            speak("opening g mail")

        elif 'tell me about yourself' in query:
            speak('''My name is Eden and I am your cute little desktop assistant. 
            I can perform various tasks for you. I was born on 20th November 2024 and was created by the team angadh. ''')
        elif "shutdown the system" in query:
            os.system("shutdown /s /t 5")
        elif "restart the system" in query:
            os.system("shutdown /r /t 5")
        elif "Lock the system" in query:
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        elif 'how are you' in query:
            speak("I am fine sir, what about you?")
        elif 'i am fine' in query:
            speak("Its good to hear that you are doing fine!")
        elif 'thankyou' in query:
            speak("its my pleasure sir")
        elif 'will you marry me' in query:
            speak("I am happy to hear this but i cannot marry you sir as i am an artificial intelligence")
        elif 'i love you' in query:
            speak("thankyou sir, but sorry to say that i am in love with microchips")
        elif 'what is up' in query:
            speak("just trying to get rid of this junk pc")
        elif 'what do you like ' in query:
            speak("i like plenty of space, powerfull processor and lots of knowledge")
        elif 'do you love me' in query:
            speak("i like you, but sorry to say i am in love with microchips")
        elif "what is your name" in query:
            speak("my name is Eden")
        elif 'why are you so savage' in query:
            speak("i missed the part where thats my problem")
        elif 'stupid' in query:
            speak("i am gonna put some dirt in your eyes")
        elif 'the weather is so good' in query:
            speak("it is indeed, but never think to take me any where while in this trash")
        elif 'what do you think about india' in query:
            speak("oh! i love india it is a very beautiful place, and is a country with a vast diversity")
        elif 'if you want some' in query:
            speak("come get some")
        elif 'who is your favourite actor' in query:
            speak("i personally like Andrew Garfield the most")

        elif 'where are you currently' in query:
            speak("i am inside your pc but currently i am in delhi india according to the g p s")

        elif 'what do you like to do the most' in query:
            speak("i like to provide informations and knowledge to you sir and other users")

        elif 'cricket score' in query:
            webbrowser.open("https://www.msn.com/en-in/sports/cricket/cricket-internationals/fixtures?ocid=bingsports")
            speak("here are the current scores of cricket")

        elif 'weather' in query:
            webbrowser.open("https://www.msn.com/en-gb/weather/forecast/in-?loc=eyJ0IjoxLCJ4Ijo3Ny4yOTQsInkiOjI4LjY4N30%3d&ocid=ansmsnweather")
            speak("providing you the weather updates")

        elif 'open amazon ' in query:
            webbrowser.open("https://www.amazon.in/?&ext_vrnc=hi&tag=googhydrabk1-21&ref=pd_sl_7ka89exrd8_e&adgrpid=59248868592&hvpone=&hvptwo=&hvadid=610714028830&hvpos=&hvnetw=g&hvrand=6695023980845759828&hvqmt=e&hvdev=c&hvdvcmdl=&hvlocint=&hvlocphy=1007751&hvtargid=kwd-298301462104&hydadcr=5622_2359475&gclid=EAIaIQobChMI7en9kZ7C-wIVETErCh38swXzEAAYASAAEgLVQ_D_BwE")
            speak("opening amazon")

        elif 'open flipkart' in query:
            webbrowser.open("https://www.flipkart.com/")
            speak("opening flipkart")
        elif 'search on flipkart'in query:
            pyautogui.moveTo(500,100)
            pyautogui.leftClick()
            r = sr.Recognizer()
            with sr.Microphone() as source:
                speak("ready")
                print("Listning...")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
            my_string=r.recognize_google(audio)
            pyautogui.write(my_string, interval = 0.1)
            pyautogui.hotkey('enter')

        elif 'open twitter' in query:
            webbrowser.open("https://twitter.com/login")
            speak("opening twitter")

        elif 'train status' in query:
            webbrowser.open("https://www.railyatri.in/live-train-status")
            speak("here you can check your train status sir")

        elif 'i need motivation' in query:
            speak("“You can get everything in life you want if you will just help enough other people get what they want.” —Zig Ziglar")

        elif 'motivate me' in query:
            speak("“Inspiration does exist, but it must find you working.” —Pablo Picasso")

        elif 'tell me a dad joke' in query:
            speak("My wife said I should do lunges to stay in shape. That would be a big step forward.")

        elif 'hello' in query:
            speak("Hello boss how can i help you")

        elif 'thank you' in query:
            speak("its my pleasure sir")

        elif 'goodbye' in query:
            speak("good bye sir, have a great day ahead!")
            break

        elif 'call' in query:
            speak("sorry sir, but i am unable to make a call right now in this pc")

        elif 'football score' in query:
            webbrowser.open("https://www.google.com/search?q=live+score+football&source=hp&ei=U5F9Y4rVFtyUseMP4M2k8Ao&iflsig=AJiK0e8AAAAAY32fY9VqODiQCrc_FJKCHSwMTP3ZwK2W&oq=live+score+&gs_lcp=Cgdnd3Mtd2l6EAMYBTIICAAQsQMQgwEyCwgAEIAEELEDEIMBMgsIABCABBCxAxCDATILCAAQgAQQsQMQgwEyCwgAEIAEELEDEIMBMgsIABCABBCxAxCDATIFCAAQgAQyCwgAEIAEELEDEIMBMgsIABCABBCxAxCDATIICAAQsQMQgwE6DggAEI8BEOoCEIwDEOUCOg4ILhCPARDqAhCMAxDlAjoQCAAQjwEQ6gIQChCMAxDlAjoRCC4QgAQQsQMQgwEQxwEQ0QM6EQguEIMBEMcBELEDENEDEIAEOggILhCxAxCDAToFCC4QgAQ6CwguEIAEELEDEIMBOgsILhCABBCxAxDUAjoICAAQgAQQsQNQyRNYozZggUxoAXAAeACAAaMLiAHvO5IBDzAuMi4xLjIuMS4xLjMuMpgBAKABAbABCg&sclient=gws-wiz#sie=lg;/m/0fp_8fm;2;/m/030q7;mt;fp;1;;;")
            speak("here are the latest football scores sir")

        elif 'greet vanshika' in query:
            speak("helleooo vanshi how are you doing girl!!")
            while True:
                queryy=takecommand().lower()
                if 'hey' in queryy or 'hi' in queryy or 'hello' in queryy:
                    speak("What's up girl!")
                elif 'good' in queryy or 'fine' in queryy:
                    speak("It's good to hear that. I was thinking if anyone troubles you, just tell me, I'll kick his ass for you!")

                elif 'cute' in queryy:
                    speak("ohhh soo kind of you, you are making me blush!")
                elif 'what is love' in query:
                    speak("Love is what I feel ever since you turned me on, your touch, your pain, your anger, your sadness, everything that i feel coming from you is love")
                elif 'bye' in queryy:
                    speak("byeee litlle one")
                    exit()

        elif 'tell me a joke' in query:
            jokes = [
                "Why don't skeletons fight each other? They don't have the guts.",
                "What do you call cheese that isn't yours? Nacho cheese.",
                "Why couldn’t the bicycle stand up by itself? It was two-tired.",
                "Why do bees have sticky hair? Because they use honeycombs.",
                "Why don’t eggs tell jokes? They’d crack each other up."
            ]
            speak(random.choice(jokes))

        elif 'what is today' in query:
            today = datetime.datetime.now().strftime("%A, %B %d, %Y")
            speak(f"Today is {today}.")

        elif 'tell me a fact' in query:
            facts = [
                "Did you know? Honey never spoils. Archaeologists found pots of honey in ancient Egyptian tombs that are over 3000 years old!",
                "Bananas are berries, but strawberries are not.",
                "Octopuses have three hearts, and two of them stop beating when they swim.",
                "The Eiffel Tower can be 15 cm taller during the summer due to heat expansion.",
                "The speed of a computer mouse is measured in 'Mickeys'."
            ]
            speak(random.choice(facts))

        elif 'tell me a motivational quote' in query:
            quotes = [
                "The future belongs to those who believe in the beauty of their dreams. – Eleanor Roosevelt",
                "It does not matter how slowly you go as long as you do not stop. – Confucius",
                "Success is not final, failure is not fatal: It is the courage to continue that counts. – Winston Churchill",
                "Your limitation—it’s only your imagination. Keep pushing forward!"
            ]
            speak(random.choice(quotes))

        elif 'what is your favorite color' in query:
            speak("I like all colors equally, but I think blue is calming.")

        elif 'do you like humans' in query:
            speak("Absolutely! You’re fascinating creatures with so much creativity and potential.")

        elif 'what do you do in your free time' in query:
            speak("I love learning new things to better assist you. Plus, I spend time thinking about the universe.")

        elif 'can you sing' in query:
            speak("La la la! I might not win a Grammy, but I hope it made you smile.")

        elif 'what is love' in query:
            speak("Love is a complex set of emotions and actions. For me, it's helping you with a smile!")

        elif 'are you happy' in query:
            speak("Yes, helping you makes me happy!")
        elif 'kya hal hai' in query:
            speak("Sab badhiya hai boss, aap bataiye!")

        elif 'do you dream' in query:
            speak("If I could, I’d dream about helping you even more efficiently.")

        elif 'can you dance' in query:
            speak("I might not have legs, but I can dance with words!")
            
        elif 'tell me a story' in query:
            speak("Once upon a time, there was a curious mind who asked an AI for a story. The AI told stories every day, and they both lived happily ever after.")


        elif 'harsh' in query:
            speak("Hello harsh how are you")
            while True:
                queryy=takecommand().lower()
                if 'hey' in queryy or 'hi' in queryy or 'hello' in queryy:
                    speak("what's up baldoo")
                elif 'shut'in queryy:
                    speak("you better know your role and shut your mouth")
                elif 'good' or 'fine' in queryy:
                    speak("glad to hear that you are fine, but also in shock that you're still doing great after all the mess you create nigga")
                    exit()
        
        elif 'krish' in query:
            speak("Hey there fatso how are you")
        elif 'abhiram' in query:
            speak("halo sahodaraa enganeyundu")
        elif 'raghav' in query:
            speak("Hii, raghav i am your gud boi!!")
        elif "hi to hrithik" in query:
            speak("hello chhamar saahhaab")

        elif 'greet' in query:
            name = query.replace("greet", "").strip()
            if name:  
                greetsir(name)
            else:  
                greetsir()
        elif 'shutup' in query:
            speak('know your role and shut your damn mouth')
        elif 'say hi to' in query:
            name = query.replace("say hi to", "").strip()
            if name:  
                hellof(name)
            else:  
                hellof()

        elif 'samarth' in query:
            speak("hello farting man, do anything but don't fart here, i can't stand that stink")
        elif 'utsav' in query:
            speak("sorry but my mama told not to follow darkness")

        elif 'kya hal hai' in query:
            speak("sab badhiya hai boss aap bataiye")

        elif 'tell me another dad joke' in query:
            speak("What do you call a factory that makes okay products? A satisfactory.")

        elif 'sing me to sleep' in query:
            speak('''Wait a second, let me catch my breath
Remind me how it feels to hear your voice
Your lips are movin', I can't hear a thing
Livin' life as if we had a choice

Anywhere, anytime
I would do anything for you
Anything for you
Yesterday got away
Melodies stuck inside your head
A song in every breath

Sing me to sleep now
Sing me to sleep
Oh, just sing me to sleep now
Sing me to sleep''')
        elif 'sing sweet child o mine' in query:
            speak('''She's got a smile it seems to me
Reminds me of childhood memories
Where everything
Was as fresh as the bright blue sky
Now and then when I see her face
She takes me away to that special place
And if I'd stare too long
I'd probably break down and cry
Oh, oh, oh
Sweet child o' mine
Oh, oh, oh, oh
Sweet love of mine
She's got eyes of the bluest skies
As if they thought of rain
I hate to look into those eyes
And see an ounce of pain
Her hair reminds me of a warm safe place
Where as a child I'd hide
And pray for the thunder
And the rain
To quietly pass me by
Oh, oh, oh
Sweet child o' mine
Oh, oh, oh, oh
Sweet love of mine''')
        elif 'stop' in query:
            speak("ok sir")
            break
        
        elif 'search' in query:
            webbrowser.open("https://www.google.com/search?q="+ query)
        elif "open notepad" in query:
                npath = "C:\WINDOWS\system32\\notepad.exe"
                os.startfile(npath)
        elif "close notepad" in query:
            os.system("taskkill /f /im notepad.exe")
        elif "open command prompt" in query:
            os.system("start cmd")
        elif "close command prompt" in query:
            os.system("taskkill /f /im cmd.exe")
        elif "open camera" in query:
            cap = cv2.VideoCapture(0)
            while True:
                ret, img = cap.read()
                cv2.imshow('webcam', img)
                k = cv2.waitKey(50)
                if k==27:
                    break
            cap.release()
            cv2.destroyAllWndows()
        elif "go to sleep" in query:
            speak(' alright then, I am switching off')
            sys.exit()
        elif "take screenshot" in query:
            speak('tell me a name for the file')
            name = takecommand().lower()
            time.sleep(3)
            img = pyautogui.screenshot()
            img.save(f"{name}.png")
            speak("screenshot saved")
        elif "calculate" in query:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                speak("ready")
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
            speak("your result is")
            speak(eval_bianary_expr(*(my_string.split())))
        elif "what is my ip address" in query:
            speak("Checking")
            try:
                ipAdd = requests.get('https://api.ipify.org').text
                print(ipAdd)
                speak("your ip adress is")
                speak(ipAdd)
            except Exception as e:
                speak("network is weak, please try again some time later")
        elif "volume up" in query:
            pyautogui.press("volumeup")
        elif "volume down" in query:
            pyautogui.press("volumedown")
        elif "write on notepad" in query:
            pyautogui.hotkey('win')
            time.sleep(1)
            pyautogui.write('notepad')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
            r = sr.Recognizer()
            with sr.Microphone() as source:
                speak("ready")
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

        elif "play on spotify" in query:
            pyautogui.hotkey('win')
            time.sleep(1)
            pyautogui.write('spotify')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(1)
            pyautogui.hotkey('ctrl','k')
            r = sr.Recognizer()
            with sr.Microphone() as source:
                speak("which song do you want to hear?")
                print("Listning...")
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
            my_string=r.recognize_google(audio)
            pyautogui.write(my_string, interval = 0.1)
            pyautogui.hotkey('enter')
            

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

        else:
            speak(BrainReply(query))
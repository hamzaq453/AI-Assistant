import pygetwindow as gw
from webbrowser import open as webopen
from pytube import Search, YouTube
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from rich import print
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load environment variables
load_dotenv()
GroqAPIKey = os.getenv("GROQ_API_KEY")

# Constants
Classes = [
    "Z0lubf", "hpKCJe", "LiX0Yv7iG", "Z0LcL", "g5rt vk bk FzWJS WpJhf",
    "pclqee", "tw-Data-text tw-text-small tw-ta", "1z6rdc", "0U5i6d 1TK00",
    "v1v6d", "webanswers-webanswers_table_webanswers-table",
    "dObNo kKb4B g5rt", "sXLa0e", "LWkfbc", "qv3Hpe", "kno-desc", "SPZz6b"
]

useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask."
]

messages = []

SystemChatBot = [
    {"role": "system", "content": f"Hello, I am {os.environ['Username']}, You're a content writer. You have to write content like letters"}
]

def GoogleSearch(Topic):
    Search(Topic)
    return True

def Content(Topic):
    """Generate and save content using AI, then open it in notepad."""
    # Create Data directory if it doesn't exist
    DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data")
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File])

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})
        return Answer

    Topic = str(Topic.replace("Content ", ""))
    ContentByAI = ContentWriterAI(Topic)

    # Use os.path.join for file path
    file_path = os.path.join(DATA_DIR, f"{Topic.lower().replace(' ', '')}.txt")
    
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(ContentByAI)
        OpenNotepad(file_path)
        return True
    except Exception as e:
        print(f"Error saving content: {e}")
        return False


# Test the function
if __name__ == "__main__":
    Content("Application for a sick leave")

def YouTubeSearch(Topic):
    """Search YouTube and open in browser."""
    UrlSearch = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(UrlSearch)
    return True

def PlayYoutube(query):
    """Search and play first YouTube result."""
    try:
        # Search for the video using pytube's Search
        search = Search(query)
        if search.results:
            # Get first result
            video = search.results[0]
            # Open video in browser
            webbrowser.open(f"https://youtube.com/watch?v={video.video_id}")
            return True
        return False
    except Exception:
        # Fallback to search if play fails
        return YouTubeSearch(query)

def OpenApp(app, sess=requests.session()):
    # Dictionary of common web apps and their URLs
    web_apps = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "gmail": "https://mail.google.com",
        "facebook": "https://www.facebook.com",
        "twitter": "https://twitter.com",
        "instagram": "https://www.instagram.com",
        "whatsapp": "https://web.whatsapp.com"
    }

    # Dictionary of system apps and their executable names
    system_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "paint": "mspaint.exe",
        "word": "winword.exe",
        "excel": "excel.exe",
        "chrome": "chrome.exe",
        "firefox": "firefox.exe",
        "edge": "msedge.exe"
    }

    try:
        # Clean the app name - remove periods, spaces, and convert to lowercase
        app_lower = app.lower().strip().rstrip('.')

        # Check if it's a web app
        if app_lower in web_apps:
            webbrowser.open(web_apps[app_lower])
            return True

        # Check if it's a system app
        if app_lower in system_apps:
            try:
                subprocess.Popen(system_apps[app_lower])
                return True
            except FileNotFoundError:
                print(f"Could not find {system_apps[app_lower]}")

        # Try to find and activate existing window
        window = gw.getWindowsWithTitle(app)
        if window:
            window[0].activate()
            return True
            
        # Try to open as direct command
        try:
            subprocess.Popen(app)
            return True
        except FileNotFoundError:
            pass

        # If all above fails, try web search
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links if link.get('href')]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sess.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(links[0])
                return True

        # If nothing works, open a Google search for the app
        webbrowser.open(f"https://www.google.com/search?q={app}")
        return True

    except Exception as e:
        print(f"Error opening {app}: {e}")
        return False

def CloseApp(app):
    if "chrome" in app.lower():
        return False  # Skip closing Chrome
    try:
        windows = gw.getWindowsWithTitle(app)
        if windows:
            windows[0].close()
            return True
        return False
    except:
        return False

def System(command):
    def mute():
        keyboard.press_and_release("volume mute")

    def unmute():
        keyboard.press_and_release("volume mute")

    def volume_up():
        keyboard.press_and_release("volume up")

    def volume_down():
        keyboard.press_and_release("volume down")

    def brightness_up():
        keyboard.press_and_release("brightness up")

    def brightness_down():
        keyboard.press_and_release("brightness down")

    def take_screenshot():
        keyboard.press_and_release("print screen")

    def sleep():
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    def shutdown():
        os.system("shutdown /s /t 60")

    def cancel_shutdown():
        os.system("shutdown /a")

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()
    elif command == "brightness up":
        brightness_up()
    elif command == "brightness down":
        brightness_down()
    elif command == "screenshot":
        take_screenshot()
    elif command == "sleep":
        sleep()
    elif command == "shutdown":
        shutdown()
    elif command == "cancel shutdown":
        cancel_shutdown()

    return True

def MediaControl(command):
    def play_pause():
        keyboard.press_and_release("play/pause media")

    def next_track():
        keyboard.press_and_release("next track")

    def previous_track():
        keyboard.press_and_release("prev track")

    def stop():
        keyboard.press_and_release("stop media")

    if command == "play":
        play_pause()
    elif command == "pause":
        play_pause()
    elif command == "next":
        next_track()
    elif command == "previous":
        previous_track()
    elif command == "stop":
        stop()

    return True

def Productivity(command, *args):
    def create_note(title, content):
        DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data", "Notes")
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        file_path = os.path.join(DATA_DIR, f"{title}.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True

    def create_task(task):
        DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data", "Tasks")
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        
        file_path = os.path.join(DATA_DIR, "tasks.txt")
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(f"- {task}\n")
        return True

    def open_calendar():
        webbrowser.open("https://calendar.google.com")
        return True

    if command == "note":
        return create_note(args[0], args[1])
    elif command == "task":
        return create_task(args[0])
    elif command == "calendar":
        return open_calendar()

    return False

async def TranslateAndExecute(commands: list[str]):
    funcs = []

    for command in commands:
        if command.startswith("open "):
            if "open it" in command or "open file" == command:
                continue
            fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
            funcs.append(fun)

        elif command.startswith("general "):
            pass

        elif command.startswith("realtime "):
            pass

        elif command.startswith("close "):
            fun = asyncio.to_thread(CloseApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):
            fun = asyncio.to_thread(Content, command)
            funcs.append(fun)

        elif command.startswith("google search "):
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun)

        elif command.startswith("media "):
            fun = asyncio.to_thread(MediaControl, command.removeprefix("media "))
            funcs.append(fun)

        elif command.startswith("note "):
            parts = command.removeprefix("note ").split(":", 1)
            if len(parts) == 2:
                title, content = parts
                fun = asyncio.to_thread(Productivity, "note", title.strip(), content.strip())
                funcs.append(fun)

        elif command.startswith("task "):
            task = command.removeprefix("task ")
            fun = asyncio.to_thread(Productivity, "task", task)
            funcs.append(fun)

        elif command == "calendar":
            fun = asyncio.to_thread(Productivity, "calendar")
            funcs.append(fun)

    results = await asyncio.gather(*funcs)
    
    for result in results:
        yield result

async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True

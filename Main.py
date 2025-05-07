from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import Chatbot
from Backend.TextToSpeech import TextToSpeech

from dotenv import dotenv_values, load_dotenv
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

# Load environment variables
load_dotenv()  # Add this line to ensure .env is loaded

# Get environment variables with fallbacks
env_vars = dotenv_values(".env")
Username = os.getenv("Username", env_vars.get("Username", "User"))  # Added fallback
Assistantname = os.getenv("Assistantname", env_vars.get("Assistantname", "Assistant"))  # Added fallback

# Add debug print to check values
print(f"Debug - Username: {Username}, Assistantname: {Assistantname}")
print(f"Debug - Environment variables: {dict(env_vars)}")

DefaultMessage = f"{Username} : Hello {Assistantname}, How are you?\n" \
                f"{Assistantname} : Welcome {Username}. I am doing well. How may I help you?...."

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ensure_directories_exist():
    """Create necessary directories and files if they don't exist."""
    # Create Data directory
    if not os.path.exists("Data"):
        os.makedirs("Data")
    
    # Create ChatLog.json if it doesn't exist
    chatlog_path = os.path.join("Data", "ChatLog.json")
    if not os.path.exists(chatlog_path):
        with open(chatlog_path, "w", encoding="utf-8") as f:
            f.write("[]")  # Empty JSON array
    
    # Create Frontend/Files directory if it doesn't exist
    frontend_files_path = os.path.join("Frontend", "Files")
    if not os.path.exists(frontend_files_path):
        os.makedirs(frontend_files_path)
    
    # Create other necessary directories
    other_dirs = [
        os.path.join("Data", "Images"),
        os.path.join("Frontend", "Graphics")
    ]
    
    for directory in other_dirs:
        if not os.path.exists(directory):
            os.makedirs(directory)

# Call this function before any other initialization
ensure_directories_exist()

def ShowDefaultChatIfNoChats():
    try:
        with open("Data/ChatLog.json", "r", encoding="utf-8") as File:
            content = File.read()
            
        if not content or content.strip() == "[]" or len(content) <= 2:
            # File is empty or just contains []
            with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
                file.write("")

            with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as file:
                file.write(DefaultMessage)
    except Exception as e:
        print(f"Error in ShowDefaultChatIfNoChats: {e}")
        # Create the file if it doesn't exist
        with open("Data/ChatLog.json", "w", encoding="utf-8") as File:
            File.write("[]")
        
        # Write default messages
        with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
            file.write("")

        with open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8") as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    try:
        with open("Data/ChatLog.json", "r", encoding="utf-8") as file:
            content = file.read().strip()
            if not content or content == "[]":
                return []
            chatlog_data = json.loads(content)
        return chatlog_data
    except Exception as e:
        print(f"Error reading ChatLog.json: {e}")
        return []

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""

    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", "Username")
    formatted_chatlog = formatted_chatlog.replace("Assistant", "Assistantname")

    with open(TempDirectoryPath("Database.data"), "w", encoding="utf-8") as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    File = open(TempDirectoryPath("Database.data"), "r", encoding="utf-8")
    Data = File.read()
    if len(str(Data)) > 0:
        lines = Data.split("\n")
        result = "\n".join(lines)
        File.close()
        File = open(TempDirectoryPath("Responses.data"), "w", encoding="utf-8")
        File.write(result)
        File.close()

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    SetAssistantStatus("Listening...")
    Query = SpeechRecognition()
    ShowTextScreen(f"Username : {Query}")
    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)

    print("")
    print(f"Decision : {Decision}")
    print("")

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])

    Merged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    for queries in Decision:
        if "generate" in queries:
            ImageGenerationQuery = str(queries)
            ImageExecution = True

    for queries in Decision:
        if TaskExecution == False:
            if any(queries.startswith(func) for func in Functions):
                run(Automation(list(Decision)))
                TaskExecution = True

    if ImageExecution == True:
        with open("Frontend/Files/ImageGeneration.data", "w") as file:
            file.write(f"{ImageGenerationQuery}", True)

        try:
            p1 = subprocess.Popen(
                ['python', 'Backend/ImageGeneration.py'],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                stdin=subprocess.PIPE, shell=False
            )
            subprocesses.append(p1)

        except Exception as e:
            print(f"Error starting ImageGeneration.py: {e}")

    if G and R or R:
        SetAssistantStatus("Searching ...")
        Answer = RealtimeSearchEngine(QueryModifier(Merged_query))
        ShowTextScreen(f"{Assistantname} : {Answer}")
        SetAssistantStatus("Answering ...")
        TextToSpeech(Answer)
        return True

    else:
        for Queries in Decision:
            if "general" in Queries:
                SetAssistantStatus("Thinking ...")
                QueryFinal = Queries.replace("general", "")
                Answer = Chatbot(QueryModifier(QueryFinal))
                ShowTextScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True

            elif "realtime" in Queries:
                SetAssistantStatus("Searching ...")
                QueryFinal = Queries.replace("realtime", "")
                Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                ShowTextScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                return True
            
            elif "exit" in Queries:
                QueryFinal = "Okay, Bye!"
                Answer = Chatbot(QueryModifier(QueryFinal))
                ShowTextScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering ...")
                TextToSpeech(Answer)
                SetAssistantStatus("Answering ...")
                os._exit(1)

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()

        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()

            if "Available ..." in AIStatus:
                sleep(0.1)
            else:
                SetAssistantStatus("Available ...")

def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()

from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create Data directory if it doesn't exist
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data")
CHAT_LOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")

# Ensure Data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

Username = os.getenv("Username")
Assistantname = os.getenv("Assistantname")
GroqAPIKey = os.getenv("GROQ_API_KEY")

if not GroqAPIKey:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")

try:
    client = Groq(api_key=GroqAPIKey)
except Exception as e:
    raise Exception(f"Failed to initialize Groq client: {str(e)}")

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Initialize messages list
try:
    with open(CHAT_LOG_PATH, "r") as f:
        messages = load(f)
except FileNotFoundError:
    messages = []
    with open(CHAT_LOG_PATH, "w") as f:
        dump(messages, f, indent=4)

def GoogleSearch(query):
    results = list(search(query, advanced=True, num_results=5))
    Answer = f"The search results for '{query}' are:\n[start]\n"

    for i in results:
        Answer += f"Title: {i.title}\nDescription: {i.description}\n\n"

    Answer += "[end]"
    return Answer

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi!"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data += "Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"

    return data

def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    try:
        with open(CHAT_LOG_PATH, "r") as f:
            messages = load(f)
    except FileNotFoundError:
        messages = []

    messages.append({"role": "user", "content": f"{prompt}"})
    SystemChatBot.append({"role": "system", "content": GoogleSearch(prompt)})

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.strip().replace("</s>", "")
        messages.append({"role": "assistant", "content": Answer})

        with open(CHAT_LOG_PATH, "w") as f:
            dump(messages, f, indent=4)

        SystemChatBot.pop()
        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error during search: {e}")
        SystemChatBot.pop()  # Make sure to remove the search results even if there's an error
        return "I apologize, but I encountered an error while searching. Please try again."

if __name__ == "__main__":
    print(f"\nRealtime Search Engine initialized. Type 'exit', 'quit', or 'bye' to end.\n")
    while True:
        try:
            prompt = input("Enter your query: ").strip()
            if not prompt:
                continue
            if prompt.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            print("\nSearching...", end="\r")
            print(RealtimeSearchEngine(prompt))
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")


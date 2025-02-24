from groq import Groq
from json import load, dump
import datetime
from dotenv import load_dotenv
import os

# Create Data directory if it doesn't exist
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data")
CHAT_LOG_PATH = os.path.join(DATA_DIR, "ChatLog.json")

# Ensure Data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

load_dotenv()

Username = os.getenv("Username")
Assistantname = os.getenv("Assistantname")
GroqAPIKey = os.getenv("GROQ_API_KEY")

if not GroqAPIKey:
    raise ValueError("GROQ_API_KEY not found in environment variables. Please check your .env file.")

try:
    client = Groq(api_key=GroqAPIKey)
except Exception as e:
    raise Exception(f"Failed to initialize Groq client: {str(e)}")

messages = []

System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"

    return data

def AnswerModifier(Answer):
    lines = Answer.split("\n")
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = "\n".join(non_empty_lines)
    return modified_answer

def Chatbot(Query):
    try:
        # Load existing chat history first
        try:
            with open(CHAT_LOG_PATH, "r") as f:
                chat_history = load(f)
        except FileNotFoundError:
            chat_history = []

        # Find the most recent age information in chat history
        age_info = None
        for msg in reversed(chat_history):
            if msg["role"] == "user" and "years old" in msg["content"].lower():
                age_info = msg["content"]
                break

        # Build conversation with context
        conversation = [
            {"role": "system", "content": System}
        ]

        # Add age context if found
        if age_info:
            conversation.append({
                "role": "system", 
                "content": f"Important context: {age_info}"
            })

        # Add real-time information
        conversation.append({
            "role": "system", 
            "content": RealtimeInformation()
        })

        # Add recent conversation context (last 2 exchanges = 4 messages)
        if chat_history:
            conversation.extend(chat_history[-4:])

        # Add current query
        conversation.append({"role": "user", "content": Query})

        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=conversation,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "").strip()

        if Answer:
            # Update chat history
            chat_history.append({"role": "user", "content": Query})
            chat_history.append({"role": "assistant", "content": Answer})

            # Keep chat history from growing too large (keep last 20 messages)
            if len(chat_history) > 20:
                chat_history = chat_history[-20:]

            # Save updated chat history
            with open(CHAT_LOG_PATH, "w") as f:
                dump(chat_history, f, indent=4)

        return AnswerModifier(Answer=Answer)

    except Exception as e:
        print(f"Error: {e}")
        return "I apologize, but I encountered an error. Please try again."

if __name__ == "__main__":
    while True:
        try:
            user_input = input("Enter Your Question: ")
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye!")
                break
            print(Chatbot(user_input))
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"An error occurred: {e}")
    
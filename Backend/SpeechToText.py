from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import mtranslate as mt
import time
import logging
import sys
from selenium.webdriver.remote.remote_connection import LOGGER
from urllib3.connectionpool import log as urllibLogger

# Load environment variables
load_dotenv()
InputLanguage = os.getenv("InputLanguage", "en")  # Default to English if not set

# Suppress selenium and urllib3 logging
LOGGER.setLevel(logging.WARNING)
urllibLogger.setLevel(logging.WARNING)

# HTML template for speech recognition
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            try {
                recognition = new webkitSpeechRecognition() || new SpeechRecognition();
                recognition.lang = '';
                recognition.continuous = true;
                recognition.interimResults = true;

                recognition.onresult = function(event) {
                    const transcript = event.results[event.results.length - 1][0].transcript;
                    output.textContent = transcript;  // Replace instead of append
                };

                recognition.onend = function() {
                    recognition.start();
                };

                recognition.onerror = function(event) {
                    console.error('Speech recognition error:', event.error);
                };

                recognition.start();
            } catch (error) {
                console.error('Error initializing speech recognition:', error);
            }
        }

        function stopRecognition() {
            if (recognition) {
                recognition.stop();
                output.textContent = "";
            }
        }
    </script>
</body>
</html>'''

# Set the input language in the HTML code
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Create Data directory if it doesn't exist
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Write the HTML file
voice_html_path = os.path.join(DATA_DIR, "Voice.html")
with open(voice_html_path, "w") as f:
    f.write(HtmlCode)

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument("--remote-debugging-port=0")
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--window-size=1,1")
chrome_options.add_argument("--window-position=-10000,0")
chrome_options.add_argument("--log-level=3")  # Only show fatal errors
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
chrome_options.add_experimental_option('useAutomationExtension', False)
chrome_options.add_experimental_option('detach', False)

# Suppress selenium logging
logging.getLogger('selenium').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

# Redirect stderr to devnull to suppress Chrome's console output
stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')

try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
except Exception as e:
    print(f"Failed to initialize Chrome driver: {e}")
    raise
finally:
    sys.stderr = stderr  # Restore stderr

# Setup paths
current_dir = os.getcwd()
frontend_files_path = os.path.join(current_dir, "Frontend", "Files")

def SetAssistantStatus(Status):
    """Update the assistant's status in the status file."""
    status_file = os.path.join(frontend_files_path, "Status.data")
    with open(status_file, "w", encoding="utf-8") as file:
        file.write(Status)

def QueryModifier(Query):
    """Modify the query to ensure proper formatting."""
    if not Query:
        return ""
        
    new_query = Query.lower().strip()
    query_words = new_query.split()
    
    if not query_words:
        return ""
        
    question_words = [
        "how", "what", "who", "where", "when", "why", "which",
        "whose", "whom", "can you", "what's", "where's", "how's"
    ]

    # Add appropriate punctuation based on query type
    if any(word in new_query for word in question_words):
        if query_words[-1] not in [".", "?", "!"]:
            new_query = " ".join(query_words) + "?"
    else:
        if query_words[-1] not in [".", "?", "!"]:
            new_query = " ".join(query_words) + "."

    return new_query.capitalize()

def UniversalTranslator(Text):
    """Translate any text to English."""
    try:
        english_translation = mt.translate(Text, "en", "auto")
        return english_translation.capitalize()
    except Exception as e:
        print(f"Translation error: {e}")
        return Text.capitalize()

def SpeechRecognition():
    """Main function to handle speech recognition."""
    try:
        driver.get(f"file:///{voice_html_path}")
        time.sleep(1)  # Wait for page to load
        
        # Use JavaScript to click the button to avoid interactability issues
        driver.execute_script("document.getElementById('start').click()")
        
        previous_text = ""
        no_change_count = 0
        
        while True:
            try:
                current_text = driver.execute_script("return document.getElementById('output').textContent")
                current_text = current_text.strip()
                
                if current_text and current_text != previous_text:
                    previous_text = current_text
                    no_change_count = 0
                    time.sleep(0.5)
                elif current_text:
                    no_change_count += 1
                    if no_change_count > 3:
                        driver.execute_script("document.getElementById('end').click()")
                        if InputLanguage.lower() == "en" or "en" in InputLanguage.lower():
                            return QueryModifier(current_text)
                        else:
                            SetAssistantStatus("Translating...")
                            return QueryModifier(UniversalTranslator(current_text))
                
                time.sleep(0.5)
                
            except Exception as e:
                time.sleep(0.5)
                
    except Exception as e:
        return ""

if __name__ == "__main__":
    print("\nSpeech Recognition initialized. Speak to begin...")
    print("Press Ctrl+C to exit\n")
    
    while True:
        try:
            Text = SpeechRecognition()
            if Text:
                print(f"Recognized: {Text}")
        except KeyboardInterrupt:
            print("\nStopping Speech Recognition...")
            driver.quit()
            break
        except Exception as e:
            time.sleep(1)


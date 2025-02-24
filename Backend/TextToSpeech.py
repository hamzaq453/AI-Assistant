import pygame
import random
import asyncio
import os
import edge_tts
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AssistantVoice = os.getenv("AssistantVoice", "en-US-EricNeural")

# Create Data directory if it doesn't exist
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

async def TextToAudioFile(text):
    """Convert text to audio file using edge-tts."""
    try:
        file_path = os.path.join(DATA_DIR, "speech.mp3")
        if os.path.exists(file_path):
            os.remove(file_path)
        
        communicate = edge_tts.Communicate(
            text, 
            AssistantVoice, 
            pitch="+0Hz",
            rate="+10%"  # Slightly increased rate for faster speech
        )
        await communicate.save(file_path)
        return file_path
    except Exception:
        raise

def TTS(Text, func=lambda x=True: x):
    """Text to speech conversion with playback control."""
    try:
        file_path = asyncio.run(TextToAudioFile(Text))
        pygame.mixer.init()
        pygame.mixer.music.load(file_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            if not func(True):
                break
            pygame.time.Clock().tick(20)  # Increased tick rate for smoother playback

        return True
    except Exception:
        return False
    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except:
            pass

def TextToSpeech(Text, func=lambda x=True: x):
    """Main function to handle text-to-speech conversion."""
    if not Text.strip():
        return
    
    sentences = str(Text).split(".")
    
    # Handle long text differently
    if len(sentences) > 4 and len(Text) > 250:
        shortened_text = ".".join(sentences[:2]) + "... " + random.choice(responses)
        TTS(shortened_text, func)
    else:
        TTS(Text, func)

# List of responses for long text
responses = [
    "The rest of the result has been printed to the chat screen.",
    "The rest of the text is now on the chat screen.",
    "You can see the rest of the text on the chat screen.",
    "The remaining text is on the chat screen.",
    "Check the chat screen for the complete text."
]

if __name__ == "__main__":
    while True:
        try:
            text = input("> ").strip()
            if text.lower() in ['exit', 'quit', 'bye']:
                break
            if text:
                TextToSpeech(text)
        except KeyboardInterrupt:
            break
        except:
            pass

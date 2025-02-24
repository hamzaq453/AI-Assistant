import asyncio
from random import randint
from PIL import Image
import requests
import os
from dotenv import load_dotenv
from time import sleep

# Load environment variables
load_dotenv()
api_key = os.getenv("HuggingFaceAPIKey")

if not api_key:
    raise ValueError("HuggingFaceAPIKey not found in .env file")

# Create all necessary directories
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Data")
IMAGES_DIR = os.path.join(DATA_DIR, "Images")
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Frontend", "Files")

for directory in [DATA_DIR, IMAGES_DIR, FRONTEND_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Create ImageGeneration.data if it doesn't exist
status_file = os.path.join(FRONTEND_DIR, "ImageGeneration.data")
if not os.path.exists(status_file):
    with open(status_file, "w") as f:
        f.write("False,False")

def ImagePrompt(prompt):
    prompt = prompt.replace(" ", "_")
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(IMAGES_DIR, jpg_file)
        try:
            img = Image.open(image_path)
            print(f"Opening Image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {api_key}"}

async def query(payload):
    try:
        response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            return response.content
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Request Error: {e}")
        return None

async def generate_images(prompt: str):
    tasks = []
    
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed = {randint(0, 1000000)}"
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes:  # Check if we got valid image data
            file_path = os.path.join(IMAGES_DIR, f"{prompt.replace(' ', '_')}{i + 1}.jpg")
            with open(file_path, "wb") as f:
                f.write(image_bytes)

def GenerateImages(prompt: str):
    if not prompt:
        return False
        
    try:
        asyncio.run(generate_images(prompt))
        ImagePrompt(prompt)
        return True
    except Exception as e:
        print(f"Error generating images: {e}")
        return False

if __name__ == "__main__":
    while True:
        try:
            with open(status_file, "r") as f:  # Use the defined path
                Data = str(f.read()).strip()

            if not Data:
                sleep(1)
                continue

            Prompt, Status = Data.split(",")
            Status = Status.strip()

            if Status == "True":
                print("Generating Images...")
                GenerateImages(Prompt)

                with open(status_file, "w") as f:  # Use the defined path
                    f.write("False,False")
                break
            else:
                sleep(1)
        except Exception as e:
            print(f"Error: {e}")
            sleep(1)

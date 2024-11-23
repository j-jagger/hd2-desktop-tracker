"""
Helldivers 2 War Tracker

Uses the HDTM api endpoints to send push notifications about MO's and ingame news.
Also my first proper attempt at code commenting.
Written in one night. Expect bugs. Probably.

Requirements:
    -pygame
    -requests
    -pillow
    -pystray
    -desktop_notifier
    
By Joe J / Wider 2024
Started: 10:07PM 22/11/2024
V1 Finished: 01:26AM 23/11/2024
"""

import os  # for interacting with the operating system
import pathlib  # for handling file paths
import pygame  # for playing sounds
import requests  # for HTTP requesting from the endpoints
import webbrowser  # to open URLs in the browser
import asyncio  # to handle asynchronous tasks
import threading  # multiple threads
from PIL import Image  # for image handling
import pystray  # tray icon for closing
from desktop_notifier import DesktopNotifier  # for desktop notifications

# empty notifier var for later initiating
notifier = ""

# cached values for comparison
cachedMO = {"id32": 8008135}
cachedN = {"id": 8008135}
firsttime = True

debug = False

# Endpoints
if debug == False:
    endpoint_dict = {
    "mos": "https://helldiverstrainingmanual.com/api/v1/war/major-orders",  # Major Orders
    "ign": "https://helldiverstrainingmanual.com/api/v1/war/news",  # In Game News
    }
else:
    endpoint_dict = { # debug version of the dictionary. connects to a flask api at 127.0.0.1:5000, check github for .py
    "mos": "http://localhost:5000/major-orders",  # Major Orders
    "ign": "http://localhost:5000/news",  # In Game News
    }

def tray():
    """
    I stole this function from GeeksForGeeks.
    I admit it.
    """
    image = Image.open("helldivers.png")
    def after_click(icon, query):
        if str(query) == "Exit":
            os._exit(1)
    
    
    icon = pystray.Icon("HWT", image, "HD2 War Tracker", 
                        menu=pystray.Menu(
        pystray.MenuItem("Exit", after_click)))
    
    icon.run()

def init():
    global notifier
    if not os.path.exists("notification.wav"):
        try:
            print(f"Downloading notification sound from github...")
            
            response = requests.get("https://github.com/j-jagger/hd2-desktop-tracker/raw/refs/heads/main/resources/notification.wav")
            response.raise_for_status()
            
            with open("notification.wav", 'wb') as f:
                f.write(response.content)
            print("Download complete!")
        except:
            print("Error downloading resources.")
    if not os.path.exists("helldivers.png"):
        try:
            print(f"Downloading HD2 icon from github...")
            response = requests.get("https://github.com/j-jagger/hd2-desktop-tracker/blob/main/resources/helldivers.png?raw=true")
            response.raise_for_status()
            with open("helldivers.png", 'wb') as f:
                f.write(response.content)
            print("Download complete!")
        except:
            exit("Error downloading resources.")
    try:
        icon_path = pathlib.Path("helldivers.png").resolve()
        notifier = DesktopNotifier(app_name="Helldivers 2 War Tracker", app_icon=icon_path)
    except Exception as e:
        exit()


# Function to fetch API data
def get_api(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Ensure we catch HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching API data from {url}: {e}")
        return []




# Main asynchronous loop
async def main_loop():
    global cachedMO, cachedN, firsttime, notifier

    while True:
        # Fetch data from endpoints
        major_orders = get_api(endpoint_dict.get("mos"))
        news = get_api(endpoint_dict.get("ign"))

        # News checker
        if isinstance(news, list) and len(news) > 0:
            first_news_item = news[0]
            
            if "id" in first_news_item and first_news_item["id"] != cachedN["id"]:
                
                cachedN["id"] = first_news_item["id"]
                msg = first_news_item.get('message', 'Something went wrong getting this news article.. Bollocks.')
                await notifier.send(
                    title="Helldivers 2 - News Updated",
                    message=f"{msg}",
                )

        # Major Order checker
        if isinstance(major_orders, list) and len(major_orders) > 0:
            first_mo_item = major_orders[0]
            
            if "id32" in first_mo_item and first_mo_item["id32"] != cachedMO["id32"]:
                cachedMO["id32"] = first_mo_item["id32"]
                first_mo_item = first_mo_item["setting"]
                title = first_mo_item.get('overrideTitle')
                desc = first_mo_item.get('overrideBrief')
                if title != "MAJOR ORDER":
                    title = title
                else:
                    title = "" # if the title isn't unique, we don't need to see it. semi-flexible for future non-"MAJOR ORDER" titles.
                await notifier.send(
                    title="Helldivers 2 - Major Order Updated",
                    message=f"{title}\n{desc}",
                    on_clicked=lambda:webbrowser.open("https://helldiverscompanion.com/#map+orders"),
                )
                
                if not firsttime: # program shows news and mo on startup, so we don't really want a loud helldivers victory sound playing on boot.
                    try:
                        pygame.mixer.init()
                        pygame.mixer.music.load("notification.wav")
                        pygame.mixer.music.play()

                        while pygame.mixer.music.get_busy():
                            await asyncio.sleep(0.1)
                    except: 
                        print("[ERROR] Failed to play major order sound.")
                if firsttime:
                    firsttime = False
        await asyncio.sleep(10)



if __name__ == "__main__":
    init()
    threading.Thread(target=tray).start()
    asyncio.run(main_loop())

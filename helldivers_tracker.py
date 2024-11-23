try:
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

    VERSION LOG
        V1 Started: 10:07PM 22/11/2024
        V1 Finished: 01:26AM 23/11/2024

        V1.1 Started: 7:51AM 23/11/2024
        V1.1 Finished: 2:56PM 23/11/2024
    """

    import os  # for interacting with the operating system
    import json # for user configurations
    import pathlib  # for handling file paths
    import sys # systuff
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # hides pygame welcome prompt
    import pygame  # for playing sounds
    import math
    from pygame import gfxdraw
    import requests  # for HTTP requesting from the endpoints
    import webbrowser  # to open URLs in the browser
    import asyncio  # to handle async tasks
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



    def options_win():
        WIDTH, HEIGHT = 400, 350  # increased height for better spacing
        SUPER_EARTH_BLUE, DEMOCRACY_GOLD, DARK_GRAY = (0, 149, 237), (255, 215, 0), (20, 20, 25)
        MILITARY_GREEN, WHITE, RED, GREEN, BRIGHT_BLUE = (75, 105, 47), (255, 255, 255), (255, 50, 50), (50, 255, 50), (0, 174, 255)
        
        pygame.init()
        screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Helldivers 2 Desktop Tracker")
        title_font, header_font, body_font = pygame.font.Font(None, 32), pygame.font.Font(None, 24), pygame.font.Font(None, 18)

        try:
            with open("settings.json", "r") as file: config = json.load(file)
        except FileNotFoundError: config = {"seconds_between_refreshes": 10, "play_major_order_sound": True}

        refresh_value, sound_enabled, input_active = str(config['seconds_between_refreshes']), config['play_major_order_sound'], False
        box_width, box_height, box_x = 140, 30, (WIDTH - 140) // 2
        refresh_box = pygame.Rect(box_x, 130, box_width - 50, box_height)
        up_arrow = pygame.Rect(box_x + box_width - 45, 130, 25, box_height//2)
        down_arrow = pygame.Rect(box_x + box_width - 45, 130 + box_height//2, 25, box_height//2) 
        toggle_button = pygame.Rect(box_x - 30, 190, box_width + 60, box_height) 
        save_button = pygame.Rect((WIDTH - 120) // 2, 260, 120, 30)  # Moved down
        button_animations = {'save': 0, 'toggle': 0, 'up': 0, 'down': 0}
        feedback_message, feedback_timer = "", 0

        def draw_military_border(surface, rect, color, width=2):
            corner_size = 8
            pygame.draw.rect(surface, color, rect, width)
            for x, y in [(rect.topleft, (1, 1)), (rect.topright, (-1, 1)), (rect.bottomleft, (1, -1)), (rect.bottomright, (-1, -1))]:
                pygame.draw.line(surface, color, (x[0], x[1] + corner_size * y[1]), (x[0], x[1]), width)
                pygame.draw.line(surface, color, (x[0] + corner_size * y[0], x[1]), (x[0], x[1]), width)

        def draw_arrow(surface, rect, direction, color, pressed=False):
            color = tuple(max(0, c - 50) for c in color) if pressed else color
            points = [(rect.centerx - 6, rect.centery + 3), (rect.centerx + 6, rect.centery + 3), (rect.centerx, rect.centery - 3)] if direction == 'up' else [(rect.centerx - 6, rect.centery - 3), (rect.centerx + 6, rect.centery - 3), (rect.centerx, rect.centery + 3)]
            pygame.draw.polygon(surface, color, points)

        running = True
        clock = pygame.time.Clock()
        temp_value = ""

        while running:
            screen.fill(DARK_GRAY)
            current_time = pygame.time.get_ticks()
            for key in button_animations: button_animations[key] = max(0, button_animations[key] - 1) if button_animations[key] > 0 else 0
            
            title_color = [max(0, min(255, c - abs(math.sin(current_time / 1000)) * 30)) for c in list(DEMOCRACY_GOLD)]
            pygame.draw.rect(screen, MILITARY_GREEN, (0, 0, WIDTH, 80))
            draw_military_border(screen, pygame.Rect(0, 0, WIDTH, 80), SUPER_EARTH_BLUE, 2)
            
            for surf, pos in [(title_font.render("SUPER EARTH COMMAND", True, title_color), ((WIDTH - title_font.size("SUPER EARTH COMMAND")[0]) // 2, 20)),
                            (header_font.render("HD2DT Settings", True, WHITE), ((WIDTH - header_font.size("HD2DT Settings")[0]) // 2, 50)),
                            (body_font.render("Refresh Interval (Seconds)", True, WHITE), ((WIDTH - body_font.size("Refresh Interval (Seconds)")[0]) // 2, refresh_box.top - 20))]:
                screen.blit(surf, pos)

            if input_active:
                focus_rect = refresh_box.inflate(4, 4)
                pygame.draw.rect(screen, BRIGHT_BLUE, focus_rect, 1)
                
            pygame.draw.rect(screen, DARK_GRAY, refresh_box)
            draw_military_border(screen, refresh_box, BRIGHT_BLUE if input_active else SUPER_EARTH_BLUE, 2)
            value_text = body_font.render(temp_value if input_active and temp_value else refresh_value, True, WHITE)
            screen.blit(value_text, value_text.get_rect(center=refresh_box.center))
            
            draw_arrow(screen, up_arrow, 'up', SUPER_EARTH_BLUE, button_animations['up'] > 0)
            draw_arrow(screen, down_arrow, 'down', SUPER_EARTH_BLUE, button_animations['down'] > 0)
            toggle_text = body_font.render(f"MAJOR ORDER SOUND: {'ENABLED' if sound_enabled else 'DISABLED'}", True, WHITE)
            text_width = toggle_text.get_width()
            button_padding = 20 
            toggle_button_width = text_width + button_padding
            toggle_button_x = (WIDTH - toggle_button_width) // 2
            toggle_button = pygame.Rect(toggle_button_x, 170, toggle_button_width, box_height)

            # Draw the button
            pygame.draw.rect(screen, MILITARY_GREEN, toggle_button)
            draw_military_border(screen, toggle_button, GREEN if sound_enabled else RED, 2)

            # Draw the text
            screen.blit(toggle_text, toggle_text.get_rect(center=toggle_button.center))




            pygame.draw.rect(screen, MILITARY_GREEN, save_button)
            draw_military_border(screen, save_button, DEMOCRACY_GOLD, 2)
            save_text = header_font.render("DEPLOY", True, WHITE)
            screen.blit(save_text, save_text.get_rect(center=save_button.center))
            
            if feedback_timer > 0:
                feedback_timer -= 1
                feedback_surf = body_font.render(feedback_message, True, WHITE)
                feedback_surf.set_alpha(min(255, feedback_timer * 4))
                screen.blit(feedback_surf, feedback_surf.get_rect(centerx=WIDTH // 2, top=save_button.bottom + 10))

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    input_active = refresh_box.collidepoint(event.pos)
                    temp_value = refresh_value if input_active else ""
                    
                    if up_arrow.collidepoint(event.pos):
                        try: refresh_value = str(min(999, int(refresh_value) + 1))  # Increased max value
                        except ValueError: refresh_value = "10"
                        button_animations['up'] = 5
                    elif down_arrow.collidepoint(event.pos):
                        try: refresh_value = str(max(5, int(refresh_value) - 1))
                        except ValueError: refresh_value = "10"
                        button_animations['down'] = 5
                    elif toggle_button.collidepoint(event.pos):
                        sound_enabled = not sound_enabled
                        feedback_message, feedback_timer = f"Major Order Sound {'Enabled' if sound_enabled else 'Disabled'}", 60
                    elif save_button.collidepoint(event.pos):
                        try:
                            refresh_int = int(refresh_value)
                            if 5 <= refresh_int <= 999:  # Increased max value
                                config.update({"seconds_between_refreshes": refresh_int, "play_major_order_sound": sound_enabled})
                                json.dump(config, open("settings.json", "w"), indent=4)
                                os.execl(sys.executable, sys.executable, *sys.argv)
                                os._exit(1)
                                feedback_message, feedback_timer = "Settings Deployed Successfully!", 60
                            else: feedback_message, feedback_timer = "Error: Interval must be between 5-999", 60
                        except ValueError: feedback_message, feedback_timer = "Error: Invalid refresh value", 60
                
                elif event.type == pygame.KEYDOWN and input_active:
                    if event.key == pygame.K_RETURN:
                        try:
                            if temp_value and 5 <= int(temp_value) <= 9999999999:  # max value
                                refresh_value = temp_value
                            temp_value = ""
                            input_active = False
                        except ValueError: pass
                    elif event.key == pygame.K_BACKSPACE: temp_value = temp_value[:-1]
                    elif event.unicode.isdigit() and len(temp_value) < 10: temp_value += event.unicode  # allow 10 digits

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()



    def tray():
        image = Image.open("helldivers.png")
        def after_click(icon, query):
            if str(query) == "Exit":
                os._exit(1)
            if str(query) == "Options":
                options_win()
            
        icon = pystray.Icon(
            "HWT",
            image,
            "HD2 War Tracker",
            menu=pystray.Menu(
                pystray.MenuItem("Exit", after_click),
                pystray.MenuItem("Options", after_click)
            )
        )

        icon.run()

    def init():
        global notifier
        if not os.path.exists("settings.json"):
            try:
                print("No settings.json found.")

                with open("settings.json", 'wb') as f:
                    f.write(b"""{
    "seconds_between_refreshes": 10,
    "play_major_order_sound": true
    }""")
                print("Created settings.json.")
            except Exception as e:
                print(f"Error creating settings.json.\n{e}")
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
            return




    # Main asynchronous loop
    async def main_loop():
        global cachedMO, cachedN, firsttime, notifier
        with open("settings.json","r") as f:
            config = json.loads(f.read())
        waittime = config['seconds_between_refreshes']
        playsound = config['play_major_order_sound']
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
                    
                    if not firsttime:
                        if playsound:
                            try:
                                pygame.mixer.init() # pygame stuff to play the MO sound
                                pygame.mixer.music.load("notification.wav")
                                pygame.mixer.music.play()

                                while pygame.mixer.music.get_busy():
                                    await asyncio.sleep(0.1)
                            except: 
                                print("[ERROR] Failed to play major order sound.")
                    if firsttime:
                        firsttime = False
            await asyncio.sleep(waittime)



    if __name__ == "__main__":
        init()
        threading.Thread(target=tray).start()
        asyncio.run(main_loop())
except Exception as e:
    print(f"[FATAL] UNHANDLED EXCEPTION! QUITTING!\n{e}")
    os._exit(1)
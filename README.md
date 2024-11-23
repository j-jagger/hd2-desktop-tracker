<p align="center">
<img src="https://github.com/user-attachments/assets/1684a804-78e2-4396-87fe-aeb82d2b170b"></img>

<br>
<br>
<br>
<sup><sub>HD2-Desktop-Tracker and J-Jagger are not related / endorsed / owned by Arrowhead Studios. This is purely fan-made content.</sub></sup>
<h1 align="center">Helldivers 2 Desktop Tracker</h1>
<h3 align="center">Keep track of managed democracy.</h3>
<p align="center">
  This program runs in the background and sends the user a push notification when new HD2 ingame news and major orders are released!
  <br>
  !! Self-building is recommended. !!
  <br>
  <br>
  Thank you to https://helldiverstrainingmanual.com/ for the API endpoints. This wouldn'tve been possible without them.
  <br>
  <br>
  Every 10 seconds, HD2DT sends 2 api requests. One to the HD2 Major Order API and another to the news API. It stores their JSON IDs, and if the ID varies from the last api request, it gives the user a push notification. It also plays a sound if it's a major order!
  <br>
  <br>
  <img src="https://github.com/user-attachments/assets/62b6e25d-bc55-4fd8-bdfb-13cf88c7b465"> </img>
  <img src="https://github.com/user-attachments/assets/0865b223-bd20-403e-b188-7df31fd56ae8"></img>

  
</p>
<h1 align="center">Technical Gargon</h1>
</p>

<h2>Building</h2>
<br>
I recommend using PyArmor for windows builds. It obfuscates the .py before turning it into an .exe with PyInstaller.
<br>
Use the following command.
<br>
<br>

```pyarmor-7 pack -e "--noconfirm --onefile --windowed --icon helldivers.ico --hidden-import desktop_notifier.resources" helldivers_tracker.py```
<br>
"helldivers.ico" can be found in the resources folder in this repo.


<h2>Testing</h2>
<br>
Alongside the main program, this repo contains a debug API for testing, built with Flask.
This API mimics the HD2 API, and is for general testing purposes.
To toggle usage of this API over the normal one, look for "debug = False" around line 39. Set it to True.
<br>
<br>
 <img src="https://github.com/user-attachments/assets/aa68597d-ea08-45fe-9e22-ee3fbf6f3d1c"> </img>


Have fun dealing with threads and asyncio!

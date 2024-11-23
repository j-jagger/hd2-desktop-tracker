import os
import sys
import requests
import ctypes
import tkinter as tk
import winreg
from tkinter import simpledialog, messagebox

def is_elevated():
    """Check if the script is running with elevated privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        messagebox.showerror("HD2DT", f"Error checking elevation status.\n{e}")
        sys.exit(1)

def elevate():
    """Re-run the script with elevated privileges."""
    try:
        script = sys.argv[0]
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, script, None, 1)
        sys.exit()
    except Exception as e:
        messagebox.showerror("HD2DT", f"Failed to elevate privileges.\n{e}")
        sys.exit(1)

def install():
    """Install the application."""
    if not is_elevated():
        elevate()

    # Create the Tkinter root window (hidden)
    root = tk.Tk()
    root.withdraw()

    # Ask the user for the install path
    pf = simpledialog.askstring(
        "HD2DT", "Please insert a path for installation. Leave blank for C:/Program Files."
    )

    # Determine the installation directory
    if not pf or pf.strip() == "":
        pfdir = os.environ.get('PROGRAMFILES', 'C:/Program Files')
        print("User requested Program Files installation.")
    else:
        if not os.path.isabs(pf) or not os.path.exists(os.path.dirname(pf)):
            messagebox.showerror("HD2DT", "Invalid path. Please ensure it exists and is absolute. Installer will exit.")
            return
        pfdir = pf.strip()
        print("User requested custom installation path.")

    # Confirm installation
    messagebox.showinfo(
        "HD2DT", "Press OK to begin installing. This may take some time depending on your internet speed."
    )

    installdir = os.path.join(pfdir, "HD2DT")
    try:
        os.makedirs(installdir, exist_ok=True)
    except Exception as e:
        messagebox.showerror("HD2DT", f"Failed to create installation directory.\n{e}")
        return

    print(f"Installing to: {installdir}")

    # Download and save the executable
    file_path = os.path.join(installdir, "helldivers_tracker.exe")
    try:
        url = "https://github.com/j-jagger/hd2-desktop-tracker/releases/download/Main/helldivers_tracker.exe"
        for attempt in range(3):  # Retry up to 3 times
            try:
                prog = requests.get(url, timeout=30)
                prog.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(prog.content)
                print("Download successful.")
                break
            except requests.RequestException as e:
                if attempt < 2:
                    print(f"Download failed. Retrying... ({attempt + 1}/3)")
                else:
                    raise e
    except Exception as e:
        messagebox.showerror("HD2DT", f"Error downloading or saving the binary.\n{e}")
        return

    # Add to registry for startup
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "HD2DT", 0, winreg.REG_SZ, file_path)
    except Exception as e:
        messagebox.showerror("HD2DT", f"Failed to add to startup registry.\n{e}")
        return

    # Confirm installation and offer to start
    choice = messagebox.askyesno("HD2DT", f"Installed successfully at {installdir}.\nStart now?")
    if choice:
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "open", file_path, None, None, 1)
        except Exception as e:
            messagebox.showerror("HD2DT", f"Failed to start the application.\n{e}")

if __name__ == "__main__":
    install()

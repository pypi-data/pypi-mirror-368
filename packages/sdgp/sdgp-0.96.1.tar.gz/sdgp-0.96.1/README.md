[[Installation(Recommended)](#Installation)] | | [[sd-get-prompt (Native C Version)](https://github.com/ScrapWare/sd-get-prompt)]

---
# SDGP (Stable-Diffusion-Get-Prompt)

Easy display for Stable Diffusion tEXt(Meitu iTXt) Exif data. Anyone can copy and paste from GTK+ dialog.

Sample picture is Japanese language but everybodは can understanding through SD(Stable Diffusion) icon picture on right click menu.

Showing Creation AI Configuration Info.

-----
# Usage (Python Module)

1. Use as Library

```markdown
from sdgp import sdgp

# return dict of iTXt contents
dict = sdgp(path)
```

2. commandline

```markdown
python -m sdgp -i PATH

or use TextView

python -m sdgp -i PATH --textview

```
-----
# Usage (Right Clickable)

How to use?

1. Run to python -m sdgp -i *PATH*

-----
## KDE

1. create .desktop file.
2. place to .kde/share/kde4/services/ServiceMenus/

````markdown
[Desktop Entry]  
Version=1.0  
Type=Application  
Name=sd-get-prompt  
Comment=Get tEXt parametor  
Exec=python -m sdgp -i %f
ServiceTypes=KonqPopupMenu/Plugin  
MimeType=image/png  
Icon=applications-graphics  
Path=  
Terminal=false  
StartupNotify=true  
````

& Apply to KDE Dolphin service dir and good changes.

-----
## XFce

1. Add right-click action for thunar(python -m sdgp -i %f)

![sample](https://raw.githubusercontent.com/ScrapWareOrg/sdgp/refs/heads/main/xfce-sample.png)

-----
## Others

for Other wm(window Manager) and file manager.

1. Should be reading your file manager manpages. May be could under run Linux Mint and other Cinnamon distribution and Gnome Nautilus, measure file manager too.

-----
## Microsoft Windows

GLib and GTK+ needed(MingW, CYgwin, Others).

-----
# <a id="Installation" name="Installation">Installation</a>

This is a desktop application built with Python using the GTK3 toolkit. It leverages **PyGObject** (the Python bindings for GTK and other GNOME libraries) to create a native user interface.

-----
## Features

* **Modern GTK3 Interface:** Utilizes the latest GTK3 features for a contemporary look and feel.
* **Pythonic Development:** Written entirely in Python, making it easy to read, understand, and extend.
* **Pango Text Rendering:** Supports rich text formatting using Pango attributes for enhanced text presentation (e.g., bold, italics, colors, varying font sizes).
* **(Add more specific features of your application here, e.g., "File management," "Data visualization," etc.)**

## Requirements

Before running the application, ensure you have the necessary dependencies installed.

* Python 3.x
* GTK3 Development Files
* PyGObject

### Installation on Linux (Debian/Ubuntu)

1.  **Update your package list:**
    ```bash
    sudo apt update
    ```
2.  **Install Python 3, GTK3 development files, and PyGObject:**
    ```bash
    sudo apt install python3 python3-venv gir1.2-gtk-3.0 python3-gi
    ```
    `gir1.2-gtk-3.0` provides the necessary GObject Introspection data for GTK3, and `python3-gi` is the Python binding itself.

### Installation on Windows (using MSYS2)

For Windows, using [MSYS2](https://www.msys2.org/) is the recommended way to get a working GTK3 development environment.

1.  **Download and install MSYS2** from the official website.
2.  **Open an MSYS2 UCRT64 (or MINGW64) terminal.**
3.  **Update the package database:**
    ```bash
    pacman -Syu
    ```
    (You might need to run this multiple times and restart the terminal.)
4.  **Install Python, pip, GTK3, and PyGObject:**
    ```bash
    pacman -S python3 python3-pip mingw-w64-ucrt-x86_64-gtk3 mingw-w64-ucrt-x86_64-python-gobject
    ```
    (Adjust `ucrt` to `mingw` if you are using the MINGW64 terminal.)

### Installation on macOS (using Homebrew)

1.  **Install Homebrew** if you haven't already:
    ```bash
    /bin/bash -c "$(curl -fsSL [https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh](https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh))"
    ```
2.  **Install GTK3:**
    ```bash
    brew install gtk+3
    ```
3.  **Install PyGObject via pip:**
    ```bash
    pip3 install PyGObject
    ```

## Setup and Running

It's highly recommended to use a **Python virtual environment** for dependency management.

1.  **Create a virtual environment:**
    When working with GTK and PyGObject, it's crucial to create the virtual environment with access to system site-packages so it can find the installed GTK libraries.
    ```bash
    python3 -m venv venv --system-site-packages
    ```
    (You can replace `venv` with your preferred virtual environment name.)

2.  **Activate the virtual environment:**
    ```bash
    source venv/bin/activate
    ```
    On Windows (MSYS2):
    ```bash
    source venv/bin/activate
    ```
    (Or `.\venv\Scripts\activate` in Command Prompt/PowerShell if not using MSYS2.)

3.  **Install project dependencies:**
    Once the virtual environment is active, install any specific Python dependencies listed in `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    ```
    (Ensure `requirements.txt` is in your project's root directory.)

4.  **Run the application:**
    ```bash
    python your_main_script.py
    ```
    (Replace `your_main_script.py` with the actual name of your application's main Python file.)

## Contribution (Optional)

If you'd like to contribute to this project, please feel free to fork the repository, make your changes, and submit a pull request.

## License (Optional)

This project is licensed under the [Resist-Psychiatry Declaration License & GNU GPL VERSION 3] - see the [LICENSE.RPTv1](LICENSE.RPTv1) and [LICENSE.GPLv3](LICENSE.GPLv3) file for details.

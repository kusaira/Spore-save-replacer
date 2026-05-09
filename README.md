# Spore Save Replacer

Warning: this project was vibe-coded, so the code may be a little rough around the edges.

Releases: [https://github.com/kusaira/Spore-save-replacer/releases](https://github.com/kusaira/Spore-save-replacer/releases)

Video demo: [https://youtu.be/jfPTdSFS8dk](https://youtu.be/jfPTdSFS8dk)

Download the latest beta build here:
[spore_replacer.exe](https://github.com/kusaira/Spore-save-replacer/releases/download/v1.0.0-beta/spore_replacer.exe)

Simple Windows GUI app built with Python and `tkinter`.

It copies everything from a local `Spore` folder next to the app into the current Windows user's roaming Spore folder:

```text
C:\Users\<username>\AppData\Roaming\Spore
```

If the destination folder does not exist, the app creates it automatically. If it already exists, its contents are fully replaced by the contents of the local `Spore` folder.
The main window also has an optional checkbox to clear `My Spore Creations` in `Documents` or `OneDrive\Documents`.

## Auto Click Setup

The `Auto Click Setup` button helps reset and refresh the creature selection so you can quickly look for the creature you need during a run setup.

It performs two left-clicks from a 1920x1080 reference screen and scales them to your current resolution. Open Spore on the correct creature selection/setup screen before using it.

While the app is running, pressing `F11` from any active window starts the same auto-click sequence without the confirmation popup.

## Folder Layout

Keep a `Spore` folder next to `spore_replacer.py` or the built `.exe`:

```text
program-folder/
  spore_replacer.py
  spore_icon.ico
  Spore/
    ...
```

After building the executable, use this layout:

```text
program-folder/
  spore_replacer.exe
  Spore/
    ...
```

## Run from Python

Python 3.8+ is required.

```powershell
python spore_replacer.py
```

## Build a .exe with PyInstaller

Install PyInstaller:

```powershell
python -m pip install pyinstaller
```

Build a single-file executable:

```powershell
pyinstaller --onefile --windowed --icon spore_icon.ico --add-data "spore_icon.ico;." --name spore_replacer spore_replacer.py
```

The finished file will be here:

```text
dist\spore_replacer.exe
```

Copy the `Spore` folder next to `dist\spore_replacer.exe` so the app can find the save files to replace.

## "Do not ask again"

If the user clicks `Yes` and checks `Do not ask again`, the setting is saved here:

```text
C:\Users\<username>\AppData\Roaming\SporeSaveReplacer\settings.json
```

On the next launch, the warning dialog is skipped.

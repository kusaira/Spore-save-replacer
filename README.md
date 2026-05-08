# Spore Save Replacer

Releases: [https://github.com/kusaira/Spore-save-replacer/releases](https://github.com/kusaira/Spore-save-replacer/releases)

Download the latest beta build here:
[spore_replacer.exe](https://github.com/kusaira/Spore-save-replacer/releases/download/v0.2.0-beta/spore_replacer.exe)

Simple Windows GUI app built with Python and `tkinter`.

It copies everything from a local `Spore` folder next to the app into the current Windows user's roaming Spore folder:

```text
C:\Users\<username>\AppData\Roaming\Spore
```

If the destination folder does not exist, the app creates it automatically. If it already exists, its contents are fully replaced by the contents of the local `Spore` folder.

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

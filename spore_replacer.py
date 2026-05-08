import getpass
import json
import os
import shutil
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox


APP_NAME = "Spore Save Replacer"
LOCAL_SPORE_FOLDER = "Spore"
SETTINGS_FOLDER = "SporeSaveReplacer"
SETTINGS_FILE = "settings.json"


def get_program_folder() -> Path:
    """Return the folder containing this script or the built executable."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def get_settings_path() -> Path:
    """Store settings in the current user's roaming AppData folder."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        base_folder = Path(appdata)
    else:
        base_folder = Path.home() / "AppData" / "Roaming"

    return base_folder / SETTINGS_FOLDER / SETTINGS_FILE


def load_settings() -> dict:
    """Load saved settings. If the file is missing or broken, use defaults."""
    settings_path = get_settings_path()

    try:
        with settings_path.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        return {"skip_warning": False}
    except (json.JSONDecodeError, OSError):
        return {"skip_warning": False}

    return {"skip_warning": bool(data.get("skip_warning", False))}


def save_settings(settings: dict) -> None:
    """Save settings to disk so they persist between launches."""
    settings_path = get_settings_path()
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    with settings_path.open("w", encoding="utf-8") as file:
        json.dump(settings, file, indent=2)


def get_target_spore_folder() -> Path:
    """Build the current user's roaming Spore folder."""
    appdata = os.environ.get("APPDATA")
    if appdata:
        return Path(appdata) / "Spore"

    username = getpass.getuser()
    return Path("C:/Users") / username / "AppData" / "Roaming" / "Spore"


def clear_folder(folder: Path) -> None:
    """Remove all existing items from a folder while keeping the folder itself."""
    for item in folder.iterdir():
        if item.is_dir() and not item.is_symlink():
            shutil.rmtree(item)
        else:
            item.unlink()


def copy_spore_folder(source_folder: Path, target_folder: Path) -> None:
    """Fully replace the target folder contents with local Spore contents."""
    if source_folder.resolve() == target_folder.resolve():
        raise ValueError("Source and target folders are the same.")

    target_folder.mkdir(parents=True, exist_ok=True)
    clear_folder(target_folder)

    for item in source_folder.iterdir():
        destination = target_folder / item.name

        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination)


class ConfirmDialog(tk.Toplevel):
    """A small modal confirmation window with a persistent-choice checkbox."""

    def __init__(self, parent: tk.Tk):
        super().__init__(parent)

        self.result = False
        self.do_not_ask_again = tk.BooleanVar(value=False)

        self.title("Warning")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        container = tk.Frame(self, padx=18, pady=16)
        container.pack(fill="both", expand=True)

        message = tk.Label(
            container,
            text="ARE YOU SURE? THIS WILL OVERWRITE ALL YOUR SAVES",
            wraplength=320,
            justify="center",
        )
        message.pack(pady=(0, 12))

        checkbox = tk.Checkbutton(
            container,
            text="Do not ask again",
            variable=self.do_not_ask_again,
        )
        checkbox.pack(anchor="w", pady=(0, 14))

        buttons = tk.Frame(container)
        buttons.pack(fill="x")

        no_button = tk.Button(buttons, text="No", width=10, command=self.on_no)
        no_button.pack(side="right", padx=(8, 0))

        yes_button = tk.Button(buttons, text="Yes", width=10, command=self.on_yes)
        yes_button.pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self.on_no)
        self.bind("<Escape>", lambda _event: self.on_no())
        self.bind("<Return>", lambda _event: self.on_yes())

        self.update_idletasks()
        self.center_on_parent(parent)
        yes_button.focus_set()

        parent.wait_window(self)

    def center_on_parent(self, parent: tk.Tk) -> None:
        """Place the dialog near the center of the main window."""
        parent.update_idletasks()

        width = self.winfo_width()
        height = self.winfo_height()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)

        self.geometry(f"+{x}+{y}")

    def on_yes(self) -> None:
        self.result = True
        self.destroy()

    def on_no(self) -> None:
        self.result = False
        self.destroy()


class SporeReplacerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.settings = load_settings()

        self.root.title(APP_NAME)
        self.root.resizable(False, False)

        self.build_ui()
        self.center_window()

    def build_ui(self) -> None:
        frame = tk.Frame(self.root, padx=24, pady=22)
        frame.pack(fill="both", expand=True)

        replace_button = tk.Button(
            frame,
            text="Replace",
            width=16,
            command=self.on_replace,
        )
        replace_button.pack(pady=(0, 10))

        cancel_button = tk.Button(
            frame,
            text="Cancel",
            width=16,
            command=self.root.destroy,
        )
        cancel_button.pack()

    def center_window(self) -> None:
        self.root.update_idletasks()

        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.root.geometry(f"+{x}+{y}")

    def on_replace(self) -> None:
        if not self.settings.get("skip_warning", False):
            dialog = ConfirmDialog(self.root)

            if not dialog.result:
                return

            if dialog.do_not_ask_again.get():
                self.settings["skip_warning"] = True
                try:
                    save_settings(self.settings)
                except PermissionError:
                    messagebox.showerror(
                        "Access error",
                        "Could not save settings because access was denied.",
                    )
                except OSError as error:
                    messagebox.showerror(
                        "Settings error",
                        f"Could not save settings:\n{error}",
                    )

        self.replace_saves()

    def replace_saves(self) -> None:
        program_folder = get_program_folder()
        source_folder = program_folder / LOCAL_SPORE_FOLDER
        target_folder = get_target_spore_folder()

        if not source_folder.is_dir():
            messagebox.showerror(
                "Missing folder",
                f'The folder "{LOCAL_SPORE_FOLDER}" was not found next to the program.',
            )
            return

        try:
            copy_spore_folder(source_folder, target_folder)
        except PermissionError as error:
            messagebox.showerror(
                "Access error",
                f"Access denied while copying saves:\n{error}",
            )
            return
        except OSError as error:
            messagebox.showerror(
                "Copy error",
                f"Could not copy saves:\n{error}",
            )
            return
        except Exception as error:
            messagebox.showerror(
                "Unexpected error",
                f"An unexpected error occurred:\n{error}",
            )
            return

        messagebox.showinfo("Confirmed", "Confirmed")


def main() -> None:
    root = tk.Tk()
    SporeReplacerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

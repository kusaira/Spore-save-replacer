import getpass
import json
import os
import shutil
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox


APP_NAME = "Spore Save Replacer"
APP_VERSION = "v1.0.0 Beta"
LOCAL_SPORE_FOLDER = "Spore"
SETTINGS_FOLDER = "SporeSaveReplacer"
SETTINGS_FILE = "settings.json"
ICON_FILE = "spore_icon.ico"

WINDOW_BG = "#eef4fb"
PANEL_BG = "#ffffff"
HEADER_BG = "#1d4ed8"
HEADER_FG = "#ffffff"
TEXT_FG = "#0f172a"
MUTED_FG = "#5b6472"
BORDER_FG = "#d9e2ee"
PRIMARY_BG = "#2563eb"
PRIMARY_HOVER = "#1d4ed8"
PRIMARY_ACTIVE = "#1e40af"
PRIMARY_FG = "#ffffff"
SECONDARY_BG = "#e2e8f0"
SECONDARY_HOVER = "#cbd5e1"
SECONDARY_ACTIVE = "#94a3b8"
SECONDARY_FG = "#0f172a"
DANGER_BG = "#dc2626"
DANGER_HOVER = "#b91c1c"
DANGER_ACTIVE = "#991b1b"
DANGER_FG = "#ffffff"

TITLE_FONT = ("Segoe UI", 17, "bold")
HEADER_FONT = ("Segoe UI", 15, "bold")
BODY_FONT = ("Segoe UI", 10)
BODY_BOLD_FONT = ("Segoe UI", 10, "bold")
BUTTON_FONT = ("Segoe UI", 10, "bold")


def get_program_folder() -> Path:
    """Return the folder containing this script or the built executable."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def resource_path(name: str) -> Path:
    """Resolve a file from either the source folder or the PyInstaller bundle."""
    bundle_root = Path(getattr(sys, "_MEIPASS", get_program_folder()))
    return bundle_root / name


def apply_window_icon(window: tk.Misc) -> None:
    """Set the window icon if the icon file is available."""
    icon_path = resource_path(ICON_FILE)
    if not icon_path.is_file():
        return

    try:
        window.iconbitmap(default=str(icon_path))
    except tk.TclError:
        pass


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


def get_documents_roots() -> list[Path]:
    """Return the most likely Documents roots for the current Windows user."""
    roots: list[Path] = []

    if os.name == "nt":
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
            ) as key:
                personal, _ = winreg.QueryValueEx(key, "Personal")
            roots.append(Path(os.path.expandvars(personal)))
        except (OSError, ValueError, TypeError):
            pass

    home = Path.home()
    roots.extend(
        [
            home / "Documents",
            home / "OneDrive" / "Documents",
        ]
    )

    one_drive = os.environ.get("OneDrive")
    if one_drive:
        roots.append(Path(one_drive) / "Documents")

    unique_roots: list[Path] = []
    seen: set[str] = set()
    for root in roots:
        resolved = str(root)
        if resolved not in seen:
            seen.add(resolved)
            unique_roots.append(root)

    return unique_roots


def get_my_spore_creations_paths() -> list[Path]:
    """Return the My Spore Creations folders that should be deleted."""
    return [root / "My Spore Creations" for root in get_documents_roots()]


def clear_folder(folder: Path) -> None:
    """Remove all existing items from a folder while keeping the folder itself."""
    for item in folder.iterdir():
        if item.is_dir() and not item.is_symlink():
            shutil.rmtree(item)
        else:
            item.unlink()


def remove_path(path: Path) -> None:
    """Delete a file or folder even if some items are read-only."""
    if path.is_dir() and not path.is_symlink():
        shutil.rmtree(path, onerror=remove_readonly)
    else:
        path.unlink()


def remove_readonly(func, path, _exc_info):
    """Retry removing read-only files during tree deletion."""
    os.chmod(path, 0o666)
    func(path)


def clear_my_spore_creations() -> None:
    """Delete both possible My Spore Creations folders if they exist."""
    for folder in get_my_spore_creations_paths():
        if folder.exists():
            remove_path(folder)


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


def make_button(
    parent: tk.Misc,
    text: str,
    command,
    *,
    bg: str,
    hover_bg: str,
    active_bg: str,
    fg: str,
    width: int = 16,
) -> tk.Button:
    """Create a flat button with simple hover feedback."""
    button = tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        font=BUTTON_FONT,
        bg=bg,
        fg=fg,
        activebackground=active_bg,
        activeforeground=fg,
        relief="flat",
        bd=0,
        padx=12,
        pady=9,
        cursor="hand2",
        highlightthickness=0,
    )

    def on_enter(_event):
        button.configure(bg=hover_bg)

    def on_leave(_event):
        button.configure(bg=bg)

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    return button


class ConfirmDialog(tk.Toplevel):
    """A small modal confirmation window with a persistent-choice checkbox."""

    def __init__(self, parent: tk.Tk):
        super().__init__(parent)

        self.result = False
        self.do_not_ask_again = tk.BooleanVar(value=False)

        self.configure(bg=WINDOW_BG)
        self.title("Warning")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        apply_window_icon(self)

        shell = tk.Frame(self, bg=WINDOW_BG)
        shell.pack(fill="both", expand=True)

        header = tk.Frame(shell, bg=DANGER_BG, padx=18, pady=14)
        header.pack(fill="x")

        title = tk.Label(
            header,
            text="ARE YOU SURE?",
            bg=DANGER_BG,
            fg=HEADER_FG,
            font=HEADER_FONT,
        )
        title.pack(anchor="w")

        warning = tk.Label(
            header,
            text="THIS WILL DELETE EVERYTHING IN %APPDATA%\\SPORE",
            bg=DANGER_BG,
            fg="#fee2e2",
            font=BODY_FONT,
            wraplength=360,
            justify="left",
        )
        warning.pack(anchor="w", pady=(2, 0))

        impact = tk.Label(
            header,
            text="YOU WILL LOSE ALL PLANETS, CREATIONS, AND SETTINGS",
            bg=DANGER_BG,
            fg="#fee2e2",
            font=BODY_FONT,
            wraplength=360,
            justify="left",
        )
        impact.pack(anchor="w", pady=(2, 0))

        panel = tk.Frame(
            shell,
            bg=PANEL_BG,
            padx=18,
            pady=18,
            highlightbackground=BORDER_FG,
            highlightthickness=1,
        )
        panel.pack(fill="both", expand=True, padx=18, pady=18)

        checkbox = tk.Checkbutton(
            panel,
            text="Do not ask again",
            variable=self.do_not_ask_again,
            bg=PANEL_BG,
            fg=TEXT_FG,
            activebackground=PANEL_BG,
            activeforeground=TEXT_FG,
            selectcolor=PANEL_BG,
            font=BODY_FONT,
            highlightthickness=0,
            bd=0,
        )
        checkbox.pack(anchor="w", pady=(10, 16))

        buttons = tk.Frame(panel, bg=PANEL_BG)
        buttons.pack(fill="x")

        no_button = make_button(
            buttons,
            "No",
            self.on_no,
            bg=SECONDARY_BG,
            hover_bg=SECONDARY_HOVER,
            active_bg=SECONDARY_ACTIVE,
            fg=SECONDARY_FG,
            width=10,
        )
        no_button.pack(side="right", padx=(8, 0))

        yes_button = make_button(
            buttons,
            "Yes",
            self.on_yes,
            bg=DANGER_BG,
            hover_bg=DANGER_HOVER,
            active_bg=DANGER_ACTIVE,
            fg=DANGER_FG,
            width=10,
        )
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
        self.clear_creations_var = tk.BooleanVar(value=False)

        self.root.title(APP_NAME)
        self.root.configure(bg=WINDOW_BG)
        self.root.resizable(False, False)
        self.root.minsize(460, 385)
        apply_window_icon(self.root)

        self.build_ui()
        self.center_window()

    def build_ui(self) -> None:
        shell = tk.Frame(self.root, bg=WINDOW_BG)
        shell.pack(fill="both", expand=True)

        header = tk.Frame(shell, bg=HEADER_BG, padx=20, pady=18)
        header.pack(fill="x")

        title = tk.Label(
            header,
            text=APP_NAME,
            bg=HEADER_BG,
            fg=HEADER_FG,
            font=TITLE_FONT,
        )
        title.pack(anchor="w")

        version = tk.Label(
            header,
            text=APP_VERSION,
            bg=HEADER_BG,
            fg="#dbeafe",
            font=BODY_FONT,
        )
        version.pack(anchor="w", pady=(2, 0))

        body = tk.Frame(shell, bg=WINDOW_BG, padx=20, pady=20)
        body.pack(fill="both", expand=True)

        card = tk.Frame(
            body,
            bg=PANEL_BG,
            padx=18,
            pady=18,
            highlightbackground=BORDER_FG,
            highlightthickness=1,
        )
        card.pack(fill="both", expand=True)

        button_stack = tk.Frame(card, bg=PANEL_BG)
        button_stack.pack(fill="both", expand=True)

        replace_button = make_button(
            button_stack,
            "Replace",
            self.on_replace,
            bg=PRIMARY_BG,
            hover_bg=PRIMARY_HOVER,
            active_bg=PRIMARY_ACTIVE,
            fg=PRIMARY_FG,
            width=18,
        )
        replace_button.pack(fill="x", pady=(0, 12))

        cancel_button = make_button(
            button_stack,
            "Cancel",
            self.root.destroy,
            bg=SECONDARY_BG,
            hover_bg=SECONDARY_HOVER,
            active_bg=SECONDARY_ACTIVE,
            fg=SECONDARY_FG,
            width=18,
        )
        cancel_button.pack(fill="x")

        options = tk.Frame(card, bg=PANEL_BG)
        options.pack(fill="x", pady=(16, 0))

        clear_creations = tk.Checkbutton(
            options,
            text="Clear My Spore Creations",
            variable=self.clear_creations_var,
            bg=PANEL_BG,
            fg=TEXT_FG,
            activebackground=PANEL_BG,
            activeforeground=TEXT_FG,
            selectcolor=PANEL_BG,
            font=BODY_FONT,
            highlightthickness=0,
            bd=0,
        )
        clear_creations.pack(anchor="w")

        option_note = tk.Label(
            options,
            text="This deletes the entire folder from Documents or OneDrive Documents if it exists.",
            bg=PANEL_BG,
            fg=MUTED_FG,
            font=BODY_FONT,
            wraplength=400,
            justify="left",
        )
        option_note.pack(anchor="w", pady=(4, 0))

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
        except ValueError as error:
            messagebox.showerror("Copy error", str(error))
            return
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

        if self.clear_creations_var.get():
            try:
                clear_my_spore_creations()
            except PermissionError as error:
                messagebox.showerror(
                    "Access error",
                    f"Access denied while clearing My Spore Creations:\n{error}",
                )
                return
            except OSError as error:
                messagebox.showerror(
                    "Cleanup error",
                    f"Could not clear My Spore Creations:\n{error}",
                )
                return
            except Exception as error:
                messagebox.showerror(
                    "Unexpected error",
                    f"An unexpected error occurred while clearing My Spore Creations:\n{error}",
                )
                return

        messagebox.showinfo("Confirmed", "Confirmed")


def main() -> None:
    root = tk.Tk()
    SporeReplacerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

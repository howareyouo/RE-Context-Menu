import os
import sys
import subprocess
import winreg as reg
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent.resolve()
PYTHON_PATH = str(Path(sys.executable))
MAIN_SCRIPT = str(SCRIPT_DIR / "Convert.py")

EXTENSIONS = [
    ("RE4R", ".143221013"),
    # ("DMC5", ".11"),
    # ("RE3R_RT", ".34"),
]

# File associations that will have context menus registered
MENU_FILES = {".dds", ".png"} | {ext for _, ext in EXTENSIONS}

# Protect registry roots during removal
IS_PATH_END = {"SOFTWARE", "CLASSES", "SYSTEMFILEASSOCIATIONS"}

# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------
ROOT_KEY_NAME = "HKEY_CURRENT_USER"

def full_path(path):
    """Return a complete, copyable registry path like 'HKEY_CURRENT_USER\\...'"""
    return f"{ROOT_KEY_NAME}\\{path}"

# ---------------------------------------------------------------------------
# Core registry helpers
# ---------------------------------------------------------------------------
def _open_key(root, path):
    """Open or create (recursively) 'root\\path', returning the key handle."""
    return reg.CreateKey(root, path)

def _set_shell_default(shell_path):
    """Set the 'open' default value on a shell key."""
    with _open_key(reg.HKEY_CURRENT_USER, shell_path) as k:
        reg.SetValueEx(k, "", 0, reg.REG_SZ, "open")

def _create_menu(menu_path, command_line):
    """Create a single context menu item with its command handler."""
    with _open_key(reg.HKEY_CURRENT_USER, menu_path) as k:
        reg.SetValueEx(k, "Position", 0, reg.REG_SZ, "Bottom")
        reg.SetValueEx(k, "MultiSelectModel", 0, reg.REG_SZ, "Player")
    with _open_key(reg.HKEY_CURRENT_USER, menu_path + "\\command") as k:
        reg.SetValueEx(k, "", 0, reg.REG_SZ, command_line)

def _register_file_assoc(path):
    """Ensure SystemFileAssociations registration for an extension exists."""
    _open_key(reg.HKEY_CURRENT_USER, path)

def install_item_menu(ext, item_name, command_line):
    """Register a single context menu item for extension 'ext'."""
    shell = f"SOFTWARE\\Classes\\SystemFileAssociations\\{ext}\\shell"
    menu = f"{shell}\\{item_name}"
    _register_file_assoc(shell)
    _set_shell_default(shell)
    _create_menu(menu, command_line)

def install_script_menu(ext, item_name, script_name, extra_args=None):
    """Register a context menu item that runs a script."""
    script = SCRIPT_DIR / script_name
    if not script.exists():
        print(f"  ✗ Could not find {script_name}, skipping '{item_name}' menu")
        return False
    python = PYTHON_PATH
    args = f' "%1"' + (f" {extra_args}" if extra_args else "")
    cmd = f'"{python}" "{script}"{args}'
    install_item_menu(ext, item_name, cmd)
    return True

# ---------------------------------------------------------------------------
# Registration functions
# ---------------------------------------------------------------------------
def register_tex_to_dds():
    """Right-click .tex.{version} -> Convert to DDS (per game)"""
    try:
        for game, ext in EXTENSIONS:
            _open_key(reg.HKEY_CURRENT_USER, f"SOFTWARE\\Classes\\{ext}\\shell")
            python = PYTHON_PATH
            script = MAIN_SCRIPT
            cmd = f'"{python}" "{script}" "%1"'
            install_item_menu(ext, "Convert to DDS", cmd)
            print(f"  ✓ Registered {game} ({ext}) -> Convert to DDS")
    except Exception as e:
        print(f"  ✗ Failed adding Convert to DDS: {e}")

def register_tex_to_tex_re():
    """Right-click .dds -> Convert to TEX (to RE4R, single item)"""
    try:
        game, ext = EXTENSIONS[0]
        python = PYTHON_PATH
        script = MAIN_SCRIPT
        version = ext.lstrip(".")
        cmd = f'"{python}" "{script}" "%1" -game {game} -version {version}'
        install_item_menu(".dds", "Convert to TEX", cmd)
        print(f"  ✓ Registered Convert to TEX menu for .dds (-> {game} {version}).")
    except Exception as e:
        print(f"  ✗ Failed {e}")

def register_png_to_tex():
    """Right-click .png -> Convert to TEX (RE4R)"""
    try:
        script_name = "Convert_PNG2TEX.py"
        if install_script_menu(".png", "Convert to TEX", script_name):
            print("  ✓ Registered PNG to TEX Menu (RE4R).")
    except Exception as e:
        print(f"  ✗ Failed {e}")

def register_upscale():
    """Right-click .tex.{version} -> AI Upscale (per game)"""
    try:
        for game, ext in EXTENSIONS:
            script = SCRIPT_DIR / "Upscale.py"
            if not script.exists():
                print(f"  ✗ Could not find Upscale.py, skipping AI Upscale menu")
                return
            python = PYTHON_PATH
            cmd = f'"{python}" "{script}" "%1"'
            install_item_menu(ext, "AI Upscale", cmd)
            print(f"  ✓ Registered AI Upscale menu for {game}.")
    except Exception as e:
        print(f"  ✗ Failed adding AI Upscale menu: {e}")

def register_tex_to_png():
    """Right-click .tex.{version} -> Convert to PNG (per game)"""
    try:
        for game, ext in EXTENSIONS:
            script = SCRIPT_DIR / "Convert_PNG.py"
            if not script.exists():
                print(f"  ✗ Could not find Convert_PNG.py, skipping Convert to PNG menu")
                return
            python = PYTHON_PATH
            cmd = f'"{python}" "{script}" "%1"'
            install_item_menu(ext, "Convert to PNG", cmd)
            print(f"  ✓ Registered Convert to PNG menu for {game}.")
    except Exception as e:
        print(f"  ✗ Failed adding Convert to PNG menu: {e}")

# ---------------------------------------------------------------------------
# Removal helpers
# ---------------------------------------------------------------------------
def delete_key(path):
    """Forcefully delete a registry key tree via 'reg delete /f'."""
    full = full_path(path)
    try:
        result = subprocess.run(
            ["reg", "delete", full, "/f"],
            capture_output=True, text=True, shell=True,
        )
        if result.returncode == 0:
            print(f"  ✓ Deleted {full}")
        elif "not found" in (result.stderr + result.stdout).lower():
            print(f"  (not found) {full}")
        else:
            print(f"  ✗ Failed: {(result.stderr or result.stdout).strip()}")
    except Exception as e:
        print(f"  ✗ Error deleting {full}: {e}")

def _collect_existing_paths():
    """Collect registry paths that exist and should be removed."""
    paths = []
    # Per-extension paths (the shell key of any registered extension)
    for ext in MENU_FILES:
        shell = f"SOFTWARE\\Classes\\SystemFileAssociations\\{ext}\\shell"
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, shell, 0, reg.KEY_READ):
                paths.append(shell)
        except FileNotFoundError:
            pass
    # Also pick up .tex.{version} class root keys
    for _, ext in EXTENSIONS:
        root_key = f"SOFTWARE\\Classes\\{ext}"
        try:
            with reg.OpenKey(reg.HKEY_CURRENT_USER, root_key, 0, reg.KEY_READ):
                paths.append(root_key)
        except FileNotFoundError:
            pass
    return paths

def remove_context_menu():
    """Unregister all context menu entries."""
    try:
        print("The following registry paths will be deleted:\n")
        paths = _collect_existing_paths()

        if not paths:
            print("No registered keys found, nothing to unregister.")
            return

        for p in paths:
            print(f"  {full_path(p)}")

        print("\n⚠ WARNING:")
        print("  This will permanently remove the context menu entries listed above.")
        print("  Changes will take effect after the next Explorer restart or logon.\n")

        for path in paths:
            if not path or path.split("\\")[-1].upper() in IS_PATH_END:
                print("You can't unregister/delete this!! Aborting...")
                return
            delete_key(path)

        print("\nContext menu uninstalled successfully.")
    except PermissionError:
        print("  ✗ Permission denied (run as admin)")
    except Exception as e:
        print("  ✗ Error:", e)

# ---------------------------------------------------------------------------
# Installation planning (used for pre-install listing)
# ---------------------------------------------------------------------------
def build_install_paths():
    """Return all registry paths that will be created during install."""
    paths = []
    for _, ext in EXTENSIONS:
        paths.append(f"SOFTWARE\\Classes\\{ext}")
        paths.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\{ext}\\shell")

    paths.append("SOFTWARE\\Classes\\SystemFileAssociations\\.dds\\shell")
    paths.append("SOFTWARE\\Classes\\SystemFileAssociations\\.png\\shell")
    return paths

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=== DDS / RE Engine TEX - Context Menu Installer ===\n")
    print(f"Using script: {MAIN_SCRIPT}\n")

    choice = input("Do you want to install this ? (y/n): ").strip().lower()
    print()

    if choice == "y":
        print("The following registry paths will be created:\n")
        for p in build_install_paths():
            print(f"  {full_path(p)}")
        print("\nStarting installation...\n")

        register_tex_to_dds()
        register_upscale()
        register_tex_to_tex_re()
        register_tex_to_png()
        register_png_to_tex()

        print("\nContext menu installed successfully.")

    elif choice == "n":
        remove_context_menu()

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()

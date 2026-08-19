import os
import sys
import winreg as reg
from pathlib import Path

# HKEY_CURRENT_USER\Software\Classes\SystemFileAssociations
ALL_PATHS = ["SOFTWARE\\Classes\\SystemFileAssociations\\.dds\\shell\\Convert to TEX"]

IS_PATH_END = ["SOFTWARE", "CLASSES", "SYSTEMFILEASSOCIATIONS"] # Can't end in Software, Classes, SystemFileAssociations
            
HIVES = [reg.HKEY_CURRENT_USER,
         reg.HKEY_LOCAL_MACHINE, # No need to use, ignore
         reg.HKEY_CLASSES_ROOT] # No need to use, ignore
         
SCRIPT_NAME = "Convert.py"

EXTENSIONS = [
    ("RE4R", ".143221013"),
    # ("DMC5", ".11"),
    # ("RE3R_RT", ".34"),
]

for game in EXTENSIONS:
    ALL_PATHS.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\{game[1]}\\shell\\AI Upscale")
    ALL_PATHS.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\{game[1]}\\shell\\Convert to DDS")
    ALL_PATHS.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\{game[1]}\\shell\\Convert to PNG")
            
# ===================================================

def get_python_path():
    python_exe = Path(sys.executable)
    python = python_exe.parent / "pythonw.exe"
    
    if python.exists():
        return str(python)

def get_python_console_path():
    """Returns the console-enabled python.exe, used for scripts that need to show progress (e.g. AI upscale)"""
    return str(Path(sys.executable))

def get_script_path():

    # If the installer and script are in the same folder
    script_path = Path(__file__).parent / SCRIPT_NAME
    
    if script_path.exists():
        return str(script_path.resolve())
    else:
        # Ask user to enter full path manually if not found
        print(f"Could not find {SCRIPT_NAME} in the current folder.")
        manual_path = input("Please enter the FULL path to your converter script: ").strip().strip('"')
        print()
        return manual_path


#######################################
"""
def add_RE_Engine_Texture():
    try:
        base_path = "SOFTWARE\\Classes\\RE_Engine_Texture\\shell\\"
        
        print(f"Follwing paths will be registered for RE_Engine in HKEY_CURRENT_USER: {base_path}")
        print(f"Follwing paths will be registered for RE_Engine in HKEY_CURRENT_USER: {base_path}\\RE Engine Texture (Convert to DDS)")
        print(f"Follwing paths will be registered for RE_Engine in HKEY_CURRENT_USER: {base_path}\\RE Engine Texture (Convert to DDS)\\command")
        
        install_re = input("Do you want to install this RE_Engine File Handler ? (yes/no)\n")
        print("\n")
        
        if install_re == "yes":
            with reg.CreateKey(reg.HKEY_CURRENT_USER, base_path) as key:
                reg.SetValueEx(key, "", 0, reg.REG_SZ, "open")
                
            
            with reg.CreateKey(reg.HKEY_CURRENT_USER, f'{base_path}\\RE Engine Texture (Convert to DDS)') as key:
                reg.SetValueEx(key, "Position", 0, reg.REG_SZ, "Bottom")
                
            
            with reg.CreateKey(reg.HKEY_CURRENT_USER, f'{base_path}\\RE Engine Texture (Convert to DDS)\\command') as key:
                # Build the command
                python_path = get_python_path()
                script_full_path = get_script_full_path()
                
                command_line = f'cmd.exe /k ""{python_path}" "{script_full_path}" --game null --version null --file "%1""'

                reg.SetValueEx(key, "", 0, reg.REG_SZ, command_line)
            
        else:
            print("Nothing has been executed. Nothing has been registered.")
            print()


    except Exception as e:
        print(f"✗ Failed: {e}")"""
##############################################
 
def add_context_menu(Extensions):
    """Register the .tex.{version} context menu (Convert to DDS) for each game, install directly without per-item prompts"""
    try:
        for game in Extensions:
            game_key = f"SOFTWARE\\Classes\\{game[1]}"
            reg.CreateKey(reg.HKEY_CURRENT_USER, f"{game_key}\\shell")

            game_key_SFA_shell = f"SOFTWARE\\Classes\\SystemFileAssociations\\{game[1]}\\shell"
            with reg.CreateKey(reg.HKEY_CURRENT_USER, game_key_SFA_shell) as key:
                reg.SetValueEx(key, "", 0, reg.REG_SZ, "open")  # Default action is "open"

            game_menu_item_key = f"{game_key_SFA_shell}\\Convert to DDS"
            with reg.CreateKey(reg.HKEY_CURRENT_USER, game_menu_item_key) as key:
                reg.SetValueEx(key, "Position", 0, reg.REG_SZ, "Bottom")  # Place at the bottom
                reg.SetValueEx(key, "MultiSelectModel", 0, reg.REG_SZ, "Player")  # Bypass Windows 15-file limit

            command_key = game_menu_item_key + "\\command"
            with reg.CreateKey(reg.HKEY_CURRENT_USER, command_key) as key:
                python_path = get_python_path()
                script_path = get_script_path()
                command_line = f'"{python_path}" "{script_path}" "%1"'
                reg.SetValueEx(key, "", 0, reg.REG_SZ, command_line)

            print(f"✓ Registered {game[0]} ({game[1]}) -> Convert to DDS")

    except Exception as e:
        print(f"✗ Failed adding Convert to DDS for each game: {e}")


def add_dds_context_menu(Extensions):
    """Register the Convert to TEX submenu for .dds, install directly without per-item prompts"""
    try:
        re_engine_texture_key = "SOFTWARE\\Classes\\SystemFileAssociations\\.dds\\shell\\Convert to TEX"

        with reg.CreateKey(reg.HKEY_CURRENT_USER, re_engine_texture_key) as key:
            reg.SetValueEx(key, "Position", 0, reg.REG_SZ, "Bottom")  # Place at the bottom
            reg.SetValueEx(key, "SubCommands", 0, reg.REG_SZ, "")  # Allow submenu
            reg.SetValueEx(key, "MultiSelectModel", 0, reg.REG_SZ, "Player")  # Bypass Windows 15-file limit

        for item in Extensions:
            command_key = re_engine_texture_key + f"\\shell\\{item[0]}\\command"

            shell_key = "SOFTWARE\\Classes\\SystemFileAssociations\\.dds\\shell\\"
            with reg.CreateKey(reg.HKEY_CURRENT_USER, shell_key) as key:
                reg.SetValueEx(key, "", 0, reg.REG_SZ, "open")  # Default action is "open"

            with reg.CreateKey(reg.HKEY_CURRENT_USER, command_key) as key:
                python_path = get_python_path()
                script_path = get_script_path()
                version = item[1].lstrip(".")  # ".11" -> "11"
                command_line = f'"{python_path}" "{script_path}" "%1" -game {item[0]} -version {version}'
                reg.SetValueEx(key, "", 0, reg.REG_SZ, command_line)
                print(f"✓ Registered .dds submenu item for {item[0]}.")

        print(f"✓ Registered DDS Menu.")

    except Exception as e:
        print(f"✗ Failed {e}")
 
 
def add_upscale_context_menu(Extensions):
    """Register the AI Upscale context menu item for each game's .tex.{version}, install directly without per-item prompts"""
    try:
        upscale_script = os.path.join(os.path.dirname(get_script_path()), "Upscale.py")
        if not os.path.exists(upscale_script):
            print(f"✗ Could not find {upscale_script}, skipping AI Upscale menu")
            return

        for game in Extensions:
            menu_key = f"SOFTWARE\\Classes\\SystemFileAssociations\\{game[1]}\\shell\\AI Upscale"
            with reg.CreateKey(reg.HKEY_CURRENT_USER, menu_key) as key:
                reg.SetValueEx(key, "Position", 0, reg.REG_SZ, "Bottom")  # Place at the bottom
                reg.SetValueEx(key, "MultiSelectModel", 0, reg.REG_SZ, "Player")  # Bypass Windows 15-file limit

            command_key = menu_key + "\\command"
            with reg.CreateKey(reg.HKEY_CURRENT_USER, command_key) as key:
                # Use the console-enabled python.exe so upscale progress and errors are visible
                python_path = get_python_console_path()
                command_line = f'"{python_path}" "{upscale_script}" "%1"'
                reg.SetValueEx(key, "", 0, reg.REG_SZ, command_line)

            print(f"✓ Registered AI Upscale menu for {game[0]}.")

    except Exception as e:
        print(f"✗ Failed adding AI Upscale menu: {e}")


def add_png_context_menu(Extensions):
    """Register the Convert to PNG context menu item for each game's .tex.{version}, install directly without per-item prompts"""
    try:
        png_script = os.path.join(os.path.dirname(get_script_path()), "Convert_PNG.py")
        if not os.path.exists(png_script):
            print(f"✗ Could not find {png_script}, skipping Convert to PNG menu")
            return

        for game in Extensions:
            menu_key = f"SOFTWARE\\Classes\\SystemFileAssociations\\{game[1]}\\shell\\Convert to PNG"
            with reg.CreateKey(reg.HKEY_CURRENT_USER, menu_key) as key:
                reg.SetValueEx(key, "Position", 0, reg.REG_SZ, "Bottom")  # Place at the bottom
                reg.SetValueEx(key, "MultiSelectModel", 0, reg.REG_SZ, "Player")  # Bypass Windows 15-file limit

            command_key = menu_key + "\\command"
            with reg.CreateKey(reg.HKEY_CURRENT_USER, command_key) as key:
                # Use the console-enabled python.exe so conversion progress and errors are visible
                python_path = get_python_console_path()
                command_line = f'"{python_path}" "{png_script}" "%1"'
                reg.SetValueEx(key, "", 0, reg.REG_SZ, command_line)

            print(f"✓ Registered Convert to PNG menu for {game[0]}.")

    except Exception as e:
        print(f"✗ Failed adding Convert to PNG menu: {e}")


def print_key(root, path, indent=0):
    try:
        with reg.OpenKey(root, path, 0, reg.KEY_READ) as key:
            print("  " * indent + f"[KEY] {path}")

    except FileNotFoundError:
        print("  " * indent + f"[MISSING] {path}")
        print("\n")
        return False
        
    except PermissionError:
        print("  " * indent + f"[DENIED] {path}")
        print("\n")
        return False

def delete_key(root, path):
    try:
        # Open the key
        with reg.OpenKey(root, path, 0, reg.KEY_ALL_ACCESS) as key:
            
            # Delete subkeys first
            while True:
                try:
                    subkey = reg.EnumKey(key, 0)
                    delete_key(root, path + "\\" + subkey)
                except OSError:
                    break
                    
            # Delete values
            while True:
                try:
                    value = reg.EnumValue(key, 0)[0]
                    reg.DeleteValue(key, value)
                except OSError:
                    break
                    
        # Now delete the key itself
        reg.DeleteKey(root, path)
        print(f"✓ Deleted {path}")


    except FileNotFoundError:
        print(f"Key not found: {path}")
        print("\n")
    except PermissionError:
        print("✗ Permission denied (run as admin)")
        print("\n")
    except Exception as e:
        print("✗ Error:", e)
        print("\n")
    

def remove_context_menu(games):
    try:             
        for path in ALL_PATHS:
            print_key_info = print_key(reg.HKEY_CURRENT_USER, path)
                
            if print_key_info == False:
                continue
                    
            uninstall = input("Are you sure you want to delete/unregister this path (key) ? (yes/no)\n")
            print()
            if uninstall == "yes":
                if path == "" or path.split("\\")[-1].upper() in IS_PATH_END: # Safe-guard. Check if path is empty or its uppercase format ends in any of the string elements inside IS_PATH_END List
                    print("You can't unregister/delete this !!. Aborting...")
                    return
                
                delete_key(reg.HKEY_CURRENT_USER, path)
                print("✓ Successfully removed key from registry")
                print()
                
            else:
                print("Key/path hasn't been removed from registry")
                print()
                
        return

    except PermissionError:
        print("✗ Permission denied (run as admin)")
        print("\n")
        return
    except Exception as e:
        print("✗ Error:", e)
        print("\n")
        return


def build_install_paths(Extensions):
    """Return all registry paths that will be created during install (shown before installing)"""
    paths = []
    for game in Extensions:
        ext = game[1]
        # .tex.{version} context menu (Convert to DDS)
        paths.append(f"SOFTWARE\\Classes\\{ext}")
        paths.append(f"SOFTWARE\\Classes\\{ext}\\shell")
        paths.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\{ext}\\shell")
        paths.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\{ext}\\shell\\Convert to DDS")
        paths.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\{ext}\\shell\\Convert to DDS\\command")
        # .dds context menu (Convert to TEX submenu)
        paths.append("SOFTWARE\\Classes\\SystemFileAssociations\\.dds\\shell")
        paths.append("SOFTWARE\\Classes\\SystemFileAssociations\\.dds\\shell\\Convert to TEX")
        # Convert to PNG
        paths.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\{ext}\\shell\\Convert to PNG")
        paths.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\{ext}\\shell\\Convert to PNG\\command")
        # AI Upscale
        paths.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\{ext}\\shell\\AI Upscale")
        paths.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\{ext}\\shell\\AI Upscale\\command")

    for game in Extensions:
        paths.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\.dds\\shell\\Convert to TEX\\shell\\{game[0]}\\command")
        
    return paths


def main():
    print("=== DDS / RE Engine TEX - Context Menu Installer ===\n")
    
    script_path = get_script_path()
    print(f"Using script: {script_path}\n")
    
    register = input("Do you want to install this ? (y/n): ")
    print()
    
    games = EXTENSIONS
    
    if register == "y":
        # List the registry paths that will be modified
        print("The following registry paths will be created (HKEY_CURRENT_USER):\n")
        for p in build_install_paths(games):
            print(f"  {p}")
        print("\nStarting installation...\n")

        add_context_menu(games) # e.g.: .11
        add_upscale_context_menu(games)
        add_dds_context_menu(games)
        add_png_context_menu(games)
 
    elif register == "n":
            remove_context_menu(games)

    print("\nCode finished!")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
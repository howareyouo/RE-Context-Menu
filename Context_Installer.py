import winreg as reg
import os
import sys
from pathlib import Path

ALL_PATHS = ["SOFTWARE\\Classes\\SystemFileAssociations\\.dds\\shell\\RE Engine Texture (Convert to .tex)"]

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
    ALL_PATHS.append(f"SOFTWARE\\Classes\\SystemFileAssociations\\{game[1]}\\shell\\{game[0]} Texture (Convert to .dds)")
            
# ===================================================

def get_python_path():
    python_exe = Path(sys.executable)
    python = python_exe.parent / "pythonw.exe"
    
    if python.exists():
        return str(python)

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
        print(f"Follwing paths will be registered for RE_Engine in HKEY_CURRENT_USER: {base_path}\\RE Engine Texture (Convert to .dds)")
        print(f"Follwing paths will be registered for RE_Engine in HKEY_CURRENT_USER: {base_path}\\RE Engine Texture (Convert to .dds)\\command")
        
        install_re = input("Do you want to install this RE_Engine File Handler ? (yes/no)\n")
        print("\n")
        
        if install_re == "yes":
            with reg.CreateKey(reg.HKEY_CURRENT_USER, base_path) as key:
                reg.SetValueEx(key, "", 0, reg.REG_SZ, "open")
                
            
            with reg.CreateKey(reg.HKEY_CURRENT_USER, f'{base_path}\\RE Engine Texture (Convert to .dds)') as key:
                reg.SetValueEx(key, "Position", 0, reg.REG_SZ, "Bottom")
                
            
            with reg.CreateKey(reg.HKEY_CURRENT_USER, f'{base_path}\\RE Engine Texture (Convert to .dds)\\command') as key:
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

    try:
        for game in Extensions:
            whole_key = f"SOFTWARE\\Classes\\{game[1]}"
            whole_key_SFA = f"SOFTWARE\\Classes\\SystemFileAssociations\\{game[1]}\\shell\\{game[0]} Texture (Convert to .dds)\\command"
            
            print(f"All the following keys will be registered for {game[0]} in HKEY_CURRENT_USER: {whole_key}")
            print(f"All the following keys will be registered for {game[0]} in HKEY_CURRENT_USER: {whole_key_SFA}")
            install_game = input("Do you want to install the game for converting to .dds ? (yes/no)")
            print("\n")
            
            if install_game == "yes":
                game_key =  f"SOFTWARE\\Classes\\{game[1]}"
                reg.CreateKey(reg.HKEY_CURRENT_USER, f"{game_key}\\shell")
                
                game_key_SFA_shell = f"SOFTWARE\\Classes\\SystemFileAssociations\\{game[1]}\\shell"
                
                with reg.CreateKey(reg.HKEY_CURRENT_USER, game_key_SFA_shell) as key:
                    reg.SetValueEx(key, "", 0, reg.REG_SZ, "open") # Set default action when double-clicking to Open if there is a default associated app, otherwise Open with...
               
                game_menu_item_key = f"{game_key_SFA_shell}\\{game[0]} Texture (Convert to .dds)"
                with reg.CreateKey(reg.HKEY_CURRENT_USER, game_menu_item_key) as key:
                    reg.SetValueEx(key, "Position", 0, reg.REG_SZ, "Bottom") # Place at the bottom
                    reg.SetValueEx(key, "MultiSelectModel", 0, reg.REG_SZ, "Player") # Bypass windows 15 file limit
                
                
                command_key = game_menu_item_key + "\\command"
                with reg.CreateKey(reg.HKEY_CURRENT_USER, command_key) as key:
                    # Build the command
                    python_path = get_python_path()
                    script_path = get_script_path()
                    
                    command_line = f'"{python_path}" "{script_path}" "%1"'

                    reg.SetValueEx(key, "", 0, reg.REG_SZ, command_line)
                
                
                
                print(f"✓ Successfully added for {game[0]}: {game[1]}")
                print("\n")
        
            else:
                print("This game hasn't been registered for conversion to .dds")
                print("\n")
            
            
            
    except Exception as e:
        print(f"✗ Failed adding convert to .dds for each game: {e}")



def add_dds_context_menu(Extensions):
    try:
        re_engine_texture_key = "SOFTWARE\\Classes\\SystemFileAssociations\\.dds\\shell\\RE Engine Texture (Convert to .tex)"
        
        print(f"All the follwing keys will be registered for .dds in HKEY_CURRENT_USER: {re_engine_texture_key}")
        install_dds_context_menu = input("Do you want to install .dds context menu ? (yes/no)\n")
        print("\n")
        
        if install_dds_context_menu == "yes":
            with reg.CreateKey(reg.HKEY_CURRENT_USER, re_engine_texture_key) as key:
                reg.SetValueEx(key, "Position", 0, reg.REG_SZ, "Bottom") # Place at the bottom
                reg.SetValueEx(key, "SubCommands", 0, reg.REG_SZ, "") # Allow submenu items
                reg.SetValueEx(key, "MultiSelectModel", 0, reg.REG_SZ, "Player") # Bypass windows 15 file limit
            
            print(f"✓ Successfully added DDS Menu.")
            print("\n")
        
            for item in Extensions:
                command_key = re_engine_texture_key + f"\\shell\\{item[0]}\\command"
                
                print(f"All the follwing keys will be registered for .dds in HKEY_CURRENT_USER: {command_key}")
                install_game_dds = input("Do you want to install dds submenu item for this game ? (yes/no)\n")
                print("\n")
                
                if install_game_dds == "yes":
                    shell_key = "SOFTWARE\\Classes\\SystemFileAssociations\\.dds\\shell\\"
                    with reg.CreateKey(reg.HKEY_CURRENT_USER, shell_key) as key:\
                        reg.SetValueEx(key, "", 0, reg.REG_SZ, "open") # Set default action when double-clicking to Open if there is a default associated app, otherwise Open with...

                    with reg.CreateKey(reg.HKEY_CURRENT_USER, command_key) as key: # e.g.: \\shell\\DMC5\\command
                        # Build the command
                        python_path = get_python_path()
                        script_path = get_script_path()
                        
                        version = item[1].lstrip(".")  # ".11" becomes "11"
                        
                        command_line = f'"{python_path}" "{script_path}" "%1" -game {item[0]} -version {version}'

                        reg.SetValueEx(key, "", 0, reg.REG_SZ, command_line)
        
                        print(f"✓ Successfully added DDS Submenu item for {item[0]}.")
                        print("\n")
            
                else:
                    print("This game hasn't been registered for conversion to .tex")
                    
        else:
            print("DDS Menu hasn't been registered.")
            
            
    except Exception as e:
        print(f"✗ Failed {e}")
 
 
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



def main():
    print("=== DDS / RE Engine TEX - Context Menu Installer ===\n")
    
    script_path = get_script_path()
    print(f"Using script: {script_path}\n")
    
    register = input("Do you want to install this ? (yes/no)\n")
    print()
    
    games = EXTENSIONS
    
    if register == "yes":
        add_context_menu(games) # e.g.: .11
        add_dds_context_menu(games)
 
    elif register == "no":
            remove_context_menu(games)

    print("\nCode finished!")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
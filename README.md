# RE Engine Texture Context Menu Tool

A Windows context-menu tool to convert between standard DDS files and RE Engine's proprietary `.tex` texture format, plus an AI upscale feature (Topaz Gigapixel AI) and direct conversion to PNG.

## How To Install

- To install this and register the menu in Windows's registry, so it appears in the context menu (the menu that appears when you right-click a file).

- Run CMD, go to the path where you extracted the folder.
  - e.g: `E:\DMC5 Context Menu Tool`

- Enter this command: `python context_installer.py`
  - (and you have Python installed of course, I used Python 3.14.4)
  - or just simply double-click the Python file if it is associated with Python as the default app.
  - no admin privileges needed.

- The tool leaves the console window open when converting regardless of success or error, to be able to detect errors when they occur, so the user would have to close it manually.

- If you want to register, just type "yes" without quotes.
  - The tool asks you to confirm before registering any path or key.

- It will register in the current user account only. If you use admin privileges (you ran CMD as administrator), it will register in the administrator account. If you are already running Windows as an Administrator account, it won't matter and still register to that administrator account.

- If you have registered and want to unregister, run the command again, and when it asks, just type "no" without quotes.
  - The tool asks you to confirm before unregistering any path or key.

- If you register you should see "Convert to DDS" when right-clicking a `.dds` file, and "Convert to .tex" with cascading sub-menus for each game (DMC5 only for now) when right-clicking a RE Engine `.tex` file. The menu also includes "AI Upscale" and "Convert to PNG" items.

- Converted files will appear next to the file you wanted to convert. Also, if you check the Windows Registry Editor, you will find the keys and everything registered in the paths mentioned in `Context_Installer.py`.

- If you unregister, you no longer see any of the clickable items mentioned above in the context menu. Also, if you check in the Registry Editor, it should be deleted.

- The tool registers in certain paths in only one hive (HKEY_CURRENT_USER).

- When un-registering, it removes only from the same HKEY_CURRENT_USER hive. For the sake of safe-guarding and security, there are conditions that if met, the tool will abort the unregister function and exit code.
  - Such as the already-hardcoded path in `ALL_PATHS` being empty, or ending in one of the strings in `IS_PATH_END`.

- If something goes wrong, you can always check the hives and paths mentioned in `Context_Installer.py` and use the default Windows Registry Editor or Registry Workshop to inspect manually.

- Some paths to consider searching in, just in case something went wrong, and you want to register/unregister manually:
  - `HKEY_CURRENT_USER\`
  - `HKEY_CURRENT_USER\Software`
  - `HKEY_CURRENT_USER\Software\Classes`
  - `HKEY_CURRENT_USER\Software\Classes\SystemFileAssociations\`

- Keywords: `.dds`, `RE_Engine_Texture`, `.tex`, `Convert`, `DMC5`, `.11`, or any game name or version you added by yourself to the entries.

## Changelog

### Version 1.0.2

- Changed the tool such that it sets the default value as "open", now when double-clicking the files, the default Windows's Open/Open With... will execute instead of the tool itself
- Changed the tool such that it bypasses Windows's 15 file limit through the value `MultiSelectModel`=`Player`, now more than 15 files can be selected and the tool will still show in the Context Menu

### Version 1.0.1

- Settled on making the tool use `pythonw.exe` instead, which shows no console windows. However, this way if any errors occur we won't be able to catch them, unless the `Convert.py` script is ran normally from the CMD

### Version 1.0.0

- Release

# L4D2-Ultimate-Mod-Manager

**This is a fork from [TheCraZyDuDee/L4D2-Mod-Manager](https://github.com/TheCraZyDuDee/L4D2-Mod-Manager). The code of this fork is modified from original.**

## What been added in this fork?

### Force Enable Mods (GameInfo Override)

This tool allows you to force-enable mods that do not work in certain gamemodes by injecting them directly into the game's `gameinfo.txt`.

Instead of relying on the default addon system, the selected mod is copied to the root of the game directory and renamed to `pak01_dir.vpk`. A custom folder name can be chosen for better organization.

The tool then automatically adds the mod to the `SearchPaths` section of `gameinfo.txt`, ensuring it is loaded with high priority.

This method can override standard restrictions and make incompatible mods work across all gamemodes.

This is the fatest way to make addons work in versus and scavenge

## Due to the tool being AI-generated and my current focus on learning coding, support for this is limited for now.

Manager to enable Mods in Addon disabled Modes (Versus)<br>
Steam Guide can be found [here](https://steamcommunity.com/sharedfiles/filedetails/?id=3332849494)

![](https://i.imgur.com/x5tZwkf.png)


## Features

- Enable/Disable Mods for use in Mod disabled Gamemodes
- Change Priority of enabled mods in which they get loaded
- Rename/Delete Mods in the list
- Manually add .vpk Mods
- Add installed Workshop Mods

## Usage

- Download the latest Release of the Tool from [here](https://github.com/TheCraZyDuDee/L4D2-Mod-Manager/releases/latest/download/L4D2-Mod-Manager.exe)
- Move the Tool to your Left 4 Dead 2 Game Folder (the same directory where the left4dead2.exe is located)
- Now Manage your mods to your liking and apply changes (mods managed by the tool get moved to a folder called usermods)

## Building

Currently Windows only!

- Download the Repository via git or just as zip
- Install [Python](https://www.python.org/downloads/) and add it to System Path'
- Install PyInstaller using `pip install pyinstaller`
- cd to the directory containing the .png, .py and .spec file and run `pyinstaller l4d2-manager.spec` or just run the build.bat

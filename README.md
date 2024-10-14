**State:** Not yet released.

# wrsr-iniconfig

wrsr-iniconfig modifies building.ini workshopconfig.ini files. At the moment, its functionality is limited to modify building.ini files to make buildings free to build, and to update workshopconfig.ini to reflect changes in file names made during this process.

**The remainder of this readme supposes that you use Windows 11.**

## What does wrsr-iniconfig do?
wrsr-iniconfig is a Python script that converts building assets made for *Workers and Resources: Soviet Republic* to free buildings without maintenance or electricity requirements.

## Dependencies

You must have Python installed. The absolute easiest way is to grab it from the Microsoft Store. As of writing (14 October 2024), the latest version available is [3.13](https://apps.microsoft.com/detail/9pnrbtzxmb4z). Note that the Microsoft Store version does not automatically update to the next release, so you might want to [search](https://apps.microsoft.com/search?query=python) for a newer version.

Obviously, you also need the [game](https://store.steampowered.com/app/784150/).

Finally, you must have downloaded an asset that you want to modify.

## How to use it

1. Right-click in the same directory that you placed wrsr-fb.py in and select `Open in Terminal`.
2. Copy the address from the folder that you want to modify and copy and paste it (in the Terminal, you can use the middle mouse button to paste) when prompted.
3. Make your selections and follow the prompts.
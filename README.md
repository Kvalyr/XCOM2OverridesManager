# XCOM2OverridesManager
### A tool that cleans & updates XCOM2 ModClassOverride entries in XComEngine.ini in the user's config path.

The tool is distributed as a standalone executable for Windows, or it can can be run via python on any platform.

[Download Latest Release Here](https://github.com/Kvalyr/XCOM2OverridesManager/releases/latest)

# Why is it needed?
* It was created out of my frustration with XCOM2's inconsistent behaviour in how it updates ModClassOverrides entries in XComEngine.ini.

* XCOM 2 relies on the Unreal engine's handling of ini files to do this and can sometimes get into a bad state due to bugs or quirky engine behaviour where it simply stops updating the list of overrides. 
  * This is the reason why "delete your config folder" is so often the fix-all solution to mod problems with XCOM2.

* The XCOM 2 Community Launcher (https://github.com/X2CommunityCore/xcom2-launcher) is able to detect ModClassOverrides and warn of conflicts, but does not (at time of writing) update those entries in the user's XComEngine.ini; it just clears them out to let the game rebuild the list itself.

The idea behind this tool is to take charge of the list of override entries and forcibly update it outside of the game by scanning installed mods.

This tool is intended to be paired with the community launcher, but can be used with the original game launcher too.


# What does it do?
* Scans your XCOM2 / WotC / Workshop mods for ModClassOverrides
* Checks existing ModClassOverrides in your XComEngine.ini
* Removes outdated overrides
* Adds missing overrides
* Warn about duplicate & conflicting overrides

# Known Issues / Limitations
* Currently enables overrides for **any/all** mods found - Not just those enabled in XComModOptions.ini 
  * A fix is underway. Users who only install/subscribe to mods they actually want to enable can use this tool without problem.

# How to Use
* Download this tool and extract it somewhere convenient.
* Open the `config.ini` file in the tool's folder and set the Mod paths to match your XCOM2 mod paths.
  * On Windows you will typically only need to change the Drive letter and base steam folder location.
  * Google "XCOM 2 Mod paths" if you get stuck.
* Change `WOTC` to false in `config.ini` if you are playing vanilla XCOM2 without WotC.
* Run the tool. It will work automatically without any further prompts.
* A backup of your previous XComEngine.ini will be copied to XComEngine.ini.bak in the same folder.
* If the tool window just disappears immediately or otherwise fails to work, take a look at the XCOM2OM.log file it generates in its own folder. The tool logs what it's doing there, along with possible errors or problems encountered.

# Building an Executable 
### For users on Linux/Mac or those who prefer not to download precompiled binaries
* Install python 3.6 or later for your platform (https://www.python.org/downloads/) 
* Install PyInstaller using `pip install pyinstaller` from a shell
* Clone/download this repo from GitHub
* Navigate in a shell to the repo directory and type `make exe`
  * PyInstaller should then create an executable in \dist

# License
Released under MIT Licence

# Links
* [Latest Release](https://github.com/Kvalyr/XCOM2OverridesManager/releases/latest)
* [XCOM2 Community Launcher](https://github.com/X2CommunityCore/xcom2-launcher) (Unaffiliated, but recommended)
* [Discussion Thread (Reddit)](TODO) (TODO)

# Credit
* XCOM2 and WotC are Properties of Firaxis
* Unreal is a property of Epic

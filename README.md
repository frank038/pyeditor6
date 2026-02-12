# pyeditor6
A simple text editor. Or a python/bash/javascript IDE.

Requires:
- python3
- pyqt6
- qscintilla
- python3-dbus and dbus.mainloop.pyqt6 [optional] (needet to own the single instance mode by the second instance of this program after the first instance exits; without them this functionality will be disabled)

This program should be launched by using the bash script pyeditor6.sh.

Features:

- tabs for file name and displays its full path while hovering
- autocompletitions
- string/word searching with history of previous searched words
- comment out/uncomment, also for a group of lines of code
- read only mode
- highlights all the occurences of the selected word
- saves its window size
- load a file if it is passed as argument
- dialogs for loading files or saving the document
- line numbers
- file modified indicator (by changing the file name colour)
- bash scripts support (switching in the gui)
- javascript scripts support (compatible with c, c++, c#, etc.)
- plain text support (no styling at all)
- history of opened files
- zoom (Ctrl+mouse wheel)
- uppercase/lowercase/swapcase in the contextual menu
- wordwrapping
- style colours (almost) fully customizable
- status bar
- optional command line argument: -p for python file, -b for bash file, -j for javascript file, -t for text file (file name is optional)
- configurable through its setting dialog for the common settings and through its config file cfgpyeditor.py for the internal application settings.
- built-in functions from qscintilla widget: tab/untab (TAB/ALT+TAB), undo/redo (CTRL+z/y), etc.;
- clone mode (currently disabled; opens a new tab with the same content of the ancestor document);
- print dialog;
- single instance mode (all files open in the same application): the -a option disables it at launch; the next instance of this program can own this funcionality after the first instance exits;
- can reload the files not closed by the user (to enable/disable in the config dialog);
- tracks any changes made by other applications in the same files
- reload the document
- drag and drop support.

![My image](https://github.com/frank038/pyeditor6/blob/main/screenshot2.jpg)


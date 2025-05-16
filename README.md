# pyeditor6
A simple text editor. Or a python/bash/javascript IDE.

Requires:
- python3
- pyqt6
- qscintilla

This program should be launched by using the bash script pyeditor6.sh.

Features:

- tabs for file name and displays its full path while hovering
- word autocompletition
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
- configurable with its config file
- built-in functions from qscintilla widget: tab/untab (TAB/ALT+TAB), undo/redo (CTRL+z/y), etc.

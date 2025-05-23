#!/bin/bash

thisdir=$(dirname "$0")
cd $thisdir

if [[ $# -eq 0 ]]; then
    python3 pyeditor6.py
elif [[ $# -eq 1 ]]; then
    python3 pyeditor6.py "$1"
elif [[ $# -eq 2 ]]; then
    python3 pyeditor6.py "$1" "$2"
fi

cd $HOME

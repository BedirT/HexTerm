#!/bin/bash

# Check if the terminal is gnome-terminal
if [ "$COLORTERM" == "gnome-terminal" ]; then
    echo "Detected gnome-terminal, adjustion terminal settings for 256 colors"
    export TERM=xterm-256color
if [ "$COLORTERM" == "truecolor" ]; then
    echo "Detected truecolor, adjustion terminal settings for 256 colors"
    export TERM=xterm-256color
else
    echo "Terminal is not gnome-terminal, the game visual settings may not be optimal"
fi

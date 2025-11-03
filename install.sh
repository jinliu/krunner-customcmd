#!/bin/sh

mkdir -p ~/.local/share/krunner/dbusplugins/
cp krunner-customcmd.desktop ~/.local/share/krunner/dbusplugins/
kquitapp6 krunner

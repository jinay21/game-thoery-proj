#!/bin/zsh
cd -- "${0:A:h}"
python3 server.py
read -k 1 "?Press any key to close this window…"

import re

def readFile(fpath : str):
    with open(fpath, "r") as f:
        s = f.read()
    match = re.search(r"\[[^]]+\]", s)

readFile("MagnusCarlsenVsYaroslavShevchenko.pgn")
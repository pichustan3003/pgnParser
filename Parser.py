import re
from Legality import generalLegailty, MoveError

class game:
    def __init__(self, infoDict : dict[str,str], moves : list[str]) -> None:
        self.white = infoDict["White"]
        self.black = infoDict["Black"]
        if infoDict["Result"][-1] == "2":
            self.result = 0
        elif infoDict["Result"][0] == "1":
            self.result = 1
        else:
            self.result = -1
        self.date = infoDict["Date"]
        self.moves = moves
        self.boardPositionWhite = {
            "P":"a2",
            "P":"b2",
            "P":"c2",
            "P":"d2",
            "P":"e2",
            "P":"f2",
            "P":"g2",
            "P":"h2",
            "R":"a1",
            "R":"h1",
            "N":"b1",
            "N":"g1",
            "B":"c1",
            "B":"f1",
            "K":"e1",
            "Q":"d1"
        }
        self.boardPositionBlack = {
            "P":"a7",
            "P":"b7",
            "P":"c7",
            "P":"d7",
            "P":"e7",
            "P":"f7",
            "P":"g7",
            "P":"h7",
            "R":"a8",
            "R":"h8",
            "N":"b8",
            "N":"g8",
            "B":"c8",
            "B":"f8",
            "K":"e8",
            "Q":"d8"
        }
        self.checkForStrangeness()

    def checkForStrangeness(self):
        for i in self.moves:
            if not generalLegailty(i):
                raise MoveError(f"Error with move {i}")

    def __str__(self):
        if self.result == 1:
            out = "a win for white"
        elif self.result == -1:
            out = "a win for black"
        else:
            out = "a draw"
        return f"Game between {self.white} and {self.black} which ended in {out}"

def readFile(fpath : str):
    with open(fpath, "r") as f:
        s = f.read()
    match : list[str] = re.findall(r"\[(.*?)\]", s)
    if not match:
        raise KeyError("Couldn't find any game info enclosed in []")
    outInfo : dict[str,str]= {}
    for m in match:
        outInfo[m.split(" ")[0]] = m.split(" ", 1)[1][1:-1]
    mv = re.sub(r'\[.*?\]|\(.*?\)|\{.*?\}',"", s).strip()
    mv = re.split(" |\n", mv)
    temv : list[str] = []
    for i in range(0,len(mv)):
        if i % 3==0:
            continue
        temv.append(mv[i])
    mv = temv
    if mv[-1][0] == "1" or mv[-1][-1] == "1":
        mv.pop()
    print(mv)
    return game(outInfo, mv)

g = readFile("MagnusCarlsenVsYaroslavShevchenko.pgn")
print(g)
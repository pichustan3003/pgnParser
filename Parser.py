import re

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
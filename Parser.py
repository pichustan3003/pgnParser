import re
import string
from typing import overload

class piece:
    def __init__(self, type: str, rank: int, file: str, color: int) -> None:
        self.piece = type
        self.rank = rank
        self.file = file
        self.moved = False
        self.color = color
    def __str__(self) -> str:
        return f"{"white" if self.color == 1 else "black"} {self.piece} on {self.file}{self.rank}"
class game:

    def initAsFEN(self, bPos : list[piece]) -> None:
        """Don't use this it was so I can test"""
        self.white = "Unknown"
        self.black = "Unknown"
        self.boardPosition = bPos
        self.date = "Unknown"
        self.result = "This game was dirived from FEN which means the result is not known"

    def initAsInfo(self, infoDict : dict[str,str], moves : list[str]) -> None:
        """Actual constructor"""
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
        self.boardPosition : list[piece] = [
            # White pawns
            *[piece("P", 2, f, 1) for f in "abcdefgh"],

            # White back rank
            piece("R", 1, "a", 1),
            piece("N", 1, "b", 1),
            piece("B", 1, "c", 1),
            piece("Q", 1, "d", 1),
            piece("K", 1, "e", 1),
            piece("B", 1, "f", 1),
            piece("N", 1, "g", 1),
            piece("R", 1, "h", 1),

            # Black pawns
            *[piece("P", 7, f, -1) for f in "abcdefgh"],

            # Black back rank
            piece("R", 8, "a", -1),
            piece("N", 8, "b", -1),
            piece("B", 8, "c", -1),
            piece("Q", 8, "d", -1),
            piece("K", 8, "e", -1),
            piece("B", 8, "f", -1),
            piece("N", 8, "g", -1),
            piece("R", 8, "h", -1)
        ]
        self.checkForStrangeness()

    @overload
    def __init__(self, infoDict : dict[str,str], moves : list[str]) -> None: ...

    @overload
    def __init__(self, infoDict : list[piece]) -> None: ...

    def __init__(self, infoDict : dict[str,str] | list[piece], moves : list[str] | None = None): # type: ignore
        if isinstance(infoDict, list):
            self.initAsFEN(infoDict)
        else:
            self.initAsInfo(infoDict, moves) # type: ignore

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

    def makeMove(self, move : str, side : int):
        self.boardPosition = checkLegalityWithBoardPosition(move, self.boardPosition, side)

    def readFEN(self, fen : str) -> game: # type: ignore
        """This is just for testing purposes. It is bad"""
        boardPosition : list[piece] = []
        goodBit = fen.split(" ")[0]
        rows = goodBit.split("/")[::-1]
        
        for row in range(len(rows)):
            file = 97
            for char in rows[row]:
                if char not in string.ascii_letters:
                    file += int(char)
                else:
                    side = 1 if char in string.ascii_uppercase else -1
                    boardPosition.append(piece(char.upper(), row+1, chr(file), side))
                    file += 1
        return game(boardPosition)


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
    return game(outInfo, mv)
if __name__ == "__main__":
    from Legality import generalLegailty, MoveError, checkLegalityWithBoardPosition
    import Legality
    g = readFile("MagnusCarlsenVsYaroslavShevchenko.pgn")
    print(g)

    gameFromFEN = g.readFEN(r"rnbqkbnr/pp1ppPpp/3P4/8/8/2p5/PPPP1PPP/RNBQKBNR w KQkq - 0 1")
    print(Legality.returnAllSquaresPieceCanHit(gameFromFEN.boardPosition[15], gameFromFEN.boardPosition))
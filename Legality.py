import string
pieceSymbols = {"R":"Rook", "N":"Knight", "B":"Bishop", "K":"King", "Q":"Queen"}

class MoveError(Exception):
    pass

def generalLegailty(move : str):
    """This will only check if a move could happen, eg bishop from f4 -> f5 could not happen.\n
    It does not check board setup"""
    try:
        readInputMoveAndReturnDescription(move)
    except MoveError:
        return False
    return True

def deserialise(move : str):
    capture = False
    start = ""
    final = ""
    genMovCode = ""
    if move[0] in string.ascii_lowercase:
        piece = "P"
        if len(move):
            final = move
            genMovCode = "p"
    return capture, start, final, genMovCode

def squareFree(square : str, pieces : dict[str,str]):
    return square not in pieces.values()

def checkLegalityWithBoardPosition(move: str, ownSidePieces : dict[str, str], opposingPieces : dict[str,  str], side : int):
    capture, start, final, genMovCode = deserialise(move)
    piecePos = ownSidePieces | opposingPieces
    match genMovCode:
        case "p":
            if not squareFree(final, piecePos):
                raise MoveError("move cannot be made (Square is not free for pawn to move to)")
            # add actual move processing

    
            

def kingLegalityChecker(move : str, takeAChillPill : bool = False):

    destFile = move[0]
    destRow = int(move[1])
    if 1 > destRow or 8 < destRow:
        raise MoveError("Invalid row")
    if ord("a") > ord(destFile) or ord("h") < ord(destFile):
        raise MoveError("Invalid file")

def pawnLegalityChecker(move : str):

    if move[0] not in string.ascii_lowercase: raise MoveError("Not a pawn move")
    if move[1] == "x":
        originFile = move[0]
        destFile = move[2]
        destRow = int(move[3])
        if 1 > destRow or 8 < destRow:
            raise MoveError("Invalid row")
        if ord("a") > ord(destFile) or ord("h") < ord(destFile):
            raise MoveError("Invalid file destination")
        if ord("a") > ord(originFile) or ord("h") < ord(originFile):
            raise MoveError("Invalid file of origin")
        if originFile == destFile: raise MoveError("Pawns cannot capture on the same file")
        if len(move) < 6:
            promotion = False
        else:
            promotion = True if move[4] == "=" else False
        if ord(originFile) -1 != ord(destFile) and ord(originFile) + 1 != ord(destFile):
            raise MoveError(f"Pawn attempted capture on a square not directly diagonal to it {originFile}->{destFile}")

        if destRow in [1, 8] and not promotion:
            raise MoveError("Pawn reached end row and did not promote")

        if promotion and (move[5] not in pieceSymbols.keys() or move[5] == "K"):
            raise MoveError("Pawn Promoted to an invalid piece", move[5])

    else:
        destFile = move[0]
        destRow = int(move[1])
        if 1 > destRow or 8 < destRow:
            raise MoveError("Invalid row")
        if ord("a") > ord(destFile) or ord("h") < ord(destFile):
            raise MoveError("Invalid file destination")
        if len(move) < 4:
            promotion = False
        else:
            promotion = True if move[2] == "=" else False

        if destRow in [1, 8] and not promotion:
            raise MoveError("Pawn reached end row and did not promote")

        if promotion and (move[3] not in pieceSymbols.keys() or move[3] == "K"):
            raise MoveError("Pawn Promoted to an invalid piece", move[3])

def rookLegalityChecker(origin : str | None, dest : str):

    destFile = dest[0]
    destRow = int(dest[1])
    if 1 > destRow or 8 < destRow:
        raise MoveError("Invalid row destination")
    if ord("a") > ord(destFile) or ord("h") < ord(destFile):
        raise MoveError("Invalid file destination")

    if origin:
        if len(origin) == 1:
            if origin in string.ascii_lowercase:
                originFile = origin[0]
                originRow = destRow
            else:
                originRow = int(origin[0])
                originFile = destFile
        else:
            originFile = origin[0]
            originRow = int(origin[1])

        if ord("a") > ord(originFile) or ord("h") < ord(originFile):
            raise MoveError("Invalid file of origin")
        if 1 > originRow or 8 < originRow:
            raise MoveError("Invalid row of origin")

        if destRow != originRow and destFile != originFile:
            raise MoveError(f"Rook attempting to move diagonally {originFile}{originRow}->{destFile}{destRow}")

def bishopLegalityChecker(origin : str | None, dest : str):

    destFile = dest[0]
    destRow = int(dest[1])
    if 1 > destRow or 8 < destRow:
        raise MoveError("Invalid row destination")
    if ord("a") > ord(destFile) or ord("h") < ord(destFile):
        raise MoveError("Invalid file destination")
    if not origin:
        return
    if len(origin) == 2:
        originFile = origin[0]
        originRow = int(origin[1])

        if ord("a") > ord(originFile) or ord("h") < ord(originFile):
            raise MoveError("Invalid file of origin")
        if 1 > originRow or 8 < originRow:
            raise MoveError("Invalid row of origin")

        difInFile = ord(originFile) - ord(destFile)
        difInRow = originRow - destRow

        if difInFile != difInRow:
            raise MoveError(f"Bishop attempting to move non-diagonally {originFile}{originRow}->{destFile}{destRow}")
    else:
        if origin in string.ascii_lowercase:
            if origin == destFile: raise MoveError("Bishop cannot remain on the same file when moving")
        else:
            if int(origin) == destRow: raise MoveError("Bishop cannot remain on the same row when moving")

def knightLegalityChecker(origin : str | None, dest : str):

    destFile = dest[0]
    destRow = int(dest[1])
    if 1 > destRow or 8 < destRow:
        raise MoveError("Invalid row destination")
    if ord("a") > ord(destFile) or ord("h") < ord(destFile):
        raise MoveError("Invalid file destination")
    if not origin:
        return
    if len(origin) == 2:
        originFile = origin[0]
        originRow = int(origin[1])

        if ord("a") > ord(originFile) or ord("h") < ord(originFile):
            raise MoveError("Invalid file of origin")
        if 1 > originRow or 8 < originRow:
            raise MoveError("Invalid row of origin")

        difInFile = abs(ord(originFile) - ord(destFile))
        difInRow = abs(originRow - destRow)

        if (difInFile != 1 or difInRow != 2) and (difInFile != 2 or difInRow != 1):
            raise MoveError(f"Knight attempting to move in an invalid shape {originFile}{originRow}->{destFile}{destRow}")
    else:
        if origin in string.ascii_lowercase:
            if origin == destFile: raise MoveError("Knight cannot remain on the same file when moving")
            if not abs(ord(origin) - ord(destFile)) in [1,2]: raise MoveError(f"Knight attempting to move in an invalid shape {origin}x->{destFile}{destRow}")
        else:
            if int(origin) == destRow: raise MoveError("Knight cannot remain on the same row when moving")
            if not abs(int(origin) - destRow) in [1,2]: raise MoveError(f"Knight attempting to move in an invalid shape x{origin}->{destFile}{destRow}")

def readInputMoveAndReturnDescription(move : str):
    out = ""
    if move[0] in string.ascii_lowercase:
        # Pawn Move
        pawnLegalityChecker(move)
        if move[1] == "x":

            # Pawn Capture

            out += f"The {move[0]} pawn took the piece on {move[2:4]}"
            move = move[4:]
        else:

            # No capture

            out += f"The {move[0]} pawn moved to {move}"
            move = move[2:]
        if not move:
            return out

        if move[0] == "=":
            out += f" and promoted to a {pieceSymbols[move[1]]}"
            move = move[2:]

        if not move:
            return out

        if move[0] == "+":
            out += " with check"

        elif move[0] == "#":
            out += " with checkmate"

        else:

            raise ValueError("I fucked up somewhere, this should never appear please raise an issue with your move")

        return out

    if move[0] == "O":

        if len(move) > 4:

            # Long castle

            out += "Castled Queen Side (Long Castle)"

        else:

            # Short Castle

            out += "Castled King Side (Short Castle)"

        match move[-1]:
            case "+":
                out += " with check"
            case "#":
                out += " with checkmate"

            case _: pass

        return out

    # Major piece

    check = True if move[-1] in ["+", "#"] else False
    piece = pieceSymbols[move[0]]
    out += piece
    if len(move) == 3 + check:

        # No tomfoolery
        out += " moved to " + move[1:3]
        dest = move[1:3]
        origin = None

    elif len(move) == 4 + check:

        # unknown tomfoolery

        if move[1] == "x":

            # takefoolery

            out += " took on " + move[2:4]

            dest = move[2:4]
            origin = None

        else:

            # minor tomfoolery

            out += " on " + move[1] + " moved to " + move[2:4]
            dest = move[2:4]
            origin = move[1]

    elif len(move) == 5 + check:

        if move[2] == "x":

            out += " on " + move[1] + " took on " + move[3:5]
            dest = move[3:5]
            origin = move[1]

        else:

            # Major tomfoolery

            out += " on " + move[1:3] + " moved to " + move[3:5]
            dest = move[3:5]
            origin = move[1:3]

    else:

        out += " on " + move[1:3] + " took on to " + move[4:6]
        dest = move[4:6]
        origin = move[1:3]

    match move[0]: # type: ignore
        case "R":
            rookLegalityChecker(origin, dest)
        case "B":
            bishopLegalityChecker(origin, dest)
        case "K":
            kingLegalityChecker(dest)
        case "Q":
            try:
                bishopLegalityChecker(origin,dest)
                bishPass = True
            except MoveError as e:
                bishPass = False
                b = e
            try:
                rookLegalityChecker(origin,dest)
                rookPass = True
            except MoveError as e:
                rookPass = False
                r = e
            if not bishPass and not rookPass:
                raise MoveError(f"Queen failed to move as both rook or bishop Rook: {r} Bishop: {b}") #type: ignore

        case "N":
            knightLegalityChecker(origin, dest)


    if move[-1] == "+": out += " with check"
    elif move[-1] == "#": out += " with checkmate"

    return out

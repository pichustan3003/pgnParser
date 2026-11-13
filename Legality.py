import string
from Parser import piece 
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
    start = ""
    final = ""
    genMovCode = ""
    if move[0] in string.ascii_lowercase:
        if len(move) == 2:
            final = move
            genMovCode = "p"
        if move[1] == "x" and len(move) == 4:
            final = move
            genMovCode = "px"
        if len(move) == 3 and move[-1] == "+":
            final = move[0:2]
            genMovCode = "p+"
        if len(move) == 5 and move[-1] == "+":
            final = move[:-1]
            genMovCode = "px+"
    return start, final, genMovCode

def squareFree(square : str, pieces : list[str]):
    return square not in pieces

def checkLegalityWithBoardPosition(move: str, board : list[piece], side : int):
    start, final, genMovCode = deserialise(move)
    global usedSquares
    usedSquares = [p.file + str(p.rank) for p in board]
    match genMovCode:
        case "p":
            board, _ = p(board, final, side)
        case "px":
            board, _ = px(board, final, side)
        case "p+":
            board, _ = pc(board, final, side)
        case "px+":
            board, _ = pxc(board, final, side)
        case _: pass
    return board

def p(board : list[piece], final : str, side : int):
    if not squareFree(final, usedSquares):
        raise MoveError("move cannot be made (Square is not free for pawn to move to)")
    usedPiece = None
    for piece in board:
        if piece.piece == "P" and piece.color == side:
            if (piece.rank + 1 * side == int(final[-1]) or (piece.rank + 2 * side == int(final[-1]) and piece.moved == 0)) and piece.file == final[0]:
                usedPiece = piece
                piece.file, piece.rank = final[0], int(final[1])
                break
    else:
        raise MoveError("No pawn can make this move")
    return board, usedPiece

def px(board : list[piece], final : str, side : int):
    pawn = piece("", 0, "", 0)
    foe = False
    attacker = False
    moveTo = final[2:4]
    for p in board:
        if f"{p.file}{p.rank}" == moveTo and p.color == side * -1:
            
            board.pop(board.index(p))
            foe = True
        elif abs(ord(p.file) - ord(moveTo[0])) == 1 and int(moveTo[1])-p.rank == side and p.file == final[0]:
            p.file = moveTo[0]
            p.rank = int(moveTo[1])
            pawn = p
            attacker = True

        if foe and attacker:
            break
    else:
        if not foe: raise MoveError("No piece on square required" if attacker else "No piece on square required and no pawn can make this move")
        if not attacker: raise MoveError("No piece on square required and no pawn can make this move")
    return board, pawn

def pc(board : list[piece], final : str, side : int):
    file, rank = "", 0
    for pc in board:
        if pc.piece == "K" and pc.color != side:
            file = pc.file
            rank = pc.rank
            break
    else:
        raise MoveError("This cannot be check as no king could be found")

    board, pawn = p(board, final, side)
    if file+str(rank) in returnAllSquaresPieceCanHit(pawn, board):
        return board, pawn
    raise MoveError("This is not check")

def pxc(board : list[piece], final : str, side : int):
    file, rank = "", 0
    for pc in board:
        if pc.piece == "K" and pc.color != side:
            file = pc.file
            rank = pc.rank
            break
    else:
        raise MoveError("This cannot be check as no king could be found")

    board, pawn = px(board, final, side)
    if file+str(rank) in returnAllSquaresPieceCanHit(pawn, board):
        return board, pawn
    raise MoveError("This is not check")

def returnAllSquaresPieceCanHit(piece : piece, board : list[piece]):
    usedSquares = [p.file + str(p.rank) for p in board]
    side = piece.color
    match piece.piece:
        case "P":
            attacks : list[str] = [f"{chr(ord(piece.file)+1)}{piece.rank+1*side}", f"{chr(ord(piece.file)-1)}{piece.rank+1*side}"]
            for a in attacks:
                if not squareFree(a, usedSquares):
                    for p in board:
                        if p.file + str(p.rank) == a and p.color == piece.color:
                            attacks.pop(attacks.index(a))
        case _: raise ValueError("Invalid piece name? Somehow?")
    return attacks

def kingLegalityChecker(move : str):

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

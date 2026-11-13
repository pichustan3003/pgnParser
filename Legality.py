import string
from Parser import piece, game
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
        elif move[1] == "x" and len(move) == 4:
            start = move[0]
            final = move[2:4]
            genMovCode = "px"
        elif len(move) == 3 and move[-1] == "+":
            final = move[0:2]
            genMovCode = "p+"
        elif len(move) == 5 and move[-1] == "+":
            start = move[0]
            final = move[:-1]
            genMovCode = "px+"
        elif len(move) == 3 and move[-1] == "#":
            final = move[0:2]
            genMovCode = "p#"
        elif len(move) == 5 and move[-1] == "#":
            start = move[0]
            final = move[:-1]
            genMovCode = "px#"
    if (move[0] == "K"):
        if len(move) == 3:
            final = move[1:3]
            genMovCode = "k"
        elif move[1] == "x" and len(move) == 4:
            final = move[2:4]
            genMovCode = "kx"
    return start, final, genMovCode

def squareFree(square : str, pieces : list[str]):
    return square not in pieces

def checkLegalityWithBoardPosition(move: str, board : list[piece], side : int, parent : game):
    start, final, genMovCode = deserialise(move)
    global usedSquares
    global overallParent
    overallParent = parent
    usedSquares = [p.file + str(p.rank) for p in board]
    match genMovCode:
        case "p":
            board, out, oldF, oldR = p(board, final, side)
        case "px":
            board, out, oldF, oldR = px(board, start, final, side)
        case "p+":
            board, out, oldF, oldR = pc(board, final, side)
        case "px+":
            board, out, oldF, oldR = pxc(board, start, final, side)
        case "p#":
            board, out, oldF, oldR = pm(board, final, side)
        case "px#":
            board, out, oldF, oldR = pxm(board, start, final, side)
        case "k":
            board, out, oldF, oldR = k(board, final, side)
        case "kx":
            board, out, oldF, oldR = kx(board, final, side)
        case _: raise MoveError("Cannot read move")
    if isCheck(board, side):
        raise MoveError("This would put your king in check")
    out.moved = True
    return board, out, oldF, oldR

def p(board : list[piece], final : str, side : int):
    if not squareFree(final, usedSquares):
        raise MoveError("move cannot be made (Square is not free for pawn to move to)")
    usedPiece = None
    for piece in board:
        if piece.piece == "P" and piece.color == side:
            if (piece.rank + 1 * side == int(final[-1]) or (piece.rank + 2 * side == int(final[-1]) and piece.moved == 0)) and piece.file == final[0]:
                usedPiece = piece
                oldF, oldR = piece.file, piece.rank
                piece.file, piece.rank = final[0], int(final[1])
                break
    else:
        raise MoveError("No pawn can make this move")
    return board, usedPiece, oldF, oldR

def px(board: list[piece], start: str, final: str, side: int):

    # Find the moving pawn
    pawn = next(
        (p for p in board
         if f"{p.file}" == start and p.color == side and p.piece == "P"),
        None
    )

    if pawn is None:
        raise MoveError("No pawn on starting square")

    oldF, oldR = pawn.file, pawn.rank

    # Check that the pawn is moving diagonally forwards
    if abs(ord(final[0]) - ord(start[0])) != 1 or int(final[1]) - pawn.rank != side:
        raise MoveError("Invalid pawn capture")

    # Check for a normal capture
    victim = next(
        (p for p in board
         if f"{p.file}{p.rank}" == final and p.color == -side),
        None
    )

    # If there isn't a normal capture, check en passant
    if victim is None:

        q = overallParent.query("MOVE -1")

        # Square containing the pawn that could be captured
        enPasSquare = f"{final[0]}{pawn.rank}"

        if (
            q.piece.piece == "P"
            and q.origin[0] == q.destination[0]
            and abs(int(q.origin[1]) - int(q.destination[1])) == 2
            and q.destination == enPasSquare
        ):
            victim = next(
                (p for p in board
                    if f"{p.file}{p.rank}" == enPasSquare
                    and p.color == -side
                    and p.piece == "P"),
                None
            )

        if victim is None:
            raise MoveError("No piece on square required")

    # Remove captured piece
    board.remove(victim)

    # Move the pawn
    pawn.file = final[0]
    pawn.rank = int(final[1])

    return board, pawn, oldF, oldR

def pc(board : list[piece], final : str, side : int):
    board, pawn, oldF, oldR = p(board, final, side)
    if isCheck(board, side*-1):
        return board, pawn, oldF, oldR
    raise MoveError("This is not check")

def pxc(board : list[piece], start : str, final : str, side : int):
    board, pawn, oldF, oldR = px(board, final, start, side)
    if isCheck(board, side*-1):
        return board, pawn, oldF, oldR
    raise MoveError("This is not check")

def pm(board : list[piece], final : str, side : int):
    board, pawn, oldF, oldR = p(board, final, side)
    if isMate(board, side*-1):
        return board, pawn, oldF, oldR
    raise MoveError("This is not mate")

def pxm(board : list[piece], start : str, final : str, side : int):
    board, pawn, oldF, oldR = px(board, final, start, side)
    if isMate(board, side*-1):
        return board, pawn, oldF, oldR
    raise MoveError("This is not mate")

def k(board : list[piece], final : str, side : int):
    king = None
    for p in board:
        if p.piece == "K" and side == p.color:
            king = p
            break
    else:
        raise MoveError("Cannot find king")
    atk = kingAttacks(king, board)
    oldF, oldR = king.file, king.rank
    if final in atk:
        king.file, king.rank = final[0], int(final[1])
    else:
        raise MoveError("Cannot make move")
    return board, king, oldF, oldR

def kx(board : list[piece], final : str, side : int):
    vict = findPieceOnSquare(final, board)
    board, king, oldF, oldR = k(board, final, side)
    if vict:
        board.remove(vict)
    return board, king, oldF, oldR

def isCheck(board : list[piece], side : int):
    """
    Checks if king is currently in check based off the board position (SIDE REFERS TO THE SIDE THE KING IS ON NOT THE CHECK GIVER)
    """
    attacks : list[str]= []
    king = None
    for i in board:
        if i.piece == "K" and i.color == side:
            king = i
        else:
            if i.color == side:
                continue
            attacks += returnAllSquaresPieceCanHit(i, board)
    if not king: raise ValueError("Cannot find king")
    return king.file + str(king.rank) in attacks

def isMate(board : list[piece], side : int):
    """
    Checks if king is currently in checkmate based off the board position (SIDE REFERS TO THE SIDE THE KING IS ON NOT THE CHECK GIVER)
    """
    attacks : list[str]= []
    king = None
    for i in board:
        if i.piece == "K" and i.color == side:
            king = i
        else:
            if i.color == side:
                continue
            attacks += returnAllSquaresPieceCanHit(i, board)
    if not king: raise ValueError("Cannot find king")
    kingSpots = returnAllSquaresPieceCanHit(king, board) + [king.file + str(king.rank)]
    for s in kingSpots:
        if s not in attacks:
            return False
    return True

def findPieceOnSquare(square : str, board : list[piece]) -> (piece | None):
    for p in board:
        if p.file + str(p.rank) == square:
            return p
    else: return None

def returnAllSquaresPieceCanHit(piece : piece, board : list[piece]):
    match piece.piece:
        case "P":
            attacks = pawnAttacks(piece, board)
        case "K":
            attacks = kingAttacks(piece, board)
        case "N":
            attacks = knightAttacks(piece, board)
        case "B":
            attacks = bishopAttacks(piece, board)
        case "R":
            attacks = rookAttacks(piece, board)
        case "Q":
            attacks = rookAttacks(piece, board) + bishopAttacks(piece, board)
        case _: raise ValueError("Invalid piece name? Somehow?")
    attacksF : list[str] = []
    for a in attacks:
        if ord("a") <= ord(a[0]) <= ord("h") and 1 <= int(a[1:]) <= 8:
            attacksF.append(a)
    return attacksF

def getOwnColorPieces(board : list[piece], side : int):
    return [x.file + str(x.rank) for x in board if x.color == side]

def pawnAttacks(piece : piece, board : list[piece]):
    attacks : list[str] = [f"{chr(ord(piece.file)+1)}{piece.rank+1*piece.color}", f"{chr(ord(piece.file)-1)}{piece.rank+1*piece.color}"]
    temp : list[str] = []
    usedSquares = [p.file + str(p.rank) for p in board]
    for a in attacks:
        if not squareFree(a, usedSquares):
            for p in board:
                if not (p.file + str(p.rank) == a and p.color == piece.color):
                    temp.append(a)
    return temp

def kingAttacks(piece : piece, board : list[piece]):
    attacks : list[str] = []
    ownColorPieces = getOwnColorPieces(board, piece.color)
    for i in range(-1,2):
        for j in range(-1,2):
            attacks.append(chr(ord(piece.file)+i)+str(piece.rank+j))
    tempAttacks : list[str] = []
    for an in range(len(attacks)):
        a = attacks[an]
        if a not in ownColorPieces:
            tempAttacks.append(a)
    attacks = tempAttacks
    return attacks

def knightAttacks(piece : piece, board : list[piece]):
    attacks = [f"{chr(ord(piece.file)+1)}{piece.rank+2}", f"{chr(ord(piece.file)+2)}{piece.rank+1}", f"{chr(ord(piece.file)+2)}{piece.rank-1}",f"{chr(ord(piece.file)+1)}{piece.rank-2}",f"{chr(ord(piece.file)-1)}{piece.rank-2}", f"{chr(ord(piece.file)-2)}{piece.rank-1}", f"{chr(ord(piece.file)-2)}{piece.rank+1}", f"{chr(ord(piece.file)-1)}{piece.rank+2}"]
    tempAttacks : list[str] = []
    ownColorPieces = getOwnColorPieces(board, piece.color)
    for an in range(len(attacks)):
        a = attacks[an]
        if a not in ownColorPieces:
            tempAttacks.append(a)
    attacks = tempAttacks
    return attacks

def rookAttacks(piece : piece, board : list[piece]):
    arrangements = [(1,0),(-1,0),(0,-1),(0,1)]
    ownColorPieces = getOwnColorPieces(board, piece.color)
    attacks : list[str] = []
    for i in range(4):
        hor = arrangements[i][0]
        ver = arrangements[i][1]
        rnk = piece.rank
        fle = ord(piece.file)
        while chr(fle+hor)+str(rnk+ver) not in ownColorPieces and (ord('a')<=fle+hor<=ord('h')) and (1<=rnk+ver<=8):
            attacks.append(chr(fle+hor)+str(rnk+ver))
            if findPieceOnSquare(chr(fle+hor)+str(rnk+ver), board):
                break
            rnk += ver
            fle += hor
    return attacks

def bishopAttacks(piece : piece, board : list[piece]):
    arrangements = [(1,1),(-1,1),(1,-1),(-1,-1)]
    ownColorPieces = getOwnColorPieces(board, piece.color)
    attacks : list[str] = []
    for i in range(4):
        hor = arrangements[i][0]
        ver = arrangements[i][1]
        rnk = piece.rank
        fle = ord(piece.file)
        while chr(fle+hor)+str(rnk+ver) not in ownColorPieces and (ord('a')<=fle+hor<=ord('h')) and (1<=rnk+ver<=8):
            attacks.append(chr(fle+hor)+str(rnk+ver))
            if findPieceOnSquare(chr(fle+hor)+str(rnk+ver), board):
                break
            rnk += ver
            fle += hor
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

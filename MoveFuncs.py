from Parser import piece

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
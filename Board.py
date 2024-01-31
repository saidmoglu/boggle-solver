class XY:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

class BoardCell:
    def __init__(self, char, is_yellow=False) -> None:
        self.char = char
        self.is_yellow = is_yellow

class Board:
    def __init__(self, board) -> None:
        self.board = board
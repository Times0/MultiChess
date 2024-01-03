import enum


class Side(enum.Enum):
    QUEEN = 0
    KING = 1


class Square:
    def __init__(self, *args):
        if len(args) == 1:
            square_string = args[0]
            self.j = ord(square_string[0]) - 97
            self.i = int(square_string[1]) - 1
        else:
            self.i = args[0]
            self.j = args[1]

    def __str__(self):
        return f"{chr(self.j + 97)}{self.i + 1}"

    def __repr__(self):
        return f"{chr(self.j + 97)}{self.i + 1}"

    def __eq__(self, other):
        return self.i == other.i and self.j == other.j

    def __hash__(self):
        return hash((self.i, self.j))


class Move:
    def __init__(self, origin: Square, destination: Square, is_check: bool = False, is_capture: bool = False,
                 promotion: str = None):
        self.origin = origin
        self.destination = destination
        self.promotion = promotion

        self.is_capture = is_capture
        self.is_check = is_check

    def __eq__(self, other):
        return self.origin == other.origin and self.destination == other.destination

    def __str__(self):
        s = f"{self.origin} -> {self.destination}"
        if self.is_check:
            s += " *"
        return s

    def __repr__(self):
        return self.__str__()

    def get_uci(self):
        return f"{self.origin}{self.destination}"

from enum import IntEnum


class Strand(IntEnum):
    UNKNOWN = 0
    PLUS = 1
    MINUS = -1

    @classmethod
    def from_char(cls, char: str | bytes) -> "Strand":
        if isinstance(char, bytes):
            char = char.decode()
        if char == "+":
            return cls.PLUS
        elif char == "-":
            return cls.MINUS
        return cls.UNKNOWN

    @classmethod
    def from_int(cls, value: int) -> "Strand":
        if value == 1:
            return cls.PLUS
        elif value == -1:
            return cls.MINUS
        return cls.UNKNOWN

    def to_char(self) -> str:
        if self == Strand.PLUS:
            return "+"
        elif self == Strand.MINUS:
            return "-"
        return "?"
    
    def flip(self) -> "Strand":
        if self == Strand.PLUS:
            return Strand.MINUS
        elif self == Strand.MINUS:
            return Strand.PLUS
        return self

    def __str__(self) -> str:
        return self.to_char()
class Tile:
    """
    characters(m): 1m -9m
    dots(p): 1p - 9p
    bamboo(s): 1s - 9s
    honors(z): East(E), South(S), West(W), North(N), White(P), Green(F), Red(C)
    """

    def __init__(self, suit, value):
        """
        suit: 'm', 'p', 's', 'z'
        value: 0-9 for m/p/s (0 represents for red 5 tiles), 'E','S','W','N','P','F','C' for z
        """
        self.suit = suit
        self.value = value

    def __repr__(self):
        if self.suit == 'z':
            return str(self.value)
        return f"{self.value}{self.suit}"

    def __eq__(self, other):
        return self.suit == other.suit and self.value == other.value

    def __hash__(self):
        return hash((self.suit, self.value))



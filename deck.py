import random

# Ranks: 2-9, T, J, Q, K, A (0-12)
# Suits: s, h, d, c (0-3)
# To map to phevaluator, cards can be strings like "2s", "Ah"

RANKS = "23456789TJQKA"
SUITS = "shdc"

class Deck:
    def __init__(self):
        self.cards = [r + s for r in RANKS for s in SUITS]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self, n=1):
        if n == 1:
            return self.cards.pop()
        return [self.cards.pop() for _ in range(n)]

    def get_remaining(self):
        return len(self.cards)

    @staticmethod
    def get_all_cards():
        return [r + s for r in RANKS for s in SUITS]

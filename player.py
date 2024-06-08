from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from deck import Deck


class Player:
    """A class to represent a player in the hearts game"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.hand: list[Deck.Card] = []
        self.points = 0

    def set_hand(self, hand: 'list[Deck.Card]'):
        self.hand = hand

    def __str__(self):
        return self.name

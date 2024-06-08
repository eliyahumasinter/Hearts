
from deck import Deck


class Player:
    """A class to represent a player in the hearts game"""

    def __init__(self, name: str) -> None:
        self.name = name
        self.hand: list[Deck.Card] = []
        self.total_score = 0
        self.round_score = 0  # The score of the player in the current round
        # A list of tricks taken by the player in the current round
        self.tricks_taken: list[TRICK] = []

    def set_hand(self, hand: list[Deck.Card]):
        self.hand = hand

    def finish_round(self):
        self.total_score += self.round_score
        # TODO: Check if the player has shot the moon
        self.round_score = 0
        self.tricks_taken = []

    def __repr__(self):
        return self.name


TRICK = dict[Player, Deck.Card]

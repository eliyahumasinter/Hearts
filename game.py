from player import Player
from deck import Deck


class Game:
    def __init__(self, players: list[Player]):
        self.players = players
        self.deck = Deck()
        self.hands = self.deck.deal()
        for i, player in enumerate(self.players):
            player.set_hand(self.hands[i])

    def print_current_hands(self):
        for player in self.players:
            print(f"{player}: ", end="")
            for card in player.hand:
                print(card, end=", ")
            print("\n\n", "-"*20, "\n")

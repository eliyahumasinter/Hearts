from player import Player
from deck import Deck


class BadPlayerListError(Exception):
    pass


class Game:
    def __init__(self, players: list[Player]):
        """Initialize the game with the given players and deal the cards. Ensure that there are a correct number of unique players
        Version 1.0 - Only supports 4 players

        Args:
            players (list[Player]): A list of players
        """

        if len(players) != 4 or len([player.name.lower() for player in players]) != 4:
            raise BadPlayerListError(
                "The game only supports 4 players. Please provide a list of 4 players with unique names.")

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

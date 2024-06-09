from typing import Callable, Optional, TYPE_CHECKING
from player import Player
from deck import Deck
from exceptions import BadPlayerListError
from round import Round
from settings import END_GAME_SCORE

if TYPE_CHECKING:
    from deck import SUIT


class Game:
    def __init__(self, players: list[Player], play_card: Callable[[Player, Optional['SUIT'], bool], Deck.Card], hearts_broken_hook: Callable[[], None], round_end_hook: Callable[[], None]) -> None:
        """Initialize the game with the given players and deal the cards. Ensure that there are a correct number of unique players
        Version 1.0 - Only supports 4 players

        Args:
            players (list[Player]): A list of players
        """

        if len(players) != 4 or len([player.name.lower() for player in players]) != 4:
            raise BadPlayerListError(
                "The game only supports 4 players. Please provide a list of 4 players with unique names.")

        self.players = players
        self.play_card = play_card
        self.hearts_broken_hook = hearts_broken_hook
        self.round_end_hook = round_end_hook
        self.deck = Deck()
        self.hands = self.deck.deal()
        for i, player in enumerate(self.players):
            player.set_hand(self.hands[i])

        self.round_count = 0
        self.current_round = None

    def pass_cards(self, player: Player, cards: list[Deck.Card]) -> None:
        """Method to pass cards from one player to another. This should be  called in the beginning of each round.
        We determine who to pass the cards to based on the round number.

        Args:
            player (Player): The player who is passing the cards
            cards (list[Deck.Card]): the three cards that the player is passing
        """
        pass

    def play_game(self) -> None:
        while max([player.total_score for player in self.players]) < END_GAME_SCORE:
            self.round = Round(self)  # type: ignore
            self.round.play_round()
            for player in self.players:
                player.finish_round()  # Update player scores and prepare for next round
            self.round_count += 1

            self.round_end_hook()

            break  # ! Remove this break statement

    def reset_game(self) -> None:
        self.deck = Deck()
        self.hands = self.deck.deal()
        for i, player in enumerate(self.players):
            player.set_hand(self.hands[i])

        self.round_count = 0
        self.trick_count = 0

    def print_current_hands(self) -> None:
        for player in self.players:
            print(f"{player}: ", end="")
            for card in Deck.sort_hand(player.hand):
                print(card, end=", ")
            print("\n\n", "-"*20, "\n")

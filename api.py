

from game import Game
from typing import Callable, Optional, TYPE_CHECKING
from player import Player


if TYPE_CHECKING:
    from deck import SUIT, Deck


class API:
    """
    API class for interacting with the Hearts game
    """

    """
    Methods: 
     - Initiate a game
     - Get the current hands
     - 
    """

    def __init__(self, play_card: Callable[['Player', Optional['SUIT'], bool], 'Deck.Card']):
        self.game = None
        self.play_card = play_card
        self.players: list[Player] = []

    def add_player(self, player_name: str):
        if player_name in self.players:
            raise ValueError("Player name already exists")
        if len(self.players) == 4:
            raise ValueError("Game already has 4 players")
        self.players.append(Player(player_name))

    def start_game(self):
        if len(self.players) != 4:
            raise ValueError("Game must have 4 players to start")

        # We can not be sure the play_card function is valid so we override it with a validated version
        def validate_play_card(player: Player, led_suit: Optional['SUIT'], is_leading: bool) -> 'Deck.Card':
            card = self.play_card(player, led_suit, is_leading)
            if card not in self.get_allowed_cards(player, led_suit, is_leading):
                raise ValueError("Invalid card played")
            return card

        self.game = Game(self.players, validate_play_card)
        self.game.play_game()

    def reset_game(self):
        if not self.game:
            raise ValueError("Game has not started")
        self.game.reset_game()

    def get_current_state(self):
        if not self.game:
            raise ValueError("Game has not started")

        state = {
            "round_count": self.game.round_count,
            "players": {
                player.name: {
                    "total_score": player.total_score,
                    "round_score": player.round_score,
                    "cards_taken":  [card.short_name() for card in self.sort_hand(player.cards_taken)],
                    "hand": [card.short_name() for card in self.sort_hand(player.hand)],
                } for player in self.game.players
            }
        }
        return state

    def get_allowed_cards(self, player: 'Player', led_suit: Optional['SUIT'], is_leading: bool):
        if not self.game:
            raise ValueError("Game has not started")

        allowed_cards = player.allowed_cards_to_play(
            self.game.round.current_trick, led_suit, is_leading)
        return allowed_cards

    def sort_hand(self, hand):
        if not self.game:
            raise ValueError("Game has not started")

        return self.game.deck.sort_hand(hand)

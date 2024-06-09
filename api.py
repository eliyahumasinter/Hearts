

from game import Game
from typing import Callable, Literal, Optional, TYPE_CHECKING
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

    def __init__(self) -> None:
        self.players: list[Player] = []

        # * Mandatory hooks
        # This hook gets called when a player needs to play a card
        self.play_card: Callable[[
            'Player', Optional['SUIT'], bool], 'Deck.Card'] | None = None
        # This hook gets called when a player needs to choose 3 cards to pass
        self.pass_cards: Callable[[
            'Player'], list['Deck.Card']] | None = None

        # *Optional hooks
        # This hook gets called when the round ends
        self.round_end_hook = lambda: None
        # This hook gets called when hearts are broken
        self.hearts_broken_hook = lambda: None
        # This hook gets called when the game ends
        self.end_game_hook = lambda: None
        # This hook gets called when the players have passed their cards, it sends which cards were passed
        self.passed_cards_hook: Callable[[
        ], dict['Player', list['Deck.Card']]] = lambda: {}

        self.game = None

    def set_play_card_hook(self, hook: Callable[['Player', Optional['SUIT'], bool], 'Deck.Card']):
        self.play_card = hook

    def set_get_pass_cards_hook(self, hook: Callable[['Player'], list['Deck.Card']]):
        self.pass_cards = hook

    def set_round_end_hook(self, hook: Callable[[], None]):
        self.round_end_hook = hook

    def set_passed_cards_hook(self, hook: Callable[[], dict['Player', list['Deck.Card']]]):
        self.passed_cards_hook = hook

    def set_hearts_broken_hook(self, hook: Callable[[], None]):
        self.hearts_broken_hook = hook

    def set_end_game_hook(self, hook: Callable[[], None]):
        self.end_game_hook = hook

    def add_player(self, player_name: str):
        if player_name in self.players:
            raise ValueError("Player name already exists")
        if len(self.players) == 4:
            raise ValueError("Game already has 4 players")
        self.players.append(Player(player_name))

    def get_pass_cards_validated(self, player: Player) -> list['Deck.Card']:
        if not self.game:
            raise ValueError("Game has not started")
        if player not in self.players:
            raise ValueError("Player is not in the game")
        cards = self.pass_cards(player)
        if not all([card in player.hand for card in cards]):
            raise ValueError("Player does not have all the cards")

        if len(cards) != 3:
            raise ValueError("You must pass exactly 3 cards")
        return cards

    def start_game(self):
        if len(self.players) != 4:
            raise ValueError("Game must have 4 players to start")
        if not self.play_card or not self.pass_cards:
            raise ValueError("Play card and pass cards hooks must be set")

        # We can not be sure the play_card function is valid so we override it with a validated version
        def play_card_validated(player: Player, led_suit: Optional['SUIT'], is_leading: bool) -> 'Deck.Card':
            card = self.play_card(player, led_suit, is_leading)  # type: ignore
            if card not in self.get_allowed_cards(player, led_suit, is_leading):
                raise ValueError("Invalid card played")
            return card

        self.game = Game(self.players,
                         play_card_validated,
                         self.get_pass_cards_validated,
                         self.hearts_broken_hook,
                         self.round_end_hook,
                         self.end_game_hook,
                         self.passed_cards_hook
                         )
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
                    "cards_taken":   self.sort_hand(player.cards_taken),
                    "hand": self.sort_hand(player.hand),
                } for player in self.game.players
            }
        }
        return state

    def get_player_state(self, player: 'Player'):
        if not self.game:
            raise ValueError("Game has not started")

        state = {
            "total_score": player.total_score,
            "round_score": player.round_score,
            "cards_taken":  self.sort_hand(player.cards_taken),
            "hand": self.sort_hand(player.hand),
            'passed_cards':  self.sort_hand(player.passed_cards) if player.passed_cards else None
        }
        return state

    def get_allowed_cards(self, player: 'Player', led_suit: Optional['SUIT'], is_leading: bool):
        if not self.game:
            raise ValueError("Game has not started")

        allowed_cards = player.allowed_cards_to_play(
            self.game.round.current_trick, led_suit, is_leading)
        return allowed_cards

    def get_passing_direction(self) -> Literal['left', 'right', 'across', 'hold']:
        if not self.game:
            raise ValueError("Game has not started")
        round_mod = self.game.round_count % 4
        match = {
            0: "left",
            1: "right",
            2: "across",
            3: "hold"
        }
        return match[round_mod]

    def sort_hand(self, hand):
        if not self.game:
            raise ValueError("Game has not started")

        return self.game.deck.sort_hand(hand)

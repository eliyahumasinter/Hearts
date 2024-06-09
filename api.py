
from inspect import signature, Parameter, _empty
from typing import Callable, Literal, Optional

from backend.exceptions import BadPlayerListError
from backend.game import Game
from backend.player import Player
from backend.deck import Deck, SUIT


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

    def set_end_game_score(self, score: int):
        """Set the score at which the game ends

        Args:
            score (int): positive integer

        """
        if not self.game:
            raise ValueError("Game has not started")
        if not isinstance(score, int) or score <= 0:
            raise ValueError("Score must be a positive integer")

        self.game.settings['END_GAME_SCORE'] = score

    def set_play_card_hook(self, hook: Callable[['Player', Optional[SUIT], bool], 'Deck.Card']):
        """Set the hook that will be called when a player needs to play a card. Get input from the user in any way you like.

        Args:
            hook (Callable[[Player, Optional[SUIT], bool], Deck.Card]): your function header should look like this
        """
        # Make sure the hook is a callable function that takes the correct arguments
        if not callable(hook):
            raise ValueError("Hook must be a callable function")
        sig = signature(hook)
        expected_params = [
            Parameter('player', Parameter.POSITIONAL_OR_KEYWORD,
                      annotation=Player),
            Parameter('led_suit', Parameter.POSITIONAL_OR_KEYWORD,
                      annotation=Optional[SUIT]),
            Parameter('is_leading', Parameter.POSITIONAL_OR_KEYWORD,
                      annotation=bool)
        ]
        expected_return_type = Deck.Card

        # Check if the parameters match
        if len(sig.parameters) != len(expected_params) or \
           any(sig.parameters[key].annotation != expected_params[index].annotation for index, key in enumerate(sig.parameters)):
            raise ValueError("Hook does not have the correct parameters")

        # Check if the return type matches
        if sig.return_annotation is not _empty and sig.return_annotation != expected_return_type:
            raise ValueError("Hook does not return the correct type")

        self.play_card = hook

    def set_get_pass_cards_hook(self, hook: Callable[['Player'], list['Deck.Card']]):
        """Set the hook that will be called when a player needs to pass cards. Get input from the user in any way you like.

        Args:
            hook (Callable[[Player], list[Deck.Card]]): your function header should look like this

        """

        # Make sure the hook is a callable function that takes the correct arguments
        if not callable(hook):
            raise ValueError("Hook must be a callable function")
        sig = signature(hook)
        expected_params = [
            Parameter('player', Parameter.POSITIONAL_OR_KEYWORD,
                      annotation=Player)
        ]
        expected_return_type = list[Deck.Card]

        # Check if the parameters match
        if len(sig.parameters) != len(expected_params) or \
                any(sig.parameters[key].annotation != expected_params[index].annotation for index, key in enumerate(sig.parameters)):
            raise ValueError("Hook does not have the correct parameters")

        # Check if the return type matches
        if sig.return_annotation is not _empty and sig.return_annotation != expected_return_type:
            raise ValueError("Hook does not return the correct type")

        self.pass_cards = hook

    def set_round_end_hook(self, hook: Callable[[], None]):
        """Set the hook that will be called when the round ends

        Args:
            hook (Callable[[], None]): the `round_end_hook` must be a callable function
        """
        if not callable(hook):
            raise ValueError("Hook must be a callable function")

        self.round_end_hook = hook

    def set_passed_cards_hook(self, hook: Callable[[], dict['Player', list['Deck.Card']]]):
        """Set the hook that will be called when the players have passed their cards, it sends which cards were passed

        Args:
            hook (Callable[[], dict[Player, list[Deck.Card]]]): the `passed_cards_hook` must be a callable function
        """
        if not callable(hook):
            raise ValueError("Hook must be a callable function")

        self.passed_cards_hook = hook

    def set_hearts_broken_hook(self, hook: Callable[[], None]):
        """Hook that will be called when hearts are broken

        Args:
            hook (Callable[[], None]): 
        """
        if not callable(hook):
            raise ValueError("Hook must be a callable function")
        self.hearts_broken_hook = hook

    def set_end_game_hook(self, hook: Callable[[], None]):
        """Hook that will be called when the game ends

        Args:
            hook (Callable[[], None]): 
        """
        if not callable(hook):
            raise ValueError("Hook must be a callable function")

        self.end_game_hook = hook

    def add_player(self, player_name: str):
        """Add a player to the game

        Args:
            player_name (str): The name of the player

        """
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
        try:
            self.game = Game(self.players,
                             play_card_validated,
                             self.get_pass_cards_validated,
                             self.hearts_broken_hook,
                             self.round_end_hook,
                             self.end_game_hook,
                             self.passed_cards_hook
                             )
        except BadPlayerListError as e:
            raise ValueError(str(e))

        self.game.play_game()

    def reset_game(self):
        '''Reset the game to the initial state'''

        if not self.game:
            raise ValueError("Game has not started")
        self.game.reset_game()

    def get_current_state(self):
        '''
        Get the current state of the game'''
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
        '''Get the state of a player in the game'''
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
        '''Get the cards that the player is allowed to play in the current trick.'''
        if not self.game:
            raise ValueError("Game has not started")

        allowed_cards = player.allowed_cards_to_play(
            self.game.round.hearts_broken, self.game.round_count == 0, led_suit, is_leading)
        return allowed_cards

    def get_passing_direction(self) -> Literal['left', 'right', 'across', 'hold']:
        '''Get the direction in which the player should pass cards in the current round. Note, this is informational only. Passing is handled by the game automatically.'''
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
        '''Sort the hand of the player'''
        if not self.game:
            raise ValueError("Game has not started")

        return self.game.deck.sort_hand(hand)

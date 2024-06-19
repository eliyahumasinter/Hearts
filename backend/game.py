from typing import Callable, Optional, TYPE_CHECKING
from backend.player import Player
from backend.deck import Deck
from backend.exceptions import BadPlayerListError
from backend.round import Round

if TYPE_CHECKING:
    from backend.deck import SUIT


class Game:
    def __init__(self,
                 players: list[Player],
                 play_card: Callable[[Player, Optional['SUIT'], bool], Deck.Card],
                 get_pass_cards: Callable[[Player], list[Deck.Card]],
                 hearts_broken_hook: Callable[[], None],
                 round_end_hook: Callable[[], None],
                 trick_end_hook: Callable[[Round.Trick], None],
                 end_game_hook: Callable[[], None],
                 passed_cards_hook: Callable[[dict[Player, list[Deck.Card]]], None],
                 settings={'END_GAME_SCORE': 50, 'JACK_NEGATIVE': True}
                 ) -> None:
        """Initialize the game with the given players and deal the cards. Ensure that there are a correct number of unique players
        Version 1.0 - Only supports 4 players

        Args:
            players (list[Player]): A list of players
        """

        if len(players) != 4 or len([player.name.lower() for player in players]) != 4:
            raise BadPlayerListError(
                "The game only supports 4 players. Please provide a list of 4 players with unique names.")

        self.players = players
        self.settings = settings

        # Hook that will be called when a player needs to play a card, it will return a valid card to play
        self.play_card = play_card
        # Hook that will be called when a player needs to pass cards, it will return a list of 3 valid cards to pass
        self.get_pass_cards = get_pass_cards

        self.hearts_broken_hook = hearts_broken_hook
        self.trick_end_hook = trick_end_hook
        self.round_end_hook = round_end_hook
        self.end_game_hook = end_game_hook
        self.passed_cards_hook = passed_cards_hook

        self.deck = Deck()

        self.current_round = None
        # The number of rounds that have been played in this game
        self.round_count = 0

    def pass_cards(self, player: Player, cards: list[Deck.Card]) -> None:
        """Method to pass cards from one player to another. This should be  called in the beginning of each round.
        We determine who to pass the cards to based on the round number.

        Args:
            player (Player): The player who is passing the cards
            cards (list[Deck.Card]): the three cards that the player is passing
        """
        if len(cards) != 3:
            raise ValueError("You must pass exactly 3 cards")
        if not all([card in player.hand for card in cards]):
            raise ValueError("You must pass cards that are in your hand")

        player.hand = [card for card in player.hand if card not in cards]
        # Pass the cards to the correct player
        if self.round_count % 4 == 0:  # pass to the left
            other = self.players[(self.players.index(player) - 1) % 4]
        elif self.round_count % 4 == 1:  # pass to the right
            other = self.players[(self.players.index(player) + 1) % 4]
        elif self.round_count % 4 == 2:  # pass across
            other = self.players[(self.players.index(player) + 2) % 4]
        else:  # Hold hand
            raise ValueError("You should not be passing cards on a hold round")

        # We don't want to put the cards in the hand yet until everyone has passed
        other.passed_cards.extend(cards)

    def play_game(self) -> None:
        """Main play loop for the game. We keep playing rounds until a player reaches the end game score.
        """
        while max([player.total_score for player in self.players]) < self.settings['END_GAME_SCORE']:
            self.hands = self.deck.deal()
            for i, player in enumerate(self.players):
                player.set_hand(self.hands[i])

            # Pass cards
            if self.round_count % 4 != 3:
                for player in self.players:
                    cards = self.get_pass_cards(player)

                    self.pass_cards(player, cards)
                # Put the passed cards in the hand
                passed_cards = {}
                for player in self.players:
                    player.hand.extend(player.passed_cards)
                    passed_cards[player] = player.passed_cards
                    player.passed_cards = []

            self.round = Round(self)  # type: ignore
            self.round.play_round()
            for player in self.players:
                player.finish_round()  # Update player scores and prepare for next round

            self.round_count += 1
            self.round_end_hook()  # Call round end hook
        self.end_game_hook()  # Call end game hook

    def reset_game(self) -> None:
        """
        Reset the game to the initial state
        """
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

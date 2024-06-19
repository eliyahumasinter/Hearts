from __future__ import annotations
from typing import TYPE_CHECKING, Optional

from backend.exceptions import NoLegalMovesError

if TYPE_CHECKING:
    from deck import SUIT, Deck
    from round import Round


class Player:
    """A class to represent a player in the hearts game"""

    def __init__(self, name: str, am_bot=False) -> None:
        self.name = name
        self.am_bot = am_bot  # Am I a bot?
        self.hand: list[Deck.Card] = []
        self.total_score = 0
        self.round_score = 0  # The score of the player in the current round
        # A list of tricks taken by the player in the current round
        self.cards_taken: list['Deck.Card'] = []
        # The cards that the player has passed
        self.passed_cards: list['Deck.Card'] = []

    def set_hand(self, hand: list['Deck.Card']):
        self.hand = hand

    def finish_round(self):
        self.total_score += self.round_score
        # TODO: Check if the player has shot the moon
        self.round_score = 0
        self.cards_taken = []
        self.passed_cards = []

    def allowed_cards_to_play(self, hearts_broken: bool, first_round: bool, led_suit: Optional['SUIT'], is_leading: bool) -> list['Deck.Card']:
        """Get the cards that the player is allowed to play in the current trick.

        Args:
            hearts_broken (bool): True if hearts has been broken, False otherwise
            first_round (bool): True if it is the first round, False otherwise

            led_suit (Optional[SUIT]): The suit that was led in the trick, None if the player is leading (except first round where it is clubs)
            is_leading (bool): true if the player is leading the trick, false otherwise



        Returns:
            list[Deck.Card]: The cards that the player is allowed to play
        """

        void_in_led_suit = led_suit and not any(
            [card.suit == led_suit for card in self.hand])
        only_hearts_left = all([card.suit == "hearts" for card in self.hand])
        if first_round:
            if is_leading:
                # We must have the 2 of clubs
                result = [card for card in self.hand if card.suit ==
                          "clubs" and card.rank == 2]
            else:
                if void_in_led_suit:  # Play any non point card
                    # Play any card if no non point card is found
                    result = [card for card in self.hand if card.points()
                              <= 0] or self.hand
                else:
                    result = [
                        card for card in self.hand if card.suit == "clubs"]

        else:  # Not the first round
            if led_suit is None:  # Player is leading
                if hearts_broken or only_hearts_left:
                    result = self.hand
                else:
                    result = [
                        card for card in self.hand if card.suit != "hearts"]
            else:  # someone else led
                if void_in_led_suit:
                    result = self.hand
                else:
                    # Play the same suit if possible
                    result = [
                        card for card in self.hand if card.suit == led_suit]
        if not result:
            raise NoLegalMovesError("No legal moves for player")
        return result

    def __repr__(self):
        return self.name

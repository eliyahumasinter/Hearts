from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from deck import SUIT, Deck
    from round import Round


class Player:
    """A class to represent a player in the hearts game"""

    def __init__(self, name: str) -> None:
        self.name = name
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

    def allowed_cards_to_play(self, trick: 'Round.Trick', led_suit: Optional['SUIT'], is_leading: bool) -> list['Deck.Card']:
        """Get the cards that the player is allowed to play in the current trick.

        Args:
            trick (Round.Trick): The current trick
            led_suit (Optional[SUIT]): The suit that was led in the trick, None if the player is leading (except first round where it is clubs)
            is_leading (bool): true if the player is leading the trick, false otherwise

        Returns:
            list[Deck.Card]: The cards that the player is allowed to play
        """

        hearts_broken = trick.round.hearts_broken
        first_round = trick.round.trick_count == 0
        void_in_led_suit = not any(
            [card.suit == led_suit for card in self.hand])
        only_hearts_left = all([card.suit == "hearts" for card in self.hand])
        if first_round:
            if is_leading:
                # We must have the 2 of clubs
                return [card for card in self.hand if card.suit ==
                        "clubs" and card.rank == 2]
            else:
                if void_in_led_suit:  # Play any non point card
                    # Play any card if no non point card is found
                    return [card for card in self.hand if card.points()
                            <= 0] or self.hand
                else:
                    return [
                        card for card in self.hand if card.suit == "clubs"]

        else:  # Not the first round
            if led_suit is None:  # Player is leading
                if hearts_broken or only_hearts_left:
                    return self.hand
                else:
                    return [
                        card for card in self.hand if card.suit != "hearts"]
            else:  # someone else led
                if led_suit == "hearts" or hearts_broken or void_in_led_suit:
                    return self.hand
                else:
                    # Play the same suit if possible
                    return [
                        card for card in self.hand if card.suit == led_suit]

    def __repr__(self):
        return self.name

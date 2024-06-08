from typing import Literal, get_args
import random

SUIT = Literal["hearts", "diamonds", "clubs", "spades"]


class BadPlayingCardError(Exception):
    pass


class Card:
    '''
    A class to represent a playing card in hearts. Each card has a suit, a value, and a point value. 
    The value is an integer, 2-14, where 11 is a jack, 12 is a queen, 13 is a king, and 14 is an ace. (Note that in hearts, the ace is high, so it has a value of 14.)
    '''
    faceCardNames = {11: "Jack", 12: "Queen", 13: "King", 14: "Ace"}
    suiteValues = {"clubs": 0, "hearts": 1, "spades": 2,
                   "diamonds": 3}  # used for sorting value

    def __init__(self, suit: SUIT, value: int):
        """Create a new card with the given suit and value after validating the data.

        Args:
            suit (SUIT): one of the four suits in a deck of cards
            value (int): the value of the card, 2-14 (2-10, 11=jack, 12=queen, 13=king, 14=ace)
        """
        if suit not in ["hearts", "diamonds", "clubs", "spades"]:
            raise BadPlayingCardError(f"Invalid suit: {suit}")
        if value < 2 or value > 14:
            raise BadPlayingCardError(f"Invalid value: {value}")

        self.suit = suit
        self.value = value

    def short_name(self) -> str:
        """A method to get a cards 'short name'. This is a string that represents the card in a short form. 
        For example, the 2 of hearts would have a short name of 'h2'. The ace of spades would have a short name of 's14'.

        Returns:
            str: The short name of the card
        """
        return f"{self.suit[0].lower()}{self.value}"

    def points(self) -> int:
        """Return the number of points this card is worth in the game hearts. 1 point for each heart, 13 for the queen of spades, -10 for the jack of diamonds.

        Returns:
            int: points
        """
        if self.suit == "hearts":
            return 1
        elif self.suit == "spades" and self.value == 12:
            return 13
        elif self.suit == "diamonds" and self.value == 11:
            return -10
        else:
            return 0

    def __lt__(self, other: 'Card') -> bool:
        """The order of cards we will consider by suite is a personal preference of Clubs, Hearts, Spades, Diamonds, and next by value.

        Args:
            other (Card): A card

        Returns:
            bool: true if this card should appear before the other card, false otherwise
        """
        if self.suit == other.suit:
            return self.value < other.value
        return self.suiteValues[self.suit] < self.suiteValues[other.suit]

    def __str__(self) -> str:
        """Display card name as a human would expect it to be displayed. 

        Returns:
            str: A string representation of the card
        """
        if self.value in self.faceCardNames:
            return f"{self.faceCardNames[self.value]} of {self.suit.capitalize()}"
        return f"{self.value} of {self.suit.capitalize()}"


class Deck:
    """
    A class to represent the 52 playing cards along with deck utility functions.
    """

    def __init__(self) -> None:
        """Initialize the deck with the 52 cards.
        """
        self.cards = [Card(suit, value)
                      for suit in get_args(SUIT) for value in range(2, 15)]

    def shuffle(self) -> None:
        """Shuffle the deck of cards.
        """
        random.shuffle(self.cards)  # shuffle the deck in place

    def deal(self) -> list[list[Card]]:
        """Deal a hand of 13 cards from the deck.

        Returns:
            list[Card]: A list of 4 lists of 13 cards each
        """
        self.shuffle()
        return [self.cards[i::4] for i in range(4)]

    @classmethod
    def sort_hand(cls, hand: list[Card]) -> list[Card]:
        """Sort the hand of cards by suit and then by value.

        Args:
            hand (list[Card]): A list of cards

        Returns:
            list[Card]: A sorted list of cards
        """
        return sorted(hand)

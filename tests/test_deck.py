import unittest
from deck import Deck


class DeckTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.deck = Deck()

    def test_initialization(self):
        self.assertEqual(len(self.deck.cards), 52,
                         "The deck should have 52 cards")
        self.assertEqual(sum([c.points() for c in self.deck.cards]), 16,
                         "The sum of the points of all cards should be 16 due to the Jack of Diamonds=-10")

    def test_shuffle(self):
        original_order = self.deck.cards.copy()
        self.deck.shuffle()
        self.assertNotEqual(self.deck.cards, original_order,
                            "Failed to shuffle the deck")

    def test_deal(self):
        hands = self.deck.deal()
        self.assertEqual(len(hands), 4, "There should be 4 hands")
        self.assertEqual(len(hands[0]), 13, "Each hand should have 13 cards")
        self.assertEqual(len(set([str(card) for hand in hands for card in hand])),
                         52, "All cards should be dealt exactly once")

    def test_sorting(self):
        deck = Deck()
        deck_cards = [card.short_name() for card in deck.cards]
        deck.shuffle()
        sorted_deck = Deck.sort_hand(deck.cards)
        sorted_deck_cards = [card.short_name() for card in sorted_deck]
        self.assertEqual(deck_cards, sorted_deck_cards,
                         "The sorted deck should be the same as the original deck")


class CardTests(unittest.TestCase):

    def test_points(self):
        deck = Deck()
        for card in deck.cards:
            if card.suit == "hearts":
                self.assertEqual(card.points(), 1,
                                 f"The {card} should be worth 1 point")
            elif card.suit == "diamonds" and card.rank == 11:
                self.assertEqual(card.points(), -10,
                                 f"The {card} should be worth -10 points")
            elif card.suit == "spades" and card.rank == 12:
                self.assertEqual(card.points(), 13,
                                 f"The {card} should be worth 13 points")
            else:
                self.assertEqual(card.points(), 0,
                                 f"The {card} should be worth 0 points")

    def test_str(self):
        card = Deck.Card("clubs", "10")  # 10 of clubs
        self.assertEqual(str(card), "10 of clubs",
                         "The string representation of the card is incorrect")
        card = Deck.Card("hearts", 14)  # Ace of hearts
        self.assertEqual(str(card), "Ace of hearts",
                         "The string representation of the card is incorrect")
        card = Deck.Card("diamonds", 11)  # Jack of diamonds
        self.assertEqual(str(card), "Jack of diamonds",
                         "The string representation of the card is incorrect")


if __name__ == '__main__':
    unittest.main()

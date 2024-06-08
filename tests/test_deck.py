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


if __name__ == '__main__':
    unittest.main()

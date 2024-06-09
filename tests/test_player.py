import unittest
from backend.deck import Deck
from backend.exceptions import NoLegalMovesError
from backend.player import Player


class PlayerTests(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.player = Player("Test")

    def test_allowed_cards_to_play_first_round_lead(self):
        # Test that the player can only play the 2 of clubs in the first round
        cards = [Deck.Card("clubs", 2), Deck.Card("hearts", 3), Deck.Card(
            "spades", 4), Deck.Card("diamonds", 5)]
        self.player.set_hand(cards)
        allowed_cards = self.player.allowed_cards_to_play(
            False, True, 'clubs', True)
        self.assertEqual(allowed_cards, [Deck.Card(
            "clubs", 2)], "The player should only be able to play the 2 of clubs")

    def test_allowed_cards_to_play_first_round_follow(self):
        cards = [Deck.Card("clubs", 3), Deck.Card("hearts", 3), Deck.Card(
            "spades", 4), Deck.Card("diamonds", 5)]
        self.player.set_hand(cards)
        allowed_cards = self.player.allowed_cards_to_play(
            False, True, 'clubs', False)
        self.assertEqual(allowed_cards, [Deck.Card(
            "clubs", 3)], "The player must play a club if he has one")

        cards = [Deck.Card("diamonds", 11), Deck.Card(
            "hearts", 3), Deck.Card("spades", 12), Deck.Card("hearts", 5)]
        self.player.set_hand(cards)
        allowed_cards = self.player.allowed_cards_to_play(
            False, True, 'clubs', False)
        self.assertEqual(allowed_cards, [Deck.Card(
            "diamonds", 11)], "The player must play a non point card if he has one")

        cards = [Deck.Card("hearts", 11), Deck.Card("spades", 12)]
        self.player.set_hand(cards)
        allowed_cards = self.player.allowed_cards_to_play(
            False, True, 'clubs', False)
        self.assertEqual(allowed_cards, cards, "The player can play any card")

    def test_allowed_cards_to_play_not_first_round_lead(self):
        # Test that the player can play any card if he is leading and hearts has been broken
        cards = [Deck.Card("clubs", 3), Deck.Card("hearts", 3), Deck.Card(
            "spades", 4), Deck.Card("diamonds", 5)]
        self.player.set_hand(cards)
        allowed_cards = self.player.allowed_cards_to_play(
            True, False, None, True)
        self.assertEqual(allowed_cards, cards, "The player can play any card")

        # Test that the player may not lead a heart if hearts have not been broken
        cards = [Deck.Card("clubs", 3), Deck.Card("hearts", 3), Deck.Card(
            "spades", 4), Deck.Card("diamonds", 5)]
        self.player.set_hand(cards)
        allowed_cards = self.player.allowed_cards_to_play(
            False, False, None, True)
        self.assertEqual(allowed_cards, [Deck.Card("clubs", 3), Deck.Card(
            "spades", 4), Deck.Card("diamonds", 5)], "The player can not lead a heart")

    def test_allowed_cards_to_play_not_first_round_follow(self):
        # Test that the player can play any card if he can not follow suit
        cards = [Deck.Card("clubs", 3), Deck.Card("hearts", 3), Deck.Card(
            "spades", 12)]
        self.player.set_hand(cards)
        allowed_cards = self.player.allowed_cards_to_play(
            False, False, 'diamonds', False)
        self.assertEqual(allowed_cards, cards, "The player can play any card")

        # Test that the player must follow suit if possible
        cards = [Deck.Card("clubs", 3), Deck.Card("hearts", 3), Deck.Card(
            "spades", 4), Deck.Card("diamonds", 5)]
        self.player.set_hand(cards)
        allowed_cards = self.player.allowed_cards_to_play(
            True, False, 'clubs', False)
        self.assertEqual(allowed_cards, [Deck.Card(
            "clubs", 3)], "The player must follow suit")

    def test_no_moves(self):
        # Test that the correct error is raised in the invalid case where the player has no legal moves (Shouldn't happen in a real game!)
        cards = []

        self.player.set_hand(cards)
        with self.assertRaises(NoLegalMovesError):
            self.player.allowed_cards_to_play(
                True, False, None, False)

        with self.assertRaises(NoLegalMovesError):
            self.player.allowed_cards_to_play(
                False, True, 'clubs', False)

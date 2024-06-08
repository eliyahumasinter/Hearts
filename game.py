from __future__ import annotations

from player import Player
from deck import Deck
from exceptions import BadPlayerListError
from typing import Optional, TYPE_CHECKING
from settings import END_GAME_SCORE

if TYPE_CHECKING:
    from deck import SUIT


class Game:
    def __init__(self, players: list[Player]) -> None:
        """Initialize the game with the given players and deal the cards. Ensure that there are a correct number of unique players
        Version 1.0 - Only supports 4 players

        Args:
            players (list[Player]): A list of players
        """

        if len(players) != 4 or len([player.name.lower() for player in players]) != 4:
            raise BadPlayerListError(
                "The game only supports 4 players. Please provide a list of 4 players with unique names.")

        self.players = players
        self.deck = Deck()
        self.hands = self.deck.deal()
        for i, player in enumerate(self.players):
            player.set_hand(self.hands[i])

        self.round_count = 0
        self.lead_player = self.get_first_player()

    def pass_cards(self, player: Player, cards: list[Deck.Card]) -> None:
        """Method to pass cards from one player to another. This should be  called in the beginning of each round.
        We determine who to pass the cards to based on the round number.

        Args:
            player (Player): The player who is passing the cards
            cards (list[Deck.Card]): the three cards that the player is passing
        """
        pass

    def play_card(self, player: Player, led_suit: SUIT, is_first_round=False) -> Deck.Card:
        """Method to play a card from the player's hand. 

        Args:
            player (Player): The player who is playing the card
            play_count (int): The number of cards played in the trick thus far
            led_suite (Optional[str]): The suite that was led in the trick (None if no cards have been played yet)

        Returns:
            Deck.Card: The legal card selected by the player
        """
        allowed_cards = Deck.sort_hand(self.allowed_cards_to_play(
            player, led_suit, is_first_round))
        print("Player: ", player)
        print("Allowed cards: ", dict(enumerate(allowed_cards)))
        card = int(input("Enter the card to play by number in list: \n"))
        print(f"{player} played {allowed_cards[card]}")
        print()
        return allowed_cards[card]

    def get_winner_of_trick(self, played: dict[Player, Deck.Card], led_suit) -> Player:
        """Method to determine the winner of a trick. The winner is the player who played the highest card of the leading suit.

        Args:
            played (dict[Player, Deck.Card]): A dictionary of players and the cards they played in the trick
            led_suit (str): The suit that was led in the trick

        Returns:
            Player: The player who won the trick
        """
        players_on_suit = [
            player for player in played if played[player].suit == led_suit]
        return max(players_on_suit, key=lambda player: played[player].rank)

    def play_trick(self, trick_count: int) -> tuple[dict[Player, Deck.Card], SUIT]:
        """Method to play a trick. A trick is a round of 4 cards, one from each player. The player who plays the highest card of the suit that leads wins the trick.

        Returns:
            Player: The player who won the trick
        """
        current_player = self.lead_player
        led_suit: Optional[SUIT] = "clubs" if trick_count == 0 else None

        played: dict[Player, Optional[Deck.Card]] = {
            player: None for player in self.players
        }

        played[current_player] = self.play_card(
            current_player, led_suit, True)  # type: ignore

        led_suit = played[current_player].suit  # type: ignore

        for _ in range(3):
            current_player = self.players[(
                self.players.index(current_player) + 1) % 4]
            played[current_player] = self.play_card(current_player, led_suit)

        return (played, led_suit)  # type: ignore

    def play_round(self) -> None:
        trick_count = 0

        for _ in range(13):
            trick, led_suit = self.play_trick(trick_count)
            winner = self.get_winner_of_trick(trick, led_suit)
            trick_count += 1
            # Update local score of the player who took the trick
            winner.round_score += sum([card.points()
                                      for card in trick.values()])

            # Store the trick in the player's tricks_taken list
            winner.tricks_taken.append(trick)

            # Update the lead player for the next trick
            self.lead_player = winner
            print(f"{winner} won the trick!")
            # Remove the played cards from the player's hand
            for player, card in trick.items():
                player.hand.remove(card)

    def play_game(self) -> None:
        while max([player.total_score for player in self.players]) < END_GAME_SCORE:
            self.play_round()
            for player in self.players:
                player.finish_round()  # Update player scores and prepare for next round
            self.round_count += 1
            for player in self.players:
                print(f"{player}: {player.total_score}")

            break  # ! Remove this break statement

    def allowed_cards_to_play(self, player: Player, led_suit: SUIT, is_first_round) -> list[Deck.Card]:

        return player.hand

    def get_first_player(self) -> Player:
        """Method to determine the first player of the round. This is the player with the 2 of clubs.

        Returns:
            Player: The player who has the 2 of clubs
        """

        for player in self.players:
            if Deck.Card("clubs", 2) in player.hand:
                return player

        # To fix the typing error possibility of no player returning
        raise ValueError("No player has the 2 of clubs")

    def reset_game(self) -> None:
        self.deck = Deck()
        self.hands = self.deck.deal()
        for i, player in enumerate(self.players):
            player.set_hand(self.hands[i])

        self.round_count = 0
        self.trick_count = 0
        self.lead_player = self.get_first_player()

    def print_current_hands(self) -> None:
        for player in self.players:
            print(f"{player}: ", end="")
            for card in Deck.sort_hand(player.hand):
                print(card, end=", ")
            print("\n\n", "-"*20, "\n")

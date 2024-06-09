
from typing import Optional, TYPE_CHECKING

from deck import Deck

if TYPE_CHECKING:
    from player import Player
    from deck import SUIT


class Round:
    def __init__(self, players: list['Player']) -> None:
        """Initialize the round with the given players. The round will keep track of the tricks played and the lead player for each trick.

        Args:
            players (list[Player]): The list of players
        """

        self.players = players
        self.trick_count = 0
        self.lead_player: 'Player' = self.get_first_player()
        self.hearts_broken = False

    def play_round(self) -> None:
        """
        Play the 13 tricks of the round. Update the scores of the players and store the tricks taken by each player.
        """
        for _ in range(13):
            trick = self.Trick(self)
            trick.play_trick()
            winner = trick.winner
            # Update local score of the player who took the trick
            played_cards = trick.played.values()
            winner.round_score += sum([card.points()
                                      for card in played_cards])

            # Store the trick in the player's tricks_taken list
            winner.cards_taken.extend(played_cards)

            # Update the lead player for the next trick
            self.lead_player = winner

            # Remove the played cards from the player's hand
            for player, card in trick.played.items():
                player.hand.remove(card)
            print(trick)
            self.trick_count += 1

    def get_first_player(self) -> 'Player':
        """Method to determine the first player of the round. This is the player with the 2 of clubs.

        Returns:
            Player: The player who has the 2 of clubs
        """

        for player in self.players:
            if Deck.Card("clubs", 2) in player.hand:
                return player

        # To fix the typing error possibility of no player returning
        raise ValueError("No player has the 2 of clubs")

    class Trick:
        def __init__(self, round: 'Round') -> None:
            """Sub class of Round to represent a trick. A trick is a single play of each player in a round of hearts.

            Args:
                round (Round): The round that the trick is being played in
            """
            self.round = round
            self.players = round.players
            self.played: dict['Player', Deck.Card] = {}
            self.current_player = self.round.lead_player

        def play_trick(self) -> None:
            """
            Play a single trick. Each player plays a card and the winner of the trick is determined.
            """
            led_suit: Optional['SUIT'] = "clubs" if self.round.trick_count == 0 else None
            played_card = self.play_card(self.current_player, led_suit, True)
            self.played[self.current_player] = played_card

            self.led_suit = led_suit if led_suit else self.played[self.current_player].suit

            if played_card.suit == "hearts" and not self.round.hearts_broken:
                self.round.hearts_broken = True
                print("Hearts have been broken!")

            # Play the remaining cards
            for _ in range(3):
                self.current_player = self.players[(
                    self.players.index(self.current_player) + 1) % 4]
                self.played[self.current_player] = self.play_card(
                    self.current_player, self.led_suit, False)
            self.winner = self.__get_winner_of_trick()

        def play_card(self, player: 'Player', led_suit: Optional['SUIT'], is_leading: bool) -> Deck.Card:
            """Method to get the card to play from the player. This method will be called for each player in the trick. We will soon move this function to outside of the class.

            Args:
                player (Player): The player whose turn it is to play
                led_suit (Optional[SUIT]): The suit that was led in the trick or None if the player is leading (except the first round where it is clubs)
                is_leading (bool): True if the player is leading the trick, False otherwise

            Returns:
                Deck.Card: The validated card the player wants to play
            """

            allowed_cards = Deck.sort_hand(
                player.allowed_cards_to_play(self, led_suit, is_leading))

            print("Player: ", player)
            print("Allowed cards: ", dict(enumerate(allowed_cards)))
            card = int(input("Enter the card to play by number in list: \n"))
            print()
            return allowed_cards[card]

        def __get_winner_of_trick(self) -> 'Player':
            """Private method to determine the winner of a trick. The winner is the player who played the highest card of the leading suit.


            Returns:
                Player: The player who won the trick
            """

            players_on_suit = [
                player for player in self.played
                if self.played[player].suit == self.led_suit  # type: ignore
            ]
            return max(players_on_suit,
                       key=lambda player: self.played[player].rank)  # type: ignore

        def __repr__(self) -> str:
            result = ''
            for player, card in self.played.items():
                result += f"{player}: {card}\n"
            result += f"Winner: {self.winner}"
            return result

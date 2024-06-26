
from typing import Optional, TYPE_CHECKING

from backend.deck import Deck
import backend.ai as ai
if TYPE_CHECKING:
    from backend.player import Player
    from backend.deck import SUIT
    from backend.game import Game


class Round:
    def __init__(self, game: 'Game') -> None:
        """Initialize the round with the given players. The round will keep track of the tricks played and the lead player for each trick.

        Args:
            players (list[Player]): The list of players
        """
        self.game = game

        self.players = game.players
        self.bots = game.bots
        self.trick_count = 0
        self.lead_player: 'Player' = self.get_first_player()
        self.hearts_broken = False
        self.current_trick: Optional[self.Trick] = None

    def play_round(self) -> None:
        """
        Play the 13 tricks of the round. Update the scores of the players and store the tricks taken by each player.
        """
        for _ in range(13):
            self.current_trick = self.Trick(self)
            self.current_trick.play_trick()
            self.game.trick_end_hook(self.current_trick)
            print('\n', self.current_trick, '\n')

            winner = self.current_trick.winner
            if winner is None:
                raise ValueError("No winner found for the trick")
            # Update local score of the player who took the trick
            played_cards = self.current_trick.played.values()
            winner.round_score += sum([card.points()
                                      for card in played_cards])

            # Store the trick in the player's tricks_taken list
            winner.cards_taken.extend(played_cards)

            # Update the lead player for the next trick
            self.lead_player = winner

            # Remove the played cards from the player's hand
            for player, card in self.current_trick.played.items():
                player.hand.remove(card)
            self.trick_count += 1

    def get_first_player(self) -> 'Player':
        """Method to determine the first player of the round. This is the player with the 2 of clubs.

        Returns:
            Player: The player who has the 2 of clubs
        """

        for player in self.players+self.bots:
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
            self.game = round.game
            self.players = round.players
            self.bots = round.bots
            self.all_players = self.players+self.bots
            self.played: dict['Player', Deck.Card] = {}
            self.current_player = self.round.lead_player
            self.winner: Optional['Player'] = None

        def play_trick(self) -> None:
            """
            Play a single trick. Each player plays a card and the winner of the trick is determined.
            """
            led_suit: Optional['SUIT'] = "clubs" if self.round.trick_count == 0 else None
            if self.current_player.am_bot:
                bot_allowed_cards = self.current_player.allowed_cards_to_play(
                    self.round.hearts_broken, self.round.trick_count == 0, led_suit, True)
                played_card = ai.play_card(
                    self.current_player, led_suit, True, bot_allowed_cards)
            else:
                played_card = self.round.game.play_card(
                    self.current_player, led_suit, True)
            self.played[self.current_player] = played_card

            self.led_suit = led_suit if led_suit else self.played[self.current_player].suit
            if self.led_suit == "hearts" and not self.round.hearts_broken:
                self.round.hearts_broken = True
                self.game.hearts_broken_hook()

            self.game.card_played_hook(self.current_player, played_card)
            # Play the remaining cards
            for _ in range(3):
                self.current_player = self.all_players[(
                    self.all_players.index(self.current_player) + 1) % 4]
                if self.current_player.am_bot:
                    bot_allowed_cards = self.current_player.allowed_cards_to_play(
                        self.round.hearts_broken, self.round.trick_count == 0, self.led_suit, False)
                    card = ai.play_card(self.current_player,
                                        self.led_suit, False, bot_allowed_cards)
                else:
                    card = self.round.game.play_card(
                        self.current_player, self.led_suit, False)

                self.played[self.current_player] = card
                if card.suit == "hearts" and not self.round.hearts_broken:
                    self.round.hearts_broken = True
                    self.game.hearts_broken_hook()

                self.game.card_played_hook(self.current_player, card)

            self.winner = self.__get_winner_of_trick()

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

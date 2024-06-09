from typing import Optional, TYPE_CHECKING
from api import API
if TYPE_CHECKING:
    from deck import Deck, SUIT
    from player import Player


def main():
    users = ["Alice", "Bob", "Charlie", "David"]

    def play_card(player: 'Player', led_suit: Optional['SUIT'], is_leading: bool) -> 'Deck.Card':
        """Method to get the card to play from the player. This method will be called for each player in the trick. 

            Args:
                player (Player): The player whose turn it is to play
                led_suit (Optional[SUIT]): The suit that was led in the trick or None if the player is leading (except the first round where it is clubs)
                is_leading (bool): True if the player is leading the trick, False otherwise

            Returns:
                Deck.Card: The validated card the player wants to play
            """

        print("Player: ", player)
        # Get the cards that the player is allowed to play
        allowed_cards = api.get_allowed_cards(player, led_suit, is_leading)

        print("Allowed cards: ", dict(enumerate(allowed_cards)))
        # card = int(input("Enter the card to play by number in list: \n"))
        print()
        return allowed_cards[0]

    def hearts_broken_callback():
        print('\n\n\n', "Hearts has been broken!", '\n\n\n')

    api = API(play_card)
    api.set_hearts_broken_hook(hearts_broken_callback)

    def print_round_score():
        state = api.get_current_state()
        players = state["players"]
        for player in players:
            print(player, ":", players[player]['total_score'], end=" | ")
    api.set_round_end_hook(print_round_score)

    for user in users:
        api.add_player(user)
    api.start_game()


if __name__ == "__main__":
    main()

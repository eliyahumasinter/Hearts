from typing import Optional, TYPE_CHECKING
from api import API
from backend.player import Player
from backend.deck import Deck, SUIT
if TYPE_CHECKING:
    pass


def main():
    users = ["Alice", "Bob", "Charlie", "David"]

    def play_card_hook(player: Player, led_suit: Optional[SUIT], is_leading: bool) -> Deck.Card:
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

    api = API()

    api.set_play_card_hook(play_card_hook)
    api.set_hearts_broken_hook(hearts_broken_callback)

    def get_pass_cards(player: Player) -> list[Deck.Card]:
        """Method to get the cards to pass from the player. This method will be called for each player at the beginning of the round."""
        print('Passing', api.get_passing_direction())
        print("Player: ", player)
        player_state = api.get_player_state(player)
        player_hand = player_state['hand']
        print("Hand: ", dict(enumerate(player_hand)))
        chosen_cards = []
        for i in range(3):
            card = int(input("Enter the card to pass by number in list: \n"))
            chosen_cards.append(player_hand[card])
            player_hand.pop(card)
        return chosen_cards

    api.set_get_pass_cards_hook(get_pass_cards)

    def print_round_score():
        state = api.get_current_state()
        players = state["players"]
        for player in players:
            print(player, ":", players[player]['total_score'], end=" | ")
    api.set_round_end_hook(print_round_score)

    def passed_cards_hook(passed_card_details: dict[str, list[Deck.Card]]):
        print("Cards have been passed!")
        for player, cards in passed_card_details.items():
            print(player, " received: ", cards)

    api.set_passed_cards_hook(passed_cards_hook)

    def end_game_hook():
        print("Game Over")
        state = api.get_current_state()
        players = state["players"]
        winner = min(players, key=lambda x: players[x]['total_score'])
        print("Winner: ", winner, " with score: ",
              players[winner]['total_score'])
    api.set_end_game_hook(end_game_hook)
    for user in users:
        api.add_player(user)
    api.start_game()


if __name__ == "__main__":
    main()

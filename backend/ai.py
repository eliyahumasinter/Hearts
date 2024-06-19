
from backend.player import Player
from backend.deck import Deck
from backend.deck import SUIT


def bot_pass_cards(bot: 'Player') -> list['Deck.Card']:
    possible_cards = bot.hand
    return possible_cards[:3]


def play_card(player: 'Player', led_suit: SUIT | None, leading: bool, allowed_cards_to_play: list['Deck.Card']) -> 'Deck.Card':
    """Function to play a card for a bot player

    Args:
        player (Player): The bot player
        led_suit (SUIT | None): What SUIT was led (None if leading)
        leading (bool): Am I leading?
        allowed_cards_to_play (list[Deck.Card]): The cards that the bot is allowed to play

    Returns:
        Deck.Card: The card the bot chooses to play
    """
    return allowed_cards_to_play[0]

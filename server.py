import socket
import select
from typing import Optional
from api import API
from backend.player import Player
from backend.deck import Deck, SUIT
from backend.round import Round
import threading

SERVER_PORT = 2345
SERVER_IP = "0.0.0.0"


class Print:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def print(*args, color=None, bold=False, underline=False, end='\n', sep=' ', encode=True):

        string = ''
        if color:
            string += color
        if bold:
            string += Print.BOLD
        if underline:
            string += Print.UNDERLINE
        for arg in args:
            string += str(arg) + sep
        string += Print.END + end

        if encode:
            return string.encode()
        return string

    def clear(cls):
        return "\033[H\033[J".encode()

    def display_hand(cls, hand: list[Deck.Card]):
        string = ""
        for index, card in enumerate(hand):
            string += f"{index}: {card}\n"
        return cls.print(string, color=cls.BLUE)

    def __call__(cls, *args, **kwargs):
        return cls.print(*args, **kwargs)


def print_client_sockets(client_sockets):
    print("Current clients:")
    for c in client_sockets:
        # getpeername() returns the remote address to which the socket is connected
        print("\t", c.getpeername())


def socket_to_name(clients_names, current_socket):
    sender_name = None
    for entry in clients_names.keys():
        if clients_names[entry] == current_socket:
            sender_name = entry
    return sender_name


class ThreadError(Exception):
    def __init__(self, message, error, thread):
        super().__init__(message)
        self.error = error
        self.thread = thread


def main():
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("Listening for clients...")
    staging_room_players = {}
    client_threading_map = {}
    all_players = {}
    games = []
    NUM_PLAYERS = 1

    def close_on_error(thread: Optional[threading.Thread] = None):
        game = all_players[current_socket]
        if game:
            for player in game.players:
                if game.players[player] != current_socket:
                    game.players[player].send(Game.printer(
                        "A player has left the game, destroying game", color=Game.printer.FAIL))
                    game.players[player].close()
                    del all_players[player]

            games.remove(thread)  # type: ignore

        current_socket.close()
        del all_players[current_socket]
        client_sockets.remove(current_socket)

    while True:
        try:
            client_sockets, _, _ = select.select(
                [server_socket] + list(all_players.keys()), [], [])
            for current_socket in client_sockets:
                if current_socket == server_socket:
                    client_socket, _ = server_socket.accept()
                    print("New client connected")
                    all_players[client_socket] = None
                else:
                    try:
                        data = current_socket.recv(1024).decode()
                    except ConnectionError:
                        print("Client disconnected")
                        # Get the thread that the client is in
                        thread = client_threading_map.get(current_socket)
                        close_on_error(thread)
                        continue
                    if data.startswith("NAME: "):
                        name = data.split(":")[1].strip().capitalize()
                        if name in staging_room_players:
                            current_socket.send(Game.printer(
                                "Name already taken", color=Game.printer.Warning))
                            continue
                        staging_room_players[name] = current_socket
                        for player in staging_room_players.values():
                            if player != current_socket:
                                player.send(Game.printer(
                                    f"{name} has joined", color=Game.printer.BLUE))
                            else:
                                player.send(Game.printer(
                                    f"Welcome, {name}", color=Game.printer.BLUE))
                    elif data == 'EXIT':
                        current_socket.close()
                        del all_players[current_socket]
                        continue
                    if not data:
                        print("Client disconnected")
                        # Get the thread that the client is in
                        thread = client_threading_map.get(current_socket)
                        close_on_error(thread)
                    else:
                        print("Received data from client\n", data)

            def thread_target_wrapper(players, shared_data):
                try:
                    create_game(players)
                except Exception as e:
                    shared_data['exception'] = ThreadError(
                        "Error in game thread", e, threading.current_thread()
                    )

            def create_game(players):
                game = Game(players)  # dict forces copy
                for player in players:
                    players[player].send(Game.printer.clear())
                    players[player].send(Game.printer(
                        "Game starting!\n", color=Game.printer.GREEN))
                    all_players[players[player]] = game

                game.api.start_game()
            if NUM_PLAYERS == len(staging_room_players):
                shared_data = {}
                game_thread = threading.Thread(target=thread_target_wrapper, args=(
                    dict(staging_room_players), shared_data))  # dict forces copy
                games.append(game_thread)
                for player in staging_room_players:
                    client_threading_map[staging_room_players[player]
                                         ] = game_thread

                staging_room_players.clear()
                game_thread.start()

                if 'exception' in shared_data:
                    raise shared_data['exception']
        except ThreadError as e:
            e.thread.join()
            if not issubclass(type(e.error), (ConnectionError)):
                raise e.error
            close_on_error(e.thread)


class Game:
    printer = Print()

    def __init__(self, players: dict[str, socket.socket]):
        self.api = API()

        self.players = players
        for player in self.players:
            self.api.add_player(player)

        self.api.set_play_card_hook(self.play_card_hook)
        self.api.set_get_pass_cards_hook(self.get_pass_cards_hook)
        self.api.set_hearts_broken_hook(self.hearts_broken_hook)
        self.api.set_round_end_hook(self.round_end_hook)
        self.api.set_trick_end_hook(self.trick_end_hook)
        self.api.set_card_played_hook(self.card_played_hook)

    def round_end_hook(self):
        for user in self.players:
            self.players[user].send(Game.printer.clear())
            self.players[user].send(Game.printer(
                "Round has ended!\n", bold=True, color=Game.printer.GREEN))
            self.players[user].send(Game.printer(
                "\n\nScores:\n", bold=True, color=Game.printer.CYAN))
            state = self.api.get_current_state()
            player_state = state['players']
            for player in player_state:
                self.players[user].send(
                    Game.printer(f"{player}: {player_state[player]['total_score']}", color=Game.printer.CYAN))

    def play_card_hook(self, player: Player, led_suit: Optional[SUIT], is_leading: bool) -> Deck.Card:
        """Method to get the card to play from the player. This method will be called for each player in the trick.

            Args:
                player (Player): The player whose turn it is to play
                led_suit (Optional[SUIT]): The suit that was led in the trick or None if the player is leading (except the first round where it is clubs)
                is_leading (bool): True if the player is leading the trick, False otherwise

            Returns:
                Deck.Card: The validated card the player wants to play
            """
        player_socket = self.players[player.name]
        # Get the cards that the player is allowed to play
        allowed_cards = self.api.get_allowed_cards(
            player, led_suit, is_leading)
        player_socket.send(Game.printer(
            "Your turn to play", color=Game.printer.GREEN))
        player_socket.send(Game.printer(
            "Cards you can play:", color=Game.printer.HEADER))
        player_socket.send(Game.printer.display_hand(allowed_cards))

        return allowed_cards[self.get_valid_user_input(
            player_socket, "Enter the card to play by number in list: ", len(allowed_cards))]

    def get_valid_user_input(self, player_socket: socket.socket, message: str, upper_bound: int) -> int:
        player_socket.send(Game.printer(message, color=Game.printer.CYAN))
        player_socket.send("INPUT".encode())
        card = player_socket.recv(1024).decode().strip()
        if card.isdigit() and int(card) < upper_bound:
            return int(card)
        else:
            while True:
                player_socket.send(
                    Game.printer("Invalid input, enter a number in range: ", color=Game.printer.FAIL))
                player_socket.send("INPUT".encode())
                card = player_socket.recv(1024).decode().strip()
                if card.isdigit() and int(card) < upper_bound:
                    return int(card)

    def get_pass_cards_hook(self, player: Player) -> list[Deck.Card]:
        """Method to get the cards to pass from the player. This method will be called for each player at the beginning of the round."""
        player_socket = self.players[player.name]
        player_socket.send(Game.printer(
            f'Passing {self.api.get_passing_direction()}\n', color=self.printer.CYAN, bold=True, underline=True))
        player_state = self.api.get_player_state(player)
        player_hand = player_state['hand']

        chosen_cards = []
        for i in range(3):

            player_socket.send(
                Game.printer("Your hand:", color=Game.printer.HEADER))
            player_socket.send(
                Game.printer.display_hand(player_hand))

            card_index = self.get_valid_user_input(
                player_socket, "Enter the card to pass by number in list: ", len(
                    player_hand)
            )
            chosen_cards.append(player_hand[card_index])
            player_hand.pop(card_index)
        player_socket.send(Game.printer.clear())
        return chosen_cards

    def trick_end_hook(self, trick: 'Round.Trick') -> None:
        trick_outcome = str(trick)
        for player in self.players:
            self.players[player].send(Game.printer.clear())
            self.players[player].send(
                Game.printer(f"\n{'-'*10}\n\n{trick_outcome}\n\n{'-'*10}\n", color=Game.printer.CYAN))

    def card_played_hook(self, player: Player, card: Deck.Card) -> None:
        for p in self.players:
            if p != player.name:
                self.players[p].send(Game.printer(
                    f"{player.name}: {card}", color=Game.printer.CYAN))

    def hearts_broken_hook(self):
        for player in self.players:
            self.players[player].send(Game.printer(
                "\nHearts has been broken!\n", bold=True, color=Game.printer.GREEN))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Server shutting down...")
        exit()

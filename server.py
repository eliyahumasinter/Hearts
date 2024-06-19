import socket
import select
from typing import Optional
from api import API
from backend.player import Player
from backend.deck import Deck, SUIT
from backend.round import Round

SERVER_PORT = 2345
SERVER_IP = "0.0.0.0"


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


def main():
    print("Setting up server...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("Listening for clients...")
    staging_room_players = []
    games = []
    players = {}
    # The server will wait for 4 players to connect and then it will start a game
    while True:
        client_sockets, _, _ = select.select(
            [server_socket] + staging_room_players, [], [])
        for current_socket in client_sockets:
            if current_socket == server_socket:
                client_socket, _ = server_socket.accept()
                print("New client connected")
                staging_room_players.append(client_socket)
            else:
                data = current_socket.recv(1024).decode()
                if data.startswith("NAME: "):
                    name = data.split(":")[1].strip().capitalize()
                    if name in players:
                        current_socket.send("Name already taken".encode())
                        continue
                    players[name] = current_socket
                    for player in staging_room_players:
                        if player != current_socket:
                            player.send(f"{name} has joined".encode())
                        else:
                            player.send(f"Welcome, {name}".encode())
                elif data == 'EXIT':
                    current_socket.close()
                    staging_room_players.remove(current_socket)
                    continue
                if not data:
                    print("Client disconnected")
                    current_socket.close()
                    staging_room_players.remove(current_socket)
                else:
                    print("Received data from client")
                    print(data)
                    # for client in staging_room_players:
                    #     if client != current_socket:
                    #         client.sendall(data.encode())

        if len(players) == 4:
            game = API()
            games.append(game)
            for player in players:
                game.add_player(player)
                players[player].send("Game starting!".encode())
            staging_room_players = []

            def hearts_broken_hook():
                for player in players:
                    players[player].send("Hearts has been broken!".encode())

            def round_end_hook():
                for user in players:
                    players[user].send("Round has ended!\n".encode())
                    players[user].send("Current scores: \n".encode())
                    state = game.get_current_state()
                    player_state = state['players']
                    for player in player_state:
                        players[user].send(
                            f"{player}: {player_state[player]['total_score']}\n".encode())

            def play_card_hook(player: Player, led_suit: Optional[SUIT], is_leading: bool) -> Deck.Card:
                """Method to get the card to play from the player. This method will be called for each player in the trick. 

                    Args:
                        player (Player): The player whose turn it is to play
                        led_suit (Optional[SUIT]): The suit that was led in the trick or None if the player is leading (except the first round where it is clubs)
                        is_leading (bool): True if the player is leading the trick, False otherwise

                    Returns:
                        Deck.Card: The validated card the player wants to play
                    """

                player_socket = players[player.name]
                # Get the cards that the player is allowed to play
                allowed_cards = game.get_allowed_cards(
                    player, led_suit, is_leading)
                player_socket.send("Your turn to play\n".encode())
                player_socket.send(
                    f"Allowed cards: {dict(enumerate(allowed_cards))}\n\n\n".encode())
                player_socket.send("INPUT".encode())

                card = player_socket.recv(1024).decode().strip()
                # Alert the other players of the card played
                for p in players:
                    if p != player.name:
                        players[p].send(
                            f"{player} played {allowed_cards[int(card)]}\n".encode())

                return allowed_cards[int(card)]

            def get_pass_cards_hook(player: Player) -> list[Deck.Card]:
                """Method to get the cards to pass from the player. This method will be called for each player at the beginning of the round."""
                player_socket = players[player.name]
                player_socket.send(
                    f'Passing {game.get_passing_direction()}'.encode())
                player_state = game.get_player_state(player)
                player_hand = player_state['hand']

                chosen_cards = []
                for i in range(3):
                    player_socket.send(
                        f"Hand: {dict(enumerate(player_hand))}\n".encode())
                    player_socket.send(
                        "Enter the card to pass by number in list: \n".encode())
                    player_socket.send("INPUT".encode())
                    card_index = player_socket.recv(1024).decode().strip()
                    if card_index.isdigit() and int(card_index) < len(player_hand):
                        card_index = int(card_index)

                    else:
                        player_socket.send("Invalid input\n".encode())
                        i -= 1
                        continue
                    chosen_cards.append(player_hand[card_index])
                    player_hand.pop(card_index)
                return chosen_cards

            def trick_end_hook(trick: 'Round.Trick') -> None:
                trick_outcome = str(trick)
                for player in players:
                    players[player].send(trick_outcome.encode())

            game.set_play_card_hook(play_card_hook)
            game.set_get_pass_cards_hook(get_pass_cards_hook)

            game.set_hearts_broken_hook(hearts_broken_hook)
            game.set_round_end_hook(round_end_hook)
            game.set_trick_end_hook(trick_end_hook)
            game.start_game()


if __name__ == '__main__':
    main()

from player import Player
from game import Game


def main():
    users = ["Alice", "Bob", "Charlie", "David"]
    players = [Player(user) for user in users]

    game = Game(players)
    game.print_current_hands()


if __name__ == "__main__":
    main()

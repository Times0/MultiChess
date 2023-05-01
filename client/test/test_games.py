import os
import logic
from constants import STARTINGPOSFEN
from square import Square, Move

games_dir = "data"


def main():
    for game in os.listdir(games_dir):
        if not game.endswith(".txt"):
            continue
        print(f"File {game}")
        game_instance = Logic.Logic(STARTINGPOSFEN)
        with open(os.path.join(games_dir, game), "r") as f:
            game_content = f.read()
        for i, line in enumerate(game_content.splitlines()):
            if line.startswith("#"):
                continue

            if line == "/quit":
                print("Quitting")
                break
            ori, dest = line[:2], line[2:4]
            move = Move(Square(ori), Square(dest))
            if move in game_instance.legal_moves(game_instance.turn):
                game_instance.real_move(move)
                print(f"Performed move {move}")
            else:
                print(f"Move {move} is not legal")


if __name__ == "__main__":
    main()

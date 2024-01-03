import enum
import logging
import os
import threading
import time
from queue import Queue
from random import choice
import chess.polyglot
from logic import Logic, PieceColor, State, Move, Square
from pieces import piece_value

logging.basicConfig(level=logging.DEBUG)


# Amazing video about the minimax algorithm with alpha beta pruning
# "https://youtu.be/l-hh51ncgDI"


class PlayerType(enum.Enum):
    HUMAN = 0
    BOT = 1
    ONLINE = 2


def play_random(logic, color: PieceColor) -> (int, int, int, int):
    return choice(logic.legal_moves(color))


class Bot:
    @staticmethod
    def play(logic, queue: Queue):
        """ Used with multiprocessing that is why we need a list"""
        print("Starting reflection..")
        time.sleep(0.1)
        start = time.time()
        queue.put(play_well(logic))
        end = time.time()
        print(f"Temps de reflexion du bot : {end - start:.2f}s")


def play_well(logic, randomize=True) -> tuple[float, Move]:
    # Try to find a move in the opening book
    directory = os.path.dirname(__file__)
    with chess.polyglot.open_reader(os.path.join(directory, "opening_books", "performance.bin")) as r:
        good_moves = []
        board = chess.Board(logic.get_fen())
        for move_entry in r.find_all(board):
            good_moves.append(move_entry.move)
        if len(good_moves) > 0:
            if randomize:
                chosen_move = choice(good_moves)
            else:
                chosen_move = good_moves[0]
            chosen_move = chosen_move.__str__()
            print(f"Opening book move found : {chosen_move}")
            origin, destination = chosen_move[0:2], chosen_move[2:4]
            return 0, Move(Square(origin), Square(destination))

    color = logic.turn
    M = True if color == PieceColor.WHITE else False
    depth = 2
    return minmax_alpha_beta_root_multithread(logic, depth, -1000, 1000, M, randomize=randomize, num_threads=10)


def minmax_alpha_beta(logic, depth, alpha, beta, maximizing, force_continue: bool, debug=False) -> tuple[
    float, Move or None]:
    if debug:
        print(f"Here is the board after the move : \n {logic} \n {logic.state=}\n {maximizing=} \n\n")
    if logic.state == State.WHITEWINS:
        return 1000, None
    elif logic.state == State.BLACKWINS:
        return -1000, None
    elif logic.state == State.DRAW:
        return 0, None

    if depth <= 0 and not force_continue:
        return eval_position(logic), None
    elif depth < -2:
        return eval_position(logic), None

    else:
        best_move = None
        if maximizing:
            max_evaluation = -1000
            possible_moves = logic.ordered_legal_moves(PieceColor.WHITE)
            for move in possible_moves:
                virtual = Logic(fen=logic.get_fen())
                f_continue = move.is_check
                virtual.real_move(move)
                new_depth = depth if force_continue else depth - 1
                evaluation, _ = minmax_alpha_beta(virtual, new_depth, alpha, beta, False, f_continue)

                if evaluation >= max_evaluation:
                    max_evaluation, best_move = evaluation, move
                alpha = max(alpha, max_evaluation)
                if alpha >= beta:
                    max_evaluation += 0.01
                    break
            return max_evaluation, best_move
        else:
            min_evaluation = 1000
            possible_moves = logic.ordered_legal_moves(PieceColor.BLACK)
            if debug:
                print(f"{possible_moves=}")
            for move in possible_moves:
                virtual = Logic(fen=logic.get_fen())
                f_continue = move.is_capture
                virtual.real_move(move)
                new_depth = depth if force_continue else depth - 1
                evaluation, _ = minmax_alpha_beta(virtual, new_depth, alpha, beta, True, f_continue)

                if evaluation <= min_evaluation:
                    min_evaluation, best_move = evaluation, move
                if debug:
                    print(f"{move=}  {evaluation=}  {min_evaluation=}")
                beta = min(beta, min_evaluation)

                if alpha >= beta:
                    min_evaluation -= 0.01
                    break

            return min_evaluation, best_move


def minmax_alpha_beta_root_multithread(logic, depth, alpha, beta, maximizing, num_threads=4, debug=False,
                                       randomize=True) -> tuple[float, Move]:
    all_evals_move = []
    if maximizing:
        possible_moves = logic.ordered_legal_moves(PieceColor.WHITE)
    else:
        possible_moves = logic.ordered_legal_moves(PieceColor.BLACK)

    if debug:
        logging.debug(f"{len(possible_moves)}")

    def evaluate_moves(moves):
        for move in moves:
            virtual = Logic(fen=logic.get_fen())
            virtual.real_move(move)
            force_continue = move.is_check or move.is_capture
            new_depth = depth if force_continue else depth - 1
            evaluation, _ = minmax_alpha_beta(virtual, new_depth, alpha, beta, not maximizing, force_continue)

            if evaluation >= 1000 and maximizing:
                all_evals_move.append((evaluation, move))
                return evaluation, move
            elif evaluation <= -1000 and not maximizing:
                all_evals_move.append((evaluation, move))
                return evaluation, move

            all_evals_move.append((evaluation, move))

    threads = []
    # Split possible moves into chunks for each thread
    moves_per_thread = len(possible_moves) // num_threads
    if debug:
        logging.debug(f"{moves_per_thread=}")
    if moves_per_thread == 0:
        chunks = [possible_moves]
    else:
        chunks = [possible_moves[i:i + moves_per_thread] for i in range(0, len(possible_moves), moves_per_thread)]
        chunks[-1] += possible_moves[moves_per_thread * num_threads:]

    for i, chunk in enumerate(chunks):
        if debug:
            logging.debug(f"{i=} {len(chunk)=}")
        t = threading.Thread(target=evaluate_moves, args=(chunk,))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    evals = [i[0] for i in all_evals_move]
    if maximizing:
        max_evaluation = max(evals)
        all_best_eval_moves = [e for e in all_evals_move if e[0] == max_evaluation]
    else:
        min_evaluation = min(evals)
        all_best_eval_moves = [e for e in all_evals_move if e[0] == min_evaluation]

    if debug:
        logging.debug(f"{len(all_evals_move)}")
        logging.debug(f"{all_evals_move=}")

    if randomize:
        return choice(all_best_eval_moves)
    else:
        return all_best_eval_moves[0]


def minmax_alpha_beta_root(logic, depth, alpha, beta, maximizing, debug=False, randomize=True) -> tuple[float, Move]:
    all_evals_move = []
    if maximizing:
        possible_moves = logic.ordered_legal_moves(PieceColor.WHITE)
    else:
        possible_moves = logic.ordered_legal_moves(PieceColor.BLACK)

    if debug:
        logging.debug(f"{len(possible_moves)}")

    for move in possible_moves:
        virtual = Logic(fen=logic.get_fen())
        virtual.real_move(move)
        force_continue = move.is_check or move.is_capture
        new_depth = depth if force_continue else depth - 1
        evaluation, _ = minmax_alpha_beta(virtual, new_depth, alpha, beta, not maximizing, force_continue)

        if evaluation >= 1000 and maximizing:
            all_evals_move.append((evaluation, move))
            return evaluation, move
        elif evaluation <= -1000 and not maximizing:
            all_evals_move.append((evaluation, move))
            return evaluation, move

        all_evals_move.append((evaluation, move))

    evals = [i[0] for i in all_evals_move]
    if maximizing:
        max_evaluation = max(evals)
        all_best_eval_moves = [e for e in all_evals_move if e[0] == max_evaluation]
    else:
        min_evaluation = min(evals)
        all_best_eval_moves = [e for e in all_evals_move if e[0] == min_evaluation]

    if debug:
        logging.debug(f"{len(all_evals_move)}")
        logging.debug(f"{all_evals_move=}")

    if randomize:
        return choice(all_best_eval_moves)
    else:
        return all_best_eval_moves[0]


def eval_material(logic: Logic) -> float:
    white = 0
    black = 0
    for i in range(8):
        for j in range(8):
            piece = logic.board[i][j]
            if piece is not None:
                if piece.color == PieceColor.WHITE:
                    white += piece.value
                else:
                    black += piece.value
    return white - black


def eval_position(logic: Logic) -> float:
    eval_sum = 0
    for i in range(8):
        for j in range(8):
            piece = logic.board[i][j]
            if piece is None:
                continue

            color = piece.color
            if color == PieceColor.WHITE:
                eval_sum += piece_value[piece.abbreviation]
            else:
                eval_sum -= piece_value[piece.abbreviation]

            if piece.abbreviation != "P":
                if piece.never_moved and piece.abbreviation != "K":
                    if color == PieceColor.WHITE:
                        eval_sum += 0.2
                    else:
                        eval_sum -= 0.2
    return eval_sum


if __name__ == "__main__":
    board = chess.Board()
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Nf3")
    board.push_san("Nc6")
    board.push_san("Bc4")
    board.push_san("Nf6")
    board.push_san("Ng5")
    board.push_san("Bc5")
    board.push_san("Nxf7")

    with chess.polyglot.open_reader("opening_books/Human.bin") as reader:
        for entry in reader.find_all(board):
            print(entry.move, entry.weight, entry.learn)
            print(type(entry.move))

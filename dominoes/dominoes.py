import random
import json
import os
from datetime import datetime

SCORE_FILE = "domino_scores.json"


def load_scores():
    if not os.path.exists(SCORE_FILE):
        return {"player": 0, "computer": 0, "draws": 0, "history": []}
    try:
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"player": 0, "computer": 0, "draws": 0, "history": []}


def save_scores(scores):
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f, indent=4)


def record_match(scores, result, snake, turn_count):
    # Correctly handles "player_wins", "computer_wins", and "draws"
    if "wins" in result:
        result = result.split("_")[0]  # "player_wins" -> "player"

    scores[result] += 1
    scores["history"].append({
        "result": result,
        "turns": turn_count,
        "snake_length": len(snake),
        "timestamp": datetime.now().isoformat()
    })


# === DOMINO SETUP ===
def generate_full_domino_set():
    return [[i, j] for i in range(7) for j in range(i, 7)]


def deal_dominoes():
    while True:
        domino_set = generate_full_domino_set()
        random.shuffle(domino_set)

        player_pieces = domino_set[:7]
        computer_pieces = domino_set[7:14]
        stock_pieces = domino_set[14:]

        all_doubles = [[i, i] for i in range(6, -1, -1)]
        for double in all_doubles:
            if double in player_pieces:
                player_pieces.remove(double)
                return stock_pieces, computer_pieces, player_pieces, [double], "computer"
            if double in computer_pieces:
                computer_pieces.remove(double)
                return stock_pieces, computer_pieces, player_pieces, [double], "player"


# === DISPLAY ===
def format_snake(snake):
    if len(snake) <= 6:
        return ''.join(str(piece) for piece in snake)
    return ''.join(str(piece) for piece in snake[:3]) + '...' + ''.join(str(piece) for piece in snake[-3:])


def display_interface(stock_pieces, computer_pieces, player_pieces, domino_snake, status):
    print("=" * 70)
    print(f"Stock size: {len(stock_pieces)}")
    print(f"Computer pieces: {len(computer_pieces)}\n")
    print(format_snake(domino_snake))
    print("\nYour pieces:")
    for index, piece in enumerate(player_pieces, 1):
        print(f"{index}:{piece}")
    print()
    if status == "player":
        print("Status: It's your turn to make a move. Enter your command.")
    elif status == "computer":
        print("Status: Computer is about to make a move. Press Enter to continue...")
    elif status == "player_wins":
        print("Status: The game is over. You won!")
    elif status == "computer_wins":
        print("Status: The game is over. The computer won!")
    elif status == "draw":
        print("Status: The game is over. It's a draw!")


# === LOGIC ===
def is_draw(snake, player_hand, computer_hand):
    if len(snake) < 2: return False  # Draw condition not possible early
    left_end = snake[0][0]
    right_end = snake[-1][1]

    # Standard draw condition: no player can make a move
    if len(stock) == 0:
        player_can_play = any(can_play(p, left_end) or can_play(p, right_end) for p in player_hand)
        computer_can_play = any(can_play(p, left_end) or can_play(p, right_end) for p in computer_hand)
        if not player_can_play and not computer_can_play:
            return True

    # Original draw condition from the provided code
    if left_end == right_end:
        count = sum(piece.count(left_end) for piece in snake)
        if count >= 8:
            return True
    return False


def can_play(piece, end_value):
    return end_value in piece


def orient_piece(piece, end_value, place_left):
    if place_left:
        return piece if piece[1] == end_value else piece[::-1]
    else:  # place_right
        return piece if piece[0] == end_value else piece[::-1]


def try_move(index, domino_snake, pieces):
    if index == 0:
        return "draw", None

    # Check for valid index range
    if not (1 <= abs(index) <= len(pieces)):
        return "illegal", None

    piece = pieces[abs(index) - 1]
    left_end = domino_snake[0][0]
    right_end = domino_snake[-1][1]

    if index > 0:  # Play on the right
        if can_play(piece, right_end):
            return "right", orient_piece(piece, right_end, place_left=False)
    elif index < 0:  # Play on the left
        if can_play(piece, left_end):
            return "left", orient_piece(piece, left_end, place_left=True)

    return "illegal", None


def apply_move(move_type, piece, snake):
    if move_type == "left":
        snake.insert(0, piece)
    elif move_type == "right":
        snake.append(piece)


# === SMART AI (DEBUGGED) ===
def count_numbers(pieces, snake):
    counts = {i: 0 for i in range(7)}
    for piece in pieces + snake:
        counts[piece[0]] += 1
        counts[piece[1]] += 1
    return counts


def score_piece(piece, counts):
    return counts[piece[0]] + counts[piece[1]]


def get_computer_move(computer_pieces, domino_snake):
    left_end = domino_snake[0][0]
    right_end = domino_snake[-1][1]
    counts = count_numbers(computer_pieces, domino_snake)

    possible_moves = []
    for index, piece in enumerate(computer_pieces):
        score = score_piece(piece, counts)
        # Check if playable on the right side
        if can_play(piece, right_end):
            move = (index + 1, "right", orient_piece(piece, right_end, False), score)
            possible_moves.append(move)
        # Check if playable on the left side
        if can_play(piece, left_end):
            move = (-1 * (index + 1), "left", orient_piece(piece, left_end, True), score)
            possible_moves.append(move)

    if not possible_moves:
        return 0, "draw", None

    # Sort all possible moves by their score, descending
    possible_moves.sort(key=lambda x: x[3], reverse=True)

    # Return the details of the best move
    best_move = possible_moves[0]
    return best_move[0], best_move[1], best_move[2]


# === MAIN GAME LOOP ===
scores = load_scores()
turn_count = 0

print("=" * 70)
print("Domino Game Scoreboard")
print(f"Player Wins   : {scores.get('player', 0)}")
print(f"Computer Wins : {scores.get('computer', 0)}")
print(f"Draws         : {scores.get('draws', 0)}")
print("=" * 70 + "\n")

stock, computer, player, snake, current_turn = deal_dominoes()

while True:
    game_status = current_turn
    # Check for game end conditions first
    if not player:
        game_status = "player_wins"
    elif not computer:
        game_status = "computer_wins"
    elif is_draw(snake, player, computer):
        game_status = "draw"

    display_interface(stock, computer, player, snake, game_status)

    if game_status in ["player_wins", "computer_wins", "draw"]:
        record_match(scores, game_status, snake, turn_count)
        save_scores(scores)
        break

    turn_count += 1
    # PLAYER TURN
    if current_turn == "player":
        while True:
            try:
                move_str = input()
                move = int(move_str)
                move_type, oriented_piece = try_move(move, snake, player)

                if move_type == "illegal":
                    print("Illegal move. Please try again.")
                    continue

                if move_type == "draw":
                    if stock:
                        player.append(stock.pop())
                else:  # Legal move was made
                    apply_move(move_type, oriented_piece, snake)
                    player.pop(abs(move) - 1)
                break  # Exit input loop
            except ValueError:
                print("Invalid input. Please enter an integer.")
        current_turn = "computer"

    # COMPUTER TURN
    else:  # current_turn == "computer"
        input()  # wait for Enter
        move_index, move_type, oriented_piece = get_computer_move(computer, snake)

        if move_type == "draw":
            if stock:
                computer.append(stock.pop())
        else:
            apply_move(move_type, oriented_piece, snake)
            # Find the original index of the piece to pop
            original_index = abs(move_index) - 1
            computer.pop(original_index)
        current_turn = "player"
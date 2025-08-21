import operator
import random
from typing import Callable, Dict, Tuple

# --- Configuration Constants ---
N_TASKS = 5
RESULTS_FILENAME = "results.txt"
LEVEL_TEXT = {
    "1": "simple operations with numbers 2-9",
    "2": "integral squares 11-29",
}
OPS: Dict[str, Callable[[int, int], int]] = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul
}


# --- Task Generation Functions ---
def generate_simple_task() -> Tuple[str, int]:
    """Generates a simple arithmetic task (e.g., '5 * 7')."""
    x = random.randint(2, 9)
    y = random.randint(2, 9)
    op_symbol = random.choice(list(OPS.keys()))
    expr = f"{x} {op_symbol} {y}"
    result = OPS[op_symbol](x, y)
    return expr, result


def generate_square_task() -> Tuple[str, int]:
    """Generates a task for squaring a number between 11 and 29."""
    x = random.randint(11, 29)
    expr = str(x)
    result = x * x
    return expr, result


# Maps level IDs to their corresponding task generator function
TASK_GENERATORS: Dict[str, Callable[[], Tuple[str, int]]] = {
    "1": generate_simple_task,
    "2": generate_square_task,
}


# --- User Interaction and File I/O ---
def ask_and_grade(expr: str, correct: int) -> int:
    """Prompts with an expression, validates input, and grades the answer."""
    print(expr)
    while True:
        try:
            given = int(input().strip())
            break
        except ValueError:
            print("Incorrect format. Please enter an integer.")

    if given == correct:
        print("Right!")
        return 1
    else:
        print(f"Wrong! The correct answer was {correct}.")
        return 0


def ask_level() -> str:
    """Prompts the user to select a difficulty level."""
    print("Which level do you want? Enter a number:")
    for level, desc in LEVEL_TEXT.items():
        print(f"{level} - {desc}")

    while True:
        level = input().strip()
        if level in LEVEL_TEXT:
            return level
        print("Incorrect format. Please enter a valid level number.")


def maybe_save(score: int, level: str) -> None:
    """Asks the user if they want to save their score to a file."""
    prompt = "Would you like to save your result to the file? Enter yes or no.\n> "
    answer = input(prompt).strip().lower()

    if answer in {"yes", "y"}:
        name = input("What is your name? ").strip()
        desc = LEVEL_TEXT[level]
        line = f"{name}: {score}/{N_TASKS} in level {level} ({desc})\n"

        try:
            with open(RESULTS_FILENAME, "a", encoding="utf-8") as f:
                f.write(line)
            print(f'The results are saved in "{RESULTS_FILENAME}".')
        except IOError as e:
            print(f"Error: Could not save results. {e}")


# --- Main Application Logic ---
def main() -> None:
    """Runs the main quiz loop."""
    level = ask_level()
    task_generator = TASK_GENERATORS[level]
    score = 0

    for i in range(N_TASKS):
        print(f"\n--- Question {i + 1}/{N_TASKS} ---")
        expr, correct = task_generator()
        score += ask_and_grade(expr, correct)

    print(f"\nYour final mark is {score}/{N_TASKS}.")
    maybe_save(score, level)


if __name__ == "__main__":
    main()
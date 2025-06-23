from random import choice

RATING_FILE = "rating.txt"
CLASSIC_OPTIONS = ["rock", "paper", "scissors"]
CLASSIC_RULES = {
    "rock": ["scissors"],
    "paper": ["rock"],
    "scissors": ["paper"]
}

def load_scores(filename):
    scores = {}
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                if line.strip():
                    name, score = line.strip().split()
                    scores[name] = int(score)
    except FileNotFoundError:
        pass
    return scores

def get_result(user, computer, options):
    if user == computer:
        return "draw"
    if options == CLASSIC_OPTIONS:
        if computer in CLASSIC_RULES[user]:
            return "win"
        else:
            return "lose"
    else:
        n = len(options)
        idx = options.index(user)
        # Rotate the list so that user is at index 0
        rotated = options[idx+1:] + options[:idx]
        half = n // 2
        lose = rotated[:half]
        win = rotated[half:]
        if computer in win:
            return "win"
        else:
            return "lose"

def main():
    name = input()
    print(f"Hello, {name}")
    options_line = input()
    if options_line.strip() == "":
        options = CLASSIC_OPTIONS
    else:
        options = [x.strip() for x in options_line.strip().split(",") if x.strip() != ""]
    print("Okay, let's start")
    scores = load_scores(RATING_FILE)
    score = scores.get(name, 0)
    while True:
        user_input = input()
        if user_input == "!exit":
            print("Bye!")
            break
        if user_input == "!rating":
            print(f"Your rating: {score}")
            continue
        if user_input not in options:
            print("Invalid input")
            continue

        computer_choice = choice(options)
        result = get_result(user_input, computer_choice, options)

        if result == "draw":
            print(f"There is a draw ({computer_choice})")
            score += 50
        elif result == "win":
            print(f"Well done. The computer chose {computer_choice} and failed")
            score += 100
        else:
            print(f"Sorry, but the computer chose {computer_choice}")

if __name__ == "__main__":
    main()

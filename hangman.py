import random

def play_game():
    word_list = ['python', 'java', 'swift', 'javascript']
    secret_word = random.choice(word_list)
    guessed_letters = set()
    attempts = 8

    while attempts > 0:
        current_state = ''.join(letter if letter in guessed_letters else '-' for letter in secret_word)
        print(current_state)
        print("Input a letter:")
        guess = input()

        if len(guess) != 1:
            print("Please, input a single letter.")
            continue
        if not guess.isalpha() or not guess.islower():
            print("Please, enter a lowercase letter from the English alphabet.")
            continue
        if guess in guessed_letters:
            print("You've already guessed this letter.")
            attempts -= 1
            continue

        guessed_letters.add(guess)

        if guess in secret_word:
            current_state = ''.join(letter if letter in guessed_letters else '-' for letter in secret_word)
            if '-' not in current_state:
                print(current_state)
                print(f"You guessed the word {secret_word}!")
                print("You survived!")
                return True  # win
        else:
            print("That letter doesn't appear in the word.")
            attempts -= 1

    print("You lost!")
    return False  # loss


# Scoreboard
wins = 0
losses = 0

print("H A N G M A N")

# Main menu loop
while True:
    print('\nType "play" to play the game, "results" to show the scoreboard, and "exit" to quit:')
    command = input().strip().lower()

    if command == "play":
        if play_game():
            wins += 1
        else:
            losses += 1
    elif command == "results":
        print(f"You won: {wins} times.")
        print(f"You lost: {losses} times.")
    elif command == "exit":
        break
    else:
        # If invalid input, show the menu again
        continue

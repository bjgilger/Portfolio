# HONEST CALCULATOR

# Message constants
msg_0 = "Enter an equation"
msg_1 = "Do you even know what numbers are? Stay focused!"
msg_2 = "Yes ... an interesting math operation. You've slept through all classes, haven't you?"
msg_3 = "Yeah... division by zero. Smart move..."
msg_4 = "Do you want to store the result? (y / n):"
msg_5 = "Do you want to continue calculations? (y / n):"
msg_6 = " ... lazy"
msg_7 = " ... very lazy"
msg_8 = " ... very, very lazy"
msg_9 = "You are"
msg_10 = "Are you sure? It is only one digit! (y / n)"
msg_11 = "Don't be silly! It's just one number! Add to the memory? (y / n)"
msg_12 = "Last chance! Do you really want to embarrass yourself? (y / n)"

one_digit_confirmations = [
    msg_10,
    msg_11,
    msg_12
]

def is_one_digit(number: float) -> bool:
    """
    Returns True if number is a one-digit integer or float.
    """
    return (isinstance(number, int) or (isinstance(number, float) and number.is_integer())) and -10 < number < 10

def check(number1: float, number2: float, operator: str) -> None:
    """
    Checks for 'lazy' patterns and prints a message if found.
    """
    msg = ""
    if is_one_digit(number1) and is_one_digit(number2):
        msg += msg_6
    if (number1 == 1 or number2 == 1) and operator == "*":
        msg += msg_7
    if (number1 == 0 or number2 == 0) and operator in ["*", "+", "-"]:
        msg += msg_8
    if msg:
        print(msg_9 + msg)

def get_yes_no(prompt: str) -> bool:
    """
    Prompt user for 'y' or 'n', repeat until valid, return True for 'y', False for 'n'.
    """
    while True:
        answer = input(prompt).strip().lower()
        if answer == "y":
            return True
        elif answer == "n":
            return False

def confirm_store_one_digit(result: float) -> bool:
    """
    Ask up to three times if the user wants to store a one-digit result. 
    Return True if confirmed all three times, otherwise False.
    """
    for prompt in one_digit_confirmations:
        if not get_yes_no(prompt):
            return False
    return True

def main():
    memory = 0.0

    while True:
        print(msg_0)
        calc = input()
        parts = calc.split()
        if len(parts) != 3:
            print(msg_2)
            continue

        x_str, oper, y_str = parts

        try:
            x = memory if x_str == "M" else float(x_str)
            y = memory if y_str == "M" else float(y_str)
        except ValueError:
            print(msg_1)
            continue

        if oper not in "+-*/":
            print(msg_2)
            continue

        check(x, y, oper)

        if oper == "+":
            result = x + y
        elif oper == "-":
            result = x - y
        elif oper == "*":
            result = x * y
        elif oper == "/":
            if y == 0:
                print(msg_3)
                continue
            result = x / y

        print(result)

        # Memory store logic
        while True:
            if get_yes_no(msg_4):
                if is_one_digit(result):
                    if confirm_store_one_digit(result):
                        memory = result
                    # Regardless of store or not, exit the store loop
                    break
                else:
                    memory = result
                    break
            else:
                break

        # Continue calculations prompt
        while True:
            if get_yes_no(msg_5):
                break  # Continue outer loop
            else:
                exit()  # User chose not to continue

if __name__ == "__main__":
    main()

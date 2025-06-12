from random import choice

# Step 1: Take user input — how many people want to join
try:
    num_friends = int(input("Enter the number of friends joining (including you):\n"))
except ValueError:
    num_friends = 0  # Treat non-numeric input as invalid

# Step 2: Handle invalid input
if num_friends <= 0:
    print("No one is joining for the party")
else:
    print("Enter the name of every friend (including you), each on a new line:")
    friends = [input() for _ in range(num_friends)]

    # Step 3: Store names in a dictionary with amount initialized to 0
    friends_dict = {name: 0 for name in friends}

    # Step 4: Get the bill amount
    try:
        total_bill = float(input("Enter the total bill value:\n"))
    except ValueError:
        print("Invalid bill amount")
        total_bill = 0

    # Step 5: Ask about the "Who is lucky?" feature
    lucky_feature = input('Do you want to use the "Who is lucky?" feature? (Yes/No)\n')

    if lucky_feature == "Yes":
        lucky_person = choice(friends)
        print(f"{lucky_person} is the lucky one!")

        if num_friends > 1:
            split_bill = round(total_bill / (num_friends - 1), 2)
            for friend in friends:
                if friend != lucky_person:
                    friends_dict[friend] = split_bill
        else:
            # Only one person, they pay nothing
            friends_dict[lucky_person] = 0
    else:
        print("No one is going to be lucky")
        split_bill = round(total_bill / num_friends, 2)
        friends_dict = {name: split_bill for name in friends}

    print(friends_dict)

class CoffeeMachine:
    COFFEE_RECIPES = {
        "1": {"name": "espresso",    "water": 250, "milk": 0,   "beans": 16, "cost": 4},
        "2": {"name": "latte",       "water": 350, "milk": 75,  "beans": 20, "cost": 7},
        "3": {"name": "cappuccino",  "water": 200, "milk": 100, "beans": 12, "cost": 6},
    }

    def __init__(self):
        self.water = 400
        self.milk = 540
        self.beans = 120
        self.cups = 9
        self.money = 550

    def print_state(self):
        print("\nThe coffee machine has:")
        print(f"{self.water} ml of water")
        print(f"{self.milk} ml of milk")
        print(f"{self.beans} g of coffee beans")
        print(f"{self.cups} disposable cups")
        print(f"${self.money} of money")

    def has_resources(self, recipe):
        missing = []
        if self.water < recipe["water"]:
            missing.append("water")
        if self.milk < recipe["milk"]:
            missing.append("milk")
        if self.beans < recipe["beans"]:
            missing.append("coffee beans")
        if self.cups < 1:
            missing.append("disposable cups")
        return missing

    def buy(self):
        print("What do you want to buy? 1 - espresso, 2 - latte, 3 - cappuccino, back - to main menu:")
        choice = input("> ").strip()
        if choice == "back":
            return

        recipe = self.COFFEE_RECIPES.get(choice)
        if not recipe:
            print("Unknown coffee type.")
            return

        missing = self.has_resources(recipe)
        if missing:
            print(f"Sorry, not enough {', '.join(missing)}!")
        else:
            print("I have enough resources, making you a coffee!")
            self.water -= recipe["water"]
            self.milk -= recipe["milk"]
            self.beans -= recipe["beans"]
            self.cups -= 1
            self.money += recipe["cost"]

    def fill(self):
        self.water += int(input("Write how many ml of water you want to add:\n> "))
        self.milk += int(input("Write how many ml of milk you want to add:\n> "))
        self.beans += int(input("Write how many grams of coffee beans you want to add:\n> "))
        self.cups += int(input("Write how many disposable cups you want to add:\n> "))

    def take(self):
        print(f"I gave you ${self.money}")
        self.money = 0

    def process(self, action):
        if action == "buy":
            self.buy()
        elif action == "fill":
            self.fill()
        elif action == "take":
            self.take()
        elif action == "remaining":
            self.print_state()
        elif action == "exit":
            return False
        else:
            print("Unknown action.")
        return True

def main():
    machine = CoffeeMachine()
    while True:
        print("\nWrite action (buy, fill, take, remaining, exit):")
        action = input("> ").strip()
        if not machine.process(action):
            break

if __name__ == "__main__":
    main()

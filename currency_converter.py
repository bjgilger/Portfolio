import requests

# Step 1: Read base currency
base_currency = input().strip().lower()

# Step 2: Get initial exchange rates from FloatRates
url = f"http://www.floatrates.com/daily/{base_currency}.json"
rates = requests.get(url).json()

# Step 3: Initialize cache and pre-fill with USD and EUR
cache = {}
for code in ['usd', 'eur']:
    if code in rates:
        cache[code] = rates[code]['rate']

# Step 4–9: Interactive loop
while True:
    target_currency = input().strip().lower()
    if not target_currency:
        break

    amount = float(input())

    print("Checking the cache...")

    if target_currency in cache:
        print("Oh! It is in the cache!")
    else:
        print("Sorry, but it is not in the cache!")
        if target_currency in rates:
            cache[target_currency] = rates[target_currency]['rate']
        else:
            # Attempt to fetch dynamically if not in original JSON
            new_url = f"http://www.floatrates.com/daily/{base_currency}.json"
            new_rates = requests.get(new_url).json()
            if target_currency in new_rates:
                cache[target_currency] = new_rates[target_currency]['rate']
            else:
                print(f"Currency code '{target_currency.upper()}' not found.")
                continue

    result = amount * cache[target_currency]
    print(f"You received {round(result, 2)} {target_currency.upper()}.\n")

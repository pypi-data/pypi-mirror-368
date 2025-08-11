import random

def cows_and_bulls():
    comp = random.sample(range(10), 4)
    comp_str = ''.join(map(str, comp))
    attempts = 0

    print("Guess the 4-digit number. Digits must be unique.")
    print("Cow: Correct digit in the correct position")
    print("Bull: Correct digit but in the wrong position")

    while True:
        try:
            guess = input("Your guess: ").strip()
        except EOFError:
            print("Input error. Please run this in a terminal or console.")
            break

        # Debug: Show what input was received
        print(f"DEBUG: Received input -> {guess}")

        if len(guess) != 4 or not guess.isdigit() or len(set(guess)) != 4:
            print("Invalid guess. Enter 4 unique digits.")
            continue

        attempts += 1
        cows = sum(comp_str[i] == guess[i] for i in range(4))
        bulls = sum(guess[i] != comp_str[i] and guess[i] in comp_str for i in range(4))

        print(f"✅ {cows} Cows, {bulls} Bulls")

        if cows == 4:
            print(f"You guessed it in {attempts} attempts! The number was {comp_str}.")
            break

# Uncomment the line below to run the game
# cows_and_bulls()
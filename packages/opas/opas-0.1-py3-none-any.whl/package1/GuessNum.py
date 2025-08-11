import random

def guess_the_number():
    comp_choice = random.randint(0, 20)
    attempts = 0

    while attempts < 5:
        try:
            userGuess = int(input(f"Attempt {attempts + 1}: Guess a number between 0 and 20: "))
        except ValueError:
            print("Please enter a valid integer.")
            continue

        attempts += 1

        if userGuess < comp_choice:
            print("Too low, so try again.")
        elif userGuess > comp_choice:
            print("Too high, so try again.")
        else:
            print(" Congratulations! You guessed the right number.")
            break

    if attempts == 5 and userGuess != comp_choice:
        print(f"Sorry, you've used all 5 attempts. The correct number was {comp_choice}")

# To run the game
# guess_the_number()
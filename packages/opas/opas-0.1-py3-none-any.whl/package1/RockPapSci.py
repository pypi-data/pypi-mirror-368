import random

def play_rps():
    choices = ['rock', 'paper', 'scissors']
    user = input("Choose one: rock, paper, or scissors: ").lower()

    if user not in choices:
        print("Invalid choice. Please select rock, paper, or scissors.")
        return

    computer = random.choice(choices)
    print(f"Computer chose: {computer}")

    if user == computer:
        print("It's a tie!")
    elif (user == "rock" and computer == "scissors") or \
         (user == "paper" and computer == "rock") or \
         (user == "scissors" and computer == "paper"):
        print("You win!")
    else:
        print("You lose.")

# To run the game
# play_rps()
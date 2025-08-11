import random

def play_rps():
    try:
        user = int(input("0=Rock, 1=Paper, 2=Scissors: "))
        if user not in [0, 1, 2]:
            print("Invalid choice. Please enter 0, 1, or 2.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    computer = random.randint(0, 2)
    choices = ["Rock", "Paper", "Scissors"]
    winning_moves = {
        0: 2,
        1: 0,
        2: 1
    }

    print(f"You: {choices[user]}, Computer: {choices[computer]}")

    if user == computer:
        print("Tie!")
    elif winning_moves[user] == computer:
        print("You win!")
    else:
        print("You lose!")

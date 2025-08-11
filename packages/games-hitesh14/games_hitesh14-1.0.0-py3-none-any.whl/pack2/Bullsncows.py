import random

def play_bulls_and_cows():
    secret = ''.join(random.sample('0123456789', 4))
    guessed = set()
    attempts = 0

    print("Guess the 4-digit number. Digits won't repeat.")
    print("Type 'q' or 'quit' to exit the game.\n")

    while True:
        g = input("Your guess: ").lower()

        if g in {"q", "quit"}:
            print("Game exited.")
            break

        if len(g) != 4 or not g.isdigit():
            print("Enter exactly 4 digits.")
            continue

        bulls = sum(g[i] == secret[i] for i in range(4))

        if bulls == 4:
            print("\nCongratulations! You've guessed the number correctly!")
            print(f"The number is: {secret}")
            print(f"Total attempts: {attempts + 1}")
            print("Game Over.")
            break

        if g in guessed:
            print(f"You already guessed '{g}'. Try something else.")
            continue

        guessed.add(g)
        attempts += 1

        cows = {d for i, d in enumerate(g) if d != secret[i] and d in secret}

        print(f"{bulls} Bull(s), {len(cows)} Cow(s): {' '.join(cows) if cows else 'None'}")


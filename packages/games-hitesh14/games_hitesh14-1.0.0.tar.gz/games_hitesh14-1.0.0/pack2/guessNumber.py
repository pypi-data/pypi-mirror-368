import random

def guess_the_number():
    number = random.randint(1, 20)
    print("Guess the number between 1 and 20. You have 5 attempts.\n")

    for attempt in range(1, 6):
        guess = int(input(f"Attempt {attempt}: "))
        if guess == number:
            print("Sath crore!")
            return
        diff = abs(number - guess)
        print("Very close!" if diff <= 5 else "Close!" if diff <= 10 else "Far" if guess < number else "Maxed up")
        if attempt == 5:
            print(f"Game over! The number was {number}.")


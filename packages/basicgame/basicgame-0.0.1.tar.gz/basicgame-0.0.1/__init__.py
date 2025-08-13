import random
num = random.randint(1, 10)
while True:
    guess = int(input("Guess a number (1-10): "))
    if guess == num:
        print("Correct! You win.")
        break
    elif guess < num:
        print("Too low.")
    else:
        print("Too high.")

import random

def guess_number():
    randomNumber = random.randint(0, 20)
    print("Guess a number between 0 and 20 (you have 5 attempts): ")

    count = 0
    while count < 5:
        userGuess = int(input())
        count += 1
        if userGuess == randomNumber:
            print(f"Congratulations! You guessed the number {randomNumber} correctly!")
            break
        elif userGuess < randomNumber:
            print("Low!")
        else:
            print("High!")

        if count == 5:
            print(f"Sorry, you've used all your attempts. The number was {randomNumber}.")

import random

def play_rock_paper_scissors():
    choices = ['Rock', 'Paper', 'Scissors']

    user_choice = input("Enter your choice (Rock/Paper/Scissors): ").capitalize()

    if user_choice not in choices:
        print("Invalid Choice!")

    computer_choice = random.choice(choices)
    print(f"Computer chose: {computer_choice}")

    if user_choice == computer_choice:
        print("Tie!")
    elif (user_choice == 'Rock' and computer_choice == 'Scissors') or \
        (user_choice == 'Paper' and computer_choice == 'Rock') or \
        (user_choice == 'Scissors' and computer_choice == 'Paper'):
        print("You win!")
    else:
        print("You Lost!")

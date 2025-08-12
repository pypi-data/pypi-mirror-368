import random

def Guess():
    pc_number = random.randint(1000, 9999)
    user_number = input("Enter your four-digit guess: ")
    while not (user_number.isdigit() and len(user_number) == 4):
        user_number = input("Invalid input. Enter a four-digit number: ")

    print(f"PC's number: {pc_number}")

    if int(user_number) == pc_number:
        print("You won!")
    else:
        print("You lost!")

# To run the game, uncomment the line below:
# guess_game()
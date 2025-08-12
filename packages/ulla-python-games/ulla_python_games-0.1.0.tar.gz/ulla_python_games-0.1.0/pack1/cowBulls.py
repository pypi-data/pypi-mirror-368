import random

def cowBulls():
    pc = str(random.randint(1000, 9999))
    print("Guess the 4-digit number!")
    user = input("Enter your number: ")

    cows = 0
    bulls = 0
    for i in range(4):
        if user[i] == pc[i]:
            cows += 1
        elif user[i] in pc:
            bulls += 1

    print(f"Bulls: {bulls}")
    print(f"Cows: {cows}")
    print(f"pc has chosen {pc} and you have chosen {user}")

# To run the game, uncomment the following line
# cow_bulls_game()
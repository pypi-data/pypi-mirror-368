import random

choices = ['rock', 'paper', 'scissors']


while True:
    user = input("I choose: ").lower()
    
    if user == 'exit':
        print("Thanks for playing!")
        break
    
    if user not in choices:
        print("Invalid input.")
        continue
    
    computer = random.choice(choices)
    print(f"\nUser: {user}")
    print(f"Computer: {computer}")
    
    if user == computer:
        print("It's a tie!\n")
    elif (user == 'rock' and computer == 'scissors') or \
         (user == 'paper' and computer == 'rock') or \
         (user == 'scissors' and computer == 'paper'):
        print("You win!\n")
    else:
        print("Computer wins!\n")
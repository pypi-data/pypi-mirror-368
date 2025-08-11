import random

secret_number = random.randint(1, 20)
max_attempts = 6
attempts = 0


while attempts < max_attempts:
    guess = input(f"Attempt {attempts + 1}: Your guess: ").strip()
    
    if guess.lower() == 'exit':
        print(f" Thanks for playing!")
        break
    
    if not guess.isdigit():
        print("Please enter a valid number.\n")
        continue
    
    guess = int(guess)
    attempts += 1
    
    if guess == secret_number:
        print("Correct! You guessed the number!\n")
        break
    else:
        difference = abs(secret_number - guess)
        
        if guess < secret_number:
            hint = "Too low"
        else:
            hint = "Too high"
        
        if difference <= 2:
            hint += " but very close! "
        elif difference <= 5:
            hint += " but close. "
        else:
            hint += " and far off. "
        
        print(hint + "\n")

if attempts == max_attempts and guess != secret_number:
    print(f" Out of attempts! The number was {secret_number}. Better luck next time!\n")
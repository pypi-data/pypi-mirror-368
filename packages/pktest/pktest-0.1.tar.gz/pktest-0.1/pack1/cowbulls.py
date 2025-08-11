import random
secret = str(random.randint(1000, 9999))
attempts = 0
while True:
    guess = input("Enter your 4-digit guess: ")
    if not guess.isdigit() or len(guess) != 4:
        print("Please enter a 4-digit number.")
        continue
    attempts += 1
    cows = 0
    bulls = 0
    for s_digit, g_digit in zip(secret, guess):
        if g_digit == s_digit:
            cows += 1
    for g_digit in guess:
        if g_digit in secret:
            if guess.index(g_digit) != secret.index(g_digit):
                bulls += 1
    print(f"Cows : {cows}, Bulls: {bulls}")
    if cows == 4:
        print(f"Congratulations! You guessed the number in {attempts} tries.")
        break
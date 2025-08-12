import random
def guess_number():
    number_to_guess = random(1,20)
    print(number_to_guess)
    attempts = 5
    
    while True:
        try:
            player_guess = int(input("Guess a number between 1 and 20: "))
            attempts += 1
            
            if player_guess < 1 or player_guess > 20:
                print("Please guess a number within the range of 1 to 100.")
                continue
            # if attempts > 5:
            #     print("Sorry, you've used all your attempts. The number was:", number_to_guess)
            #     break
            if player_guess < number_to_guess:
                print("Too low! Try again.")
            elif player_guess > number_to_guess:
                print("Too high! Try again.")
            else:
                print(f"Congratulations! You've guessed the number {number_to_guess} in {attempts} attempts.")
                break
        except ValueError:
            print("Invalid input! Please enter a valid integer.")
# if __name__ == "__main__":
#     guess_number()

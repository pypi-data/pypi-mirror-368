# rps_game.py
import random

def play_game(player_choice):
    choices = ['rock', 'paper', 'scissors']
    computer_choice = random.choice(choices)
    
    if player_choice not in choices:
        print("Invalid choice! Please choose rock, paper, or scissors.")
        return
    
    print(f"Computer chose: {computer_choice}")
    
    if player_choice == computer_choice:
        print(f"Both chose {player_choice}. It's a tie!")
    elif (player_choice == 'rock' and computer_choice == 'scissors') or \
         (player_choice == 'paper' and computer_choice == 'rock') or \
         (player_choice == 'scissors' and computer_choice == 'paper'):
        print(f"You win! {player_choice} beats {computer_choice}.")
    else:
        print(f"You lose! {computer_choice} beats {player_choice}.")
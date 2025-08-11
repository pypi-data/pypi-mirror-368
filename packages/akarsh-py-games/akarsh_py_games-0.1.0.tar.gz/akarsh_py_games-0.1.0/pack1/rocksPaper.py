import random
 
def rocksPaper():
    user = int(input("0=Rock, 1=Paper, 2=Scissors: "))
    computer = random.randint(0, 2)
    choices = ["Rock", "Paper", "Scissors"]
    winning_moves = {
        0: 2,  
        1: 0,
        2: 1  
    }
    
    print(f"You: {choices[user]}, Computer: {choices[computer]}")
    
    if user == computer:
        print("Tie!")
    elif winning_moves[user] == computer:
        print("You win!")
    else:
        print("You lose!")
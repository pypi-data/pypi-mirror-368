import random
def play_rps():
    abc = ['rock', 'paper', 'scissor']
    player = input("Choose rock, paper, or scissor: ")
    comp = random.choice(abc)
    print(f"Your choice is {player}")
    print(f"Computer's choice is {comp}")
    if ((player == "rock" and comp == "scissor") or 
        (player == "paper" and comp == "rock") or 
        (player == "scissor" and comp == "paper")):
        print("You win")
    elif ((player == "paper" and comp == "scissor") or 
          (player == "scissor" and comp == "rock") or 
          (player == "rock" and comp == "paper")):
        print("Computer wins")
    else:
        print("Draw")

import random

def guess_the_number():
    num = random.randint(1, 20)
    flag = 0
    while flag != 5:
        choice = int(input("Give your choice: "))
        if num == choice:
            print(f"correct choice {choice}")
            break
        else:
            if num > choice:
                print("too low")
            else:
                print("too high")
            flag += 1
    if flag == 5:
        print("Attempts are over")
import random

def play_bulls_and_cows():
    while True:
        n = str(random.randint(1000, 9876))
        if len(set(n)) == 4:  
            break
    print(n)
    count = 0
    while True:
        while True:
            m = input("Enter a 4-digit number: ")
            if m.isdigit() and len(m) == 4:
                break
        cows = 0
        bulls = 0
        for i in range(4):
            if m[i] == n[i]:
                cows += 1
            elif m[i] in n:
                bulls += 1
        print(f"Cows = {cows}")
        print(f"Bulls = {bulls}")
        count += 1
        if cows == 4:
            break
    print(f"guessed the number: {m} in {count} attempts")
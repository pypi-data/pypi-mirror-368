import random

def guessNumber():
    computer_choice = random.randint(1,20)
    count=0
    # maxi=5
    while(count<5):
        user_choice = int(input("Enter a random number from 1 - 20 only >"))
        if (user_choice==computer_choice):
            print("correct")
            break
        else:
            diff = abs(user_choice-computer_choice)
            isEven=computer_choice%2==0
            if(diff<=5):
                if(isEven) :
                    print("Very near guess and number is Even")
                else :
                    print("Very near guess and number is odd")
            else:
                print("guess not near")
        
        count += 1

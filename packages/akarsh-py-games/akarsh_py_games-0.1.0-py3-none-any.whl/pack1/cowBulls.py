import random 
def cowBulls():
    str1=''.join(random.sample('1234567890',4))
    print("Computer random is :",str1)
    game=True
    attempts=0
    while game:
        str2=input("Enter a number->")
        attempts+=1
        cow=0 
        bull=0
        for i in range(4):
            if str1[i]==str2[i]:
                cow+=1
            elif(str1[i] in str2):
                bull+=1
        if(cow==4):
            game=False

        print("cow is ",cow,"bull is ",bull)

    print("Attemps took is :", attempts)
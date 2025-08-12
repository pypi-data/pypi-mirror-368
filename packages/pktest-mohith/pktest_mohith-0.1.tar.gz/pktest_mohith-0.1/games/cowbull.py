# from random import randint
# "The numbers generated should be unique and not repeat digits. "
# numbers = [1, 2, 3, 4, 2, 34, 5, 6, 7, 8, 9, 0]
# max_value = numbers[0]
# for num in numbers:
#     if num > max_value:
#         max_value = num
# print(max_value)    
# # Generate a random 4-digit number with unique digits
# # If the number has repeating digits, it should be regenerated






# num1 = randint(1000, 9999)
# num1 = str(num1)
# if num1[0] == num1[1] or num1[0] == num1[2] or num1[0] == num1[3] or num1[1] == num1[2] or num1[1] == num1[3] or num1[2] == num1[3]:
#     print("Number must not have repeating digits.")
# else:
#     print("Generated number:", num1)
# print(f"First number: {num1}")
# num1 = str(num1)
# num2 = input("Enter second number: ")
# count  = 0
# if len(num1) != len(num2):
#     print("Numbers must be of the same length for position-wise comparison.")
# else:
#     matching = []
#     non_matching = []

#     for i in range(len(num1)):
#         if num1[i] == num2[i]:
#             matching.append((i, num1[i]))
#         else:
#             non_matching.append((i, num1[i], num2[i]))

#     print(" Matching digits:")
#     for pos, digit in matching:
#         # print(f"Position {pos}: {digit}")
#         count+=1
#     cow = count
#     print(f"Total matching digits: {count}")    

#     print("\nNon-matching digits:")
#     count2 = 0
#     for pos, d1, d2 in non_matching:
#         # print(f"Position {pos}: {d1} vs {d2}")
#         count2 += 1
#     bull = count2
#     print(f"Total non-matching digits: {count2}")
import random 

def getDigits(num):
    return [int(i) for i in str(num)]
         
def noDuplicates(num):
    num_li = getDigits(num)
    if len(num_li) == len(set(num_li)):
        return True
    else:
        return False
  
def generateNum():
    while True:
        num = random.randint(1000,9999)
        if noDuplicates(num):
            return num

def numOfBullsCows(num,guess):
    bull_cow = [0,0]
    num_li = getDigits(num)
    guess_li = getDigits(guess)
    
    for i,j in zip(num_li,guess_li):
        if j in num_li:
            if j == i:
                bull_cow[0] += 1
            else:
                bull_cow[1] += 1
                
    return bull_cow
    
num = generateNum()
tries =int(input('Enter number of tries: '))

while tries > 0:
    guess = int(input("Enter your guess: "))
    
    if not noDuplicates(guess):
        print("Number repeated ")
        continue
    if guess < 1000 or guess > 9999:
        print("Enter 4 digit number")
        continue
    
    bull_cow = numOfBullsCows(num,guess)
    print(f"{bull_cow[0]} bulls, {bull_cow[1]} cows")
    tries -=1
    
    if bull_cow[0] == 4:
        print("Guessed right!")
        break
else:
    print(f"You ran out of tries. Number was {num}")
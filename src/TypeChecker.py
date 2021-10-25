def isPalindrome(text):
    if text==text[::-1]:
        return True
    else:
        return False

with open ('test.py', 'r') as f:
    for lines in f:
        print("Palindrome ", isPalindrome(lines.strip("\n")))
    #lines= [x.strip("\n") for x in f]
    
test = [2,3,4,5]
test = [1]
test = 1
number = 4
string = "hello"
calc = 1 + 2
calc = calc +"calc"

# Testing the # comment
'''Testing docstring 
comment style'''
for i in range (0,12):
    hello = "hello"
    i+=1

half = unit* 0.5 +g

def trapezoidArea(a:int,b:int,h:int) ->int:
    base = a+ b
    base = 1
    area = (base/2)*h
    return area

def print2(word, num) :
    return word

def stringSum(a, b):
    cool= a+b
    return len(cool)

def nestfunc(arg, arg2):
    test = arg
    return print2(arg, arg2)

area = "area"
area = trapezoidArea(1,number,2)
trapezError = trapezoidArea(1,"hello",cool)
trapezError = trapezoidArea(a=1,b="hello",h=cool)
ca = print2(word = cool,num = "hey")
print= print2(string, 5235)
count = stringSum("hey", string)
ok = len("exciting")
nest= nestfunc(string, number)


class student:
    def __init__(self, name, year):
        self.name = name
        self.year = year
    
    def studentID(self, a , b):
        id =self.name + a
        return id
    
    def getYear(self):
        return self.year

stu = student("hello",2020)
id= stu.studentID("yup","huh")
ye = stu.getYear()
check = stu.grade()

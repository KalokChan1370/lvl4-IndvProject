fname = "Joe"
if fname == type("h"):
    confirm = "str"
    yes = True
else:
    confirm= 1

for i in range(10):
    temp = counter

class student:
    def __init__(self, name, year):
        self.name = name
        self.year = year
    
    def studentID(self, a, b):
        id =self.name + a+b
        return id
    
    def getYear(self):
        unknown = self.sname
        return self.year

    def saveGrade(self, grade):
        self.grade= grade
        return self.grade

stu = student("hello",2020)
id= stu.studentID("name","1")
newid = stu.studentID(a="yup",b=1)
year = stu.getYear()
grade = stu.saveGrade(grade="1")
grade = stu.saveGrade(1)

def stringTogether(str1, str2):
    result = str1 + "2" + str2
    return result

def extend(a,b):
    dummy = "string"
    dummy = 2
    return a+b

def check(grade):
    grades = {"1":"A","2":"B","3":"C","4":"D","5":"E","6":"F"}
    percentage= grade/6*100
    if grade not in grades:
        result = "invalid"
    else:
        result = grades[grade]
    return result

def newGrades(g1, g2):
    temp = 2
    converted1 = stringTogether(str1=g2,str2=g2)
    converted2 = stringTogether(g1,g2)
    return check(grade=g1)

#initialise
fname = "Joe"
sname = "Man"

#consistency args/params
full = stringTogether(fname, sname)
grade = check(1)
grade2 = check(grade=Nograde)
prod = extend (a=[1,2,3,4],b=["a","b","c","d"])
prod2 = extend(a=1, b=2)
full = ['Joe','Man']

#other functions
len = len([1,2,3,4])
Nonfunc = newfunc("1,2",3)

#nested
nest1 = newGrades(g1=1,g2="2")
nest2 = newGrades("2","1")

def trapezoidArea(a,b,h):
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
    return print2(1,arg2)

test = [2,3,4,5]
test = [1]
test = 1
number = 4
string = "hello"
calc = 1+1
calc = calc +"calc"

# Testing the # comment
'''Testing docstring 
comment style'''
for i in range (0,12):
    hello = "hello"
    i+=1

half = unit* 0.5 +g

area = trapezoidArea(1,number,2)
area = "area"
trapezError = trapezoidArea(1,"hello",cool)
trapezError2 = trapezoidArea(a=1,b="hello",h=cool)
printError = print2(word = area,num = "hey")
print= print2(string, 5235)
count = stringSum("hey", string)
len = len("exciting")
nest= nestfunc(string, number)
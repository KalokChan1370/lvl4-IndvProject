#initalise
fname = "Joe"
sname = "man"
age = 19
address = [18,"Lilybank Gardens", "G128RZ"]
education = {"primary":"primary1", "secondary": "secondary2", "university":"university"}
postcode = address[1]

#consistency
fname = sname
fname = 20
education = address

#binop
luckyNo = (age * 10)/2
area = address *2
full = fname + sname
full2 = fname * sname
full3 = fname + 2


if fname == type("h"):
    confirm = "str"
    yes = True
else:
    confirm= 1

for i in range(10):
    temp = i

def stringTogether(str1, str2):
    result = str1 + "2" + str2
    return result

def extend(a:list,b:list)-> list:
    dummy = "string"
    dummy = 2
    return a+b

def check(grade:int) -> str:
    grades = {"1":"A","2":"B","3":"C","4":"D","5":"E","6":"F"}
    percentage= grade/6*100
    if grade not in grades:
        result = "invalid"
    else:
        result = grades[str(grade)]
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
prod2 = extend([1,2,3,4], 2)
full = ['Joe','Man']

#other functions
len = len([1,2,3,4])
Nonfunc = newfunc("1,2",3)

#nested
nest1 = newGrades(g1=1,g2="2")
nest2 = newGrades("2","1")

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
    

class course:
    def __init__(self, course, ID):
        self.course = course
        self.ID = ID
    
    def capacity(self):
        return 200
    
    def coordinator(self, name:str):
        self.coord= name
        return self.coord

    def AvgGrade(self, grades:list) ->str:
        avg=0
        for i in grades:
            avg+=i

        avg=int(avg/len(grades))

        if avg==1:
            converted= "A"
        elif avg==2:
            converted= "B"
        elif avg==3:
            converted= "C"
        else:
            converted = "invalid"
        return converted

#initialise
stu = student("hello",2020)
compsci= course("project","2022")

#consistency
id= stu.studentID("name","1")
newid = stu.studentID(a="yup",b=1)
year = stu.getYear()
grade = stu.saveGrade(grade="1")
grade = stu.saveGrade(1)
cap = compsci.capacity()
avg = compsci.AvgGrade([1,2,3])
avg = compsci.AvgGrade(2)
Cyear = compsci.getYear()

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
    return print2(1,arg2)

area = trapezoidArea(1,number,2)
area = "area"
trapezError = trapezoidArea(1,"hello",cool)
trapezError2 = trapezoidArea(a=1,b="hello",h=cool)
printError = print2(word = area,num = "hey")
print= print2(string, 5235)
count = stringSum("hey", string)
len = len("exciting")
nest= nestfunc(string, number)


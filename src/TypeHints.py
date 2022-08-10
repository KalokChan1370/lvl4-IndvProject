def stringTogether(str1:str, str2:str) -> str:
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

def newGrades(g1:int, g2:str) -> str:
    temp = 2
    converted1 = stringTogether(str1=g2,str2=g2)
    converted2 = stringTogether(g1,g2)
    return check(grade=g1)

#initialise
fname = "Joe"
sname = "Man"
number = 1
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

compsci= course("project","2022")
cap = compsci.capacity()
avg = compsci.AvgGrade([1,2,3])
avg = compsci.AvgGrade(2)
Cyear = compsci.getYear()

def trapezoidArea(a:int,b:int,h:int) ->int:
    base = a+ b
    base = 1
    area = (base/2)*h
    return area

def print2(word:str, num:int) ->str:
    return word

def stringSum(a:str, b:str) ->int:
    cool= a+b
    return len(cool)

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
print= print2(fname, 5235)
count = stringSum("hey", fname)
len = len("exciting")

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

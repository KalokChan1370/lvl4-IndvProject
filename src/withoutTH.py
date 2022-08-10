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
prod2 = extend(a=1, b=2)
full = ['Joe','Man']

#other functions
len = len([1,2,3,4])
Nonfunc = newfunc("1,2",3)

#nested
nest1 = newGrades(g1=1,g2="2")
nest2 = newGrades("2","1")
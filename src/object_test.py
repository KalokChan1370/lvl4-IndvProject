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
    def __init__(self, course:str, ID:str):
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
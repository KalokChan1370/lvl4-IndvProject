import ast
import re 

variableDict = {}
codeLine = 0
arithmeticOp=["+","-","*","/","%","**","//"] 
commentAnotations=["#","'''"]
comment= False

def equalCheck(data):
    print("equals")

def calculationCheck(data):
    values = re.split('\s?(?:\+|\-)\s?', data[1])
    dataT1 = type(ast.literal_eval(values[0]))
    dataT2 = type(ast.literal_eval(values[1]))
    if dataT1 == dataT2:
        data[1]=values[0]
        duplicateCheck(data)
    else :
        print("The Data type of the values for the calculation of", data[0], "do not match! Recommended to change them")

def compareCheck(key, data):
    dataT = variableDict[key]
    newDataT = type(ast.literal_eval(data[1]))
    if dataT == newDataT:
        del variableDict[key]
        variableDict[data[0]] = newDataT 
    else:
        print("Data type for variables at line",key, "and line",data[0], "do not match!")


#   checks if variable is already used
def duplicateCheck(data):
    dup = False
    new = data[0].split("-")[1]
    for key in variableDict.keys():
        name = key.split("-")[1]
        if name == new:
            dup = True
            compareCheck(key, data)
            break
    if dup == False:
        variableDict[data[0]] = type(ast.literal_eval(data[1]))

def variableAssign(data):
    if len(data) == 2:
        if any(op in data[1] for op in arithmeticOp):
            calculationCheck(data)
        else:
            duplicateCheck(data)
            
    elif len(data) == 3:
        equalCheck(data)
    else:
        print(data, " is not a variable assignment")

#   Reads in test.py file
with open ('test.py', 'r') as f:
    for lines in f:
        codeLine += 1
        if lines: 
            #   formatting code line before filtering
            line = lines.strip("\n")
            line = line.lstrip()

            #   checks for comments in the source code
            if any(anotation in line for anotation in commentAnotations):
                if comment:
                    comment = False
                else:
                    commment = True

            #   skips line when the code is marked as a comment in the source code
            if comment:
                continue
            else:
                #    search for assginment variables
                variable = re.search('\w+\s?=\s?',line)
                if variable != None:
                    data = re.split('\s?\+*\-*=\s?', line)
                    #   for duplicate variables
                    data[0] = str(codeLine) +"-"+data[0] 
                    variableAssign(data)
        else:
            continue
            

    print(variableDict)


        
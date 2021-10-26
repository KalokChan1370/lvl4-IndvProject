import ast
import re 

variables = {}
codeLine = 0

def variableAssign(data):
    if len(data)==2:
        variables[data[0]] = type(ast.literal_eval(data[1]))
    else:
        print(data, " is not a variable assignment")

#   Reads in test.py file
with open ('test.py', 'r') as f:
    for lines in f:
        #   formatting code line before filtering
        line = lines.strip("\n")
        line = line.lstrip()

        #    search for assginment variables
        boolean = re.search('\w+\s?=\s?',line)
        data = re.split('\s?\+*\-*=\s?', line)
        #   for duplicate variables
        data[0] = str(codeLine) +"-"+data[0] 
        variableAssign(data)
        codeLine += 1

    print(variables)


        
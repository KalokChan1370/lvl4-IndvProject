import ast
import astpretty

class vis(ast.NodeVisitor):
    def __init__(self):
        self.variables={}
        self.func_sign = {}
        self.Numtype = [type(1),type(1.1)]

#================================== obtaining variable type =============================   
    def checkBinVariable(self,component,variables, params):
        if isinstance (component, ast.Name):
            if component.id in variables:
                component = variables[component.id]['type']
            else:
                # if unnamed params
                if params is not None:
                    for tup in params[:-1]:
                        if component.id == tup[0]:
                           component = tup[1]
                           break
                else:
                    # component contains an uninitialized variable
                    component = None
        else:
            component = type(ast.literal_eval(component)) 
        return component

    def nestedBin(self,nodetype, variables, params= None):       
        if isinstance(nodetype.left, ast.BinOp):
            return self.nestedBin(nodetype.left, variables,params)
        else:
            leftCom = nodetype.left
            rightCom = nodetype.right
            lefttype = self.checkBinVariable(leftCom,variables,params)
            righttype = self.checkBinVariable(rightCom,variables,params)
            if lefttype == righttype:
                nodetype = lefttype
            # when components are both numbers ie int and float convert to int
            elif lefttype in self.Numtype and righttype in self.Numtype:
                nodetype = type(1)
            else:
                # assigns None to type when either component used before assignment or types are different thus not recommended
                if (lefttype is None) or (righttype is None):
                    nodetype = [None,0]
                    print ("uninitialized variable thus type is none")
                else:
                    # potential change to store the types of individual components
                    nodetype = [None,1]
                    print("maths operation components types are different not recomended")
            return nodetype

    def extract(self,node, variables, funcName=None):
        global reportData

        variableName=node.targets[0].id
        line= node.lineno
        nodetype= node.value
        if isinstance(nodetype, ast.BinOp):
            #obtains the types of the function signatures
            if funcName is not None:
                params = self.func_sign[funcName]
            else:
                params = None
            nodetype=self.nestedBin(nodetype,variables,params)
        else:
            nodetype = type(ast.literal_eval(nodetype))
        if isinstance(nodetype, list) and isinstance(nodetype[0], type(None)):
            if nodetype[1]==0:
                reportData.append([variableName, line, 4])
                nodetype = type(None)
            else:
                reportData.append([variableName, line, 5])
                nodetype = type(None)
        return variableName, line, nodetype

#======================================= visit functions =======================================
    def visit_Assign(self, node):
        if isinstance(node.value,ast.Call):
            astpretty.pprint(node.value)
            self.Call(node)
        else:
            variableName, line, nodetype =self.extract(node, self.variables)
            self.duplicateCheck(variableName,line,nodetype, self.variables)   

    # assumes all variables used are local
    def visit_FunctionDef(self, node):
        sub_variables = {}
        annotations = []

        print("variables in function:", node.name)

        #requires source code to use type hints
        for a in node.args.args:
            #checks if parameter has type hints
            if a.annotation !=None:
                #TODO find alternative for eval
                annotations.append((a.arg, eval(a.annotation.id)))

        #checks if return value has type hints
        if node.returns != None:
            annotations.append(('return type',eval(node.returns.id)))
        self.func_sign[node.name]=annotations

        for n in node.body:
            if isinstance(n, ast.Assign):
                variableName, line, nodetype =self.extract(n,sub_variables, node.name)
                self.duplicateCheck(variableName,line,nodetype, sub_variables) 
        
        print([k for k in sub_variables.keys()])
        print("-----"*10,"function def end","-----"*10,"\n")

    def Call(self, node):
        global reportData

        arguments = node.value.args
        print(f"-----"*10,node.value.func.id, "caller start","-----"*10)
        parameters = self.func_sign[node.value.func.id]
        count = 0
        # for unassigned arguements ie not doing product(a=1, b=2)
        if len(node.value.keywords) == 0:
            for arg in arguments:
                #TODO validate for return type 
                #checks argument to its corresponding parameter while excluding return
                if type(ast.literal_eval(arg))!= parameters[count][1] and parameters[count][0]!='return type':
                    reportData.append([node.value.func.id, arg.lineno, count, type(ast.literal_eval(arg)), parameters[count][1],2])
                count+=1
        else:
            for key in node.value.keywords:
                for pram in parameters:
                    if key.arg == pram[0]:
                        if type(ast.literal_eval(key.value)) != pram[1]:
                            reportData.append([node.value.func.id, key.arg, node.lineno, type(ast.literal_eval(key.value)), pram[1], 3])
                            
        #checks data type of return type
        if parameters[-1][0]=='return type':
            variableName = node.targets[0].id
            line = node.lineno
            nodetype = parameters[-1][1]
            print("return:", nodetype)
            self.duplicateCheck(variableName,line,nodetype, self.variables)  
        print("-----"*10,"caller end","-----"*10,"\n")

#======================================= validation ==============================

    #TODO: differentiate between mismatches ie 
    #return data type and normal assignment aka report
    def duplicateCheck(self,name,line, nodetype, variablesdict):
        global reportData

        dup = False
        if len(variablesdict) != 0:
            for k,v in variablesdict.items():
                if name == k:
                    dup = True 
                    # if either variable type is a number data type then match
                    if nodetype == variablesdict[k]['type'] or (nodetype in self.Numtype and variablesdict[k]['type'] in self.Numtype):
                        #updates variable position when type match
                        variablesdict[name]= {'type':nodetype,'line':line}
                    else:
                        reportData.append([name, variablesdict[k]['line'], line, variablesdict[k]['type'], nodetype, 1])
                    break
            if not dup:
                variablesdict[name]= {'type':nodetype,'line':line}
        else:
            variablesdict[name]= {'type':nodetype,'line':line}

def report(reportData):
    
    '''
    error types-
    1) Data types of variables mismatch
    2) Caller arguments and function parameters mismatch (Unamed)
    3) Caller arguments and function parameters mismatch (Named)
    4) uninitialized variable used in binary operations
    5) type mismatch for binary operations not recommended
    '''

    for data in reportData:

        if data[-1] == 1:
            print(f"Data type for:'{data[0]}' at {data[1]} and at {data[2]} mismatch, with types {data[3]} and {data[4]} respectively ")
        
        elif data[-1] == 2:
            print(f"The function caller '{data[0]}' on line {data[1]}, has a data type of {data[3]} at position '{data[2]}' but mismatches",\
                 f"with its corresponding type in the function signature of {data[4]}")
        
        elif data[-1] == 3:
            print(f"The function caller '{data[0]}' on line {data[2]}, has a data type of {data[3]} for argument '{data[1]}' but mismatches",\
                 f"with its corresponding type in the function signature of {data[4]}")
        
        elif data[-1] == 4:
            print(f"Unknown data type found for the variable expression '{data[0]}' at {data[1]} due to its component(s) are uninitialized ")



# Program start

reportData = []

with open("test.py",'r') as f:
    content = f.read()
    module = ast.parse(content)
    
    c=vis()
      
    for node in module.body:
        c.visit(node)

    print("\nGlobal variables")
    for k,v in c.variables.items():
        print(k,':',v)

    print("\nFuncion signatures")
    for k,v in c.func_sign.items():
        print(k,":",v)

    print("\nPotential errors found:")
    report(reportData)



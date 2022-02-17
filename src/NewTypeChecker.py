import ast
from built_func_type import funcs as built_funcs
import astpretty

class Node:
    def __init__(self, item):
        self.item = item
        self.children = []
    
    def add_children(self, children):
        self.children = children 

def buildTree():
    custom = []
    with open("test.py",'r') as f:
        content = f.read()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            n = Node(node)
            childs = ast.iter_child_nodes(node)
            n.add_children(childs)
            custom.append(n)
    return custom

class vis(ast.NodeVisitor):
    def __init__(self):
        self.variables={}
        self.func_sign = {}
        # custom number type to associate float and int
        self.Numtype = [type(1),type(1.1)]

#================================== obtaining variable type =============================   
    def checkBinVariable(self,component,variables, params):
        if isinstance (component, ast.Name):
            if component.id in variables:
                component = variables[component.id]['type']
            else:
                # if unnamed params
                if params is not None and params[0]["hints"]:
                    for tup in params[1:-1]:
                        if component.id == tup[0]:
                           component = tup[1]
                           break    
                elif params is not None and not params[0]["hints"]:
                    component = component
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
            elif isinstance(lefttype,ast.Name) or isinstance(righttype, ast.Name):
                nodetype = "TBC"
            else:
                # assigns None to type when either component used before assignment or types are different thus not recommended
                if (lefttype is None) or (righttype is None):
                    nodetype = [None,0]
                else:
                    # potential change to store the types of individual components
                    nodetype = [None,1]
            return nodetype

    def extract(self,node, variables, funcName=None, returnV = False):
        global reportData

        line= node.lineno
        if not returnV:
            variableName=node.targets[0].id
            nodetype= node.value
        else:
            nodetype = node

        if isinstance(nodetype, ast.BinOp):
            #obtains the types of the function signatures
            if funcName is not None:
                params = self.func_sign[funcName]
            else:
                params = None
            nodetype=self.nestedBin(nodetype,variables,params)
        else:
            if not isinstance (nodetype, ast.Name):
                nodetype = type(ast.literal_eval(nodetype))
            else:
                for name in variables.keys():
                    if nodetype.id == name:
                        nodetype = variables[name]["type"]
                        break
    
        # for errors 
        if isinstance(nodetype, list) and isinstance(nodetype[0], type(None)):
            if returnV:
                reportData.append([line,6])
                return line, nodetype
            else:
                if nodetype[1]==0:
                    reportData.append([variableName, line, 4])
                    nodetype = type(None)
                else:
                    reportData.append([variableName, line, 5])
                    nodetype = type(None)
        if returnV:
            return line, nodetype
        else:
            return variableName, line, nodetype

#======================================= visit functions =======================================
    def visit_Assign(self, node):
        if isinstance(node.value,ast.Call):
            self.Call(node)
        else:
            variableName, line, nodetype =self.extract(node, self.variables)
            self.duplicateCheck(variableName,line,nodetype, self.variables)   

    def visit_FunctionDef(self, node, hints=False):
        sub_variables = {}
        annotations = []
        hints = True
        print("local variables of function",node.name,"when defined:")

        #requires source code to use type hints
        for a in node.args.args:
            try:
                #TODO find alternative for eval
                annotations.append((a.arg, eval(a.annotation.id)))
            except:
                hints = False
                annotations.append(a.arg)        
        try:
            #checks if return value has type hints
            annotations.append(('return type',eval(node.returns.id)))

        except :
            hints = False
            for n in node.body:
                if isinstance(n, ast.Return):
                    returnT=n.value
                    if isinstance(returnT, ast.Call):
                        returnT = self.lookUp(n.value, call=True)
                    annotations.append(('return type',returnT))

        annotations.insert(0, {"hints":hints})
        self.func_sign[node.name]=annotations

        for n in node.body:
            if isinstance(n, ast.Assign):
                variableName, line, nodetype =self.extract(n,sub_variables, node.name)
                self.duplicateCheck(variableName,line,nodetype, sub_variables)  

        print([(k,v) for k,v in sub_variables.items()],"\n")

    def Call(self, node, NestCall = False, NestArg= None):
        global reportData
        if not NestCall:
            arguments = node.value.args
            variableName = node.targets[0].id
            line = node.lineno
            funcName = node.value.func.id
            keywords = node.value.keywords
        else:
            funcName = node.func.id
            keywords = node.keywords
        
        if funcName in self.func_sign:
            parameters = self.func_sign[funcName][1:]
            count = 0
            hints = self.func_sign[funcName][0]["hints"] 
            
            nodetype = parameters[-1][1]
            if hints:
                # performs type checking against parameters and arguments

                # for unassigned arguements ie not doing product(a=1, b=2)
                if len(keywords) == 0:
                    for arg in arguments:
                        #TODO validate for return type 
                        #checks argument to its corresponding parameter while excluding return
                        if type(ast.literal_eval(arg))!= parameters[count][1] and parameters[count][0]!='return type':
                            reportData.append([node.value.func.id, arg.lineno, count, type(ast.literal_eval(arg)), parameters[count][1],2])
                        count+=1
                else:
                    for key in keywords:
                        for pram in parameters:
                            if key.arg == pram[0]:
                                if type(ast.literal_eval(key.value)) != pram[1]:
                                    reportData.append([node.value.func.id, key.arg, node.lineno, type(ast.literal_eval(key.value)), pram[1], 3])

            # updates parameters types with caller arguments
            else:
                Nparam = {}
                # for unassigned arguements ie not doing product(a=1, b=2)
                if len(keywords) == 0:
                    if NestCall:
                        for i in range(len(NestArg)):
                            Nparam[parameters[i]]= NestArg[i][1]
                    else:
                        for arg in arguments:
                            if isinstance(arg, ast.Name) and parameters[-1][0] != 'return type':
                                if arg.id in self.variables:
                                    Nparam[parameters[count]]= self.variables[arg.id]
                            else:
                                Nparam[parameters[count]] = {"type":type(ast.literal_eval(arg)), "line": node.lineno}
                            count+=1
                else:
                    for key in keywords:
                        for p in parameters[:-1]:
                            if key.arg == p:
                                if isinstance(key.value, ast.Name):
                                    if NestCall:
                                        for i in range(len(NestArg)):
                                            if p == NestArg[i][0]:
                                                Nparam[p]= NestArg[i][1]
                                                break
                                    else:
                                        Nparam[p] = self.variables[key.value.id]
                                else:
                                    Nparam[p] = {"type":type(ast.literal_eval(key.value)), "line": node.lineno}
                #type checks the updated variables used in the function
                self.revisit_method(Nparam, funcName) 

            #checks data type of return type
            if nodetype!=None:
                if isinstance(nodetype, ast.Name):
                    if nodetype.id in Nparam:
                        nodetype = Nparam[nodetype.id]["type"]
                    elif nodetype.id in self.variables:
                        nodetype = self.variables[nodetype.id]["type"]
                elif isinstance(nodetype, ast.BinOp):
                    nodetype=self.extract(nodetype,Nparam, returnV=True)
                elif isinstance(nodetype, ast.Call):
                     # give call arguments its data type
                    callArgs = nodetype.args
                    ArgT=[]
                    for x in callArgs:
                        # if the arguments are variables in the previous function
                        if x.id in Nparam:
                            ArgT.append((x.id,Nparam[x.id]))
                    nodetype = self.Call(nodetype, NestCall=True,NestArg= ArgT)

            # if in a nested call, returns the return type of the function
            if NestCall:
                return nodetype              
            self.duplicateCheck(variableName,line,nodetype, self.variables) 
                
        else:
            nodetype = self.lookUp(funcName)
            if nodetype == None:
                print("function not defined rn or its a built in function")
            else:
                self.duplicateCheck(variableName,line,nodetype, self.variables) 

    def lookUp(self,target, call = False):
        if call:
            if target.func.id in built_funcs:
                return built_funcs[target.func.id]
            #return as a call object 
            elif target.func.id in self.func_sign:
                return target
        else:
            if target in built_funcs:
                return built_funcs[target] 
            elif target in self.func_sign:
                return self.func_sign[target]
            return None

    def revisit_method(self, sub_variables, target):
        global tree
        for elem in tree[0].item.body:
            if isinstance(elem, ast.FunctionDef) and elem.name == target:
                for n in elem.body:
                    if isinstance(n, ast.Assign):
                        variableName, line, nodetype =self.extract(n,sub_variables, target)
                        self.duplicateCheck(variableName,line,nodetype, sub_variables) 
    
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
                    #updates variable when type match
                    if nodetype == variablesdict[k]['type'] or (nodetype in self.Numtype and variablesdict[k]['type'] in self.Numtype):
                        variablesdict[name]= {'type':nodetype,'line':line}
                    else:
                        reportData.append([name, variablesdict[k]['line'], line, variablesdict[k]['type'], nodetype, 1])
                    break
        # adds variable to the dictionary
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
    6) type mismatch for binary operations not recommended (return ver)
    '''
    if len(reportData)!=0:
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
            
            elif data[-1] == 5:
                print(f"The components of '{data[0]}' on line {data[1]} performs a maths operation on different types and is not recomended ")
            
            elif data[-1] == 6:
                print(f"components of the return on line {data[0]} performs a maths operation on different types and is not recomended ")
    else:
        print("No issues found")


# Program start

reportData = []

tree = buildTree()
c = vis()
root = tree[0].item
for n in root.body:
    c.visit(n)
print("\nGlobal variables")
for k,v in c.variables.items():
    print(k,':',v)

print("\nFuncion signatures")
for k,v in c.func_sign.items():
    print(k,":",v)

print("\nPotential errors found:")
report(reportData)

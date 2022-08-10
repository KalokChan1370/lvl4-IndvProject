import ast
from built_func_type import funcs as built_funcs
import astpretty
import time

class Node:
    def __init__(self, item):
        self.item = item
        self.children = []
    
    def add_children(self, children):
        self.children = children 

def buildTree(file):
    custom = []
    with open(file,'r') as f:
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
        self.classDef = {}
        self.objectAttr={}
        # custom number type to associate float and int
        self.Numtype = [type(1),type(1.1)]

#================================== obtaining variable type =============================   
    def checkBinVariable(self,component,variables, params, definedObj = None):
        if isinstance (component, ast.Name):
            
            if component.id in variables:
                try:
                    component = variables[component.id]['type']
                except:
                    component = component
            else:
                # if unnamed params
                if params is not None and params[0]["hints"]:
                    for tup in params[1:]:
                        if component.id == tup[0]:
                            component = tup[1]
                            break    
                elif params is not None and not params[0]["hints"]:
                    component = component
                else:
                    # component contains an uninitialized variable
                    component = None
        elif isinstance(component, ast.Attribute):
            if definedObj != None:
                if component.attr in self.objectAttr[definedObj]:
                    component = self.objectAttr[definedObj][component.attr]['type']
            else:
                component = ast.BinOp
        else:
            component = type(ast.literal_eval(component)) 
        return component

    def nestedBin(self,nodetype, variables, variableNode=None,params= None,definedObj = None): 
        global reportData
        if isinstance(nodetype.left, ast.BinOp):
            lefttype=self.nestedBin(nodetype.left, variables,variableNode,params, definedObj)
        else:
            leftCom = nodetype.left
            lefttype = self.checkBinVariable(leftCom,variables,params,definedObj)

        if isinstance(nodetype.right, ast.BinOp):
            righttype=self.nestedBin(nodetype.right, variables,variableNode,params, definedObj)
        else:
            rightCom = nodetype.right
            righttype = self.checkBinVariable(rightCom,variables,params,definedObj)

        if lefttype == righttype:
            if lefttype == type("str") and not isinstance(nodetype.op, ast.Add):
                reportData.append((variableNode.id,variableNode.lineno,8))
                nodetype = type(None)
            else:
                nodetype = lefttype
        # when components are both numbers ie int and float convert to int
        elif lefttype in self.Numtype and righttype in self.Numtype:
            nodetype = type(1)
        elif isinstance(lefttype,ast.Name) or isinstance(righttype, ast.Name):
            nodetype = variableNode
        elif lefttype==ast.BinOp or righttype==ast.BinOp:
            nodetype = ast.BinOp
        else:
            # assigns None to type when either component used before assignment or types are different thus not recommended
            if (lefttype is None) or (righttype is None):
                nodetype = [None,0]
            else:
                nodetype = [None,1]
        return nodetype

    def extract(self,node, variables, funcName=None, returnV = False, className= None, definedObj = None, initial =False):
        global reportData

        line= node.lineno
        if not returnV:
            if not isinstance(node.targets[0], ast.Attribute):
                variableName=node.targets[0].id
            else:
                variableName = node.targets[0].attr
            nodetype= node.value
        else:
            nodetype = node

        if isinstance(nodetype, ast.BinOp):
            #obtains the types of the function signatures
            if funcName is not None:
                if className is not None:
                    params = self.classDef[className][funcName]
                else:
                    params = self.func_sign[funcName]
            else:
                params = None
            if returnV:
                nodetype=self.nestedBin(nodetype,variables=variables,params=params,definedObj=definedObj)
            else:
                nodetype=self.nestedBin(nodetype,variables,node.targets[0],params,definedObj)
        else:
            found = False
            if isinstance(nodetype, ast.Attribute):
                if not initial:
                    if definedObj!= None:
                        for attr, value in self.objectAttr[definedObj].items():
                            if nodetype.attr == attr:
                                found= True
                                nodetype = value['type']
                                break
                        if not found:
                            nodetype=type(None)
                            reportData.append((variableName,line, 4))
                else:
                    nodetype=nodetype
            elif isinstance (nodetype, ast.Name):
                if not initial:
                    for name in variables.keys():
                        if nodetype.id == name:
                            found= True
                            nodetype = variables[name]["type"]
                            break
                    if not found:
                        nodetype = type(None)
                        reportData.append((variableName,line, 4))
                else:
                    nodetype=nodetype
            elif isinstance(nodetype, ast.Subscript):
                nodetype = "subscript"
            else:
                nodetype = type(ast.literal_eval(nodetype))
                
        # for errors 
        if isinstance(nodetype, list) and isinstance(nodetype[0], type(None)):
            if returnV:
                if nodetype[1]==0:
                    reportData.append([line,9])
                else:
                    reportData.append([line,6])
            else:
                if nodetype[1]==0:
                    reportData.append([variableName, line, 4])
                else:
                    reportData.append([variableName, line, 5])
            nodetype = type(None)
        if returnV:
            return nodetype
        else:
            if isinstance(node.targets[0], ast.Attribute) and definedObj!=None:
                self.duplicateCheck(variableName,line,nodetype, self.objectAttr[definedObj])
            return variableName, line, nodetype

    def getFuncName(self,node):
        try:
            funcParse = node.value.func
            if isinstance(funcParse, ast.Attribute):
                object = funcParse.value.id
                #checks if caller is from a class
                if object in self.variables and self.variables[object]['type'] in self.classDef:
                    className = self.variables[object]['type']
                    #checks if func exists
                    if funcParse.attr in self.classDef[className]:

                        return className,funcParse.attr, object
                else:
                    return None
            else:
                return funcParse.id
        except:
            return node.func.id

       # returns the data type of a bulit-in function
    def returnLookUp(self,target, call = False):
        if target != None:
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
                elif "class_"+target in self.classDef:
                    return "class_"+target
            return None

    def revisit_method(self, sub_variables, target):
        global tree
        for elem in tree[0].item.body:
            if isinstance(elem, ast.ClassDef) and elem.name == target[0][6:]:
                for funcDef in elem.body:
                    if isinstance(funcDef, ast.FunctionDef) and funcDef.name == target[1]:
                        for n in funcDef.body:
                            if isinstance(n, ast.Assign):
                                self.visit_Assign(n, sub_variables, target[1],target[0], target[2])

            elif isinstance(elem, ast.FunctionDef) and elem.name == target:
                for n in elem.body:
                    if isinstance(n, ast.Assign):
                        self.visit_Assign(n, sub_variables, target)
    
#======================================= visit functions =======================================
    def visit_Assign(self, node, variableList = None, funcName = None, className = None, definedObj= None, initial = False):
        if isinstance(node.value,ast.Call):
            if variableList == None:
                variableList = self.variables
                NestCall = False
                funcSign = None
                variableName = None
            # function call within a function
            if funcName != None:
                try:
                    funcSign = self.func_sign[funcName][1:]
                    NestCall = True 
                    variableName = node.targets[0].id
                    initial= True
                except:
                    NestCall = False
                    variableName = None
                    funcSign = None
            self.Call(node, variableList = variableList,NestCall = NestCall,NestArg= funcSign,variableName=variableName, initial=initial)
        else:
            if variableList == None:
                variableList = self.variables
            variableName, line, nodetype =self.extract(node, variableList, funcName=funcName,className=className,definedObj=definedObj, initial=initial)
            self.duplicateCheck(variableName,line,nodetype, variableList)  
    
    def funcIf(self,n, sub_variables, function = None, className=None, initial = False):
        body = n.body
        for stmt in body:
            if isinstance(stmt, ast.Assign):
                self.visit_Assign(stmt, variableList=sub_variables, funcName = function, className = className, initial = initial)
    
    def visit_ClassDef(self, node):
        className="class_"+node.name 
        self.classDef[className] ={}
        for elem in node.body:
            if isinstance(elem, ast.FunctionDef):
                if elem.name != '__init__':
                    self.visit_FunctionDef(elem, classDef= True, className=className)
                else:
                    self.visit_FunctionDef(elem, classDef= True, className=className, init=True)
        

    def visit_FunctionDef(self, node, hints=False, classDef=False, className = None, init=False):
        sub_variables = {}
        annotations = []
        hints = True
        print("\nlocal variables of function '"+node.name+"' when defined:")
        
       #requires source code to use type hints
        for a in node.args.args:
            if a.arg == "self":
                continue
            try:
                 #if hints used
                
                annotations.append((a.arg, eval(a.annotation.id)))
            except:
                hints = False
                annotations.append(a.arg)   
                
        annotations.insert(0, {"hints":hints})
        
        if classDef:
            if className in self.classDef:
                if init:
                    self.classDef[className]['__init__']= annotations
                else:
                    self.classDef[className][node.name]= annotations
        else:
            self.func_sign[node.name]=annotations

        for n in node.body:
            if isinstance(n, ast.Assign):
                self.visit_Assign(n, sub_variables, node.name, className, initial = True)
            if isinstance(n,ast.If):
                self.funcIf(n, sub_variables, node.name, className, initial = True)

        # gets the return type if applicable
        try:
            #if hints used
            annotations.append(('return type',eval(node.returns.id)))
        except :
            for n in node.body:
                # consider other return types ie bin op and lists
                if isinstance(n, ast.Return):
                    hints = False
                    returnT=n.value
                    if isinstance(returnT, ast.Call):
                        returnT = self.returnLookUp(n.value, call=True)
                    elif isinstance(returnT, ast.Name):
                        if returnT.id in sub_variables:
                            returnT = sub_variables[returnT.id]['type']
                    elif isinstance(returnT, ast.Attribute) or isinstance(returnT, ast.BinOp):
                        returnT = returnT
                    else:
                        try:
                            returnT=type(ast.literal_eval(returnT))
                        except:
                            returnT = type(returnT)
                    annotations.append(('return type',returnT))
                    break
        
        annotations[0]={"hints":hints}
        
        if classDef:
            if className in self.classDef:
                if init:
                    self.classDef[className]['__init__']= annotations
                else:
                    self.classDef[className][node.name]= annotations
        else:
            self.func_sign[node.name]=annotations

        for k,v in sub_variables.items():
            print(k,":", {'type':v['type'].id,'line':v['line']} if isinstance(v['type'],ast.Name) else v)
        
    def callHints(self,node, funcName, variableName, arguments, parameters, keywords,NestCall,NestArg, initial, variableList):
        global reportData

        count = 0
        # for unassigned arguements ie not doing product(a=1, b=2)
        if len(keywords) == 0:
            if NestCall:
                if initial:
                    for arg in arguments:
                        #obtains the data type of the arguments
                        if isinstance(arg, ast.Name):
                            if arg.id in variableList:
                                argType = variableList[arg.id]['type']
                            #accounts type hints in the function signature in the parent function
                            elif type(NestArg[0])==type(()):
                                for i in range(len(NestArg)):
                                    if arg.id == NestArg[i][0]:
                                        argType = NestArg[i][1]
                                        break
                            elif type(NestArg[0]) != type(()):
                                if arg.id in NestArg:
                                    argType= 'TBC'
                            else:
                                reportData.append([variableName, arg.lineno,4])
                                break
                        else:
                            argType = type(ast.literal_eval(arg))

                        # compares the argument to its corresponding parameter
                        if argType=='TBC':
                            count+=1
                            continue
                        elif argType != parameters[count][1] and parameters[count][0]!='return type':
                            reportData.append([arg.lineno, count, argType, parameters[count][1],2])
                            count+=1
                else:    
                    for arg in NestArg:
                        argType = arg[1]['type']
                        if argType != parameters[count][1] and parameters[count][0]!='return type':
                            reportData.append([arg[1]["line"], count, argType, parameters[count][1],2])
                        count+=1

            # checks non nested calls arguments and parameters            
            else:      
                for arg in arguments:
                    if isinstance(arg, ast.Name):
                        if arg.id in self.variables:
                            argType = self.variables[arg.id]['type']
                        else:
                            reportData.append([variableName, arg.lineno,4])
                            break
                    else:
                        argType = type(ast.literal_eval(arg))
                    #checks argument to its corresponding parameter while excluding return
                    if argType != parameters[count][1] and parameters[count][0]!='return type':
                        reportData.append([arg.lineno, count, argType, parameters[count][1],2])
                    count+=1



        # check between args and params with keywords            
        else:
            if NestCall:
                if initial:
                    for key in keywords:
                        for param in parameters:
                            if key.arg == param[0]:
                                if isinstance(key.value, ast.Name):
                                    #finds if variable is in the list of defined variables
                                    if key.value.id in variableList:
                                        keyType = variableList[key.value.id]['type']
                                    elif type(NestArg[0])==type(()):
                                        for i in range(len(NestArg)):
                                            if key.value.id == NestArg[i][0]:
                                                keyType = NestArg[i][1]
                                                break
                                    elif type(NestArg[0]) != type(()):
                                        if key.value.id in NestArg:
                                            keyType= 'TBC'
                                    else:
                                        reportData.append([variableName, key.value.lineno, 4]) 
                                        break
                                else:
                                    keyType = type(ast.literal_eval(key.value))

                                if keyType =='TBC':
                                    continue
                                elif keyType != param[1]:
                                    reportData.append([key.arg, node.lineno, keyType, param[1], 3])
                                    break

                else:
                    keywords= NestArg
                    for key in keywords:
                        for param in parameters:
                            if key[0] == param[0]:
                                if key[1]['type']!=param[1]:
                                    reportData.append([key[0],key[1]['line'],key[1]['type'],param[1],3])
                                break
            else:
                for key in keywords:
                    for param in parameters:
                        if key.arg == param[0]:
                            if isinstance(key.value, ast.Name):
                                #finds if variable is in the list of defined variables
                                if key.value.id in self.variables:
                                    keyType = self.variables[key.value.id]['type']
                                else:
                                    reportData.append([variableName, key.value.lineno, 4]) 
                                    break
                            else:
                                keyType = type(ast.literal_eval(key.value))
                        
                            if keyType != param[1]:
                                reportData.append([key.arg, node.lineno, keyType, param[1], 3])
                            break
    
    # updates parameters types with caller arguments
    def callNoHints(self,node, funcName, variableName, arguments, parameters, keywords,NestCall,NestArg,initial, variableList):
        count = 0
        Nparam = {}
        
        # for unassigned arguements ie not doing product(a=1, b=2)
        if len(keywords) == 0:
            if NestCall:
                # when call occurs during function definition ie initialising a function
                if initial:
                    for arg in arguments:
                        if isinstance(arg, ast.Name) and parameters[count][0] != 'return type':
                            if arg.id in variableList:
                                Nparam[parameters[count]] = variableList[arg.id]
                            elif type(NestArg[0]) == type(()):
                                for i in range(len(NestArg)):
                                    if arg.id == NestArg[i][0]:
                                        Nparam[parameters[count]]= NestArg[i][1]
                                    break
                            elif type(NestArg[0]) != type(()):
                                if arg.id in NestArg:
                                    Nparam[parameters[count]]= arg.id
                            else:
                                reportData.append([variableName, arg.lineno, 4]) 
                            break
                        else:
                            Nparam[parameters[count]] = {"type":type(ast.literal_eval(arg)), "line": node.lineno}               
                        count+=1
                else:
                    for i in range(len(NestArg)):
                        Nparam[parameters[i]]= NestArg[i][1]
            else:
                for arg in arguments:
                    if isinstance(arg, ast.Name) and parameters[count][0] != 'return type':
                        if arg.id in self.variables:
                            Nparam[parameters[count]]= self.variables[arg.id]
                        else:
                    
                            reportData.append([variableName, arg.lineno, 4]) 
                            break
                    else:
                        Nparam[parameters[count]] = {"type":type(ast.literal_eval(arg)), "line": node.lineno}
                    count+=1
        else:
            if NestCall:
                if initial:
                    for key in keywords:
                        for p in parameters[:-1]:
                            if key.arg == p:
                                if isinstance(key.value, ast.Name):
                                    if key.value.id in variableList:
                                        Nparam[p] = variableList[key.value.id]
                                    elif type(NestArg[0]) == type(()):
                                        for i in range(len(NestArg)):
                                            if key.value.id == NestArg[i][0]:
                                                Nparam[p]= NestArg[i][1]
                                            break
                                    elif type(NestArg[0]) != type(()):
                                        if key.value.id in NestArg:
                                            Nparam[p]= key.value.id
                                    else:
                                        reportData.append([variableName,key.value.lineno, 4])
                                        return None                

                                else:
                                    Nparam[p] = {"type":type(ast.literal_eval(key.value)), "line": node.lineno}
                                break
                else:
                    for key in NestArg:
                        for p in parameters[:-1]:
                                if p == key[0]:
                                    Nparam[p]= key[1]
                                    break
            else:
                for key in keywords:
                    for p in parameters[:-1]:
                        if key.arg == p:
                            if isinstance(key.value, ast.Name):
                                if key.value.id in self.variables:
                                    Nparam[p] = self.variables[key.value.id]
                                else:
                                    reportData.append([variableName,key.value.lineno, 4])
                                    return None
                            else:
                                Nparam[p] = {"type":type(ast.literal_eval(key.value)), "line": node.lineno}
                            break

        #type checks the updated variables used in the function
        self.revisit_method(Nparam, funcName)
        return Nparam

    def Call(self, node,variableList, NestCall = False, NestArg= None, variableName = None, initial = False):
        global reportData

        funcName = self.getFuncName(node)
        line = node.lineno
        if not NestCall:
            variableName = node.targets[0].id 

        if isinstance(node, ast.Assign):
            keywords = node.value.keywords
            arguments = node.value.args
        else:
            keywords = node.keywords
            arguments= NestArg

        if funcName in self.func_sign or isinstance(funcName, tuple):
            try:
                parameters = self.classDef[funcName[0]][funcName[1]][1:]
                hints = self.classDef[funcName[0]][funcName[1]][0]["hints"]
            except:
                parameters = self.func_sign[funcName][1:]
                hints = self.func_sign[funcName][0]["hints"] 
                        
            returnType = parameters[-1][1]
        
            if hints:
                # performs type checking against parameters and arguments
                self.callHints(node, funcName, variableName, arguments, parameters, keywords,NestCall,NestArg, initial, variableList)

            # No Hints                 
            else:
                Nparam = self.callNoHints(node, funcName,variableName, arguments, parameters, keywords,NestCall,NestArg,initial, variableList)
            
            #obtains data type of return type
            if returnType!=None:
                # for functions without type hints and returns a variable or a object attribute
                if isinstance(returnType, ast.Name) or isinstance(returnType, ast.Attribute):
                    if isinstance(returnType,ast.Attribute):
                        nodeName = returnType.attr
                        if nodeName in self.objectAttr[funcName[2]]:
                            returnType = self.objectAttr[funcName[2]][nodeName]["type"]
                        else:
                            reportData.append([line,9])
                            returnType = None
                    else:
                        nodeName = returnType.id
                        if Nparam == None:
                            reportData.append([line,9])
                            returnType = None
                        else:
                            if nodeName in Nparam:
                                returnType = Nparam[nodeName]["type"]
                            elif nodeName in self.variables:
                                returnType = self.variables[nodeName]["type"]
                            else:
                                reportData.append([line,9])
                                returnType = None
                       
                elif isinstance(returnType, ast.BinOp):
                    returnType=self.extract(returnType,Nparam, returnV=True)
                elif isinstance(returnType, ast.Call):
                     # give call arguments its data type
                    ArgT=[]
                    if len(returnType.keywords) == 0: 
                        callArgs = returnType.args
                        nestsign = self.func_sign[returnType.func.id][1:-1]
                        count= 0
                        for x in callArgs:
                            # if the arguments are variables in the previous function
                            checker= False
                            count+=1
                            if isinstance(x , ast.Name):
                                if x.id in Nparam:
                                    ArgT.append((x.id,{'type':Nparam[x.id]['type'],'line': returnType.lineno}))
                                else:
                                    for param in parameters:
                                        if x.id in param[0]:
                                            value= {'type':param[1], 'line':returnType.lineno}
                                            ArgT.append((x.id,value))
                                            checker= True
                                            break
                                    if not checker:
                                        reportData.append((x.id, returnType.lineno,4))
                            else:
                                constant ={'type':type(ast.literal_eval(x)),
                                    'line': returnType.lineno}
                                ArgT.append((nestsign[count-1],constant))
                                
                    else:
                        callArgs = returnType.keywords
                        for x in callArgs:
                            if isinstance(x.value, ast.Name):
                                if x.value.id in Nparam:
                                    ArgT.append((x.arg,{'type':Nparam[x.value.id]['type'],'line': returnType.lineno}))
                                else:
                                    reportData.append((x.arg, returnType.lineno,4))
                            else:
                                constant ={'type':type(ast.literal_eval(x.value)),
                                 'line': returnType.lineno}
                                ArgT.append((x.arg,constant))
                    returnType = self.Call(returnType,variableList, NestCall=True,NestArg= ArgT, variableName=variableName)

            # if in a nested call, returns the return type of a nested call
            if NestCall:
                if initial:
                    self.duplicateCheck(variableName,line,returnType, variableList)
                return returnType     
            
            self.duplicateCheck(variableName,line,returnType, variableList) 
                
        else:
            returnType = self.returnLookUp(funcName)
            if returnType == None:
                reportData.append((line, 7))
            elif isinstance(returnType, str):
                if "class_" in returnType:
                    parameters = self.classDef[returnType]['__init__'][1:]
                    hints = self.classDef[returnType]['__init__'][0]['hints']
                    initial=True
                    if hints:
                        self.callHints(node, funcName, variableName, arguments, parameters, keywords,NestCall,NestArg, initial, variableList)
                    else:
                        parameters = self.callNoHints(node, funcName,variableName, arguments, parameters, keywords,NestCall,NestArg, initial, variableList)
                    self.objectAttr[variableName] =  parameters
                    self.duplicateCheck(variableName,line,returnType, variableList) 

            else:
                self.duplicateCheck(variableName,line,returnType, variableList) 

#======================================= validation ==============================

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
        return dup, nodetype

def report(reportData):
    
    '''
    error types-
    1) Data types of variables mismatch
    2) Caller arguments and function parameters mismatch (Unamed)
    3) Caller arguments and function parameters mismatch (Named)
    4) uninitialized variable
    5) type mismatch for binary operations not recommended
    6) type mismatch for binary operations not recommended (return ver)
    7) function node undefined
    8) an operand other than add is used for Strings
    9) uninitialized variable (return ver)
    '''
    
    if len(reportData)!=0:
        filtered = []
        for x in reportData:
            if x not in filtered:
                filtered.append(x)

        for data in filtered:
            if data[-1] == 1:
                print(f"Data type for '{data[0]}' at {data[1]} and at {data[2]} mismatch, with types {data[3]} and {data[4]} respectively")
            
            elif data[-1] == 2:
                print(f"The function called on line {data[0]} has a data type of {data[2]} at position '{data[1]}' but mismatches",\
                    f"with its corresponding type in the function signature of {data[3]}")
            
            elif data[-1] == 3:
                print(f"The function called on line {data[1]} has a data type of {data[2]} for argument '{data[0]}' but mismatches",\
                    f"with its corresponding type in the function signature of {data[3]}")
            
            elif data[-1] == 4:
                print(f"Variable '{data[0]}' found at {data[1]} has no data type as it contains an uninitialized variable")
            
            elif data[-1] == 5:
                print(f"The components of '{data[0]}' on line {data[1]} performs a binary operation on different types and is not recomended/ supported")
            
            elif data[-1] == 6:
                print(f"The components of the return on line {data[0]} performs a binary operation on different types and is not recomended/ supported")
            
            elif data[-1] == 7:
                print(f"The function called on line {data[0]} is either undefined, undefined in the class object or is a built-in function not in the pre-loaded list")
            
            elif data[-1] == 8:
                print(f"The variable {data[0]} at line {data[1]} uses a binary operand other than add for its string components and is not allowed")
    
            elif data[-1] == 9:
                print(f"The return value found at line {data[0]} has no data type as it contains an uninitialized variable")
    else:
        print("No issues found")

# Program start

reportData = []
filename = input("Input source code's file name to be tested... ")
print("-----"*10)
print("Start of analysis")
start_time= time.time()

#building the AST
tree = buildTree(filename)
c = vis()
root = tree[0].item
for n in root.body:
    c.visit(n)

if len(c.func_sign)!=0:
    print("\nFunction signatures:")
    for k,v in c.func_sign.items():
        print(k,":",v)

if len(c.classDef)!=0:
    print("\nClass Definitions:")
    for k,v in c.classDef.items():
        print(k,":")
        for l,m in v.items():
            print(f"\t {l} :{m}")

print("\nGlobal variables:")
for k,v in c.variables.items():
    print(k,':',v)

if len(c.objectAttr)!=0:
    print("\nDefined object attributes:")
    for k,v in c.objectAttr.items():
        print(k,":",v)

print("\nPotential errors found:")
report(reportData)
print("-----"*10)
print("Analysis completed in %f seconds" % (time.time()-start_time))
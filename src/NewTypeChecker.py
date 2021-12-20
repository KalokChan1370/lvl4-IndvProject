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
                # if a variable 
                if params is not None:
                    for tup in params[:-1]:
                        if component.id == tup[0]:
                           component = tup[1]
                           break
                else:
                    print(component.id, "used before assigned")
        else:
            component = type(ast.literal_eval(component)) 
        return component

    def nestedBin(self,nodetype, variables, params= None):
        if isinstance(nodetype.left, ast.BinOp):
            return self.nestedBin(nodetype.left, variables,params)
        else:
            lefttype = nodetype.left
            righttype = nodetype.right
            lefttype = self.checkBinVariable(lefttype,variables,params)
            righttype = self.checkBinVariable(righttype,variables,params)
            if lefttype == righttype:
                nodetype = lefttype
            elif lefttype in self.Numtype and righttype in self.Numtype:
                nodetype = type(1)
            else:
                print("maths operation components types are different not recomended")
            return nodetype

    def extract(self,node, variables, funcName=None):
        variableName=node.targets[0].id
        line= node.lineno
        nodetype= node.value
        if isinstance(nodetype, ast.BinOp):
            if funcName is not None:
                params = self.func_sign[funcName]
            else:
                params = None
            nodetype=self.nestedBin(nodetype,variables,params)
        else:
            nodetype = type(ast.literal_eval(nodetype))
        return variableName, line, nodetype

#================================== end of obtaining variable type =============================
#======================================= visit functions =======================================
    def visit_Assign(self, node):
        if isinstance(node.value,ast.Call):
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
            if a.annotation !=None:
                #TODO find alternative for eval
                annotations.append((a.arg, eval(a.annotation.id)))

        if node.returns != None:
            annotations.append(('return type',eval(node.returns.id)))
        self.func_sign[node.name]=annotations

        for n in node.body:
            if isinstance(n, ast.Assign):
                variableName, line, nodetype =self.extract(n,sub_variables, node.name)
                self.duplicateCheck(variableName,line,nodetype, sub_variables) 
        
        # print([k for k in sub_variables.keys()])
        print("-----"*10,"function def end","-----"*10,)

    def Call(self, node):
        arguments = node.value.args
        print(f"-----"*10,node.value.func.id, "caller start","-----"*10)
        parameters = self.func_sign[node.value.func.id]
        count = 0
        # for unassigned arguements ie not doing product(a=1, b=2)
        if len(node.value.keywords) == 0:
            for arg in arguments:
                #TODO validate for return type 
                if type(ast.literal_eval(arg))!= parameters[count][1] and parameters[count][0]!='return type':
                    print(f"data type {type(ast.literal_eval(arg))} for argument at position '{count}' on line {arg.lineno} does not match the parameters of function: {node.value.func.id} ")
                count+=1
        else:
            for key in node.value.keywords:
                for pram in parameters:
                    if key.arg == pram[0]:
                        if type(ast.literal_eval(key.value)) != pram[1]:
                            print(f"data type {type(ast.literal_eval(key.value))} for argument '{key.arg}' on line {node.lineno} does not match the parameters of function: {node.value.func.id}")
        
        #checks data type of return type
        if parameters[-1][0]=='return type':
            variableName = node.targets[0].id
            line = node.lineno
            nodetype = parameters[-1][1]
            self.duplicateCheck(variableName,line,nodetype, self.variables)  
        print("-----"*10,"caller end","-----"*10,"\n")

    #TODO: differentiate between mismatches ie 
    #return data type and normal assignment
    def duplicateCheck(self,name,line, nodetype, variablesdict):
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
                        print(f"data type for:'{name}' at {variablesdict[k]['line']} and at {line}: mismatch")
                    break
            if not dup:
                variablesdict[name]= {'type':nodetype,'line':line}
        else:
            variablesdict[name]= {'type':nodetype,'line':line}
#======================================= end of visit functions ==============================

# Program start
with open("test.py",'r') as f:
    content = f.read()
    module = ast.parse(content)
    
    c=vis()
      
    for node in module.body:
        c.visit(node)

    print("Global variables")
    for k,v in c.variables.items():
        print(k,':',v)

    print("Funcion signatures")
    for k,v in c.func_sign.items():
        print(k,":",v)


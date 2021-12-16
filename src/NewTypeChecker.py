import ast
import astpretty

class vis(ast.NodeVisitor):
    def __init__(self):
        self.variables={}
        self.func_sign = {}

    def extract(self,node):
        variableName=node.targets[0].id
        nodetype= node.value
        line= node.lineno
        return variableName, line, nodetype

    def visit_Assign(self, node):
        if isinstance(node.value,ast.Call):
            self.Call(node)
        else:
            variableName, line, nodetype =self.extract(node)
            duplicateCheck(variableName,line,nodetype, self.variables)   

    # assumes all variables used are local
    def visit_FunctionDef(self, node):
        sub_variables = {}
        annotations = []

        print("variables in function:", node.name)

        #requires source code to use type hints
        for a in node.args.args:
            if a.annotation !=None:
                # eval not recommended
                annotations.append((a.arg, eval(a.annotation.id)))

        #TODO needs amending due to using function without type hint
        if node.returns != None:
            annotations.append(('return type',node.returns.id))
        self.func_sign[node.name]=annotations

        for n in node.body:
            if isinstance(n, ast.Assign):
                variableName, line, nodetype =self.extract(n)
                duplicateCheck(variableName,line,nodetype, sub_variables) 
        
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
            duplicateCheck(variableName,line,nodetype, self.variables)  
        print("-----"*10,"caller end","-----"*10,"\n")

#TODO:Need to check about binary operations for assignments ie 
#  a=b+c, a="hello" + 3, returns match
#TODO: differentiate between mismatches ie 
#return data type and normal assignment
def duplicateCheck(name,line, nodetype, variablesdict):
    dup = False
    if len(variablesdict) != 0:
        for k,v in variablesdict.items():
            if name == k:
                dup = True 
                if isinstance(nodetype, variablesdict[k]['type']):
                    #updates variable position when type match
                    variablesdict[name]= {'type':type(nodetype),'line':line}
                else:
                    print(f"data type for:'{name}' at {variablesdict[k]['line']} and at {line}: mismatch")
                break
        if not dup:
            variablesdict[name]= {'type':type(nodetype),'line':line}
    else:
        variablesdict[name]= {'type':type(nodetype),'line':line}


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


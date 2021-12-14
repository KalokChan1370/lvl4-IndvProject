import ast
import astpretty

class vis(ast.NodeVisitor):
    def __init__(self):
        self.variables=[]
        self.func_sign = {}

    def visit_Assign(self, node):
        if isinstance(node.value,ast.Call):
            self.Call(node)
        duplicateCheck(node, self.variables)   

    # assumes all variables used are local
    def visit_FunctionDef(self, node):
        sub_variables = []
        annotations = []

        print("variables in function:", node.name)

        #requires source code to use type hints
        for a in node.args.args:
            if a.annotation !=None:
                # eval not recommended
                annotations.append((a.arg, eval(a.annotation.id)))
        if node.returns != None:
            annotations.append(('return type',eval(node.returns.id)))
        self.func_sign[node.name]=annotations

        for n in node.body:
            if isinstance(n, ast.Assign):
                duplicateCheck(n,sub_variables)
        
        print([x.targets[0].id for x in sub_variables])
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
            dup= False
            name = node.targets[0].id
            if len(self.variables)!=0:
                for x in self.variables:
                    if name == x.targets[0].id:
                        dup = True 
                        if isinstance(parameters[-1][1], type(x.value)):
                            self.variables[name]=parameters[-1][1]
                        else:
                            print(f"return value data type for function call '{node.value.func.id}' does not match with current data type of '{name}'")
                        break
        print("-----"*10,"caller end","-----"*10,"\n")

#TODO:Need to check about binary operations for assignments ie 
#  a=b+c, a="hello" + 3, returns match
#TODO: change how list is stored, dont need to store the whole node
def duplicateCheck(new, variabelsList):
    dup = False
    name = new.targets[0].id
    if len(variabelsList) != 0:
        for x in variabelsList:
            if name == x.targets[0].id:
                dup = True 
                if isinstance(new.value, type(x.value)):
                    #updates variable position when type match
                    variabelsList[variabelsList.index(x)]= new
                else:
                    print(f"data type for:'{new.targets[0].id}' at {x.lineno} and at {new.lineno}: mismatch")
                break
        if not dup:
            variabelsList.append(new)
    else:
        variabelsList.append(new)


# Program start
with open("test.py",'r') as f:
    content = f.read()
    module = ast.parse(content)
    
    c=vis()
      
    for node in module.body:
        c.visit(node)

    print("Global variables")
    print([x.targets[0].id for x in c.variables])

    print("Funcion signatures")
    for k,v in c.func_sign.items():
        print(k,":",v)


import ast

variables = []

# class vis(ast.NodeVisitor):
#     def visit_Assign(self, node):
#         for target in node.targets:
#             print(target)

def duplicateCheck(new):
    dup = False
    name = new.targets[0].id
    if len(variables) != 0:
        for x in variables:
            if name == x.targets[0].id:
                dup = True 
                if isinstance(new.value, type(x.value)):
                    print(f"data type for {new.targets[0].id} at {x.lineno} and at {new.lineno}: match")
                else:
                    print(f"data type for {new.targets[0].id} at {x.lineno} and at {new.lineno}: mismatch")
                break
        if not dup:
            variables.append(new)
    else:
        variables.append(new)

with open("test.py",'r') as f:
    content = f.read()
    module = ast.parse(content)

    # alternate method to find all assignments
    # c=vis()
    # c.visit(module)
    # for x in variables:
    #     print(x.value)
    for node in module.body:
        if isinstance(node, ast.Assign):
            duplicateCheck(node)

    print([x.targets[0].id for x in variables])

